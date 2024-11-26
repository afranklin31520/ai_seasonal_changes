import networkx as nx
import pandas as pd
import json
import os

# Sample Actants and Relationships data from your dataset (same as before)
INPUT_FILE = r"UPDATED-ai-seasonal-changes\output\gizmodo_results.csv"

# Load the CSV
df1 = pd.read_csv(INPUT_FILE)

# Extract Actants and Relationships columns
actants = df1["Actants"]
relationships = df1["Relationships"]

# Create a directed graph
G = nx.DiGraph()

# Add nodes (Actants)
for actant_str in actants:
    try:
        actant_list = json.loads(actant_str)
        for actant in actant_list:
            category = actant.get("Category", "Unknown")  # Default to "Unknown" if category is missing
            influence_score = actant.get("Influence Score", 1)  # Default influence score if missing
            G.add_node(actant["Actant Name"], category=category, influence_score=influence_score)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing actant: {e}")

# Add edges (Relationships)
for relationship_str in relationships:
    try:
        relationship_list = json.loads(relationship_str)
        for relationship in relationship_list:
            G.add_edge(relationship["Source Actant"], relationship["Target Actant"], relationship=relationship["Relationship Type"])
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error processing relationship: {e}")

# Ensure output directories exist
output_dir = r"UPDATED-ai-seasonal-changes\data_viz"
os.makedirs(output_dir, exist_ok=True)

# Export to GraphML for Gephi
nx.write_graphml(G, os.path.join(output_dir, "network_graph.graphml"))

# Optionally, export to CSV for Gephi

# Create a DataFrame for nodes
nodes_data = [{"Id": node, "Label": node, "Category": G.nodes[node].get("category", "Unknown"), "Influence Score": G.nodes[node].get("influence_score", 1)} for node in G.nodes()]
nodes_df = pd.DataFrame(nodes_data)

# Create a DataFrame for edges
edges_data = [{"Source": u, "Target": v, "Relationship": d['relationship']} for u, v, d in G.edges(data=True)]
edges_df = pd.DataFrame(edges_data)

# Save nodes and edges as CSV
nodes_df.to_csv(os.path.join(output_dir, "nodes.csv"), index=False)
edges_df.to_csv(os.path.join(output_dir, "edges.csv"), index=False)

print("Graph data with influence scores exported to GraphML and CSV.")
