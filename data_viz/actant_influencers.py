import pandas as pd
import json
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx

# Step 1: Load the CSV file
data = pd.read_csv(r'C:\Users\afran\Downloads\new_ai_research\UPDATED-ai-seasonal-changes\output\gizmodo_results.csv')

# Step 2: Parse the 'Actants' column (convert the string to JSON)
data['Actants'] = data['Actants'].apply(json.loads)

# Check the structure of 'Actants' column
# print(data['Actants'].head())  # Uncomment if you need to inspect the parsed 'Actants' data

# Extract Actants into a DataFrame
actants_list = []
for actant_group in data['Actants']:
    for actant in actant_group:  # Iterate over the list of actants for each row
        actants_list.append(actant)

# Create a DataFrame from the extracted actants
actants_df = pd.DataFrame(actants_list)

# Check the new DataFrame (actants_df contains structured data)
print(actants_df.head())  # Print the first 5 rows to inspect the structure

# Step 3: Plot influence scores by category
plt.figure(figsize=(10, 6))
sns.barplot(x='Category', y='Influence Score', data=actants_df, palette="Blues_d")
plt.title('Influence Scores by Actant Category')
plt.xlabel('Actant Category')
plt.ylabel('Influence Score')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()