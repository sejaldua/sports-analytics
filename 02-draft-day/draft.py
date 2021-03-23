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
yhat = {1: 21.89049875704587, 2: 21.260990672663116, 3: 20.612707514997908, 4: 19.95279146855855, 5: 19.28631421933996, 6: 18.6145249156371, 7: 17.889491916659075, 8: 16.929366242815053, 9: 15.977361881933772, 10: 15.089285438138239, 11: 14.24811202615428, 12: 13.373316523875575, 13: 12.534733710608654, 14: 11.857737206246474, 15: 11.392985028768464, 16: 11.066533877118918, 17: 10.744630207541755, 18: 10.440210720634699, 19: 10.341201821869943, 20: 10.44569579051804, 21: 10.498918609976483, 22: 10.406107940049697, 23: 10.267746450492904, 24: 10.1217000883914, 25: 9.964316509499616, 26: 9.659381696346028, 27: 9.155589503670097, 28: 8.53643525790357, 29: 7.959148802189338, 30: 7.466724976944517, 31: 6.985437510504275, 32: 6.571871763478209, 33: 6.267520091644083, 34: 6.052753383648731, 35: 5.968672532712644, 36: 5.979348163974323, 37: 5.976172171498783, 38: 5.925338695309286, 39: 5.882316244969108, 40: 5.849848602675141, 41: 5.841804711112943, 42: 5.839753090955274, 43: 5.838202306068998, 44: 5.8067698324050445, 45: 5.703507326722015, 46: 5.515528452064109, 47: 5.191690437653579, 48: 4.737443231652458, 49: 4.182434759933406, 50: 3.6287378723322696, 51: 3.205243957950051, 52: 2.868344211411912, 53: 2.6031201819024603, 54: 2.3172535076699865, 55: 1.9132242204909014, 56: 1.610309713183811, 57: 1.31673497761452, 58: 1.0065930627516035, 59: 0.6745844576110578, 60: 0.32416120351103705}
give_value = [yhat[x] for x in give_picks]
receive_value = [yhat[x] for x in receive_picks]
success = False
if any([x <= 14 for x in give_picks]) or any([x <= 14 for x in receive_picks]):
    # print("Value of players to give:", numpy.mean(give_value))
    # print("Values of players to receive:", numpy.mean(receive_value))
    if numpy.mean(receive_value) >= numpy.mean(give_value):
        success = True
    else:
        success = False
else:
    # print("Value of players to give:", sum(give_value))
    # print("Values of players to receive:", sum(receive_value))
    if sum(receive_value) >= sum(give_value):
        success = True
    else:
        success = False
if abs(len(receive_picks) - len(give_picks)) >= 5:
    print("ok but who in their right mind would propose this idiotic trade?! simply not realistic")


give_value = [yhat[x] for x in give_picks]
receive_value = [yhat[x] for x in receive_picks]
# print("Value of players to give:", give_value)
# print("Values of players to receive:", receive_value)
success = False
if any([x <= 14 for x in give_picks]) or any([x <= 14 for x in receive_picks]):
    if numpy.mean(receive_value) >= numpy.mean(give_value):
        success = True
    else:
        success = False
else:
    if sum(receive_value) >= sum(give_value):
        success = True
    else:
        success = False


if abs(len(receive_picks) - len(give_picks)) >= 5:
    print("ok but who in their right mind would propose this idiotic trade?! simply not realistic")




# Print feeback on trade
# DO NOT CHANGE THESE OUTPUT MESSAGES
if success:
    print("\nTrade result: Success! This trade receives more value than it gives away.\n")
    # Print additional metrics/reasoning here
else:
    print("\nTrade result: Don't do it! This trade gives away more value than it receives.\n")
    # Print additional metrics/reasoning here