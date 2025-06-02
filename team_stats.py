import pandas as pd
from nba_api.stats.endpoints import LeagueDashTeamStats
import time

print("[INFO] Fetching opponent stats allowed per game...")

# Fetch league team stats with opponent data
opponent_stats = LeagueDashTeamStats(
    per_mode_detailed='PerGame',
    measure_type_detailed_defense='Opponent',
    season='2023-24',  # Adjust to latest season if needed
    season_type_all_star='Regular Season'
)

# Convert to DataFrame
df = opponent_stats.get_data_frames()[0]

print("[DEBUG] Columns returned from API:")
print(df.columns.tolist())

# Rename key opponent stats for clarity
rename_map = {
    'OPP_PTS': 'PTS_ALLOWED',
    'OPP_OREB': 'OREB_ALLOWED',
    'OPP_STL': 'STL_ALLOWED',
    'OPP_AST': 'AST_ALLOWED',
    'OPP_BLK': 'BLK_ALLOWED',
    'OPP_TOV': 'TOV_FORCED',  # TOV committed by opponent
    'OPP_FG_PCT': 'FG_ALLOWED_PCT',
    'OPP_FG3_PCT': 'FG3_ALLOWED_PCT',
    'OPP_FTA': 'FTA_ALLOWED',
}

# Rename only existing columns
valid_renames = {k: v for k, v in rename_map.items() if k in df.columns}
df_renamed = df.rename(columns=valid_renames)

# Save to CSV
output_path = "data/opponent_team_defense.csv"
df_renamed.to_csv(output_path, index=False)
print(f"[SUCCESS] Saved to {output_path}")

# Show a few rows for verification
print(df_renamed[['TEAM_NAME', 'PTS_ALLOWED', 'OREB_ALLOWED', 'STL_ALLOWED']].head())
