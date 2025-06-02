import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load cleaned data
df = pd.read_csv("data/cleaned_game_logs_2023.csv")

# 1. Points distribution
plt.figure(figsize=(8, 5))
sns.histplot(df['PTS'], bins=30, kde=True)
plt.title("Distribution of Points Scored")
plt.xlabel("Points")
plt.ylabel("Frequency")
plt.show()

# 2. Correlation heatmap
plt.figure(figsize=(12, 8))
corr = df[['PTS', 'AST', 'REB', 'STL', 'BLK', 'TOV', 'MIN', 'FG3A', 'FG3M', 'FTA', 'FTM']].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Correlation Between Performance Metrics")
plt.show()

# 3. Home vs Away boxplot
plt.figure(figsize=(8, 5))
sns.boxplot(x='HOME_GAME', y='PTS', data=df)
plt.title("Points Scored: Home (1) vs Away (0)")
plt.xlabel("Home Game")
plt.ylabel("Points")
plt.show()

# 4. Opponent average points
opponent_avg = df.groupby('OPPONENT')['PTS'].mean().sort_values(ascending=False)
plt.figure(figsize=(12, 5))
sns.barplot(x=opponent_avg.index, y=opponent_avg.values)
plt.xticks(rotation=90)
plt.title("Average Points by Opponent Team")
plt.ylabel("Avg Points")
plt.xlabel("Opponent")
plt.show()
