# Sejal Dua
# COMP152
# 03/23/2021

import csv
import json
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import matplotlib as mlt
import matplotlib.image as mpimg
import matplotlib.animation as animation

# read in play by play data as data frame
events = pd.read_csv('0021500495.csv', index_col=None)
events = events.iloc[1:, :]

# Read in the SportVU tracking data and convert to dictionary
sportvu = []
with open('0021500495.json', mode='r') as sportvu_json:  
    sportvu = json.load(sportvu_json)
data = pd.DataFrame.from_dict(sportvu)
data['event_id'] = data['events'].apply(lambda x: int(x['eventId']))

player_fields = data['events'][0]['home']['players'][0].keys()
home_players = pd.DataFrame(data=[i for i in data['events'][0]['home']['players']], columns=player_fields)
away_players = pd.DataFrame(data=[i for i in data['events'][0]['visitor']['players']], columns=player_fields)
players = pd.merge(home_players, away_players, how='outer')
jerseydict = dict(zip(players.playerid.values, players.jersey.values))
player_dict = players.set_index('playerid').to_dict(orient='index')

# filter and merge data sources to only focus on shot events
shot_df = events[events['EVENTMSGTYPE'].isin([1, 2])]
data = data[data['event_id'].isin(list(shot_df['EVENTNUM']))].reset_index(drop=True)
shot_df = shot_df.reset_index(drop=True)
shot_df['events'] = data['events']

def find_basket_coords(event_num):
    shot_clock = [x[3] for x in shot_df['events'][event_num]['moments']] # get shot clock data
    for i in range(len(shot_clock)-1):
        if shot_clock[i] < shot_clock[i+1] and shot_clock[i+1] > 23.5:
            shot_idx = i
            break
    ball_xy = np.array([x[5][0][2:5] for x in shot_df['events'][event_num]['moments']]) #create matrix of ball data
    basket_coords = []
    for ball_coords in ball_xy[shot_idx-30:shot_idx]:
        if ball_coords[2] >= 9.5:   # z coordinates greater than height of hoop
            basket_coords = ball_coords[:2]
    return basket_coords

def get_basket_loc():
    X1, X2, Y = [], [], []
    for i in range(181):
        try:
            x, y = find_basket_coords(i)
            if x < 50:
                X1.append(x)
            else:
                X2.append(x)
            Y.append(y)
        except:
            pass
    return (np.mean(X1), np.mean(Y)), (np.mean(X2), np.mean(Y))


basket1_coords = np.array([6.13, 25.25])
basket2_coords = np.array([88.08, 25.25])

def get_shooter_info(playerid):
    playerid = int(playerid)
    return str(player_dict[playerid]['lastname']) + " (" + str(player_dict[playerid]['jersey']) + ")"

def get_all_coords_from_event(idx):
    # event_id = get_vu_index(event_num)
    ball_xy = np.array([x[5][0][2:5] for x in shot_df['events'][idx]['moments']]) #create matrix of ball data
    player_xy = np.array([np.array(x[5][1:])[:,1:4] for x in shot_df['events'][idx]['moments']]) #create matrix of player data
    return ball_xy, player_xy

def get_event_deets(idx):
    home_col = shot_df['HOMEDESCRIPTION'][idx]
    visitor_col = shot_df['VISITORDESCRIPTION'][idx]
    event = home_col if not pd.isnull(home_col) else visitor_col
    return event

def get_shot_clock_usage(idx):
    # print(idx, get_event_deets(idx), get_shooter_info(shot_df['PLAYER1_ID'][idx]))
    quarter = shot_df['events'][idx]['moments'][0][0]
    shot_clock = [x[3] for x in shot_df['events'][idx]['moments']] # get shot clock data
    # print(shot_clock)
    for i in range(len(shot_clock)-1):
        if shot_clock[i] < shot_clock[i+1] and shot_clock[i+1] > 23.5:
            shot_idx = i
            break
    time_left = shot_df['events'][idx]['moments'][shot_idx][2]
    shot_time = (quarter - 1) * 720 + (720 - time_left)
    shot_fact = 24 - shot_clock[shot_idx]
    return shot_time, shot_fact

