from math import ceil
# Returns the quarter that the month belongs to
def month2quarter(month):
    return int(ceil(month/3.0))

# Returns a string if the start year and month represent a date that is 
# strictly after the end date.  Also valid if you substitute months for quarters
def isStartBeforeEnd(startYear, startMonth, endYear, endMonth):
    if (startYear > endYear):
        return "Start year cannot be after the end year"
    elif (startYear == endYear):
        if (startMonth> endMonth):
            return "Start month cannot be after the end month"
    return ""

def isWithinTimeRange(testYear, testMonth, startYear, startMonth, endYear, endMonth):
    isAfterEnd = isStartBeforeEnd(testYear,testMonth,endYear,endMonth) == ""
    isBeforeBeginning = isStartBeforeEnd(startYear, startMonth, testYear, testMonth) == ""
    return (isAfterEnd and isBeforeBeginning) 

# Date returned is formatted MM/DD/YYYY
def tradeDateString(trade):
    return str(trade['month']) +"/"+ str(trade['day']) +"/"+ str(trade['year'])

# Assumes that date is formatted MM/DD/YYYY
# Return: Dict with year, month, day
def parseDateString(string):
    dateInfo = string.split("/")
    try:
        return {"month": dateInfo[0], "day": dateInfo[1], "year": dateInfo[2]}
    except IndexError:
        return "Invalid Date Format"