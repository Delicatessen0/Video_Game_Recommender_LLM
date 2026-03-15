import os
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from llm_recommender import get_recommendations

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON payload provided'}), 400
        
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
        
    try:
        recommendations = get_recommendations(query)
        return jsonify({'recommendations': recommendations})
    except Exception as e:
        print(f"Error in recommend endpoint: {e}")
        return jsonify({'error': str(e)}), 500

import webbrowser
from threading import Timer

if __name__ == '__main__':
    def open_browser():
        webbrowser.open_new("http://localhost:5000")
        
    Timer(1, open_browser).start()
    app.run(debug=False, port=5000)
