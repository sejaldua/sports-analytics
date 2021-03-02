from lxml import html
import requests, re, math
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import os
import glob
import csv
import matplotlib.pyplot as plt
plt.style.use('ggplot')

def scrape_team_abbrev():
    page = "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations"
    tree = requests.get(page).content
    soup = BeautifulSoup(tree, 'lxml')
    table = soup.find_all('table')[0]
    df = pd.read_html(table.prettify())[0]
    fixes = {'BKN': 'BRK', 'CHA': 'CHO', 'PHX': 'PHO'}
    for index, row in df.iterrows():
        if index > 0:
            team_name = row[list(df.columns)[1]]
            abbrev = row[list(df.columns)[0]]
            if abbrev in fixes.keys():
                team_info[team_name] = {'abbrev': fixes[abbrev]}
            else:
                team_info[team_name] = {'abbrev': abbrev}

def scrape_win_rate():
    page = "https://www.basketball-reference.com/leagues/NBA_2020_standings.html"
    tree = requests.get(page).content
    soup = BeautifulSoup(tree, 'lxml')
    table = soup.find_all('table')[:2]
    all_df = pd.DataFrame()
    for t in table:
        df = pd.read_html(t.prettify())[0]
        df = df.iloc[:,[0,3]]
        df.columns = ['Team', 'Win Rate']
        all_df = all_df.append(df)
    all_df['Team'] = all_df['Team'].apply(lambda x: x.strip(" *"))
    all_df.reset_index()
    all_df.to_csv('win_rate.csv', index=False)
    for _, row in all_df.iterrows():
        team_info[row['Team']]['win_pct'] = row['Win Rate']

# import team shooting CSV and parse 3PT field goal percentage
def parse_three_pt_rate():
    df = pd.read_csv("team_shooting.csv")
    df = df[['Rk', 'Team', '3PT Rate']]
    df['Team'] = df['Team'].apply(lambda x: x.strip(" *"))
    for index, row in df.iterrows():
        if not pd.isnull(row['Rk']):
            team_info[row['Team']]['three_pct'] = row['3PT Rate']
    df.drop(columns=['Rk'], inplace=True)
    df.to_csv('three_pt_rate.csv', index=False)

def get_box_links():
    for team in team_info.keys():
        abbrev = team_info[team]['abbrev']
        page = "https://www.basketball-reference.com/teams/" + abbrev + "/2020_games.html"
        result = requests.get(page)
        tree = html.fromstring(result.content)

        # Isolate schedule table
        schedule = tree.xpath('//table[@id="games"]')

        # Loop through every row
        games = []
        rows = schedule[0].xpath('./tbody/tr')
        for row in rows:
            # Get the boxscore column that contains the game url
            boxscore_td = row.xpath('./td[@data-stat="box_score_text"]')
            if len(boxscore_td) == 0:
                continue
            # Get the game path
            game_href = boxscore_td[0].xpath('./a/@href')[0]

            # Get the root url of the page variable
            regex = r'.*\.com'
            page_root = re.findall(regex, page)[0]
            
            # Formulate the final game base_url
            game_url = '{}{}'.format(page_root, game_href)
            games.append(game_url)
        
        # Write game links to text file
        with open("./box_links/" + team_info[team]['abbrev'] + "_games.txt", "w") as f:
            f.write(team + "\n")
            for link in games:
                # edit URLs to get play by play data
                str_idx = link.find("boxscores/") + 10
                link = link[:str_idx] + "pbp/" + link[str_idx:]
                f.write(link + "\n")
        
# identify if given team (Team X) is visitor or home
# figure out if Team X won the game (return bool)
# return 2 column df listing game play by play given the URL
# to the box score on https://sports-reference.com
# NOTE: only look at first half play by play, discard the rest
def get_scores_and_pbp(team, page):
    # get page content
    tree = requests.get(page).content
    soup = BeautifulSoup(tree, 'lxml')
    table = soup.find_all('table')[0]
    df = pd.read_html(table.prettify())[0]

    # get game score
    score = df.iloc[len(df)-2, 3]
    a_score, b_score = [int(x) for x in score.split('-')]

    # clean dataframe columns and discard second half play by play
    df = df.iloc[:, [1, 5]]
    cols = df.columns
    end = df.index[df[cols[0]] == "3rd Q"].tolist()[0]
    df = df.iloc[1:end, :]
    df = df[~df[cols[0]].isin(['1st Q', '2nd Q', '3rd Q', '4th Q'])]

    # extract visitor and home team from title string of webpage
    t = soup.title.string
    visitor = t[:(t.find(" at "))].strip()
    home = t[(t.find(" at ")+4):(t.find("Play")-1)].strip()
    df.columns = [visitor, home]
    print("Score:", {visitor: a_score, home: b_score})

    # determine if Team X won
    won = True if (team == home and b_score > a_score) or (team == visitor and a_score > b_score) else False

    # return won boolean and play by play dataframe through first half
    return won, df

