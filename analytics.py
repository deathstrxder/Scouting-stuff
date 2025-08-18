import pandas as pd
import numpy as np
from use_attributes import pitscouting_df_filtered
from main import AllianceDataLoader, AllianceCalculator, AttributeHelper
from sklearn.ensemble import RandomForestRegressor
import matplotlib.pyplot as plt

print("Loading and preprocessing data...")

# Preprocess pitscouting_df_filtered to create binary features for Deep Climb and Shallow Climb
pitscouting_df = pitscouting_df_filtered.copy()
pitscouting_df['DeepClimb'] = (pitscouting_df['CageClimb'] == 'Deep Climb').astype(int)
pitscouting_df['ShallowClimb'] = (pitscouting_df['CageClimb'] == 'Shallow Climb').astype(int)

exclude_cols = set(['driveBaseType', 'numCoralAuto'])
filterable_attributes = [col for col in pitscouting_df.columns if col not in exclude_cols and pitscouting_df[col].dropna().isin([0,1]).all()]
filterable_attributes += ['DeepClimb', 'ShallowClimb']
filterable_attributes = list(dict.fromkeys(filterable_attributes))  # Remove duplicates


# Load data and helpers using the new class system
loader = AllianceDataLoader('scouting_data.csv', 'contributed_points.csv')
alliances = loader.get_alliances()
alliances_with_match = loader.get_alliances_with_match()
calc = AllianceCalculator(loader.df, loader.dfpoints)
attr_helper = AttributeHelper(pitscouting_df, filterable_attributes)

# Build feature matrix X (rows: alliances, columns: count of teams with attribute)
X = []
for alliance in alliances_with_match:
    teams = [str(t).replace('frc', '') for t in alliance[:3]]
    features = []
    for attr in filterable_attributes:
        count = sum(attr_helper.get_team_attributes(team).get(attr, np.nan) == 1 for team in teams)
        features.append(count)
    X.append(features)
X = np.array(X)

# Target variable: actual contributed points for each alliance
contributed_points_list = []
for i in range(len(alliances_with_match)):
    team1, team2, team3 = alliances_with_match[i][:3]
    match_number = alliances_with_match[i][3]
    points = calc.contributed_points(team1, team2, team3, match_number)
    contributed_points_list.append(points)
y = np.array(contributed_points_list)

# --- Train Random Forest Regressor ---
model = RandomForestRegressor(random_state=42)
model.fit(X, y)

# --- Feature Importances ---
importances = model.feature_importances_

# Create a DataFrame with attribute and importance
importance_df = pd.DataFrame({
    'attribute': filterable_attributes,
    'importance': importances
}).sort_values('importance', ascending=False).reset_index(drop=True)

print(importance_df)

# Plot bar graph of feature importances
plt.figure(figsize=(12, 6))
plt.bar(importance_df['attribute'], importance_df['importance'], color='skyblue')
plt.xlabel('Attribute')
plt.ylabel('Feature Importance')
plt.title('Feature Importances for Alliance Contributed Points')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
