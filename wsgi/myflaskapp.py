from flask import Flask, jsonify, request, json, redirect, url_for
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
    MAIL_USERNAME = 'spam28211@gmail.com',
    MAIL_PASSWORD = 'comp523project',
))
mail = Mail(app)

from compute import run_problem, run_greedy, validate_buysell, FourhundredException
from edgar_api import *
from aux_code.dateFunctions import *
from aux_code.createCSV import *

@app.route("/", methods = ['GET'])
def home_page():
	return redirect(url_for('static', filename = "/frontend/home.html"), code=302)

def gen_compute_endpoint(runner):
    input_data = request.get_json(force=False)
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
        stella_correction = input_data.get('stella_correction', True)
        jammies_correction = input_data.get('jammies_correction', True)
        if not isinstance(stella_correction, bool):
            raise FourhundredException("illegal stella_correction value")
        if not isinstance(jammies_correction, bool):
            raise FourhundredException("illegal jammies_correction value")
    except FourhundredException as e:
        return (e.msg, 400, [])

    result = runner(purchases,sales,stella_correction,jammies_correction)
    output = []
    for (a,b,c) in result['pairs']:
        output.append(dict(buy=a.recreate_dict(), sell=b.recreate_dict(), count=c))
    result['pairs'] = output

    if 'dual_solution' in result:
        output = []
        for (a,c) in result['dual_solution']['buy']:
            output.append(dict(buy=a.recreate_dict(), dual_value=c))
        for (a,c) in result['dual_solution']['sell']:
            output.append(dict(sell=a.recreate_dict(), dual_value=c))
    result['dual_solution'] = output

    if not app.debug and 'full_result' in result:
        del result['full_result']
    if (recipient != None and recipient != ""):
        emailBody = prettifyResult(result)
        msg = Message(subject = "Test e-mail", body =emailBody, sender="kevin.valakuzhy@gmail.com", recipients=[recipient])
        csvString = trade2CSV(result['pairs'])
        msg.attach("pairingResult.csv", "text/csv", csvString)
        mail.send(msg)
    return jsonify(result)

@app.route("/compute", methods=['POST'])
def compute_endpoint():
    return gen_compute_endpoint(run_problem)

@app.route("/greedy", methods=['POST'])
def greedy_endpoint():
    return gen_compute_endpoint(run_greedy)

# function that pulls trades from the SEC database. 
@app.route("/pullSEC", methods=['POST'])
def pullSEC():
    return pull_trades()

if __name__ == "__main__":
    # the reloader would be nice but it doesn't work with subprocesses,
    # which opt.solve uses
    app.run(debug=True, host='127.0.0.1', use_reloader=False)
