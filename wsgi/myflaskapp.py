from flask import Flask, jsonify, request, json, redirect, url_for, make_response
from flask_mail import Message, Mail
from flaskext.mysql import MySQL
import sys
import os
from pyomo import *
from pyomo.opt import SolverFactory
import pyomo.environ
from functools import wraps
from datetime import timedelta

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
from daily_report import generate_daily_report
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

def gen_compute_endpoint(runner, trades = None):
    if trades is None:
        input_data = request.get_json(force=False)
    else:
        input_data = trades

    if not (isinstance(input_data, dict)
            and isinstance(input_data.get('buys'), list)
            and isinstance(input_data.get('sells'), list)):
        return ("invalid input", 400, [])

    purchases = None
    sales = None
    try:
        purchases = validate_buysell('buy', input_data.get('buys'))
        sales = validate_buysell('sell', input_data.get('sells'))
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
    return result

@app.route("/compute", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def compute_endpoint():
    result = gen_compute_endpoint(run_problem)
    return jsonify(result)

@app.route("/greedy", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def greedy_endpoint():
    result = gen_compute_endpoint(run_greedy)
    return jsonify(result)

# function that pulls trades from the SEC database.
@app.route("/pullSEC", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def pullSEC():
    trades = pull_trades()
    return jsonify(trades)

# function that pulls information on yesterday's Form 4 filings from SEC database.
@app.route("/pullDailyReport", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def pullDailyReport():
    input_data = request.get_json()
    filings = generate_daily_report(input_data['date'])
    return jsonify(filings)

@app.route("/populateWithCSV", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def populateWithCSV():
    trades = csv2trade(request.data)
    return jsonify(trades)

# @app.route("/testDB", methods=['POST'])
# @add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
# def testDB():
#     try:
#         # read the posted values from the UI
#         form = request.form
#         _cik = request.form['inputCIK']
#         _name = request.form['inputName']
#         _lp = request.form['inputLP']
#         # _liho = request.form['inputLIHO']
#         # validate the received values
#         if _cik and _name and _lp and _liho:
#             conn = mysql.connect()
#             cursor = conn.cursor()
#             cursor.callproc('add_person',(_cik, _name, _lp))
#             data = cursor.fetchall()
#             if len(data) is 0:
#                 conn.commit()
#                 return json.dumps({'message':'Person added successfully !'})
#             else:
#                 return json.dumps({'error':str(data[0])})
#         else:
#             return json.dumps({'html':'<span>Enter the required fields</span>'})
#     except Exception as e:
#         return json.dumps({'error':str(e)})
#     finally:
#         cursor.close() 
#         conn.close()
#         # return form

@app.route("/queryDB", methods=['GET'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def queryDB():
    yesterday = str(datetime.strftime(datetime.now()-timedelta(1),'%Y-%m-%d'))
    recordsDict = {}
    recordList = []
    conn = mysql.connect()
    cursor = conn.cursor()
    query = ("SELECT p.cik, p.name, p.lp, f.url, f.date FROM person p, forms f WHERE p.cik = f.cik and f.date like %s")
    cursor.execute(query, yesterday)
    for (cik, name, lp, url, date) in cursor:
        # print("***************" + str(cik) + name + str(lp) + str(date))
        recordDict = {}
        recordDict['cik'] = cik
        recordDict['name'] = name
        recordDict['lp'] = lp
        recordDict['date'] = str(date)
        recordDict['url'] = url
        recordList.append(recordDict)
    recordsDict['data'] = recordList
    return jsonify(recordsDict)

@app.route("/refreshDB", methods=['POST'])
@add_response_headers({'Access-Control-Allow-Origin': 'example.com'})
def refreshDB():
    date =  request.form['date'];
    # get date in YYYY-MM-DD
    dateFormatted = date[6:10] + "-" + date[0:2] + "-" + date[3:5]
    # print("FORMATTED: " + dateFormatted)
    recordsDict = {}
    recordList = []
    conn = mysql.connect()
    cursor = conn.cursor()
    query = ("SELECT p.cik, p.name, p.lp, f.url, f.date FROM person p, forms f WHERE p.cik = f.cik and f.date like %s")
    cursor.execute(query, dateFormatted)
    for (cik, name, lp, url, date) in cursor:
        recordDict = {}
        recordDict['cik'] = cik
        recordDict['name'] = name
        recordDict['lp'] = lp
        recordDict['date'] = str(date)
        recordDict['url'] = url
        recordList.append(recordDict)
    recordsDict['data'] = recordList
    return jsonify(recordsDict)

if __name__ == "__main__":
    # the reloader would be nice but it doesn't work with subprocesses,
    # which opt.solve uses
    # app.run(debug=True, host='127.0.0.1', use_reloader=False)
     myHost = os.getenv('OPENSHIFT_APP_DNS', '127.0.0.1')
     app.run(debug=True, host=myHost, use_reloader=False)
