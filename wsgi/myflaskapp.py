from flask import Flask, jsonify, request, json, redirect, url_for, make_response
from flask_mail import Message, Mail
from flask.ext.mysql import MySQL
import sys
import os
from pyomo import *
from pyomo.opt import SolverFactory
import pyomo.environ
from functools import wraps

app = Flask(__name__, static_url_path='')
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'relay.unc.edu',
    MAIL_PORT = 25,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'chin@unc.edu',
))
mail = Mail(app)
mysql = MySQL()

# MySQL configurations
user = os.environ['OPENSHIFT_MYSQL_DB_USERNAME']
password = os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']
db = os.environ['OPENSHIFT_APP_NAME']
host = os.environ['OPENSHIFT_MYSQL_DB_HOST']

app.config['MYSQL_DATABASE_USER'] = user
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = db
app.config['MYSQL_DATABASE_HOST'] = host
mysql.init_app(app)


from compute import run_problem, run_greedy, validate_buysell, FourhundredException
from edgar_api import *
from aux_code.dateFunctions import *
from aux_code.createCSV import *


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator

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
    if not app.debug and 'full_dual_result' in result:
        del result['full_dual_result']
    if (recipient != None and recipient != ""):
        emailBody = prettifyResult(result)
        msg = Message(subject = "16b liability calculator: Results", body = emailBody, sender = 'chin@unc.edu', recipients=[recipient])
        csvString = pair2CSV(result['pairs'])
        msg.attach("pairingResult.csv", "text/csv", csvString)
        mail.send(msg)
    return jsonify(result)

@app.route("/compute", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def compute_endpoint():
    return gen_compute_endpoint(run_problem)

@app.route("/greedy", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def greedy_endpoint():
    return gen_compute_endpoint(run_greedy)

# function that pulls trades from the SEC database.
@app.route("/pullSEC", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def pullSEC():
    return pull_trades()

# function that pulls CIKs for yesterday's Form 4 filings from SEC database.
@app.route("/pullDailyCIK", methods=['GET'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def pullDailyCIK():
    return pull_daily_filings()

@app.route("/populateWithCSV", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def populateWithCSV():
    trades = csv2trade(request.data)
    return jsonify(trades)

@app.route("/testDB", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def testDB():
    try:
        # read the posted values from the UI
        form = request.form
        _cik = request.form['inputCIK']
        _name = request.form['inputName']
        _lp = request.form['inputLP']
        _liho = request.form['inputLIHO']
        # validate the received values
        if _cik and _name and _lp and _liho:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.callproc('add_person',(_cik, _name, _lp, _liho))
            data = cursor.fetchall()
            if len(data) is 0:
                conn.commit()
                return json.dumps({'message':'Person added successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})
    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()
        # return form

@app.route("/queryDB", methods=['GET'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def queryDB():
    personsDict = {}
    personList = []
    conn = mysql.connect()
    cursor = conn.cursor()
    query = ("SELECT * FROM person")
    cursor.execute(query)
    for (cik, name, lp, liho) in cursor:
        personDict = {}
        personDict['cik'] = cik
        personDict['name'] = name
        personDict['lp'] = lp
        personDict['liho'] = liho
        personList.append(personDict)
    personsDict['data'] = personList
    return jsonify(personsDict)

@app.route("/getDateData", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def getDateData():
    date = request
    if date is None:
        print("REQUEST IS NULL")
    recordDict = {}
    recordList = []
    recordDict['cik'] = 904235920
    recordDict['name'] = "Full Name"
    recordDict['lp'] = 9000
    recordDict['url'] = "google.com"
    recordDict['date'] = "2016-05-21"
    recordList.append(recordDict)
    recordsDict = {}
    recordsDict['data'] = recordList
    print("inside getDateData")
    return jsonify(recordDict)
    # print("REQUEST DATA: " + request.data)
    # date = request.get_json()
    # dateString = "" + date[0] + date[1] + date[2]
    # print("DATE: " + date)
    # print(dateString)
    # recordDict = {}
    # recordList = []
    # conn = mysql.connect()
    # cursor = conn.cursor()
    # query = ("SELECT p.cik, p.name, p.lp, f.url, f.date FROM person p, forms f WHERE f.date == STR_TO_DATE(%s, '%d-%m-%Y')")
    # cursor.execute(query, date)
    # for (p.cik, p.name, p.lp, f.url, f.date) in cursor:
    #     recordDict = {}
    #     recordDict['cik'] = p.cik
    #     recordDict['name'] = p.name
    #     recordDict['lp'] = p.lp
    #     recordDict['url'] = f.url
    #     recordDict['date'] = f.date
    #     recordList.append(recordDict)
    # recordsDict['data'] = recordList
    # return jsonify(recordsDict)

if __name__ == "__main__":
    # the reloader would be nice but it doesn't work with subprocesses,
    # which opt.solve uses
    # app.run(debug=True, host='127.0.0.1', use_reloader=False)
     myHost = os.getenv('OPENSHIFT_APP_DNS', '127.0.0.1')
     app.run(debug=True, host=myHost, use_reloader=False)
