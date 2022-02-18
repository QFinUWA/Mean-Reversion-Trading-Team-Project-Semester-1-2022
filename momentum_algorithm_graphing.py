import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

#local imports
from gemini_modules import engine

#reads in price data
df = pd.read_csv("data/USDT_BTC.csv",parse_dates=[0])

#globals
training_period = 10
buypoints = np.array([]) #for graphing only
sellpoints = np.array([]) #for graphing only

#backtesting
backtest = engine.backtest(df)


'''Algorithm function, lookback is a data frame parsed to function continuously until end of initial dataframe is reached.'''
def logic(account, lookback):
    global buypoints,sellpoints
    try:
        if(len(lookback['close']) > training_period): #if finished training
            
            lookback['Price Moving Average'] = lookback['close'].rolling(window = training_period).mean() #update PMA
            lookback['Volumn Moving Average'] = lookback['volume'].rolling(window = training_period).mean() #update VMA
            lookback['Price Lower Than MAVG'] = lookback['Price Moving Average'].gt(lookback['close']) #update boolean
            lookback['Volumn Higher Than MAVG'] = lookback['volume'].gt(lookback['Volumn Moving Average']) #update boolean
            
            today = len(lookback)-1 #latest data frame row index

            if(lookback['Price Lower Than MAVG'][today] == True): 
                if(lookback['Volumn Higher Than MAVG'][today] == True):
                    if(account.buying_power>0):
                        account.enter_position('long', account.buying_power, lookback['close'][today]) #use 100% of portfolio to buy
                        buypoints = np.append(buypoints,today) #for graphing only

            else:
                if(lookback['Price Lower Than MAVG'][today] == False):
                    if(lookback['Volumn Higher Than MAVG'][today]== False):
                        for position in account.positions:
                            if position.type_ == 'long':
                                account.close_position(position, 1, lookback['close'][today]) #use 100% of portfolio to sell
                                sellpoints = np.append(sellpoints,today) #for graphing only
        
        
        if(len(lookback)==len(df)): #after running algorithm, graph it.
            plotAlgorithm(lookback,200,50,True,True,True,True,True)
 
    except Exception as e:
        print(e)
    pass # Handles lookback errors in beginning of dataset




'''
Graphs algorithm with given parameters.
Lookback is the dataframe.
Startindex is the index to start the graphing from and continues for 'size' units. 
plotPrice,plotBuySell,plotPMA,plotVolume,plotVMA are booleans to determine what is graphed.
'''
def plotAlgorithm(lookback,startIndex,size,plotPrice,plotBuySell,plotPMA,plotVolume,plotVMA):
    _, ax1 = plt.subplots()
    ax1.set_xlabel("Time")
    
    
    if(plotPrice):
        close_price = lookback['close'].iloc[startIndex:startIndex+size] #trim close prices
        close_price.plot(label='Close Price',color="black")
        ax1.set_ylabel('Price (USDT)')

    if(plotBuySell):
        buy = buypoints[(buypoints >= startIndex) & (buypoints <= startIndex+size)] #trim buy points
        sell = sellpoints[(sellpoints >= startIndex) & (sellpoints <= startIndex+size)] #trim sell points
        plt.scatter(buy,lookback['close'][buy],color= 'red',label='Buy Point')
        plt.scatter(sell,lookback['close'][sell],color= 'green',label='Sell Point')
   
    if(plotPMA):
        price_moving_average = lookback['Price Moving Average'].iloc[startIndex:startIndex+size] #trim moving average prices
        price_moving_average.plot(label='Price Moving Average (PMA)', color='orange')
    
    if(plotVolume or plotVMA):#setup 2nd axis
        ax2 = ax1.twinx()
        ax2.set_ylabel('Volume (Units)')
        
    if(plotVolume):
        close_volumn = lookback['volume'].iloc[startIndex:size+startIndex]#trim volume points
        ax2.plot(close_volumn, color='grey',label= "Volume")

    if(plotVMA):
        volumn_moving_average = lookback['Volumn Moving Average'].iloc[startIndex:size+startIndex]#trim volume moving average points
        ax2.plot(volumn_moving_average, color='blue',label= "Volume Moving Average (VMA)")
    
    #legend nonsense 
    handles = []
    handles1 = []  
    if(plotVolume or plotVMA):
        handles1, _ = ax2.get_legend_handles_labels()
    if(plotPrice or plotBuySell or plotPMA):
        handles, _ = ax1.get_legend_handles_labels()
    plt.legend(handles=handles+handles1)

    plt.show() #graph it

if __name__ == "__main__":
    backtest.start(100, logic)
    backtest.results()
    backtest.chart()