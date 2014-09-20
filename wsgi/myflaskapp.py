from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/name", methods=['POST'])
def name():
    input_data = request.get_json(cache=True)
    if not input_data:
        return "input not json"
    return jsonify(input_data)

if __name__ == "__main__":
    app.run()
