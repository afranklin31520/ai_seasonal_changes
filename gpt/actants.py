import os
import openai
import json
import time
import pandas as pd
import re
import networkx as nx
import collections
from datetime import datetime
# Load datasets
def load_data():
    try:
        #techcrunch_df = pd.read_csv('../data/techcrunch_dataset.csv')
        #arxiv_df = pd.read_csv('../data/arxiv_dataset.csv', low_memory=False)
        #arxiv_df = arxiv_df.loc[:, ~arxiv_df.columns.str.contains('^Unnamed')]
        gizmodo_df = pd.read_csv("ouput\gizmodo.csv")
        # Select useful columns
        useful_columns = ['title', 'author', 'pub_date', 'full_text', 'key_words']
        #techcrunch_df_useful = techcrunch_df[useful_columns]
        #arxiv_df_useful = arxiv_df[useful_columns]
        gizmodo_df_useful = gizmodo_df[useful_columns]
        # Combine datasets
        combined_df = pd.concat([gizmodo_df_useful])
        return combined_df
    except FileNotFoundError as e:
        print(f"Error loading data: {e}")
        return None

def create_prompt(row):
    prompt = f"""
You are an AI assistant that analyzes articles to identify actants according to Actor-Network Theory (ANT) for time series and knowledge graph analysis. Given the following article, please perform the following tasks:

1. **Identify and list the actants mentioned in the article**, providing the following information for each actant:
   - **Actant Name**: Use a standardized, concise name.
   - **Category**: Choose from the following categories:
     - **Technological Actant**: Technologies, tools, software, hardware, AI models.
     - **Human Actant**: Individual people (e.g., researchers, developers, executives).
     - **Institutional Actant**: Organizations, companies, institutions (e.g., Google, OpenAI).
     - **Economic Actant**: Financial elements (e.g., funding amounts, investments, economic shifts, market trends).
     - **Social and Cultural Actant**: Societal trends, cultural references, communities, public perceptions.
     - **Temporal Actant**: Time-related elements (e.g., dates, events, historical periods, past patterns, future predictions).
     - **Geographical Actant**: Locations, regions, countries.
     - **Ethical and Regulatory Actant**: Policies, regulations, ethical guidelines, policy changes.
   - **Role/Function**: Briefly describe the actant's role or relevance in the context of the article.
   - **Influence Score**: Assign a numerical value (1-5) representing the actant's degree of influence in the article (5 being highly influential).
   - **Date**: The date(s) or time period associated with the actant's relevance in the article.

2. **Identify and list relationships between actants**, specifying:
   - **Source Actant**
   - **Relationship Type**: Use active voice and a standardized verb phrase (e.g., "develops", "funds", "uses", "leads", "partners with", "competes with", "influences", "governs", etc.).
   - **Target Actant**
   - **Significance Score**: Assign a numerical value (1-5) representing the significance of the relationship (5 being highly significant).
   - **Date**: The date(s) or time period when the relationship is relevant, as mentioned in the article.

3. **Identify any patterns, trends, or predictions mentioned in the article**, including how past events relate to current developments and potential future implications.

4. **Format your response in JSON**, following this structure:

{{
  "Actants": [
    {{
      "Actant Name": "",
      "Category": "",
      "Role/Function": "",
      "Influence Score": ,
      "Date": ""
    }},
    ...
  ],
  "Relationships": [
    {{
      "Source Actant": "",
      "Relationship Type": "",
      "Target Actant": "",
      "Significance Score": ,
      "Date": ""
    }},
    ...
  ],
  "Patterns": [
    {{
      "Pattern Description": "",
      "Relevant Actants": ["", ...],
      "Implications": ""
    }},
    ...
  ]
}}

**Article Information**:

- **Title**: {row['title']}
- **Author**: {row['author']}
- **Publication Date**: {row['pub_date']}
- **Full Text**: {row['full_text']}
- **Keywords**: {row['key_words']}

**Instructions**:

- **Focus** on extracting actants, their relationships, and any patterns or trends based solely on the information provided.
- **Ensure** that all actants are relevant to the article's content and help address the research questions regarding actors in AI development cycles, their interactions, external factors, and potential predictions.
- **Use consistent naming conventions** and clearly define roles and relationships.
- **Categorize entities appropriately**: For example, companies like OpenAI should be categorized as "Institutional Actant", not "Human Actant".
- **Use active voice** for relationship types, and ensure they are in a standardized format for knowledge graph analysis.
- **Assign influence and significance scores** to actants and relationships to denote their degree of influence or significance.
- **Include dates** for actants and relationships to enable time series analysis.
- **Do not include** any additional commentary or analysis beyond what is requested.

**Important**: Ensure that your response is strictly in the JSON format provided, without any additional text or commentary. Do not include any explanations outside the JSON structure.
"""
    return prompt


