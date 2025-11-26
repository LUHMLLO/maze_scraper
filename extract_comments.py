import json
import csv

# Load the data
try:
    with open('maze_full_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: 'maze_full_report.json' not found.")
    exit()

output_file = "maze_comments_detailed.csv"

print("Extracting comments...")

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Header
    writer.writerow(['Block ID', 'Question', 'Participant ID', 'User Comment'])

    count = 0
    for block in data:
        content = block['content']
        block_id = block['block_id']
        
        # 1. Get the Question Title
        question = "Unknown"
        # Try to find the question title (usually before "Open Question" or near top)
        for i, line in enumerate(content):
            if line == "Open Question" and i > 0:
                question = content[i-1]
                break
        
        # If we couldn't find the "Open Question" label, try to guess
        if question == "Unknown":
            # Some blocks might not have the label, but have participants
            if any("Participant" in line for line in content):
                # Usually line 6 or 7 is the title in raw scrape
                if len(content) > 7:
                    question = content[6]

        # 2. Extract Comments
        # Pattern: "Participant X" is followed immediately by their comment
        for i, line in enumerate(content):
            if line.startswith("Participant"):
                participant_id = line
                # The comment is almost always the NEXT line
                if i + 1 < len(content):
                    comment_text = content[i+1]
                    
                    # Filter out garbage (sometimes the next line is "Participant..." if empty)
                    if not comment_text.startswith("Participant") and len(comment_text) > 1:
                        writer.writerow([block_id, question, participant_id, comment_text])
                        count += 1

print("-" * 30)
print(f"Success! Extracted {count} individual user comments.")
print(f"Open '{output_file}' to see them clearly.")