import os
import time
import pandas as pd
from nba_api.stats.endpoints import playergamelog, commonallplayers

SEASON = '2020'
MERGED_FILE = f"data/cached_game_logs_{SEASON}.csv"
SEASON = '2020'

os.makedirs('data', exist_ok=True)

def get_player_ids():
    """Fetch active NBA player IDs."""
    players = commonallplayers.CommonAllPlayers(is_only_current_season=1).get_data_frames()[0]
    return players[['PERSON_ID', 'DISPLAY_FIRST_LAST']]

def fetch_player_game_logs(player_id, season=SEASON):
    """Fetch game logs for a specific player."""
    logs = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    df = logs.get_data_frames()[0]
    df['PLAYER_ID'] = player_id
    return df

def fetch_and_cache_all_logs(season=SEASON):
    if os.path.exists(MERGED_FILE):
        print(f"[CACHE] Found cached file: {MERGED_FILE}")
        return pd.read_csv(MERGED_FILE)

    print(f"[FETCH] No cache found. Fetching data for {season}...")

    players = get_player_ids()
    all_logs = []

    for idx, player in players.iterrows():
        player_id = player['PERSON_ID']
        name = player['DISPLAY_FIRST_LAST']
        print(f"Fetching logs for {name} (ID: {player_id})...")

        try:
            df = fetch_player_game_logs(player_id, season)
            df['PLAYER_NAME'] = name
            all_logs.append(df)
            time.sleep(0.6)
        except Exception as e:
            print(f"[ERROR] Failed for {name}: {e}")

    combined = pd.concat(all_logs, ignore_index=True)
    combined.to_csv(MERGED_FILE, index=False)
    print(f"[DONE] Cached combined logs to {MERGED_FILE}")
    return combined

if __name__ == "__main__":
    df = fetch_and_cache_all_logs()
    print(df.head())
