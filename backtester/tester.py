import pandas as pd
from backtester import engine
import multiprocessing as mp

def backtest_stock(results,stock,logic):
    lock = mp.Lock()
    df = pd.read_csv("data/" + stock + ".csv", parse_dates=[0])
    backtest = engine.backtest(df)
    backtest.start(1000, logic)
    lock.acquire()
    data = backtest.results()
    data.extend([stock]) #coinname
    results.append(data)
    lock.release()

def testArr(arr, logic):
    # for csv in arr:
        # df = pd.read_csv("data/USDT_LTC.csv", parse_dates=[0])
        # engine.backtest(df)
    manager = mp.Manager()
    results = manager.list()
    processes = []
    # starttime = time.time()
    for coin in arr:
        p = mp.Process(target=backtest_stock, args=(results,coin,logic))
        processes.append(p)
        p.start()
    for process in processes:
        processes.remove(process)
        process.join()