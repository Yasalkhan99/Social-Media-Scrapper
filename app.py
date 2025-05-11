import subprocess
import pandas as pd
import os
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape", methods=["POST"])
def scrape():
    keyword = request.form["keyword"]
    platform = request.form["platform"]
    pages = request.form["pages"]

    # ✅ Ensure command is properly formatted
    script_command = ["python", "project.py", keyword, platform, pages]
    subprocess.run(script_command)

    time.sleep(2)  # Wait for CSV generation

    csv_file = "results.csv"
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        data = df.to_dict(orient="records")
        return jsonify(data)
    else:
        return jsonify({"error": "No data found!"})

if __name__ == "__main__":
    app.run(debug=True)
