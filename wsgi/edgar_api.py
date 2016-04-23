from ftplib import FTP
from flask import request, jsonify
import xml.etree.ElementTree as ET
import tempfile
import re
import gzip
import os.path
from aux_code.httpExceptions import *
from aux_code.dateFunctions import *

def homepage():
    return ("Whoopsie", 400, [])

def pull_trades(CIK = None, sy = None, sm = None, ey = None, em = None):
    if CIK is None:
        try:
            input_data = request.get_json()
        except Exception:
            return ("There is an issue with the information sent to the server.  Look at the HTTP POST request to identify the issue", 400, [])

        # Leading zeros for the cik are removed.
        cik = int(input_data.get('cik'))

        startYear = input_data.get('startYear')
        startMonth = input_data.get('startMonth')
        endYear = input_data.get('endYear')
        endMonth = input_data.get('endMonth')
    else:
        cik = CIK
        startYear = sy
        startMonth = sm
        endYear = ey
        endMonth = em

    startQuarter = month2quarter(startMonth)
    endQuarter = month2quarter(endMonth)
    indexType = "master"

    #Ensure that you won't run into an infinite loop due to bad input
    errorMsg = isStartBeforeEnd(startYear,startMonth,endYear, endMonth)
    if not (errorMsg == ""):
        return ("The start date must occur before the end date", 400, [])

    year = startYear
    quarter = startQuarter

    ftp = FTP('ftp.sec.gov')
    totalBuys = []
    totalSells = []
    try:
        ftp.login()
        while (isStartBeforeEnd(year, quarter, endYear, endQuarter) == ""):
            indexDirPath = 'edgar/full-index/'+str(year)+'/QTR'+str(quarter)+'/'+indexType+'.gz'
            binaryIndexFile = pull_edgar_file(ftp, indexDirPath)
            indexFile = ungzip_tempfile(binaryIndexFile)
            edgarFileURLs = get_URLs_for_CIK(indexFile, cik, ['4','4/A']) # TODO(valakuzh) allow specification of types of documents
            for url in edgarFileURLs:
                fileTrades = pull_edgar_file(ftp, url)
                xmlTree = parse_section_4(fileTrades)
                trades = return_trade_information_from_xml(xmlTree, url)
                for trade in trades[0]:
                    if (isWithinTimeRange(trade['year'],trade['month'],startYear,startMonth,endYear,endMonth)):
                        totalBuys.append(trade)
                for trade in trades[1]:
                    if (isWithinTimeRange(trade['year'],trade['month'],startYear,startMonth,endYear,endMonth)):
                        totalSells.append(trade)

            #Pull the next index file
            if (quarter<4):
                quarter = quarter + 1
            else:
                year = year + 1
                quarter = 1

    except FivehundredException as e:
        return (e.msg, 504, [])
    finally:
        ftp.close()
    return {"buys" : totalBuys, "sells": totalSells}

def pull_daily_filings(dateString):
    filings = []

    indexType = "master"
    ftp = FTP('ftp.sec.gov')
    try:
        ftp.login()

        indexDirPath = 'edgar/daily-index/'+indexType+'.'+dateString+'.idx'
        indexFile = pull_edgar_file(ftp, indexDirPath)
        form4URLs = get_all_URLs_from_idx(indexFile, ['4','4/A'])
        for idx, url in enumerate(form4URLs):
            if idx > 3:
                break
            form4File = pull_edgar_file(ftp, url)
            xmlTree = parse_section_4(form4File)
            cik, name, filingURL = return_owner_information_from_xml(xmlTree, url)
            filings.append({'cik': cik, 'name': name, 'url': filingURL})

    except FivehundredException as e:
        return (e.msg, 504, [])
    finally:
        ftp.close()
    return filings

# Function in order to retrieve an index from the edgar database
# Assumes the ftp channel has been opened already
def pull_edgar_file(ftp, directoryPath):

    pracFile = tempfile.TemporaryFile()
# Check the tempFile directory to see whether the file has already been pulled before.
    tempFileDirPath = "tempFiles/" + directoryPath
    if os.path.isfile(tempFileDirPath):
        print tempFileDirPath
        return open(tempFileDirPath,'rb')
    else:
        print directoryPath
        ftp.retrbinary('RETR '+ directoryPath, pracFile.write)
        pracFile.seek(0)
    return pracFile

parse_idx_start = re.compile(r'-+$')
parse_idx_entry = re.compile(r''' ( [0-9]  + )    # CIK
                               \|   [^|]   *      # (skip) name
                               \| ( [^|]   + )    # form type
                               \|   [0-9-] +      # (skip) date
                               \| ( edgar/data/[0-9]+/[0-9-]+\.txt ) # path
                               $ ''', re.VERBOSE)

