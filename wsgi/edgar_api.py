from ftplib import FTP
from datetime import datetime
from flask import request, jsonify
import xml.etree.ElementTree as ET
import tempfile
import re
import gzip

def homepage():
    return ("Whoopsie", 400, [])

def pull_trades():
# TODO(valakuzh) Who will test the inputs? Front-end or backend?
    input_data = request.get_json()
    year = input_data.get('year')
    quarter = input_data.get('quarter')
    indexType = input_data.get('indexType')
    cik = input_data.get('cik')

    ftp = FTP('ftp.sec.gov')
    indexDirPath = 'edgar/full-index/'+str(year)+'/QTR'+str(quarter)+'/'+indexType+'.gz'
    totalBuys = []
    totalSells = []
    try: 
        ftp.login()
        binaryIndexFile = pull_edgar_file(ftp, indexDirPath)
        indexFile = ungzip_tempfile(binaryIndexFile)
        edgarFileURLs = parse_idx(indexFile, cik, ['4']) # TODO(valakuzh) allow specification of types of documents
        for url in edgarFileURLs:
            fileTrades = pull_edgar_file(ftp, url)
            xmlTree = parse_section_4(fileTrades)
            trades = return_trade_information_from_xml(xmlTree)
            for trade in trades[0]:
                totalBuys.append(trade)
            for trade in trades[1]:
                totalSells.append(trade)
    except FourhundredException as e:
        return (e.msg, 400, [])
    finally:
        ftp.close()
    return jsonify({"buys" : totalBuys, "sells": totalSells})

# Function in order to retrieve an index from the edgar database
# Assumes the ftp channel has been opened already
def pull_edgar_file(ftp, directoryPath):

    pracFile = tempfile.TemporaryFile()

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

def parse_idx(fileobj, target_cik, form_types):
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

# Parses the tree to gain the information needed to return the proper object
# Right now : only includes non-derivative transactions
def return_trade_information_from_xml(tree):
    buy = []
    sell = []
    for node in tree.iter('nonDerivativeTransaction'):
        shares = float(node.find('.//transactionShares/value').text)
        date = node.find('.//transactionDate/value').text
        pricePerShare = float(node.find('.//transactionPricePerShare/value').text)
        BuyOrSell = node.find('.//transactionAcquiredDisposedCode/value').text

        # Parse date to get day month and year
        dateElement = datetime.strptime(date,'%Y-%m-%d')

        if (BuyOrSell == 'D'): # Implies sell
            buy.append(dict(number=shares, price=pricePerShare, year=dateElement.year, month=dateElement.month, day=dateElement.day))
        elif (BuyOrSell == 'A'): # Implies buy
            sell.append(dict(number=shares, price=pricePerShare, year=dateElement.year, month=dateElement.month, day=dateElement.day))

    return [buy,sell]