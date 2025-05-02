import os
import csv
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Directory to store uploaded CSV files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.csv'):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        # Process the CSV
        data = process_csv(filename)
        
        # Trigger bot to start with extracted URLs
        bot_response = start_bot(data)
        
        return jsonify({
            "status": "success",
            "message": "CSV uploaded and processed",
            "bot_response": bot_response
        })
    else:
        return jsonify({"error": "Invalid file format. Only CSV allowed."}), 400


def process_csv(filepath):
    # Read the CSV file and extract the URLs
    urls = []
    with open(filepath, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row:  # Ensure the row is not empty
                urls.append(row[2])  # Assuming URLs are in the first column
    return urls


def start_bot(urls):
    # Simulate sending clicks to the URLs
    print("✅ Sending clicks to the following URLs:")
    clicked_urls = []
    
    for url in urls:
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                print(f"🚀 Successfully sent click to: {url}")
                clicked_urls.append(url)
            else:
                print(f"⚠️ Failed to send click to: {url} (Status Code: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Error sending click to {url}: {e}")

    return {"status": "started", "clicked_urls": clicked_urls}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)














# from flask import Flask, request, jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)  # Allow cross-origin requests

# @app.route("/start-bot", methods=["POST"])
# def start_bot():
#     data = request.json
#     keywords = data.get("keywords", [])
#     print("✅ Received keywords:", keywords)

#     return jsonify({
#         "status": "started",
#         "keywords": keywords
#     })

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)
