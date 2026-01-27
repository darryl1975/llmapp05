from flask import Flask, render_template, request, jsonify
import requests
from config import BACKEND_URL, FLASK_PORT, DEBUG

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ai/<analysis_type>', methods=['POST'])
def proxy_analysis(analysis_type):
    allowed_types = ('summarize', 'sentiment', 'intent', 'classify')
    if analysis_type not in allowed_types:
        return jsonify({'error': f'Invalid analysis type: {analysis_type}'}), 400

    try:
        resp = requests.post(
            f'{BACKEND_URL}/api/ai/{analysis_type}',
            json=request.get_json(),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Cannot connect to backend service'}), 502
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Backend service timed out'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_PORT, debug=DEBUG)
