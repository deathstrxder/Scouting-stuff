import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mplcursors

# x_label = "Alliance Expected Contributed Points"
# y_label = "Alliance Actual Contributed Points"

df = pd.read_csv("scouting_data.csv")
dfpoints = pd.read_csv("contributed_points.csv")

# print(df[['team_key', 'match_number', 'alliance']])pip install pipenv

def contributed_points(team1, team2, team3, match_number):
    team1points = df[(df['team_key'] == team1) & (df['match_number'] == match_number)]
    team2points = df[(df['team_key'] == team2) & (df['match_number'] == match_number)]
    team3points = df[(df['team_key'] == team3) & (df['match_number'] == match_number)]
    combined_df = pd.concat([team1points, team2points, team3points])
    contributed_points = combined_df['contributedPoints'].sum()
    return contributed_points
    

def expected_contributed_points(team1, team2, team3):
    team1points = dfpoints[dfpoints['team_key'].astype(str) == str(team1)]
    team2points = dfpoints[dfpoints['team_key'].astype(str) == str(team2)]
    team3points = dfpoints[dfpoints['team_key'].astype(str) == str(team3)]
    combined_df = pd.concat([team1points, team2points, team3points])
    expected_points = combined_df['average_contributed_points'].sum()
    return expected_points

# red_present = 0
# blue_present = 0
# match_frequency = 0
# points_list = []
# for i in range(76):
#     match_frequency = df['match_number'][i].value_counts()[i]
#     while red_present < 3 or blue_present < 3:
#         if df['alliance'][i] == 'red':
#             red_present += 1
#         elif df['alliance'][i] == 'blue':
#             blue_present += 1
#     if red_present < 3:
#         points_list.append('null')
#     elif blue_present < 3:
#         points_list.append('null')
#     else:
#         points_list.append(df['expected_contributed_points'][i])
#     red_present = 0
#     blue_present = 0
# return points_list

# filter out matches with less than 3 teams on either alliance
# blue_teams = 0
# red_teams = 0
# filtered_df = df.copy()
# for num in range(76):
#     i = num + 1
#     match = (df['match_number'] == i).sum()
#     if match < 6:
#         df_of_match = df[df['match_number'] == i]
#         blue_teams = ((df['match_number'] == i) & (df['alliance'] == 'blue')).sum()
#         red_teams = ((df['match_number'] == i) & (df['alliance'] == 'red')).sum()
#         if blue_teams < 3:
#             filtered_df = filtered_df[~((filtered_df['match_number'] == i) & (filtered_df['alliance'] == 'blue'))]
#             print("removed blue teams from match", i)
#         if red_teams < 3:
#             filtered_df = filtered_df[~((filtered_df['match_number'] == i) & (filtered_df['alliance'] == 'red'))]
#             print("removed red teams from match", i)
#         blue_teams = 0
#         red_teams = 0
# filtered_df.to_csv('modified_data.csv', index=False
# alliances_df = filtered_df[['match_number', 'alliance']].drop_duplicates()
# num_alliances = alliances_df.shape[0]

# print(num_alliances)

# Create a list of alliances with their match numbers
alliances = []
for (match, alliance), group in df.groupby(['match_number', 'alliance']):
    teams = [team.replace('frc', '') for team in group['team_key']]
    if len(teams) == 3:
        alliances.append(teams)
# Create a list of expected contributed points for each alliance
expected_contributed_points_list = []
alliances_length = len(alliances)
for i in range(alliances_length):
    team1 = alliances[i][0]
    team2 = alliances[i][1]
    team3 = alliances[i][2]
    points = expected_contributed_points(team1, team2, team3)
    points = round(points, 1)
    expected_contributed_points_list.append(points)

print(expected_contributed_points_list)

# Create a list of alliances with their match numbers
alliances_with_match = []
for (match, alliance), group in df.groupby(['match_number', 'alliance']):
    teams = list(group['team_key'])
    if len(teams) == 3:
        alliances_with_match.append(teams + [match])

