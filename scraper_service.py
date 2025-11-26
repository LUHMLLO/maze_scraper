import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    # Add user-agent to avoid detection/rendering issues
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def discover_blocks(main_url, progress_callback=None):
    """
    Visits the main URL and discovers all report block URLs by clicking through the navigation.
    """
    driver = get_driver()
    discovered_urls = []
    
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    
    try:
        log(f"Visiting main URL: {main_url}")
        driver.get(main_url)
        
        # Wait for initial load
        WebDriverWait(driver, 20).until(
            lambda d: "Loading..." not in d.find_element(By.TAG_NAME, "body").text
        )
        time.sleep(5) # Buffer for animations
        
        # Initial URL might be the first block
        current_url = driver.current_url
        if "report" in current_url:
            discovered_urls.append(current_url)
            
        # Find navigation elements. 
        # Based on investigation, they are likely in a sidebar.
        # We'll look for elements that look like nav items.
        # The structure seen was: div > p "Report introduction"
        # We'll try to find the container of these items.
        
        # Strategy: Find all elements that look like menu items and click them.
        # This is tricky because the DOM might change.
        # Let's try to find all text elements in the sidebar.
        
        # A more robust way might be to find the sidebar container first.
        # But since we don't have the exact class names (they look generated), 
        # we might rely on the text or position.
        
        # Let's try to find all elements that are likely clickable in the sidebar.
        # We can assume the sidebar is on the left.
        
        # For now, let's try to find all 'p' tags that are likely nav items
        # and click them if they are not the current one.
        
        # Actually, a better approach for this specific site (Maze reports)
        # is to look for the specific structure we saw:
        # div > p with specific styles or classes? No, classes are hashed.
        
        # Let's try to find the list of screens.
        # Usually they are in a list.
        
        # Let's try to find all elements that look like "Report introduction", "Mission 1", etc.
        # But we don't know the text.
        
        # Let's try to find all clickable elements in the left part of the screen?
        # That's hard in headless.
        
        # Let's go with a broader search and filter.
        # We will look for a common parent that contains many of these items.
        
        # Alternative: Just use the URLs if we can find them in the DOM.
        # But we found they weren't in 'a' tags.
        
        # Let's try to find the container by looking for "Report introduction" and going up.
        try:
            intro_el = driver.find_element(By.XPATH, "//*[contains(text(), 'Report introduction')]")
            # Go up until we find a container with multiple children that look similar?
            # Or just find all siblings of its parent's parent?
            
            # Let's try to click everything that looks like a sibling of the intro item's container.
            # This is a bit "heuristic".
            
            # Let's try a different approach:
            # We know the URLs follow a pattern: .../report/.../ID
            # Maybe we can just extract IDs from the state or network logs?
            # Selenium doesn't give easy access to network logs without setup.
            
            # Let's stick to clicking.
            # We will find all elements that share the same class as the "Report introduction" text,
            # or their parents.
            
            # The class we saw was: "TextPrimitive-styled__StyledRoot-sc-880bba74-0 jMgQQj Text-styled__StyledTextPrimitive-sc-40327495-0 kBssIK"
            # This is likely unstable.
            
            # Let's try to find all elements that are "p" tags and are in the sidebar.
            # We can guess the sidebar is the first major div?
            
            # Let's try to iterate through all elements that look like nav items.
            # We can re-find them after each click to avoid stale elements.
            
            # Heuristic: Find all P tags. Filter for those that are likely nav items (short text, visible).
            # Then click them and check if URL changes.
            
            elements = driver.find_elements(By.TAG_NAME, "p")
            potential_nav_items = []
            for el in elements:
                try:
                    if el.is_displayed() and len(el.text) < 50 and len(el.text) > 0:
                        potential_nav_items.append(el)
                except:
                    pass
            
            print(f"Found {len(potential_nav_items)} potential nav items.")
            
            # This is risky. Let's try to be more specific.
            # The "Report introduction" is a good anchor.
            # Let's find its parent, and then find all children of that parent's parent.
            
            # Strategy: Find "Report introduction" element, get its class, and find all other elements with that class.
            intro_el = driver.find_element(By.XPATH, "//*[contains(text(), 'Report introduction')]")
            intro_class = intro_el.get_attribute("class")
            
            if intro_class:
                # Find all p tags with this class
                # Note: Classes might have spaces, CSS selector needs dots
                css_selector = f"p.{intro_class.replace(' ', '.')}"
                similar_items = driver.find_elements(By.CSS_SELECTOR, css_selector)
                log(f"Found {len(similar_items)} navigation items.")
                
                for i in range(len(similar_items)):
                    # Re-find to avoid stale elements
                    similar_items = driver.find_elements(By.CSS_SELECTOR, css_selector)
                    if i < len(similar_items):
                        item = similar_items[i]
                        try:
                            txt = item.text
                            # Click if it's not the intro (which we are already on, presumably) 
                            # or just click everything to be safe.
                            if item.is_displayed():
                                item.click()
                                time.sleep(1.5) # Wait for URL update
                                
                                if driver.current_url not in discovered_urls and "report" in driver.current_url:
                                    discovered_urls.append(driver.current_url)
                                    log(f"Found block: {driver.current_url.split('/')[-1]}")
                        except Exception as e:
                            print(f"   Error clicking item {i}: {e}")
                        
        except Exception as e:
            print(f"Could not use 'Report introduction' anchor: {e}")
            
    except Exception as e:
        print(f"Error during discovery: {e}")
    finally:
        driver.quit()
        
    return discovered_urls

def scrape_content(urls, progress_callback=None):
    """
    Scrapes content from the provided URLs.
    """
    driver = get_driver()
    results = []
    
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)
    
    log(f"Starting extraction for {len(urls)} blocks.")
    
    try:
        for i, url in enumerate(urls):
            log(f"[{i+1}/{len(urls)}] Processing: {url.split('/')[-1]}...")
            try:
                driver.get(url)
                WebDriverWait(driver, 15).until(
                    lambda d: "Loading..." not in d.find_element(By.TAG_NAME, "body").text
                )
                time.sleep(3) # Buffer
                
                body_text = driver.find_element(By.TAG_NAME, "body").text
                clean_lines = [line.strip() for line in body_text.split('\n') if line.strip()]
                
                results.append({
                    "block_id": url.split('/')[-1],
                    "url": url,
                    "content": clean_lines
                })
            except Exception as e:
                print(f"   Error scraping {url}: {e}")
                
    finally:
        driver.quit()
        
    return results

if __name__ == "__main__":
    # Test
    test_url = "https://app.maze.co/report/Clickable-prototype/5fmaz7mi8ykwvw/intro"
    links = discover_blocks(test_url)
    print("Discovered:", links)
