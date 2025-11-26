import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- YOUR LINKS ---
urls = [
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/intro",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/5d765ffd",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/114e633d",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/21fe3808",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/33efea68",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/75dc021c",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/4d37b500",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/ca4147d8",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/1ae3a70f",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/20ae8d76",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/68abc027",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/a569548d",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/68d86305",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/43b5092f",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/aae81dea",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/d2bf3381",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/f6ec4ac5",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/f9f69cbe",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/380037b8",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/635b95b6",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/2f19c5fb",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/7460e4b5",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/10107af5",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/f9c9532",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/e18c940e",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/4e5e0017",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/8eff99a9",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/8f66ceec",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/4c9c65f4",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/67a3bb1f",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/2966ae4d",
    "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/7fc6d6b1"
]

# --- SETUP BROWSER ---
chrome_options = Options()
chrome_options.add_argument("--headless=new") # Run invisible
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--log-level=3")

print("Initializing Browser... (This may take a moment)")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

results = []

print(f"Starting extraction for {len(urls)} report blocks.")
print("-" * 50)

for i, url in enumerate(urls):
    print(f"[{i+1}/{len(urls)}] Processing: {url.split('/')[-1]}...")
    
    try:
        driver.get(url)
        
        # Wait specifically for the 'Loading...' text to disappear
        WebDriverWait(driver, 15).until(
            lambda d: "Loading..." not in d.find_element(By.TAG_NAME, "body").text
        )
        
        # Give it a tiny extra buffer for charts to animate in
        time.sleep(5)
        
        # Extract the full visible text
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Clean the text (remove empty lines)
        clean_lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        # Store Data
        results.append({
            "block_id": url.split('/')[-1],
            "url": url,
            "content": clean_lines
        })
        
    except Exception as e:
        print(f"   Error: Could not load data for {url}")

driver.quit()

# --- SAVE TO FILE ---
output_file = "maze_full_report.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print("-" * 50)
print(f"SUCCESS! All data saved to {output_file}")