def ungzip_tempfile(fileobj):
    fileobj.seek(0)
    return gzip.GzipFile("", fileobj=fileobj, mode='r')

def get_URLs_for_CIK(fileobj, target_cik, form_types):
    out = []
    found_start = False
    for line in fileobj:
        if found_start: # i.e., we're looking at real entries now
            m = parse_idx_entry.match(line.strip())
            if not m:
                # we expect to be able to parse every line after the start
                raise Exception("could not parse line from EDGAR idx:", line)
            if int(m.group(1)) == target_cik and m.group(2) in form_types:
                out.append(m.group(3))
        elif parse_idx_start.match(line.strip()):
            found_start = True
    if not found_start:
        raise Exception("could not find start line in EDGAR idx")
    return out

def get_all_URLs_from_idx(fileobj, form_types):
    out = []
    found_start = False
    for line in fileobj:
        if found_start: # i.e., we're looking at real entries now
            m = parse_idx_entry.match(line.strip())
            if not m:
                # we expect to be able to parse every line after the start
                raise Exception("could not parse line from EDGAR idx:", line)
            if m.group(2) in form_types:
                out.append(m.group(3))
        elif parse_idx_start.match(line.strip()):
            found_start = True
    if not found_start:
        raise Exception("could not find start line in EDGAR idx")
    return out

# Parses a file containing text from the edgar database.  Returns a tree containing
# all the information that you need
# N.B. Assumes that the file contains valid xml within <XML> tags
def parse_section_4(inputFile):
    # Find the beginning of the xml in the file
    while not inputFile.readline().startswith('<XML'):
        pass

    # Start writing these lines into a separate file in order to remove lines at the bottom
    xmlFile = tempfile.TemporaryFile()

    while True:
        line = inputFile.readline()
        if line.startswith('</XML'):
            break
        else:
            xmlFile.write(line)
    inputFile.close()
    # Turn the file into a tree structure
    xmlFile.seek(0)
    tree = ET.parse(xmlFile)
    xmlFile.close()
    return tree

parse_url = re.compile(r''' edgar/data/
                            ( [0-9]  + )  /                    # CIK
                            ( [0-9-] + )\.txt ''', re.VERBOSE) # docno
# Parses the tree to gain the information needed to return the proper object
# Right now : only includes non-derivative transactions
def return_trade_information_from_xml(tree, url):
    buy = []
    sell = []
    for node in tree.iter('nonDerivativeTransaction'):
        try:
            shares = float(node.find('.//transactionShares/value').text)
            date = node.find('.//transactionDate/value').text
            pricePerShare = float(node.find('.//transactionPricePerShare/value').text)
            BuyOrSell = node.find('.//transactionAcquiredDisposedCode/value').text
            securityTitle = node.find('.//securityTitle/value').text
            directOrIndirectOwnership = node.find('.//directOrIndirectOwnership/value').text
            url_match = parse_url.match(url)
            if url_match:
                filingURLVal = ("http://www.sec.gov/Archives/edgar/data/" + url_match.group(1)
                                 + "/" + url_match.group(2).replace('-', '') + "/"
                                 + url_match.group(2) + "-index.htm")
            else:
                filingURLVal = "ftp://ftp.sec.gov/" + url
        except Exception:
            continue

        # Parse date to get day month and year
        dateElement = datetime.strptime(date,'%Y-%m-%d')
        newTrade = dict(number=shares,
                        price=pricePerShare,
                        year=dateElement.year,
                        month=dateElement.month,
                        day=dateElement.day,
                        securityTitle = securityTitle,
                        directOrIndirectOwnership = directOrIndirectOwnership,
                        filingURL=filingURLVal)
        if (BuyOrSell == 'D'): # Implies sell
            sell.append(newTrade)
        elif (BuyOrSell == 'A'): # Implies buy
            buy.append(newTrade)
    return [buy,sell]

def return_owner_information_from_xml(tree, url):
    cik = 0
    name = ""
    filingURLVal = url
    for node in tree.iter('reportingOwnerId'):
        try:
            cik = int(node.find('.//rptOwnerCik').text)
            name = node.find('.//rptOwnerName').text
            url_match = parse_url.match(url)
            if url_match:
                filingURLVal = ("http://www.sec.gov/Archives/edgar/data/" + url_match.group(1)
                                 + "/" + url_match.group(2).replace('-', '') + "/"
                                 + url_match.group(2) + "-index.htm")
            else:
                filingURLVal = "ftp://ftp.sec.gov/" + url
        except Exception:
            continue

    return (cik,name,filingURLVal)
