from flask import Flask, jsonify, request, json
from flask_mail import Message, Mail
import sys
import os
from coopr.pyomo import *
from coopr.opt import SolverFactory
import coopr.environ

app = Flask(__name__, static_url_path='')
app.config.update(dict(
    DEBUG = False,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'kevin.valakuzhy@gmail.com',
    MAIL_PASSWORD = 'Doingthem0st',
))
mail = Mail(app)

from compute import run_problem, validate_buysell, FourhundredException

@app.route("/", methods = ['GET'])
def homepage():
	return ("Whoopsie", 400, [])

@app.route("/compute", methods=['POST'])
def compute_endpoint():
    input_data = request.get_json()
    if not (isinstance(input_data, dict)
            and isinstance(input_data.get('buy'), list)
            and isinstance(input_data.get('sell'), list)):
        return ("invalid input", 400, [])

    purchases = None
    sales = None
    try:
        purchases = validate_buysell('buy', input_data.get('buy'))
        sales = validate_buysell('sell', input_data.get('sell'))
        recipient = input_data.get('recipient')
    except FourhundredException as e:
        return (e.msg, 400, [])

    result = run_problem(purchases,sales)
    output = []
    for (a,b,c) in result['pairs']:
        output.append(dict(buy=a.recreate_dict(), sell=b.recreate_dict(), count=c))
    result['pairs'] = output

    if not app.debug:
        del result['full_result']
    if (recipient != None):    
	    msg = Message(subject = "Test e-mail", body =str(result), sender="kevin.valakuzhy@gmail.com", recipients=[recipient])
	    mail.send(msg)
    return jsonify(result)

if __name__ == "__main__":
    # the reloader would be nice but it doesn't work with subprocesses,
    # which opt.solve uses
    app.run(debug=True, host='127.0.0.1', use_reloader=False)
