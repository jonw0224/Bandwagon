import csv
import time
import os
from collections import OrderedDict
import numpy as np
from scipy.stats import linregress

filepath = "stockQuotes.csv"
now = time.time()
# Thirty two days into the past
querytime = now - 24*60*60*32
queryRows = [];
# Perform some analysis of historical data
if os.path.exists(filepath):
    # If file exists
     with open(filepath, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            try:
                if(float(row[0]) > querytime):
                    confidence = float(row[8])*2 + float(row[9]) - float(row[11]) - float(row[12])*2
                    if confidence > 20:
                        queryRows.append(row)
            except ValueError:
                print(f"Error: Unable to convert '{row[0]}' to a float.")

unique_stocks_dict = OrderedDict((row[2], None) for row in queryRows)
unique_stocks = list(unique_stocks_dict.keys())

for stock in unique_stocks:
    stockDate = [];
    stockPrice = [];
    for row in queryRows:
        if row[2] == stock:
            stockDate.append(float(row[0])/60/60/24)
            stockPrice.append(float(row[5]))
    
    try:
        slope, intercept, r_value, p_value, std_err = linregress(stockDate, stockPrice)
    except ValueError:
        print("Cannot calculate linear regression for '{stock}'")

    min_time = min(stockDate)
    max_time = max(stockDate)
    min_value = min(stockPrice)
    max_value = max(stockPrice)
    avg_value = sum(stockPrice) / len(stockPrice)
    
    print(stock)
    print(slope)
    print(r_value)
    print(min_time)
    print(max_time)
    print(min_value)
    print(max_value)
    print(avg_value)

