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
{1: 20.890498757045858, 2: 20.260990672663123, 3: 19.61270751499791, 4: 18.952791468558562, 5: 18.286314219339964, 6: 17.6145249156371, 7: 16.889491916659075, 8: 15.929366242815048, 9: 14.977361881933776, 10: 14.08928543813824, 11: 13.248112026154278, 12: 12.373316523875577, 13: 11.534733710608654, 14: 10.857737206246476, 15: 10.39298502876847, 16: 10.066533877118918, 17: 9.744630207541755, 18: 9.440210720634703, 19: 9.341201821869948, 20: 9.44569579051805, 21: 9.49891860997649, 22: 9.406107940049703, 23: 9.267746450492913, 24: 9.121700088391405, 25: 8.964316509499618, 26: 8.659381696346028, 27: 8.155589503670086, 28: 7.53643525790358, 29: 6.95914880218933, 30: 6.4667249769445165, 31: 5.985437510504276, 32: 5.571871763478207, 33: 5.267520091644081, 34: 5.052753383648731, 35: 4.968672532712644, 36: 4.979348163974324, 37: 4.976172171498783, 38: 4.925338695309286, 39: 4.882316244969108, 40: 4.849848602675141, 41: 4.841804711112944, 42: 4.8397530909552735, 43: 4.838202306068996, 44: 4.806769832405044, 45: 4.703507326722015, 46: 4.51552845206411, 47: 4.191690437653572, 48: 3.7374432316524726, 49: 3.1824347599333986, 50: 2.6287378723322696, 51: 2.2052439579500476, 52: 1.8683442114119082, 53: 1.6031201819024576, 54: 1.3172535076699834, 55: 0.913224220490902, 56: 0.6103097131838024, 57: 0.31673497761451713, 58: 0.006593062751600043, 59: -0.32541554238894344, 60: -0.675838796488961}
give_value = [yhat[x] for x in give_picks]
receive_value = [yhat[x] for x in receive_picks]
print("Value of players to give:", give_value)
print("Values of players to receive:", receive_value)
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