def clean_json_response(response):
    response = response.strip().strip('```').strip('json').strip()
    json_start = response.find('{')
    json_end = response.rfind('}') + 1
    response = response[json_start:json_end]
    return response

def parse_json_safely(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        return None

def process_data(df):
    openai.api_key #= YOUR API KEY HERE

    for index, row in df.iterrows():
        prompt = create_prompt(row)
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.2
            )
            actant_response = response.choices[0].message.content
            if actant_response:
                cleaned_response = clean_json_response(actant_response)
                actant_data = parse_json_safely(cleaned_response)

                if actant_data:
                    # Post-processing to correct misclassifications
                    for actant in actant_data.get("Actants", []):
                        name = actant.get("Actant Name", "")
                        category = actant.get("Category", "")
                        if category == "Human Actant" and not re.match(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)*$', name):
                            actant['Category'] = "Institutional Actant"

                    # Convert actants and relationships to JSON strings
                    actants_json_str = json.dumps(actant_data.get("Actants", []))
                    relationships_json_str = json.dumps(actant_data.get("Relationships", []))
                    
                    # Store them in the DataFrame
                    df.at[index, 'Actants'] = actants_json_str
                    df.at[index, 'Relationships'] = relationships_json_str
                    
                    print(f"Processed index {index} successfully")
                else:
                    print(f"Failed to parse JSON for index {index}")
                    df.at[index, 'Actants'] = '[]'
                    df.at[index, 'Relationships'] = '[]'
            else:
                print(f"No response for index {index}")
                df.at[index, 'Actants'] = '[]'
                df.at[index, 'Relationships'] = '[]'

        except Exception as e:
            print(f"An error occurred for index {index}: {e}")
            df.at[index, 'Actants'] = '[]'
            df.at[index, 'Relationships'] = '[]'
        
        time.sleep(1)  # Respect API rate limits

    return df

def perform_network_analysis(df):
    edges = []
    for index, row in df.iterrows():
        relationships_json_str = row['Relationships']
        if isinstance(relationships_json_str, str):
            try:
                relationships = json.loads(relationships_json_str)
                for rel in relationships:
                    source = rel['Source Actant']
                    target = rel['Target Actant']
                    rel_type = rel['Relationship Type']
                    edge = (source, target, {'relationship': rel_type, 'article_index': index})
                    edges.append(edge)
            except json.JSONDecodeError:
                print(f"Invalid JSON string at index {index}")
        else:
            print(f"Non-string value in 'Relationships' column at index {index}: {relationships_json_str}")

    G = nx.MultiDiGraph()
    G.add_edges_from(edges)
    return G

def perform_time_series_analysis(df):
    df['pub_date'] = pd.to_datetime(df['pub_date'])
    actant_time_series = {}

    for index, row in df.iterrows():
        actants_json_str = row['Actants']
        if actants_json_str:
            actants = json.loads(actants_json_str)
            for actant in actants:
                name = actant['Actant Name']
                date = row['pub_date']
                if name not in actant_time_series:
                    actant_time_series[name] = []
                actant_time_series[name].append(date)

    time_series_data = {}
    for actant_name, dates in actant_time_series.items():
        counter = collections.Counter()
        for date in dates:
            year_month = date.strftime('%Y-%m')
            counter[year_month] += 1
        time_series_data[actant_name] = dict(sorted(counter.items()))

    return time_series_data

def main():
    # Load and process data
    combined_df = load_data()
    if combined_df is None:
        return

    test_df = combined_df.head(10).copy()  # Using only 10 rows for testing
    processed_df = process_data(test_df)

    # Save processed data
    processed_df.to_csv('ouput/gizmodo_results.csv', index=False)
    print("Analysis completed and results saved.")

    # Perform network analysis
    G = perform_network_analysis(processed_df)
    print(f"Network created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

    # Perform time series analysis
    time_series_data = perform_time_series_analysis(processed_df)
    print(f"Time series analysis completed for {len(time_series_data)} actants.")

    # You can add further analysis or visualization here

if __name__ == "__main__":
    main()