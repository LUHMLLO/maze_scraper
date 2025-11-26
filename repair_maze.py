import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# 1. Load the existing (partial) data
print("Loading maze_full_report.json...")
try:
    with open('maze_full_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: Could not find maze_full_report.json")
    exit()

# 2. Find blocks that failed
indices_to_fix = []
for i, block in enumerate(data):
    # Check for the specific error message you saw
    content_str = str(block.get('content', []))
    if "ApolloError" in content_str or "Unexpected error" in content_str or "Failed to fetch" in content_str:
        indices_to_fix.append(i)

if not indices_to_fix:
    print("No errors found! Your JSON file is already perfect.")
    exit()

print(f"Found {len(indices_to_fix)} broken blocks. Starting repair job...")

# 3. Setup Browser
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# 4. Retry only the broken links
for idx in indices_to_fix:
    block = data[idx]
    url = block['url']
    print(f"Re-scraping [{idx+1}/{len(data)}]: {url.split('/')[-1]}...")

    try:
        driver.get(url)
        
        # Wait up to 20 seconds for content to load
        WebDriverWait(driver, 20).until(
            lambda d: "Loading..." not in d.find_element(By.TAG_NAME, "body").text
        )
        time.sleep(5) # Give it 5 extra seconds to settle
        
        # Grab text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        clean_lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        # Verify success
        if "ApolloError" in str(clean_lines):
            print(f"  ❌ FAILED AGAIN (Server might be blocking/busy)")
        else:
            print(f"  ✅ SUCCESS")
            data[idx]['content'] = clean_lines  # Update the JSON object
            
    except Exception as e:
        print(f"  ❌ Error: {e}")

driver.quit()

# 5. Save the fixed file
with open('maze_full_report.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("-" * 50)
print("Repair complete! The 'maze_full_report.json' file has been updated.")
print("Run 'python json_to_csv.py' again to generate your complete Excel file.")