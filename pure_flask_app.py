from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/rides')
def get_rides():
    return jsonify([
        {
            "id": 1,
            "from": "Downtown",
            "to": "Airport",
            "status": "completed",
            "fare": 250
        },
        {
            "id": 2,
            "from": "Mall",
            "to": "Beach",
            "status": "in_progress",
            "fare": 180
        }
    ])

@app.route('/api/drivers')
def get_drivers():
    return jsonify([
        {"id": 101, "name": "John Driver", "rating": 4.8},
        {"id": 102, "name": "Alice Driver", "rating": 4.9}
    ])

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8000) 