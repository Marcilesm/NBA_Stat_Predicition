import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# === Load cleaned data ===
df = pd.read_csv("data/cleaned_game_logs_2023.csv")

# === Aggregate player-level stats ===
player_avg = df.groupby("PLAYER_NAME").agg({
    "PTS": "mean",
    "AST": "mean",
    "REB": "mean",
    "STL": "mean",
    "BLK": "mean",
    "TOV": "mean",
    "FG3A": "mean",
    "FTA": "mean",
    "MIN": "mean"
}).reset_index()

# === Scale features ===
features = player_avg.drop(columns=["PLAYER_NAME"])
scaler = StandardScaler()
scaled_features = scaler.fit_transform(features)

# === Elbow Method to find optimal k ===
inertia = []
k_range = range(2, 10)
for k in k_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(scaled_features)
    inertia.append(kmeans.inertia_)

plt.figure(figsize=(8, 5))
plt.plot(k_range, inertia, marker='o')
plt.title("Elbow Method: Optimal Number of Clusters")
plt.xlabel("Number of Clusters (k)")
plt.ylabel("Inertia")
plt.grid(True)
plt.tight_layout()
plt.show()

# === Fit final KMeans (choose k based on elbow graph) ===
k = 4  # adjust if elbow plot suggests a different value
kmeans = KMeans(n_clusters=k, random_state=42)
player_avg['ARCHETYPE'] = kmeans.fit_predict(scaled_features)

# === PCA for 2D Visualization ===
pca = PCA(n_components=2)
pca_components = pca.fit_transform(scaled_features)

plt.figure(figsize=(10, 7))
scatter = plt.scatter(pca_components[:, 0], pca_components[:, 1], 
                      c=player_avg['ARCHETYPE'], cmap='viridis', s=60, edgecolors='k')
plt.title("Player Archetypes (PCA Reduced)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.grid(True)
plt.tight_layout()
plt.colorbar(scatter, label="Archetype Cluster")

# Optional: label points (small font)
# for i, name in enumerate(player_avg['PLAYER_NAME']):
#     plt.text(pca_components[i, 0], pca_components[i, 1], name, fontsize=6)

plt.show()

# === Save player archetype labels to CSV ===
player_avg.to_csv("data/player_archetypes.csv", index=False)
print("[DONE] Player archetypes saved to data/player_archetypes.csv")