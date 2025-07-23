from flask import Flask, render_template, request, jsonify
import os
from invoice_service import gen_invoice

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/gen_invoice', methods=['POST'])
def generate_invoice():
    """Generate invoice PDF from JSON data and save to file system"""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "Invalid or missing JSON data"}), 400
    return gen_invoice(data)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)