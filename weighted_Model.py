import pandas as pd
import numpy as np
import os
import re

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 0)
pd.set_option('display.max_colwidth', None)

def generate_weighted_input(player_name, opponent, home_game,
                            career_df, season_df, opponent_def_df,
                            w_career=0.3, w_season=0.5, w_matchup=0.2, w_opp=0.20):
    # 1. Career stats
    career_row = career_df[career_df['PLAYER_NAME'] == player_name]
    if career_row.empty:
        raise ValueError(f"Career stats not found for player: {player_name}")

    # 2. Season stats
    season_stats = season_df[season_df['PLAYER_NAME'] == player_name]
    if season_stats.empty:
        raise ValueError(f"Season stats not found for player: {player_name}")

    season_avg = season_stats.mean(numeric_only=True)

    # 3. Matchup stats
    matchup_stats = season_stats[season_stats['OPPONENT'] == opponent]
    matchup_avg = matchup_stats.mean(numeric_only=True)

    # 4. Common columns for blending
    common_cols = set(career_row.columns) & set(season_avg.index) & set(matchup_avg.index)
    common_cols = list(common_cols - {'PLAYER_ID'})

    # 5. Load opponent defensive row early
    opponent_row = None
    if opponent_def_df is not None:
        match = opponent_def_df['TEAM_NAME'].str.contains(opponent, case=False, na=False)
        if match.any():
            opponent_row = opponent_def_df[match].iloc[0]

    weighted = {}
    for col in common_cols:
        c = float(career_row[col].values[0])
        s = float(season_avg[col])
        m = float(matchup_avg[col]) if not pd.isna(matchup_avg[col]) else s

        if col == 'REB':
            base = (0.1 * c) + (0.3 * s) + (0.6 * m)  # Stronger matchup weighting
            if opponent_row is not None:
                reb_scale = 1.0
                if 'OREB_ALLOWED' in opponent_row:
                    reb_scale *= float(opponent_row['OREB_ALLOWED']) / 10.0
                if 'FG_ALLOWED_PCT' in opponent_row:
                    reb_scale *= (1.0 - float(opponent_row['FG_ALLOWED_PCT'])) / (1.0 - 0.47)  # assuming 47% league avg
                base = (1 - w_opp) * base + w_opp * (base * reb_scale)
            weighted[col] = base
        elif col == 'FTA':
            base = (0.2 * c) + (0.3 * s) + (0.3 * m)
            if opponent_row is not None and 'FTA_ALLOWED' in opponent_row:
                fta_scale = float(opponent_row['FTA_ALLOWED']) / 23.0  # 23 is approx. league avg FTA per team
                base = (1 - w_opp) * base + w_opp * (base * fta_scale)
                weighted[col] = base
        else:
            weighted[col] = (w_career * c) + (w_season * s) + (w_matchup * m)

    # Add basic info
    weighted['OPPONENT'] = opponent
    weighted['PLAYER_NAME'] = player_name
    weighted['HOME_GAME'] = home_game

    # Add archetype
    try:
        weighted['ARCHETYPE'] = int(season_stats['ARCHETYPE'].mode()[0])
    except:
        weighted['ARCHETYPE'] = -1
    try:
        weighted['ARCHETYPE_CAREER'] = int(season_stats['ARCHETYPE_CAREER'].mode()[0])
    except:
        weighted['ARCHETYPE_CAREER'] = -1

    # 6. Final team-defense adjustment on key stats
    if opponent_row is not None:
        league_averages = {
            'PTS_ALLOWED': 114.0,
            'OREB_ALLOWED': 10.0,
            'STL_ALLOWED': 7.5,
            'AST_ALLOWED': 25.5,
        }

        for stat, opp_col in [('PTS', 'PTS_ALLOWED'),
                              ('REB', 'OREB_ALLOWED'),
                              ('STL', 'STL_ALLOWED'),
                              ('AST', 'AST_ALLOWED')]:
            if stat in weighted and opp_col in opponent_row:
                opp_val = float(opponent_row[opp_col])
                league_avg = league_averages[opp_col]
                scale = opp_val / league_avg
                adjusted = (1 - w_opp) * weighted[stat] + w_opp * (weighted[stat] * scale)
                weighted[stat] = adjusted
    else:
        print(f"[WARN] No opponent defensive stats found for {opponent}")

    return pd.DataFrame([weighted])

def find_latest_season_file():
    pattern = re.compile(r"cleaned_game_logs_(\d{4})\.csv")
    latest_year = 0
    latest_file = None

    for fname in os.listdir("data"):
        match = pattern.match(fname)
        if match:
            year = int(match.group(1))
            if year > latest_year:
                latest_year = year
                latest_file = fname

    if not latest_file:
        raise FileNotFoundError("No cleaned_game_logs_*.csv files found in /data")

    return f"data/{latest_file}", latest_year

def load_opponent_defense_data():
    df = pd.read_csv("data/opponent_team_defense.csv")
    df['TEAM_NAME'] = df['TEAM_NAME'].str.upper()
    return df

if __name__ == "__main__":
    career_df = pd.read_csv("data/player_career_averages.csv")
    season_file, detected_year = find_latest_season_file()
    season_df = pd.read_csv(season_file)
    opponent_def_df = load_opponent_defense_data()

    career_df['PLAYER_NAME'] = career_df['PLAYER_NAME'].str.lower()
    season_df['PLAYER_NAME'] = season_df['PLAYER_NAME'].str.lower()

    print(f"[INFO] Loaded season data from {season_file}")

    player = input("Enter player name: ").strip().lower()
    opponent = input("Enter opponent abbreviation (e.g., DET): ")
    home_flag = input("Is it a home game? (y/n): ").strip().lower()
    home_game = 1 if home_flag == 'y' else 0
    display_name = player.title()

    try:
        df_input = generate_weighted_input(player, opponent, home_game,
                                           career_df, season_df, opponent_def_df)
        print(f"\nGenerated model-ready input for {display_name} vs. {opponent} ({'Home' if home_game else 'Away'}):")
        print(df_input.head())

        # Accuracy check
        player_games = season_df[
            (season_df['PLAYER_NAME'] == player) &
            (season_df['OPPONENT'] == opponent) &
            (season_df['HOME_GAME'] == home_game)
        ].sort_values('GAME_DATE', ascending=False)

        if not player_games.empty:
            latest_game = player_games.iloc[0]
            print(f"\n[ACCURACY CHECK] Most recent {display_name} vs. {opponent} on {latest_game['GAME_DATE']}")
            compare_cols = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'FG3A', 'FTA', 'MIN']
            print("Stat     | Predicted | Actual | Abs Error | % Error")
            for stat in compare_cols:
                predicted = df_input[stat].values[0]
                actual = latest_game[stat]
                abs_error = abs(predicted - actual)
                pct_error = (abs_error / actual * 100) if actual != 0 else 0
                print(f"{stat:<8} | {predicted:>9.2f} | {actual:>6.2f} | {abs_error:>9.2f} | {pct_error:>7.2f}%")
        else:
            print(f"[INFO] No recent matchup found for {display_name} vs. {opponent}")

    except Exception as e:
        print(f"Error: {e}")
