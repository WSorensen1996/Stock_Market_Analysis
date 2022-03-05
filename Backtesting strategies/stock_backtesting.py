import yfinance as yf 
import matplotlib.pyplot as plt 
import pandas as pd 
from datetime import datetime 
import math 
import time 
import os 
plt.style.use("seaborn")
########################################################################################
###to do

#hvis ikke csv findes - 
    #scrape tickerkoder
    #ellers brug csv 
#Sæt det op med .so lib 
# Threading 
########################################################################################


def get_tickers(): 
    tickers = []
    dirty_words = ["SPAC", "I", "II", "ARCA", "ACE", "ACAX", "ACAB", "ADRT", "AF", "AFC", "AIB"]
    with open("ticker_code.txt", "r") as f : 
            lines = f.read()
            for line in lines.splitlines(): 
                words = line.split()
                for word in words: 
                    if len(word)<5: 
                        if word.isupper():
                            if word.find(".") ==-1:
                                if word not in dirty_words: 
                                    tickers.append(word)
    return tickers

def stockinfo(ticker): 
    stockinfo = yf.Ticker(ticker)
    stockinfo = stockinfo.info
    for key,value in stockinfo.items(): 
        print(key, ":", value)

def stock_history(ticker, start = 0, end = (datetime.today()).strftime("%Y-%m-%d")): 
    try: 
        stockinfo = yf.Ticker(ticker)
    except: 
        df = pd.DataFrame({'A' : []})
        return df
    if start != 0: 
        df = stockinfo.history(start = start, end = end) 
        return df 
    df = stockinfo.history(period = "max")
    return df 

def buy(buy_pct,capital,price,stocks,avg_stock_price): 
    buy_capital = buy_pct*capital
    remain_capital = capital - buy_capital
    
    new_stocks = math.floor(buy_capital/price)
    if new_stocks==0: 
        return capital,stocks,avg_stock_price

    remainder = buy_capital%price
    remain_capital +=remainder
    avg_stock_price =avg_stock_price*stocks + price*new_stocks

    stocks += new_stocks
    avg_stock_price = avg_stock_price/stocks

    return remain_capital,stocks,avg_stock_price


def simulate(prices, capital,buy_pct): 


    number_of_buys = 0
    n_stocks = 0 
    avg_stock_price = 0 

    for day, price in enumerate(prices): 
        if day==0: 
            date = prices.index[day].strftime("%Y-%m-%d")
            capital, n_stocks,avg_stock_price = buy(buy_pct,capital,price,n_stocks,avg_stock_price)
            number_of_buys +=1 
            #print(f" Date: {date}, Price: {price} \t - \t Remainding capital: {capital}, Number of stocks: {n_stocks}, Avg_stock_price: {avg_stock_price} , Total-capital: {n_stocks*price+capital}")

        if ((avg_stock_price-price)>(avg_stock_price*buy_pct)): 
            date = prices.index[day].strftime("%Y-%m-%d")
            prev_n_stocks = n_stocks
            capital, n_stocks,avg_stock_price = buy(buy_pct,capital,price,n_stocks,avg_stock_price)
            if prev_n_stocks == n_stocks: 
                total_capital = n_stocks*prices[-1]+capital 
                return total_capital, number_of_buys
            number_of_buys +=1 
            #print(f" Date: {date}, Price: {price} \t - \t Remainding capital: {capital}, Number of stocks: {n_stocks}, Avg_stock_price: {avg_stock_price} , Total-capital: {n_stocks*price+capital}")

    total_capital = n_stocks*prices[-1]+capital 
    #print(f" Date: {prices.index[-1].strftime('%Y-%m-%d')}, Price: {price} \t - \t Remainding capital: {capital}, Number of stocks: {n_stocks}, Avg_stock_price: {avg_stock_price} , Total-capital: {total_capital}")
    return total_capital, number_of_buys



def plot(df, param="Close"): 
    plt.figure()
    plt.plot(df[param])
    plt.show()



if __name__ == "__main__": 
    #stockinfo(tickers[0])  ## STOK INFO MUST OUTCOMMENT TO SEE

    tickers = get_tickers()
    start_capital = 10000   ## Starting ammount of capital
    starting_year = 2000    ## Starting year of simulation
    pct = 60                ## Max Investing %
    print__ = True          ## Do prints

    #tickers = ["AAPL"]      ## Ticker to analyse - overwriting atm... MUST BE DELETED TO RUN OVER ALL

    for ticker in tickers: 
        for i in range(starting_year,2023): 
            year = str(i).zfill(2)
            start = f"{year}-01-01"
            df = stock_history(ticker, start = start)
            if not(df.empty): 
                max_capital = 0 
                prices = df["Close"]
                before = time.time()
                for i in range(1,pct): 
                    buy_pct = i/100

                    total_capital, number_of_buys = simulate(prices, start_capital,buy_pct)
                    
                    if max_capital<total_capital: 
                        
                        max_capital = total_capital
                        
                        change_ = "{0:.2f}".format(((max_capital/start_capital)-1)*100)
                        number_of_buys_ = number_of_buys
                        buy_pct_ = buy_pct

                if print__ : 
                    if max_capital>=start_capital: 
                        print(f"Gained capital:\t{start}\tBuy:{buy_pct_}%\t{ticker}\tTotal-capital: {'{0:.2f}'.format(max_capital)} \t Change {change_}% \t number_of_buys: {number_of_buys_}")
                    if max_capital<start_capital: 
                        print(f"Lost   capital:\t{start}\tBuy:{buy_pct_}%\t{ticker}\tTotal-capital: {'{0:.2f}'.format(max_capital)} \t Change {change_}% \t number_of_buys: {number_of_buys_}")



