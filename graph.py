import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mplcursors
from use_attributes import pitscouting_df_filtered
from matplotlib.widgets import CheckButtons, RadioButtons


df = pd.read_csv(r"Scouting-stuff\scouting_data.csv")
dfpoints = pd.read_csv(r"Scouting-stuff\contributed_points.csv")


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

# Create a list of alliances with their match numbers
alliances = []
for (match, alliance), group in df.groupby(['match_number', 'alliance']):
    teams = [team.replace('frc', '') for team in group['team_key']]
    if len(teams) == 3:
        alliances.append(teams)



# Get filterable attributes (0/1 columns, excluding specified ones)
exclude_cols = set(['driveBaseType', 'numCoralAuto', 'CageClimb'])
filterable_attributes = [col for col in pitscouting_df_filtered.columns if col not in exclude_cols and pitscouting_df_filtered[col].dropna().isin([0,1]).all()]

# Precompute a team attribute lookup dictionary for fast filtering
pitscouting_df_filtered['team_key_stripped'] = pitscouting_df_filtered['team_key'].astype(str).str.replace('frc', '', regex=False)
team_attribute_lookup = {}
for _, row in pitscouting_df_filtered.iterrows():
    team = row['team_key_stripped']
    team_attribute_lookup[team] = {attr: row[attr] for attr in filterable_attributes}

# Initial filter state: all attributes off, and slider values at 0
active_filters = {attr: False for attr in filterable_attributes}
slider_values = {attr: 0 for attr in filterable_attributes}
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



def alliance_passes_filter(alliance):
    for attr, active in active_filters.items():
        if active:
            count = 0
            for team in alliance:
                team_str = str(team).replace('frc', '')
                val = team_attribute_lookup.get(team_str, {}).get(attr, None)
                if val == 0:
                    count += 1
            if count < slider_values[attr]:
                return False
    return True

# Prepare data for scatterplot
diffs = [e - a for e, a in zip(expected_contributed_points_list, contributed_points_list)]
general_points = [(e + a) / 2 for e, a in zip(expected_contributed_points_list, contributed_points_list)]


fig2 = plt.figure(figsize=(14, 7))
ax2 = fig2.add_axes([0.32, 0.12, 0.65, 0.8])  # [left, bottom, width, height]
sc = ax2.scatter(general_points, diffs, color='purple')
ax2.set_xlabel('General Point Value (Average of Expected and Actual)')
ax2.set_ylabel('Difference (Expected - Actual)')
ax2.set_title('Difference vs General Point Value per Alliance')
ax2.grid(True)

labels = [f"Alliance: {', '.join(map(str, alliance[:3]))}\nMatch: {alliance[3]}" for alliance in alliances_with_match]
cursor = mplcursors.cursor(sc, hover=True)
@cursor.connect("add")
def on_add(sel):
    sel.annotation.set_text(labels[sel.index])





# Add checkboxes for attributes (left panel)
num_attrs = len(filterable_attributes)
panel_left = 0.01
panel_width = 0.25
total_height = 0.95
checkbox_height = min(0.018, total_height / (2 * num_attrs))
slider_height = min(0.018, total_height / (2 * num_attrs))
slider_space = 0.004
start_y = 0.98

checkbox_axes = []
slider_axes = []
sliders = []
for idx, attr in enumerate(filterable_attributes):
    y_checkbox = start_y - idx * (checkbox_height + slider_height + 2*slider_space)
    y_slider = y_checkbox - checkbox_height - slider_space
    ax_checkbox = fig2.add_axes([panel_left, y_checkbox, panel_width, checkbox_height])
    cb = CheckButtons(ax_checkbox, [attr], [False])
    checkbox_axes.append(cb)
    short_label = attr if len(attr) <= 18 else attr[:15] + '...'
    ax_slider = fig2.add_axes([panel_left, y_slider, panel_width, slider_height])
    s = Slider(ax_slider, f"min: {short_label}", 0, 3, valinit=0, valstep=1)
    sliders.append(s)
    slider_axes.append(ax_slider)

# Connect checkbox events
def make_checkbox_callback(attr):
    def callback(label):
        active_filters[attr] = not active_filters[attr]
        update_plot()
    return callback
for idx, cb in enumerate(checkbox_axes):
    cb.on_clicked(make_checkbox_callback(filterable_attributes[idx]))




def update_slider(val, idx):
    attr = filterable_attributes[idx]
    slider_values[attr] = int(sliders[idx].val)
    update_plot()

def update_plot():
    offsets = sc.get_offsets()
    new_offsets = offsets.copy()
    for i, alliance in enumerate(alliances):
        visible = alliance_passes_filter(alliance)
        if visible:
            new_offsets[i] = offsets[i]
        else:
            new_offsets[i] = [np.nan, np.nan]
    sc.set_offsets(new_offsets)
    fig2.canvas.draw_idle()


s.on_changed(lambda val, idx=idx: update_slider(val, idx))

plt.tight_layout()
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
labels2 = [f"Alliance: {', '.join(map(str, alliance[:3]))}\nMatch: {alliance[3]}" for alliance in alliances_with_match]
cursor2 = mplcursors.cursor(sc2, hover=True)
@cursor2.connect("add")
def on_add2(sel):
    sel.annotation.set_text(labels2[sel.index])

plt.show()


