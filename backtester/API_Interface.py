import pandas as pd
import urllib.parse as urlparse
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

# List of timeslices in order to allow easy iteration
timeslicelist = [   "year2month12", "year2month11", "year2month10", "year2month9", "year2month8", "year2month7",
                        "year2month6", "year2month5", "year2month4", "year2month3", "year2month2", "year2month1",
                        "year1month12", "year1month11", "year1month10", "year1month9", "year1month8", "year1month7",
                        "year1month6", "year1month5", "year1month4", "year1month3", "year1month2", "year1month1"]
'''
Calculate_time_slice() function:
    Context:    Alpha Vantage API stores intraday_extended data as slices for each month, and a month is 30 days from todays date, 
                for example, year1month1 is the last 30 days, year1month2 is the 30 days before that. The correct slices must be calculated for the users input to return the correct data.

    Calculates the timeslices needed for the start and end dates provided.

    Input:  start_date: the starting date for the range of dates to be returned
            end_date: the ending date for the range of dates to be returned
    
    Output: timeslicestart: the starting timeslice for the range of dates to be returned
            timesliceend: the ending timeslice for the range of dates to be returned
            start_date: the starting date for the range of dates to be returned (this may be different to the input if the input is not valid)
            end_date: the ending date for the range of dates to be returned (this may be different to the input if the input is not valid)

'''
def calculate_time_slice(start_date, end_date): # Calculates the timeslices needed for the start and end dates provided

    start_datetime_object = datetime.strptime(start_date, '%d-%m-%Y') # Creates datetime object from start date
    end_datetime_object = datetime.strptime(end_date, '%d-%m-%Y') # Creates datetime object from end date
    if start_datetime_object > end_datetime_object: # If start date is after end date, swap them
        start_datetime_object, end_datetime_object = end_datetime_object, start_datetime_object # swaps the objects
        start_date, end_date = end_date, start_date # swaps the dates
    
    today = datetime.combine(date.today(), datetime.min.time()) # Creates datetime object for today
    monthsagostart = (today - start_datetime_object).days // 30 # Calculates the number of months between today and start date
    if monthsagostart < 1: # If start date is before today, set start date to today
        monthsagostart = 0
        timeslicestart = "year1month1"
    elif monthsagostart >= 24: # If start date is more than 2 years ago, set to 2 years ago
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

'''
time_controller() function:
    Context: Used to determine the timeslices needed for the start and end dates provided. May call calculate_time_slice() function.

    Input:  start_date: the starting date for the range of dates to be returned
            end_date: the ending date for the range of dates to be returned
    
    Output: startindex: the index of the starting timeslice, used to iterate over the timeslicelist data structure
            endindex: the index of the ending timeslice, used to iterate over the timeslicelist data structure
            start_date: the starting date for the range of dates to be returned (this may be different to the input if the input is not valid)
            end_date: the ending date for the range of dates to be returned (this may be different to the input if the input is not valid)

'''
def time_controller(start_date, end_date):
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
    return startindex, endindex, start_date, end_date

'''
get_intraday_extended() function:
    Context: Used to get intraday_extended data from Alpha Vantage API.

    Requires: API_Key.txt located in the root folder, Access to the internet

    Input:  symbol: the stock symbol to be returned
            start_date: the starting date for the range of dates to be returned
            end_date: the ending date for the range of dates to be returned
            interval: the interval of the data to be returned (1min, 5min, 15min, 30min, 60min)
            combine: whether to combine the data into one dataframe or not, if not, saves each timeslice as it's own csv
            save: whether to save the data to a csv file or to return the dataframe (will not be saved locally)

    Output: data: the dataframe containing the intraday_extended data
            OR
            data/SYMBOL_STARTDATE_ENDDATE_INTERVAL.csv: the csv file containing the intraday_extended data
'''

def get_intraday_extended(symbol, start_date, end_date, interval, combine=True, save=True): # Maybe rename if intraday is the only one used
    try:
        with open('API_Key.txt') as f: # Reads API key from API_Key.txt
            apikey = f.readline()
    except FileNotFoundError:
        print("API Key not found, Please contact the Director of Trading for the key.")
        return None
    
    combined_data = pd.DataFrame()

    startindex, endindex, start_date, end_date = time_controller(start_date, end_date) # Generate start and end index for retrieving data

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
            'adjusted': 'true', # Leave as true to adjust for stock splits in historical data
            "slice": timeslice,
            'apikey': apikey # TODO change to require input from user
        }
        # create a URL with urllib.parse with params
        url = 'https://www.alphavantage.co/query?' + urlparse.urlencode(params)

        # Make the API call and save it to a dataframe.
        df = pd.read_csv(url, parse_dates=[0])
        df.rename({'time': 'date'}, inplace=True, axis=1)

        if combine == True:
            combined_data = pd.concat([combined_data,df]) # Keep combining all into one dataframe if combine == True
        else:
            df.to_csv("data" + "/" +symbol + '_' + timeslice + '_' + interval + '.csv') # Save each timeslice as a csv file if combine == False
    if combine == True:
        combined_data.reset_index()
        combined_data = combined_data.sort_values(by='date')
        combined_data.reset_index(drop=True, inplace=True)

        if save == True:
            combined_data.to_csv("data" + "/" + symbol + '_' + str(start_date.date()) + '_' + str(end_date.date()) + '_' +  interval + '.csv', index=False)
        else:
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