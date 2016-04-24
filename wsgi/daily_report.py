from edgar_api import pull_daily_filings, pull_trades
from compute import run_problem
from flask import jsonify
from datetime import date, datetime, timedelta
from myflaskapp import app, mysql
import json

# Get most recent Form 4 filings from EDGAR and update liability
# database with new liability estimates for all filers
def generate_daily_report(inputDate):

    # connect to mysql
    conn = mysql.connect()
    cursor = conn.cursor()

    # Get information for yesterday's filings
    filings = []

    reportDate = datetime.strptime(inputDate, "%m/%d/%Y")
    if reportDate.weekday() < 5:
        dateString = reportDate.strftime('%Y%m%d')
        filings = pull_daily_filings(dateString)

        # For each person who filed yesterday, compute new liability estimate
        endYear = reportDate.year
        endMonth = reportDate.month

        # Start date is  2 years, 6 months ago
        if endMonth < 7:
            startYear = endYear - 3
            startMonth = endMonth + 6
        else:
            startYear = endYear - 2
            startMonth = endMonth - 6

        for idx, filing in enumerate(filings):
            if idx > 0:
                break
            trades = pull_trades(filing['cik'], startYear, startMonth, endYear, endMonth)
            from myflaskapp import gen_compute_endpoint
            compute_result = gen_compute_endpoint(run_problem, trades)
            filings[idx]['liability'] = compute_result['value']

            # also add the filing date while we're at it
            filings[idx]['lastfiling'] = reportDate.strftime('%m/%d/%Y')

            cik = filings[idx]['cik']
            name = filings[idx]['name']
            liability = filings[idx]['liability']
            date = filings[idx]['lastfiling']
            url = filings[idx]['url']
            cursor.callproc('add_person', (cik, name, liability))
            cursor.callproc('add_form', (cik, url, STR_TO_DATE(date, '%m/%d/%Y')))
            
        cursor.close() 
        conn.close()  


    return {'filings': filings}
