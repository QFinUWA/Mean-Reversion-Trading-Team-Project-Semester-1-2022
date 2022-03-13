from backtester import API_Interface as api

df = api.get_intraday_extended('AAPL', 'all', '', '1min', True, False)
# df = api.get_intraday_extended('TSLA', 'year1month2', 'year1month1', '60min', True, False)
# api.get_intraday_extended('TSLA', 'all', 'year1month1', '15min', True, True)