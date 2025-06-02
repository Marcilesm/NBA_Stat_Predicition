import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from nba_api.stats.endpoints import playercareerstats
import time

# === Load player list ===
game_logs = pd.read_csv("data/cleaned_game_logs_2023.csv")
player_names = game_logs['PLAYER_NAME'].unique()
player_ids = game_logs[['PLAYER_ID', 'PLAYER_NAME']].drop_duplicates()

# === Fetch career averages for each player ===
career_data = []

for _, row in player_ids.iterrows():
    pid = row['PLAYER_ID']
    name = row['PLAYER_NAME']
    try:
        stats = playercareerstats.PlayerCareerStats(player_id=pid)
        career_summary = stats.get_data_frames()[1]  # Totals + Career

        if 'GP' in career_summary.columns and career_summary['GP'].sum() > 0:
            totals = career_summary.sum(numeric_only=True)
            gp = totals['GP']
            
            # Manually compute per-game career averages
            career_data.append({
                'PLAYER_NAME': name,
                'PTS': totals['PTS'] / gp,
                'AST': totals['AST'] / gp,
                'REB': totals['REB'] / gp,
                'STL': totals['STL'] / gp,
                'BLK': totals['BLK'] / gp,
                'TOV': totals['TOV'] / gp,
                'FG3A': totals['FG3A'] / gp,
                'FTA': totals['FTA'] / gp,
                'MIN': totals['MIN'] / gp
            })
            print(f"[FETCHED] {name}")
        else:
            print(f"[WARN] Missing 'GP' column or zero games played for {name}")
        
        time.sleep(0.3)
    except Exception as e:
        print(f"[ERROR] Failed to fetch {name}: {e}")


career_df = pd.DataFrame(career_data).dropna()
career_df.to_csv("data/player_career_averages.csv", index=False)

# === Scale and cluster career stats ===
features = career_df.drop(columns=['PLAYER_NAME'])
scaler = StandardScaler()
scaled = scaler.fit_transform(features)

# === Choose number of clusters ===
k = 4
kmeans = KMeans(n_clusters=k, random_state=42)
career_df['ARCHETYPE_CAREER'] = kmeans.fit_predict(scaled)

# === PCA for visualization ===
pca = PCA(n_components=2)
components = pca.fit_transform(scaled)

plt.figure(figsize=(10, 7))
scatter = plt.scatter(components[:, 0], components[:, 1], 
                      c=career_df['ARCHETYPE_CAREER'], cmap='viridis', s=60, edgecolors='k')
plt.title("Career-Based Player Archetypes (PCA Reduced)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.grid(True)
plt.tight_layout()
plt.colorbar(scatter, label="Career Archetype Cluster")
plt.show()

# === Merge career archetypes back into main logs ===
game_logs = game_logs.merge(career_df[['PLAYER_NAME', 'ARCHETYPE_CAREER']], on='PLAYER_NAME', how='left')
game_logs.to_csv("data/game_logs_with_dual_archetypes.csv", index=False)

print("[DONE] Dual archetypes added to data/game_logs_with_dual_archetypes.csv")
