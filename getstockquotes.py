#!/usr/bin/python3
#
###############################################################################
#  
# getstockquotes.py
#
# Usage: getstockquotes.py
#
# Use the finnhub API to retrieve a daily list of stock prices in the US 
# stock market. This file should be run as part of a cron job at 5:00 PM, EST
# Monday thru Friday using the following:
#
# sudo crontab -e
# 
# 0 17 * * 1-5 sh /[path to getstockquotes]/getStockQuotes.sh
#
# The retrieval takes around 8 hours to complete using the free finnhub API
# rates of 60 calls per minute.
#
#
# Author: Jonathan Weaver, jonw0224@gmail.com
# Date: 11/9/2024
# Version: 
# 1.00 - 2024-11-08 - Wrote code
# 1.01 - 2024-11-09 - Added error correction for robustness of internet
#                     connection and finnhub API timeouts. 
#
#
# Copyright (C) 2024 Jonathan Weaver
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################

# Import library and interface files
import finnhub
import csv
import time
import os
import requests
import time 

# Time execution
# startTime = time.time()
# Setup client and connect to finnhub
finnhub_client = finnhub.Client(api_key="csk431pr01qvrnd772b0csk431pr01qvrnd772bg")

# Get a list of stocks
while True:
    try:
        stocks = finnhub_client.stock_symbols('US')
        break
    except finnhub.exceptions.FinnhubAPIException as e:
        print(e)
        if (e.status_code == 429):
            # Because I'm using the free API, I'm limited to one API call per second. I exceeded the limit, so wait
            time.sleep(10)
        else:
            # Reestablish client
            finnhub_client = finnhub.Client(api_key="csk431pr01qvrnd772b0csk431pr01qvrnd772bg")
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
        print(e)
        # Wait and then try again
        time.sleep(1)

# Record the price for each stock in a seperate CSV file
f = open("log.txt", "w")
f.write("Number of stocks: " + str(len(stocks)) + '\n')
print(len(stocks))
csvdata = None
for stock in stocks:
    # Get the stock price quote
    quote = None
    while True:
        try:
            quote = finnhub_client.quote(stock['symbol'])
            break
        except finnhub.exceptions.FinnhubAPIException as e:
            print(e)
            if (e.status_code == 429):
                # Because I'm using the free API, I'm limited to one API call per second. I exceeded the limit, so wait
                time.sleep(10)
            else:
                # Reestablish client connection
                finnhub_client = finnhub.Client(api_key="csk431pr01qvrnd772b0csk431pr01qvrnd772bg")
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print(e)
            # Wait and then try again
            time.sleep(1)
    # Get the trading recommendation
    if quote is not None: 
        f.write(stock['symbol'] + '\n')
        print(stock['symbol'])
        print(quote)
        if quote['d'] is not None:         
            recommend = None
            while True:
                try:
                    recommend = finnhub_client.recommendation_trends(stock['symbol'])[0]
                    break
                except IndexError:
                    break
                except finnhub.exceptions.FinnhubAPIException as e:
                    print(e)
                    if (e.status_code == 429):
                        # Because I'm using the free API, I'm limited to one API call per second. I exceeded the limit, so wait
                        time.sleep(10)
                    else:
                        # Reestablish client connection
                        finnhub_client = finnhub.Client(api_key="csk431pr01qvrnd772b0csk431pr01qvrnd772bg")
                except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                    print(e)
                    # Wait and then try again
                    time.sleep(1)
            if recommend is not None:
                print(recommend)
            # To give feedback
            f.write(stock['symbol'] + ": " + str(quote['c']))
            print(stock['symbol'] + ": " + str(quote['c']))
            if recommend is None:
                f.write("No Recommendation")
                print("No Recommendation")
                csvrow = [quote['t'], time.ctime(quote['t']), stock['symbol'], quote['h'], quote['l'], quote['o'], quote['pc'], "None", "0", "0", "0", "0", "0"]
            else:
                csvrow = [quote['t'], time.ctime(quote['t']), stock['symbol'], quote['h'], quote['l'], quote['o'], quote['pc'], recommend['period'], recommend['strongBuy'], recommend['buy'], recommend['hold'], recommend['sell'], recommend['strongSell']]
            filepath = "PriceData/" + stock['symbol'] + ".csv"
            csvdata = [csvdata, csvrow]
            if os.path.exists(filepath):
                # If file exists, open CSV as append
                with open(filepath, 'a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write data to end of file
                    writer.writerow(csvrow)
            else:
                # File does not exist, open CSV as write
                with open(filepath, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write header row
                    writer.writerow(['Time UNIX Seconds', 'Time Stamp', 'Symbol', 'High', 'Low', 'Open', 'Previous Close', 'Recommend Period', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
                    # Write data
                    writer.writerow(csvrow)
        else:
            print("Quote is empty")
            f.write("Quote is empty\n")
filepath = "stockQuotes.csv"
if os.path.exists(filepath):
    # If file exists, open CSV as append
    with open(filepath, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write data to end of file
        writer.writerowa(csvdata)
else:
    # File does not exist, open CSV as write
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header row
        writer.writerow(['Time UNIX Seconds', 'Time Stamp', 'Symbol', 'High', 'Low', 'Open', 'Previous Close', 'Recommend Period', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
        # Write data
        writer.writerows(csvdata)
# Finish timing of execution and add it to the log
endTime = time.time()
duration = endTime - startTime
print(duration)
f.write(str(duration) + '\n')
f.close()


# Financials as reported
#print(finnhub_client.financials_reported(symbol='AAPL', freq='annual'))