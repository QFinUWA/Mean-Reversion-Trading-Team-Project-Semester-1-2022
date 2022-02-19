# from re import A
# import requests
import pandas as pd
import urllib.parse as urlparse
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

'''
Should take input of a number of parameters and save a csv file of the requested data, AND return a dataframe of the data if applicable

Inputs:
    Stock symbol (or name?)
    Start date
    End date
    Time interval
    combine: True or False, combine all data into one csv/dataframe
    (API key?)
    (Maybe allow other functions, not just Intraday Extended? Would require other functions)

Calculations:
    Calculate which slices required to get the data
    Create a API call URL for each slice (May have to consider call limits? Maybe not if we get an academic key) - Function
    Loop through and append slices to a single file
    
Output:
    CSV file of requested data (custom name depending on inputs)
    Dataframe of requested data

'''
def calculate_time_slice(start_date, end_date): # Calculates the timeslices needed for the start and end dates provided

    start_datetime_object = datetime.strptime(start_date, '%d-%m-%Y') # Creates datetime object from start date
    end_datetime_object = datetime.strptime(end_date, '%d-%m-%Y') # Creates datetime object from end date
    if start_datetime_object > end_datetime_object: # If start date is after end date, swap them
        temp = start_datetime_object
        start_datetime_object = end_datetime_object
        end_datetime_object = temp
        temp = start_date
        start_date = end_date
        end_date = temp
    
    today = datetime.combine(date.today(), datetime.min.time()) # Creates datetime object for today
    monthsagostart = (today - start_datetime_object).days // 30 # Calculates the number of months between today and start date
    if monthsagostart < 1: # If start date is before today, set start date to today
        monthsagostart = 0
        timeslicestart = "year1month1"
    elif monthsagostart >= 24: 
        monthsagostart = 24
        timeslicestart = "year2month12"
    else:
        yearsagostart = (monthsagostart // 12) + 1 # Calculates the number of years between today and start date
        if yearsagostart == 2: monthsagostart = monthsagostart - 12 # If the start date is in the year "2", 
        timeslicestart = "year" + str(yearsagostart) + "month" + str(monthsagostart)

    monthsagoend = (today - end_datetime_object).days // 30
    if monthsagoend >= 24: 
        monthsagoend = 24
        timesliceend = "year2month12"
    elif monthsagoend < 0:
        monthsagoend = 0
        timesliceend = "year1month1"
    else:
        if monthsagoend > 24: 
            monthsagoend = 24
        yearsagoend = (monthsagoend // 12) + 1
        if yearsagoend == 2: monthsagoend = monthsagoend - 12
        timesliceend = "year" + str(yearsagoend) + "month" + str(monthsagoend)

    start_date = str((today - relativedelta(months=monthsagostart)).date())
    end_date = str((today - relativedelta(months=monthsagoend)).date())
    return timeslicestart, timesliceend, start_date, end_date

def get_intraday_extended(symbol, start_date, end_date, interval, combine=True, save=True): # Maybe rename if intraday is the only one used
    with open('API_Key.txt') as f:
        apikey = f.readline()
    timeslicelist = [   "year2month12", "year2month11", "year2month10", "year2month9", "year2month8", "year2month7",
                        "year2month6", "year2month5", "year2month4", "year2month3", "year2month2", "year2month1",
                        "year1month12", "year1month11", "year1month10", "year1month9", "year1month8", "year1month7",
                        "year1month6", "year1month5", "year1month4", "year1month3", "year1month2", "year1month1"]
    if start_date == "all":
        start_date = "year2month12"
        end_date = "year1month1"
    if start_date in timeslicelist and end_date in timeslicelist:
        timeslicestart, timesliceend = start_date, end_date
        start_date = datetime.today() - timedelta(days=((int(timeslicestart[4])-1)*12 + int(timeslicestart[10:12]))*30)
        end_date = datetime.today() - timedelta(days=((int(timesliceend[4])-1)*12 + int(timesliceend[10:12]))*30)
    else: 
        timeslicestart, timesliceend, start_date, end_date = calculate_time_slice(start_date, end_date)
    startindex = timeslicelist.index(timeslicestart)
    endindex = timeslicelist.index(timesliceend)
    combined_data = pd.DataFrame()

    for i in range(startindex, endindex + 1):
        timeslice = timeslicelist[i]
        print(timeslice)

        # Set the API call parameters.
        params = {
            'function': 'TIME_SERIES_INTRADAY_EXTENDED',
            'symbol': symbol,
            'interval': interval, # allowed = 1min, 5min, 15min, 30min, 60min
            'outputsize': 'full',
            'datatype': 'csv',
            'adjusted': 'true',
            "slice": timeslice,
            'apikey': apikey # TODO change to require input from user
        }
        # create a URL with urllib.parse with params
        url = 'https://www.alphavantage.co/query?' + urlparse.urlencode(params)

        # Make the API call and save it to a dataframe.
        df = pd.read_csv(url)#, index_col=0)
        df.rename({'time': 'date'}, inplace=True, axis=1)
        if combine == True:
            combined_data = pd.concat([combined_data,df])
        else:
            # print(df)
            df.to_csv("data" + "/" +symbol + '_' + timeslice + '_' + interval + '.csv')
    if combine == True:
        combined_data.reset_index()
        combined_data = combined_data.sort_values(by='date')
        # print(combined_data)
        if save == True:
            combined_data.to_csv("data" + "/" + symbol + '_' + str(start_date.date()) + '_' + str(end_date.date()) + '_' +  interval + '.csv')
        else:
            # print(combined_data)
            return combined_data


# get_intraday_extended('IBM', '01-01-2008', '01-03-2022', '60min', True)
# get_intraday_extended('AAPL', 'year2month12', 'year1month1', '60min', True)
# get_intraday_extended('IBM', 'year2month12', 'year1month1', '60min', True)
# get_intraday_extended('IBM', 'all', None, '60min', True)
# calculate_time_slice('01-01-2008', '01-03-2022')
# calculate_time_slice('01-01-2021', '01-03-2020')

# print(calculate_time_slice('01-01-2019', '01-03-2018'))
# get_intraday_extended('IBM', '01-01-2019', '01-03-2018', '1min', True)
# calculate_time_slice('01-01-2021', '01-03-2020')