def get_shot_distance(idx):
    # print(idx, get_event_deets(idx), get_shooter_info(shot_df['PLAYER1_ID'][idx]))
    quarter = shot_df['events'][idx]['moments'][0][0]
     # identify moment when ball left shooter's hands
    ball_xy, player_xy = get_all_coords_from_event(idx)
    ball_possession_moments = []
    flag = True
    for n in range(len(player_xy)):
        for i,ii in enumerate(player_xy[n]): #loop through all the players
            if np.linalg.norm(np.array([ii[1], ii[2]]) - np.array([ball_xy[n,0],ball_xy[n,1]])) <= 2.5 and ball_xy[n,2] <= 9:
                # print(get_shooter_info(ii[0]))
                ball_possession_moments.append((ii[0], [ii[1], ii[2]])) # (player jersey number, [player x, player y])
                flag = True
            if (np.linalg.norm([ball_xy[n,0],ball_xy[n,1]] - basket1_coords) <= 3 or np.linalg.norm([ball_xy[n,0],ball_xy[n,1]] - basket2_coords) <= 3) and ball_xy[n, 2] >= 9.5 and flag:
                # print(ball_possession_moments)
                for shot_pos in ball_possession_moments[::-1]:
                    # get shot possession (point at which shooter last had ball)
                    if int(shot_pos[0]) == int(shot_df['PLAYER1_ID'][idx]):
                        time_left = shot_df['events'][idx]['moments'][n][2]
                        shot_time = (quarter - 1) * 720 + (720 - time_left)
                        shot_fact = min(np.linalg.norm(shot_pos[1] - basket1_coords), np.linalg.norm(shot_pos[1] - basket2_coords))
                        # print(shot_time, shot_fact)
                        if shot_fact > 30:
                            return
                        return shot_time, shot_fact
                flag = False
    return shot_time, shot_fact


def get_shot_fact_from_event(idx, fact_type="distance"):
    # get shot time info
    if fact_type == "shot clock usage":
        shot_time, shot_fact = get_shot_clock_usage(idx)
    elif fact_type == "distance":
        shot_time, shot_fact = get_shot_distance(idx)


    return shot_time, shot_fact

colors = []
errors = []
shot_times, shot_facts = [], []
c_map = list(shot_df['EVENTMSGTYPE'].apply(lambda x: 'g' if x == 1 else 'r'))
fact_type = "shot clock usage"
for idx in range(len(shot_df)):
    try:
        time, fact = get_shot_fact_from_event(idx, fact_type=fact_type)
        shot_times.append(time)
        shot_facts.append(fact)
        colors.append(c_map[idx])
    except:
        errors.append(idx)
shot_facts = [sf * (10 / max(shot_facts)) for sf in shot_facts]  # scale between 0 and 10


# This code creates the timeline display from the shot_times
# and shot_facts arrays.
# DO NOT MODIFY THIS CODE APART FROM THE SHOT FACT LABEL
fig, ax = plt.subplots(figsize=(12,3))
fig.canvas.set_window_title('Shot Timeline')

plt.scatter(shot_times, np.full_like(shot_times, 0), marker='o', s=50, color=colors, edgecolors='black', zorder=3, label='shot')
plt.bar(shot_times, shot_facts, bottom=2, color=colors, edgecolor='black', width=5, label='shot clock usage') # <- This is the label you can modify

ax.spines['bottom'].set_position('zero')
ax.spines['top'].set_color('none')
ax.spines['right'].set_color('none')
ax.spines['left'].set_color('none')
ax.tick_params(axis='x', length=20)
ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([0,720,1440,2160,2880])) 
ax.set_yticks([])

_, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()
ax.set_xlim(-15, xmax)
ax.set_ylim(ymin, ymax+5)
ax.text(xmax, 2, "time", ha='right', va='top', size=10)
plt.legend(ncol=5, loc='upper left')

plt.tight_layout()
plt.show()
