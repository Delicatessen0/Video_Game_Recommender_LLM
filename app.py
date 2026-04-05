import os
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
from llm_recommender import get_recommendations

if os.path.exists('.env'):
    load_dotenv()

import sys

if getattr(sys, 'frozen', False):
    template_folder = os.path.join(sys._MEIPASS, 'templates')
    static_folder = os.path.join(sys._MEIPASS, 'static')
    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
else:
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
        if not os.environ.get("RENDER"):
            webbrowser.open_new("http://localhost:5000")
        
    Timer(1, open_browser).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
