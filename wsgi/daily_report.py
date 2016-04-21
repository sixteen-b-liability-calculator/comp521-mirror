from edgar_api import pull_daily_filings
from compute import run_problem
from flask import jsonify

# Get most recent Form 4 filings from EDGAR and update liability
# database with new liability estimates for all filers
def generate_daily_report():
    # Get information for yesterday's filings
    filings = pull_daily_filings()

    # For each person who filed yesterday, compute new liability estimate
    for idx, filing in enumerate(filings):
        trades = pull_trades(filing['cik'], startYear, startMonth, endYear, endMonth)
        compute_result = gen_compute_endpoint(run_problem, trades)
        filings[idx]['liability'] = compute_result['value']

    # Update entry for each person in the database

    return jsonify({'filings': filings})
