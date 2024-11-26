import fitz  # PyMuPDF for PDF reading
import openai
import json
import os

# Initialize OpenAI API key
openai.api_key #YOUR API KEY HERE 

def read_pdf(file_path):
    """
    Extracts text from a PDF file.
    """
    text = ""
    try:
        # Open the PDF file
        with fitz.open(file_path) as pdf:
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip().replace("\n", "")

def get_important_dates(text):
    """
    Sends the extracted PDF text to OpenAI's model to analyze and return key AI Winter/Spring dates in JSON format.
    """
    prompt = (
    "Please analyze the following academic article text to extract any important dates associated with significant "
    "events related to 'Artificial Intelligence' (including events related to 'AI Winter' and 'AI Spring'). "
    "If there are no relevant AI events, return an empty JSON array.\n\n"
    "For each relevant date, return the data in the following JSON format ONLY, with no extra text or explanations:\n\n"
    "[\n"
    "    {\n"
    "        \"file_name\": \"{file_name}\",\n"
    "        \"date\": \"YYYY-MM-DD\",\n"
    "        \"event_type\": \"AI Winter or AI Spring or another AI-related event\",\n"
    "        \"event_description\": \"Brief description of the event, such as major discoveries, funding cuts, societal impacts, or technological milestones.\",\n"
    "        \"impact_score\": \"Integer from 1 to 5, where 1 = minor impact and 5 = transformative impact\",\n"
    "        \"outcome_classification\": \"Category of outcome, e.g., 'funding boost', 'public perception shift', 'breakthrough technology', or 'regulatory change'\",\n"
    "        \"significance_today\": \"Explanation of how this event impacts or relates to modern AI, including any lasting effects or technologies that originated or changed due to the event.\"\n"
    "    },\n"
    "    ...\n"
    "]\n\n"
    "Return only a JSON array following this format, with no additional text. If no relevant dates are found, return an empty JSON array: []\n\n"
    "Here is the academic article text:\n\n" + text
        )
    
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Specify the GPT model
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in extracting structured data from text."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.5
    )
    
    # Parse response to JSON
    try:
        response_text = response.choices[0].message.content
        dates_json = json.loads(response_text)  # Convert response text to JSON
    except json.JSONDecodeError:
        print("Error parsing response to JSON format. Returning raw text.")
        dates_json = response_text  # Return raw text if JSON parsing fails
    
    return dates_json

def main(pdf_path):
    # Extract text from the PDF
    pdf_text = read_pdf(pdf_path)
    
    # Send the extracted text to the model and get the dates data
    important_dates = get_important_dates(pdf_text)
    
    # Output the results to JSON file if the response is in valid JSON format
    if isinstance(important_dates, list):  # Check if it's a list, which is the expected JSON format
        output_dir = "../output"
        os.makedirs(output_dir, exist_ok=True)
        output_file_path = os.path.join(output_dir, "important_dates.json")
        
        # Append the new data to the JSON file
        if os.path.exists(output_file_path):
            with open(output_file_path, "r") as file:
                existing_data = json.load(file)
        else:
            existing_data = []
        
        existing_data.extend(important_dates)  # Combine new data with existing data
        
        # Save to the output JSON file
        with open(output_file_path, "w") as file:
            json.dump(existing_data, file, indent=4, ensure_ascii=False)
        print(f"Appended data for {pdf_path} to important_dates.json.")
    else:
        print(f"Skipping appending non-JSON content for {pdf_path}")


# Example usage
if __name__ == "__main__":
    pdf_dir = "UPDATED-ai-seasonal-changes/pdfs"
    os.chdir(pdf_dir)
    for pdf_file in os.listdir(os.curdir):
        try:
            if pdf_file.endswith(".pdf"):
                print(f"Processing file: {pdf_file}")
                main(pdf_file)
        except Exception as e:
            print("Error processing {} : {}".format(pdf_file,e))
