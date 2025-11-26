import json
import csv
import re

# Load the scraped data
try:
    with open('maze_full_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: Could not find 'maze_full_report.json'. Make sure it is in the same folder.")
    exit()

# Prepare CSV file
output_file = 'maze_results_final.csv'

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write Header
    writer.writerow(['Block ID', 'Question/Title', 'Type', 'Metric 1', 'Value 1', 'Metric 2', 'Value 2', 'Metric 3', 'Value 3', 'User Comments'])

    print(f"Processing {len(data)} blocks...")

    for block in data:
        content = block['content']
        url = block['url']
        block_id = block['block_id']
        
        # Skip error blocks
        if "ApolloError" in str(content):
            print(f"Skipping error block: {block_id}")
            continue

        # --- EXTRACT TITLE ---
        # Usually the line before "Prototype Test" or "Opinion Scale" or "Multiple Choice"
        # Or often the 7th or 8th line in the list.
        title = "Unknown"
        block_type = "Unknown"
        
        # Heuristic to find type and title
        for i, line in enumerate(content):
            if line in ["Prototype Test", "Prototype Test • Screen-based", "Opinion Scale", "Multiple Choice", "Open Question", "Yes/No"]:
                block_type = line
                # The title is usually 1 or 2 lines before the type
                if i > 0:
                    title = content[i-1]
                break
        
        # If we couldn't find a standard type, try to guess from content
        if block_type == "Unknown":
            if "Report introduction" in content:
                title = "Introduction"
                block_type = "Intro"

        # --- EXTRACT METRICS BASED ON TYPE ---
        m1_name, m1_val, m2_name, m2_val, m3_name, m3_val = "", "", "", "", "", ""
        comments = []

        # 1. PROTOTYPE / MISSION BLOCKS
        if "Prototype" in block_type:
            try:
                # Find indices of key metrics
                if "Success rate" in content:
                    idx = content.index("Success rate")
                    m1_name = "Success Rate"
                    m1_val = content[idx-1] # Value is usually before label
                
                if "Misclick rate" in content:
                    idx = content.index("Misclick rate")
                    m2_name = "Misclick Rate"
                    m2_val = content[idx-1]

                if "Avg. duration" in content:
                    idx = content.index("Avg. duration")
                    m3_name = "Avg Duration"
                    m3_val = content[idx-1]
            except:
                pass

        # 2. OPINION SCALES
        elif "Opinion Scale" in block_type:
            try:
                if "Average" in content:
                    idx = content.index("Average")
                    m1_name = "Average Score"
                    m1_val = content[idx-1]
                
                if "Responses" in content:
                    idx = content.index("Responses")
                    m2_name = "Total Responses"
                    m2_val = content[idx-1]
            except:
                pass

        # 3. YES/NO & MULTIPLE CHOICE
        elif block_type in ["Yes/No", "Multiple Choice"]:
             # Try to grab top 3 results
            try:
                # This is tricky because the format varies, but usually: Label, Percentage, Count
                # We will just dump the first few percentages we find
                found_percentages = [x for x in content if "%" in x]
                if len(found_percentages) > 0:
                    m1_name = "Result 1"
                    m1_val = found_percentages[0]
                if len(found_percentages) > 1:
                    m2_name = "Result 2"
                    m2_val = found_percentages[1]
            except:
                pass

        # 4. OPEN QUESTIONS (COMMENTS)
        elif "Open Question" in block_type:
            # Gather lines that look like user comments (usually after "Participant X")
            for i, line in enumerate(content):
                if line.startswith("Participant"):
                    # The comment is usually the NEXT line
                    if i + 1 < len(content):
                        comments.append(f"{line}: {content[i+1]}")
            
            m1_name = "Comment Count"
            m1_val = len(comments)

        # Write the row
        writer.writerow([
            block_id, 
            title, 
            block_type, 
            m1_name, m1_val, 
            m2_name, m2_val, 
            m3_name, m3_val, 
            " | ".join(comments)
        ])

print("-" * 30)
print(f"Done! Open '{output_file}' in Excel/LibreOffice.")