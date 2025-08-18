import pandas as pd
import numpy as np
from use_attributes import pitscouting_df_filtered

# Add binary columns for DeepClimb and ShallowClimb
pitscouting_df_filtered = pitscouting_df_filtered.copy()
pitscouting_df_filtered['DeepClimb'] = (pitscouting_df_filtered['CageClimb'] == 'Deep Climb').astype(int)
pitscouting_df_filtered['ShallowClimb'] = (pitscouting_df_filtered['CageClimb'] == 'Shallow Climb').astype(int)

class AllianceDataLoader:
    def __init__(self, scouting_path, points_path):
        self.df = pd.read_csv(scouting_path)
        self.dfpoints = pd.read_csv(points_path)

    def get_alliances(self):
        alliances = []
        for (match, alliance), group in self.df.groupby(['match_number', 'alliance']):
            teams = [team.replace('frc', '') for team in group['team_key']]
            if len(teams) == 3:
                alliances.append(teams)
        return alliances

    def get_alliances_with_match(self):
        alliances_with_match = []
        for (match, alliance), group in self.df.groupby(['match_number', 'alliance']):
            teams = list(group['team_key'])
            if len(teams) == 3:
                alliances_with_match.append(teams + [match])
        return alliances_with_match

class AllianceCalculator:
    def __init__(self, df, dfpoints):
        self.df = df
        self.dfpoints = dfpoints

    def contributed_points(self, team1, team2, team3, match_number):
        team1points = self.df[(self.df['team_key'] == team1) & (self.df['match_number'] == match_number)]
        team2points = self.df[(self.df['team_key'] == team2) & (self.df['match_number'] == match_number)]
        team3points = self.df[(self.df['team_key'] == team3) & (self.df['match_number'] == match_number)]
        combined_df = pd.concat([team1points, team2points, team3points])
        return combined_df['contributedPoints'].sum()

    def expected_contributed_points(self, team1, team2, team3):
        team1points = self.dfpoints[self.dfpoints['team_key'].astype(str) == str(team1)]
        team2points = self.dfpoints[self.dfpoints['team_key'].astype(str) == str(team2)]
        team3points = self.dfpoints[self.dfpoints['team_key'].astype(str) == str(team3)]
        combined_df = pd.concat([team1points, team2points, team3points])
        return combined_df['average_contributed_points'].sum()


# Combined AttributeHelper: can use default or custom filterable_attributes
class AttributeHelper:
    def __init__(self, pitscouting_df, filterable_attributes=None):
        self.exclude_cols = set(['driveBaseType', 'numCoralAuto'])
        if filterable_attributes is None:
            self.filterable_attributes = [col for col in pitscouting_df.columns if col not in self.exclude_cols and pitscouting_df[col].dropna().isin([0,1]).all()]
        else:
            self.filterable_attributes = filterable_attributes
        pitscouting_df['team_key_stripped'] = pitscouting_df['team_key'].astype(str).str.replace('frc', '', regex=False)
        self.team_attribute_lookup = {}
        for _, row in pitscouting_df.iterrows():
            team = row['team_key_stripped']
            self.team_attribute_lookup[team] = {attr: row[attr] for attr in self.filterable_attributes}

    def get_team_attributes(self, team):
        return self.team_attribute_lookup.get(team, {})

# Example usage:
if __name__ == "__main__":
    loader = AllianceDataLoader('scouting_data.csv', 'contributed_points.csv')
    alliances = loader.get_alliances()
    alliances_with_match = loader.get_alliances_with_match()
    calc = AllianceCalculator(loader.df, loader.dfpoints)
    attr_helper = AttributeHelper(pitscouting_df_filtered)
    print("First alliance:", alliances[0])
    print("Attributes for first team:", attr_helper.get_team_attributes(alliances[0][0]))
    print("Contributed points for first alliance:", calc.contributed_points(*alliances_with_match[0][:3], alliances_with_match[0][3]))
    print("Expected points for first alliance:", calc.expected_contributed_points(*alliances_with_match[0][:3]))
