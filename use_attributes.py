import pandas as pd

pitscouting_df = pd.read_csv('pitscouting.csv')

cols_to_drop = [
	'org_key', 'year', 'event_key', 'Length', 'Width', 'Weight', 'doAuto',
	'StartA', 'StartB', 'StartC', 'StartD', 'StartE', 'describeAuto',
	'preferredStrategy', 'notes'
]

pitscouting_df_filtered = pitscouting_df.drop(columns=cols_to_drop)

