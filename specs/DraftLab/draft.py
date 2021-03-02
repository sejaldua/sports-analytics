import csv
import numpy
# You may or may not want to use this package, or others like it
# this is just a starting point for you
from sklearn.linear_model import LinearRegression

# Read the player database into an array of dictionaries
players = []
with open('playerDB.csv', mode='r') as player_csv:
    player_reader = csv.DictReader(player_csv)
    line_count = 0
    for row in player_reader:
        players.append(dict(row))

# Read the draft database into an array of dictionaries
draftPicks = []
with open('draftDB.csv', mode='r') as draft_csv:
    draft_reader = csv.DictReader(draft_csv)
    line_count = 0
    for row in draft_reader:
        draftPicks.append(dict(row))


# Get the draft picks to give/receive from the user
# You can assume that this input will be entered as expected
# DO NOT CHANGE THESE PROMPTS
print("\nSelect the picks to be traded away and the picks to be received in return.")
print("For each entry, provide 1 or more pick numbers from 1-60 as a comma-separated list.")
print("As an example, to trade the 1st, 3rd, and 25th pick you would enter: 1, 3, 25.\n")
give_str = input("Picks to give away: ")
receive_str = input("Picks to receive: ")

# Convert user input to an array of ints
give_picks = list(map(int, give_str.split(',')))
receive_picks = list(map(int, receive_str.split(',')))

# Success indicator that you will need to update based on your trade analysis
success = True



# YOUR SOLUTION GOES HERE



# Print feeback on trade
# DO NOT CHANGE THESE OUTPUT MESSAGES
if success:
    print("\nTrade result: Success! This trade receives more value than it gives away.\n")
    # Print additional metrics/reasoning here
else:
    print("\nTrade result: Don't do it! This trade gives away more value than it receives.\n")
    # Print additional metrics/reasoning here