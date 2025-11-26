from flask import Flask, render_template, request, jsonify, send_file
import scraper_service
import os
import json
import csv
import io

import threading

app = Flask(__name__)

# Store results in memory for simplicity (or file)
LATEST_RESULTS = []
JOB_STATUS = {
    "status": "idle", # idle, running, completed, error
    "message": "",
    "logs": []
}

def run_scrape_job(url):
    global LATEST_RESULTS, JOB_STATUS
    
    def update_progress(msg):
        JOB_STATUS["message"] = msg
        JOB_STATUS["logs"].append(msg)
        
    try:
        JOB_STATUS["status"] = "running"
        JOB_STATUS["logs"] = []
        update_progress(f"Starting job for {url}")
        
        # 1. Discover blocks
        update_progress("Discovering blocks...")
        block_urls = scraper_service.discover_blocks(url, progress_callback=update_progress)
        
        if not block_urls:
            JOB_STATUS["status"] = "error"
            update_progress("No blocks found.")
            return
            
        update_progress(f"Found {len(block_urls)} blocks.")
        
        # 2. Scrape content
        results = scraper_service.scrape_content(block_urls, progress_callback=update_progress)
        LATEST_RESULTS = results
        
        JOB_STATUS["status"] = "completed"
        update_progress("Scraping complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        JOB_STATUS["status"] = "error"
        update_progress(f"Error: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def scrape():
    global JOB_STATUS
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
        
    if JOB_STATUS["status"] == "running":
        return jsonify({"error": "A job is already running"}), 409
        
    # Start background thread
    thread = threading.Thread(target=run_scrape_job, args=(url,))
    thread.start()
    
    return jsonify({"message": "Job started"})

@app.route('/api/status')
def status():
    return jsonify(JOB_STATUS)

@app.route('/api/download/<format>')
def download(format):
    global LATEST_RESULTS
    if not LATEST_RESULTS:
        return "No data to download", 404
        
    if format == 'json':
        return jsonify(LATEST_RESULTS)
        
    elif format == 'csv':
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Block ID', 'URL', 'Content'])
        
        for item in LATEST_RESULTS:
            content_str = " | ".join(item['content'])
            writer.writerow([item['block_id'], item['url'], content_str])
            
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='maze_results.csv'
        )
        
    return "Invalid format", 400

if __name__ == '__main__':
    # Debug mode should be False for production/public use
    app.run(debug=False, port=5000)
