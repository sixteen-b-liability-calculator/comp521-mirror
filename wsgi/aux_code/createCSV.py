from dateFunctions import *
import csv
import StringIO

# Given pairings, create a csv string that represents them.
def pair2csv(pairings):

    outputString = ""

    CSV_title_columns = "buy_date, buy_price, sell_date, " + \
                         "sell_price, num_of_shares, pairing_profit\n"
    
    outputString += CSV_title_columns

    count = 1
    for pair in pairings:
        buy = pair['buy']
        buyDate = tradeDateString(buy)
        sell = pair['sell']
        sellDate = tradeDateString(sell)

        outputString += buyDate + ", "              #buy_date
        outputString += str(buy['price']) + ", "         #buy_price
        outputString += sellDate + ", "             #sell_date
        outputString += str(sell['price']) + ", "        #sell_price
        outputString += str(pair['count']) + ", "        #num_of_shares
        outputString += str(pairProfit(pair)) + "\n"#pairing_profit
        count += 1
    return outputString

# Requires the string to be in the following format
# "date, price, numberOfShares"
def csv2trade(inputString):
    # Using stringIO since csv reader only works with files.
    reader = csv.reader(StringIO.StringIO(inputString))

    if not (inputString[0].isdigit()):
        reader.next()
    
    trades = []

    for line in reader:
        trade = parseDateString(line[0])
        trade['price'] = line[1]
        trade['number'] = line[2]
        trades.append(trade)
    return trades

# Creates a nicer looking text e-mail that contains the results of a compute run.
def prettifyResult(result):
    pairings = result['pairs']
    outputString = "The following is the result of your 16b liability calculation!\n"
    count = 1
    for pair in pairings:
        buy = pair['buy']
        buyDate = tradeDateString(buy)
        sell = pair['sell']
        sellDate = tradeDateString(sell)

        lineString = "Pairing " + str(count) + ": "
        lineString += "Buy Date: " + buyDate + "  Buy Price: $" + str(buy['price'])+"  "
        lineString += "Sell Date: " + sellDate + "  Sell Price: $" + str(sell['price'])+"  "
        lineString += "# of Shares: " + str(pair['count']) + "  "
        outputString += lineString + "\n"
        count += 1
    outputString += "Total Profit: " + str(result['value'])
    return outputString

# Return the profit made through a pairing of trades.
def pairProfit(pair):
    buy = pair['buy']['price']
    sell = pair['sell']['price']
    count = pair['count']
    return (sell-buy)*count