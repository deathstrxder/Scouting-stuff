import pandas as pd
import numpy as np
from use_attributes import pitscouting_df_filtered
from sklearn.ensemble import RandomForestRegressor
from graph import alliances_with_match, contributed_points_list

# --- 1. Prepare Data ---
# alliances_with_match: list of [team1, team2, team3, match_number]
# contributed_points_list: list of contributed points for each alliance

# Get filterable attributes (0/1 columns, excluding specified ones)
exclude_cols = set(['driveBaseType', 'numCoralAuto', 'CageClimb'])
filterable_attributes = [col for col in pitscouting_df_filtered.columns if col not in exclude_cols and pitscouting_df_filtered[col].dropna().isin([0,1]).all()]

# Precompute a team attribute lookup dictionary
pitscouting_df_filtered['team_key_stripped'] = pitscouting_df_filtered['team_key'].astype(str).str.replace('frc', '', regex=False)
team_attribute_lookup = {}
for _, row in pitscouting_df_filtered.iterrows():
    team = row['team_key_stripped']
    team_attribute_lookup[team] = {attr: row[attr] for attr in filterable_attributes}

# Build feature matrix X (rows: alliances, columns: count of teams with attribute)
X = []
for alliance in alliances_with_match:
    teams = [str(t).replace('frc', '') for t in alliance[:3]]
    features = []
    for attr in filterable_attributes:
        count = sum(team_attribute_lookup.get(team, {}).get(attr, np.nan) == 0 for team in teams)
        features.append(count)
    X.append(features)
X = np.array(X)

# Target variable
y = np.array(contributed_points_list)

# --- 2. Train Random Forest Regressor ---
model = RandomForestRegressor(random_state=42)
model.fit(X, y)

# --- 3. Feature Importances ---
importances = model.feature_importances_
for attr, imp in sorted(zip(filterable_attributes, importances), key=lambda x: -x[1]):
    print(f"{attr}: {imp:.3f}")

# The attributes with the highest importances are most correlated with higher alliance contributed points.
