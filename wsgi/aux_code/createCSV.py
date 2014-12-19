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

# Requires the string to be in the following format  'date, price, numberOfShares' "
# If the format is incorrect, the trade is dropped. 
# Returns an array containing the buys, then the sells
def csv2trade(inputString):
    # Using stringIO since csv reader only works with files.

    csv.register_dialect('withoutSpaces', skipinitialspace=True)
    reader = csv.reader(StringIO.StringIO(inputString), "withoutSpaces")

    if not (inputString[0].isdigit()):
        reader.next()
    
    # What strings are accepted as indicating a buy or sell.
    buySet = ["b", "B", "buy", "Buy", "BUY"]
    sellSet = ["s", "S", "sell", "Sell", "SELL"]

    buys = []
    sells = []

    for line in reader:
        try:
            trade = parseDateString(line[0])
            if type(trade) is str:   # Implies that an error message was sent
                continue
            trade['price'] = line[1]
            trade['number'] = line[2]
            if line[3] in buySet:
                buys.append(trade)
            elif line[3] in sellSet:
                sells.append(trade)
        except IndexError:
            continue
    return {"buys": buys, "sells": sells}


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