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