# zig zag through the dataframe to get a 1-dimensional list of plays
# in the form of tuples (Team, Play)
def get_merged_plays(df):
    merged_plays = []
    for index, row in df.iterrows():
        for col in df.columns:
            if not pd.isnull(row[col]):
                merged_plays.append((col, row[col]))
    return merged_plays

# use regex expression to tally up made 3s per team
# return dictionary containing final tally in the first half 
def get_threes(cols, plays):
    threes = {cols[0]: 0, cols[1]: 0}
    for idx, event in enumerate(plays):
        if re.match(r'^(?=.*?\bmakes 3-pt\b).*$', event[1]):
            threes[event[0]] += 1
    return threes

# helper func
def get_key(boool):
    if boool:
        return "won"
    else:
        return "lost"

# get all files within box_links directory and scrape all game
# play by play data for 2019-2020 season
# tally up number of advantageous first half three point performances
# and record results separately depending on if Team X won or not
def get_three_tally_by_team():
    folder_path = './box_links'
    # traverse all files in directory
    for filename in glob.glob(os.path.join(folder_path, '*box_links.txt')):
        with open(filename, 'r') as f:
            tally = {'won': [0, 0], 'lost': [0, 0]}
            pages = [s.strip() for s in list(f.readlines())]
            team = pages[0]
            print("--- " + team + " ---", end="\n\n")
            pages = pages[1:]
            for idx, page in enumerate(pages):
                if page.find("2021") != -1:
                    continue
                # use try-except statements in case there are wack pages
                try:
                    won, df = get_scores_and_pbp(team, page)
                    plays = get_merged_plays(df)
                    threes = get_threes(df.columns, plays)
                    print("3PT:", threes, end="\n\n")
                    try:
                        for t in df.columns:
                            if t != team:
                                opponent = t
                        if (threes[team] >= threes[opponent]):
                            tally[get_key(won)][0] += 1
                        else:
                            tally[get_key(won)][1] += 1
                    except:
                        print("uh oh", team, opponent, page)
                except:
                    print("aight bet")
                    print()

            print(tally, end="\n\n")
            team_info[team]['tally'] = tally

# compute bayes theorem for all teams using dictionary of all 2019-2020 season
# data (includes the playoffs)
# P(A) = prior = probability of winning (estimated via win percentage)
# P(B|A) = likelihood = probability of making more 3s in the first half 
# given Team X wins
def bayes():
    for key in team_info.keys():
        try:
            likelihood = (team_info[key]['tally']['won'][0] / sum(team_info[key]['tally']['won']))
            prior = team_info[key]['win_pct']
            marginal = (likelihood * prior) + ((team_info[key]['tally']['lost'][0] / sum(team_info[key]['tally']['lost'])) * (1 - prior))
            posterior = (likelihood * prior) / marginal
            team_info[key]['marginal'] = marginal
            team_info[key]['posterior'] = posterior
        except:
            print(key)

# visualize posterior probability as bar chart for all teams
def visualize_posterior_proba():
    y = []
    for key in team_info.keys():
        y.append(team_info[key]['posterior'])
    x = list(team_info.keys())
    y, x = zip(*sorted(zip(y, x)))
    print("Average Posterior Probability Across All Teams (2019-2020):", np.mean(y))
    fig = plt.figure()
    plt.bar(x, y, color='#3a7ca5')
    plt.ylim([0, 1])
    plt.xticks(rotation=90)
    plt.ylabel('Posterior Probability')
    plt.title('Probability of Winning Given More 3s Made in First Half')
    plt.show()
    plt.tight_layout()
    fig.savefig('./posterior_plot_all_teams.png', bbox_inches='tight')

### MAIN SCRIPT ###

# STEP 1: scrape / accumulate the data
team_info = dict()
scrape_team_abbrev()
scrape_win_rate()
parse_three_pt_rate()
# get_box_links()
# parse_files_for_teams("teams_3pts.txt", "teams_win_pcts.txt")
# get_three_tally_by_team()

# # STEP 2: compute posterior probability for all teams
# bayes()

# # (EXTRA) save data to CSV
# df = pd.DataFrame.from_dict(team_info, orient='index')
# df.to_csv('team_info.csv')

# # (EXTRA) visualize posterior probability for all teams
# visualize_posterior_proba()