from flask import Flask, jsonify, request
import sys
app = Flask(__name__)

@app.route("/")
def hello():
    return str(sys.version_info)

@app.route("/name", methods=['POST'])
def name():
    input_data = request.get_json(cache=True)
    if not input_data:
        return "input not json"
    if isinstance(input_data, dict):
        output = dict()
        for (k,v) in input_data.iteritems():
            output[k[::-1] if isinstance(k,unicode) else k] = v
        return jsonify(output)
    return jsonify(input_data)

if __name__ == "__main__":
    app.run()
