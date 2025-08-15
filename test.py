import pandas as pd

# Create a sample DataFrame
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, 22, 35, 28],
    'City': ['New York', 'London', 'Paris', 'New York', 'Tokyo']
})

# Remove rows where 'City' is 'New York'
df_filtered = df[~((df['City'] == 'New York') & (df['Age'] == 25))]
print(df_filtered)