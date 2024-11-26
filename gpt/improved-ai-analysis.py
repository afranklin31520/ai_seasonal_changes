import fitz
import openai
import json
import os
from datetime import datetime

def get_important_dates(text, file_name):
    """
    Enhanced prompt for more structured analysis of AI periods and events.
    """
    prompt = f"""
    Analyze the following academic article to extract events related to AI development periods, focusing on identifying AI Winter and AI Spring phases. Format the response as a structured JSON array with enhanced metadata.

    Specific requirements:
    1. Identify both explicit dates and contextual time periods
    2. Classify the AI development phase for each event
    3. Quantify the impact and provide evidence-based reasoning
    
    Return the data in this exact JSON format:
    [{{
        "file_name": "{file_name}",
        "date": {{
            "exact_date": "YYYY-MM-DD",  # If known, otherwise null
            "period_start": "YYYY-MM-DD", # Approximate period start
            "period_end": "YYYY-MM-DD",   # Approximate period end
            "confidence_level": "HIGH/MEDIUM/LOW"
        }},
        "phase_classification": {{
            "primary_category": "AI_WINTER/AI_SPRING/TRANSITION",
            "subcategory": "FUNDING/RESEARCH/TECHNOLOGICAL/SOCIETAL",
            "evidence": "Quote or reference from the text supporting this classification"
        }},
        "event_details": {{
            "title": "Brief title of the event",
            "description": "Detailed description of the event",
            "key_actors": ["List of involved institutions, researchers, or organizations"],
            "technical_domains": ["List of relevant technical areas"],
            "funding_changes": {{
                "direction": "INCREASE/DECREASE/STABLE",
                "magnitude": "Integer 1-5",
                "details": "Specific funding details if available"
            }}
        }},
        "impact_analysis": {{
            "immediate_impact": {{
                "score": "Integer 1-5",
                "description": "Immediate effects and reactions"
            }},
            "long_term_impact": {{
                "score": "Integer 1-5",
                "description": "Lasting influence on AI development"
            }},
            "affected_areas": ["List of impacted research/industry areas"]
        }},
        "metadata": {{
            "citations": ["Related works cited"],
            "verification_sources": ["Sources confirming the event"],
            "extraction_confidence": "HIGH/MEDIUM/LOW"
        }}
    }}]

    Guidelines for classification:
    - AI_SPRING indicators: Funding increases, breakthrough achievements, public/private investment growth, significant publications
    - AI_WINTER indicators: Funding cuts, project cancellations, reduced interest, criticism of AI capabilities
    - TRANSITION indicators: Mixed signals, methodology shifts, emerging alternative approaches

    If no relevant events are found, return an empty array: []

    Original text for analysis:
    {text}
    """
    
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a specialized AI historian focused on identifying and analyzing key periods in AI development."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.3
    )
    
    try:
        response_text = response.choices[0].message.content
        dates_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing response for {file_name}: {e}")
        dates_json = []
    
    return dates_json

def process_results(json_data):
    """
    Process and analyze the collected data for time series analysis.
    """
    timeline_analysis = {
        "periods": [],
        "trends": {
            "ai_spring_periods": [],
            "ai_winter_periods": [],
            "transition_periods": []
        },
        "impact_progression": [],
        "funding_patterns": []
    }
    
    # Sort events chronologically
    sorted_events = sorted(json_data, key=lambda x: x['date']['period_start'])
    
    # Analyze periods and transitions
    current_period = None
    for event in sorted_events:
        period = {
            "start": event['date']['period_start'],
            "end": event['date']['period_end'],
            "phase": event['phase_classification']['primary_category'],
            "confidence": event['date']['confidence_level'],
            "key_events": []
        }
        
        # Add to appropriate trend category
        if event['phase_classification']['primary_category'] == 'AI_SPRING':
            timeline_analysis['trends']['ai_spring_periods'].append(period)
        elif event['phase_classification']['primary_category'] == 'AI_WINTER':
            timeline_analysis['trends']['ai_winter_periods'].append(period)
        else:
            timeline_analysis['trends']['transition_periods'].append(period)
        
        # Track impact progression
        timeline_analysis['impact_progression'].append({
            "date": event['date']['period_start'],
            "immediate_impact": event['impact_analysis']['immediate_impact']['score'],
            "long_term_impact": event['impact_analysis']['long_term_impact']['score']
        })
        
        # Track funding patterns
        if event['event_details']['funding_changes']['direction'] != 'STABLE':
            timeline_analysis['funding_patterns'].append({
                "date": event['date']['period_start'],
                "direction": event['event_details']['funding_changes']['direction'],
                "magnitude": event['event_details']['funding_changes']['magnitude']
            })
    
    return timeline_analysis

def main(pdf_path):
    # Extract text and process
    pdf_text = read_pdf(pdf_path)
    file_name = os.path.basename(pdf_path)
    important_dates = get_important_dates(pdf_text, file_name)
    
    # Save raw results
    output_dir = "../output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save raw data
    raw_output_path = os.path.join(output_dir, "raw_events.json")
    if os.path.exists(raw_output_path):
        with open(raw_output_path, "r") as file:
            existing_data = json.load(file)
    else:
        existing_data = []
    
    existing_data.extend(important_dates)
    
    with open(raw_output_path, "w") as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
    
    # Process and save analysis
    timeline_analysis = process_results(existing_data)
    analysis_output_path = os.path.join(output_dir, "timeline_analysis.json")
    
    with open(analysis_output_path, "w") as file:
        json.dump(timeline_analysis, file, indent=4, ensure_ascii=False)
    
    print(f"Processed {file_name}. Results saved to raw_events.json and timeline_analysis.json")

if __name__ == "__main__":
    pdf_dir = "UPDATED-ai-seasonal-changes/pdfs"
    os.chdir(pdf_dir)
    for pdf_file in os.listdir(os.curdir):
        if pdf_file.endswith(".pdf"):
            print(f"Processing file: {pdf_file}")
            try:
                main(pdf_file)
            except Exception as e:
                print(f"Error processing {pdf_file}: {e}")
