from flask import Flask, request, jsonify, render_template, send_file
from scraper import WebScraper
import os
import pandas as pd
import pdb

app = Flask(__name__)
scraper = WebScraper()

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.form.get('url')
    print(f"Received URL: {url}")  # Debugging statement
    if not url:
        return jsonify({"error": "Please provide a URL to scrape."}), 400
    try:
        data = scraper.scrape(url)
        print(f"Scraped data: {data}")  # Debugging statement
        excel_file = "scraped_data.xlsx"
        scraper.export_to_excel(data, file_name=excel_file)
        return jsonify({"message": "Scraping successful!", "download_url": "/download"})
    except Exception as e:
        print(f"Error during scraping: {e}")  # Debugging statement
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading."}), 400

    if not file.filename.endswith(('.xls', '.xlsx')):
        return jsonify({"error": "Invalid file format. Please upload an Excel file."}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    try:
        data = process_uploaded_file(file_path)
        return jsonify({
            "message": "File processed successfully!",
            "data_summary": data['summary'],
            "recommendations": data['recommendations']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download():
    excel_file = "scraped_data.xlsx"
    if os.path.exists(excel_file):
        return send_file(excel_file, as_attachment=True)
    return "File not found.", 404

def process_uploaded_file(file_path):
    try:
        # Read the uploaded file (assuming it's an Excel file)
        df = pd.read_excel(file_path)
        print(f"Dataframe loaded: {df.head()}")  # Debugging statement

        # Sort and classify data
        sorted_data = df.sort_values(by=df.columns[0])  # Sort by the first column
        grouped_data = sorted_data.groupby(df.columns[0]).size().to_dict()  # Group by the first column

        # Generate summaries
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "grouped_data": grouped_data
        }

        # Generate recommendations (example: based on data patterns)
        recommendations = []
        if len(df) > 100:
            recommendations.append("The dataset is large. Consider filtering unnecessary rows.")
        if "Price" in df.columns:
            avg_price = df["Price"].mean()
            recommendations.append(f"The average price is {avg_price:.2f}. Consider adjusting pricing strategies.")

        return {
            "summary": summary,
            "recommendations": recommendations
        }
    except Exception as e:
        print(f"Error processing file: {e}")  # Debugging statement
        raise

if __name__ == '__main__':
    app.run(port=8080, debug=True)