import pandas as pd

# Load cached data
df = pd.read_csv("data/cached_game_logs_2023.csv")

# Show first few columns
print("Columns in raw data:", df.columns.tolist())
print(df.head())

def clean_nba_data(df):
    keep_cols = ['PLAYER_ID', 'PLAYER_NAME', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL']
    numeric_stats = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'MIN', 'PLUS_MINUS', 'FG3M', 'FG3A', 'FTA', 'FTM']
    
    # Keep core columns + stats
    df = df[keep_cols + numeric_stats]

    # Matchup breakdown
    df['HOME_GAME'] = df['MATCHUP'].apply(lambda x: 1 if 'vs.' in x else 0)
    df['OPPONENT'] = df['MATCHUP'].apply(lambda x: x.split()[-1])
    df = df.drop(columns=['MATCHUP'])

    # WIN -> binary
    df['WIN'] = df['WL'].map({'W': 1, 'L': 0})
    df = df.drop(columns=['WL'])

    # Date formatting
    df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'])
    df = df.sort_values(by=['PLAYER_ID', 'GAME_DATE'])

    # Rolling stats
    for stat in ['PTS', 'AST', 'REB', 'STL', 'BLK', 'TOV']:
        df[f'{stat}_ROLL3'] = df.groupby('PLAYER_ID')[stat].transform(lambda x: x.shift().rolling(3).mean())

    # Drop rows with missing rolling stats
    df = df.dropna()

    return df

if __name__ == "__main__":
    df = pd.read_csv("data/cached_game_logs_2023.csv")
    clean_df = clean_nba_data(df)
    clean_df.to_csv("data/cleaned_game_logs_2023.csv", index=False)
    print("Cleaned data saved! Here's a preview:")
    print(clean_df.head())