# Create a list of actual contributed points for each alliance
contributed_points_list = []
for i in range(alliances_length):
    team1 = alliances_with_match[i][0]
    team2 = alliances_with_match[i][1]
    team3 = alliances_with_match[i][2]
    match_number = alliances_with_match[i][3]
    print(team1, team2, team3, match_number)
    points = contributed_points(team1, team2, team3, match_number)
    points = round(points, 1)
    contributed_points_list.append(points)

print(contributed_points_list)

# Add interactive slider to filter alliances by difference
from matplotlib.widgets import Slider

diffs = [abs(e - a) for e, a in zip(expected_contributed_points_list, contributed_points_list)]

fig, ax = plt.subplots(figsize=(14, 7))
plt.subplots_adjust(bottom=0.25)

bar_width = 0.4
x_labels = [f"{team1},{team2},{team3}" for team1, team2, team3 in alliances]
x = np.arange(len(x_labels))

bars_expected = ax.bar(x - bar_width/2, expected_contributed_points_list, width=bar_width, color='red', label='Expected Contributed Points')
bars_actual = ax.bar(x + bar_width/2, contributed_points_list, width=bar_width, color='blue', label='Actual Contributed Points')
ax.set_xlabel('Alliance (Team1, Team2, Team3)')
ax.set_ylabel('Points')
ax.set_title('Expected vs Actual Contributed Points per Alliance')
ax.set_xticks(x)
ax.set_xticklabels(x_labels, rotation=90)
ax.legend()

ax_slider = plt.axes([0.2, 0.1, 0.6, 0.03])
slider = Slider(ax_slider, 'Min Diff', 0, max(diffs), valinit=0, valstep=0.1)

def update(val):
    threshold = slider.val
    for i, (bar_e, bar_a) in enumerate(zip(bars_expected, bars_actual)):
        show = diffs[i] >= threshold
        bar_e.set_visible(show)
        bar_a.set_visible(show)
    fig.canvas.draw_idle()

slider.on_changed(update)
plt.tight_layout()
plt.show()



# Scatter plot: y-axis = difference, x-axis = general point values (average of expected and actual)
diffs = [e - a for e, a in zip(expected_contributed_points_list, contributed_points_list)]
general_points = [(e + a) / 2 for e, a in zip(expected_contributed_points_list, contributed_points_list)]

plt.figure(figsize=(10, 6))
plt.scatter(general_points, diffs, color='purple')

# Add hover tooltips for alliance and match number using mplcursors
sc = plt.scatter(general_points, diffs, color='purple')
plt.xlabel('General Point Value (Average of Expected and Actual)')
plt.ylabel('Difference (Expected - Actual)')
plt.title('Difference vs General Point Value per Alliance')
plt.grid(True)
plt.tight_layout()

labels = [f"Alliance: {', '.join(map(str, alliance[:3]))}\nMatch: {alliance[3]}" for alliance in alliances_with_match]
cursor = mplcursors.cursor(sc, hover=True)
@cursor.connect("add")
def on_add(sel):
    sel.annotation.set_text(labels[sel.index])

plt.show()

# Scatter plot: y-axis = (actual - expected), x-axis = actual contributed points
diffs_actual_expected = [a - e for e, a in zip(expected_contributed_points_list, contributed_points_list)]
actual_points = contributed_points_list

plt.figure(figsize=(10, 6))
sc2 = plt.scatter(actual_points, diffs_actual_expected, color='green')
plt.xlabel('Actual Contributed Points')
plt.ylabel('Difference (Actual - Expected)')
plt.title('Difference vs Actual Contributed Points per Alliance')
plt.grid(True)
plt.tight_layout()

# Hover tooltips for this plot
import mplcursors
labels2 = [f"Alliance: {', '.join(map(str, alliance[:3]))}\nMatch: {alliance[3]}" for alliance in alliances_with_match]
cursor2 = mplcursors.cursor(sc2, hover=True)
@cursor2.connect("add")
def on_add2(sel):
    sel.annotation.set_text(labels2[sel.index])

plt.show()


