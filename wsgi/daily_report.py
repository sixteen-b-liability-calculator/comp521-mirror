from edgar_api import pull_daily_filings, pull_trades
from compute import run_problem
from flask import jsonify
from datetime import date, datetime, timedelta
import json

# Get most recent Form 4 filings from EDGAR and update liability
# database with new liability estimates for all filers
def generate_daily_report():
    # Get information for yesterday's filings
    yesterday = datetime.now() - timedelta(days=1)
    dateString = yesterday.strftime('%Y%m%d')

    filings = pull_daily_filings(dateString)

    # For each person who filed yesterday, compute new liability estimate
    startDate = datetime.now() - timedelta(years=2, months=6, days=3)
    startYear = startDate.year
    startMonth = startDate.month
    endYear = yesterday.year
    endMonth = yesterday.month

    for idx, filing in enumerate(filings):
        if idx > 3:
            break
        trades = pull_trades(filing['cik'], startYear, startMonth, endYear, endMonth)
        compute_result = gen_compute_endpoint(run_problem, json.dumps(trades))
        filings[idx]['liability'] = compute_result['value']

        # also add the filing date while we're at it
        filings[idx]['lastfiling'] = yesterday.strftime('%Y/%m/%d')

    # Update entry for each person in the database

    return jsonify({'filings': filings})
