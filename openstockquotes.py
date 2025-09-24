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

stockSummary = [];
for stock in unique_stocks:
    stockDate = [];
    stockPrice = [];
    confidence = 0
    for row in queryRows:
        if row[2] == stock:
            stockDate.append(float(row[0])/60/60/24)
            stockPrice.append(float(row[5]))
            confidence = float(row[8])*2 + float(row[9]) - float(row[11]) - float(row[12])*2
    try:
        slope, intercept, r_value, p_value, std_err = linregress(stockDate, stockPrice)
    except ValueError:
        print("Cannot calculate linear regression for '{stock}'")

    min_time = min(stockDate)
    local_struct_min_time = time.localtime(min_time*60*60*24)
    min_time_str = time.strftime("%Y-%m-%d", local_struct_min_time)
    max_time = max(stockDate)
    local_struct_max_time = time.localtime(max_time*60*60*24)
    max_time_str = time.strftime("%Y-%m-%d", local_struct_max_time)

    min_value = min(stockPrice)
    max_value = max(stockPrice)
    avg_value = sum(stockPrice) / len(stockPrice)
    first_value = stockPrice[0]
    last_value = stockPrice[len(stockPrice)-1]

    growth = (last_value - first_value) / first_value
    rng = max_value/min_value/avg_value
    risk = growth/rng
    slp = slope*(max_time - min_time)/avg_value

    stockSummary.append([stock, first_value, last_value, min_value, avg_value, max_value, 
        growth, rng, risk, slp, r_value*r_value, slp*r_value*r_value, min_time_str, max_time_str, confidence])

sortedStockSummary = sorted(stockSummary, key=lambda x: x[11], reverse=True)

with open("stocks.html", "w") as f:
    f.write("<html><head><style>\n")
    f.write("   html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}\n")
    f.write("   body { background-color: #fff; color: #333;}\n")
    f.write("   @media (prefers-color-scheme: dark) { body { background-color: #333; color: #fff; } }\n")
    f.write("   tr:nth-child(odd) { background-color: #f2f2f2; color: #333}\n")
    f.write("   tr:nth-child(even) { background-color: #ffffff; color: #333}\n")
    f.write("   th { background-color: #375a7f; color: white; position: sticky; top: 0; z-index: 1; }\n")
    f.write("   th, td {\n")
    f.write("       padding-top: 5px;\n")
    f.write("       padding-right: 15px;\n")
    f.write("       padding-bottom: 5px;\n")
    f.write("       padding-left: 15px;\n")
    f.write("   }\n")
    f.write("</style><body><table>\n")
    f.write("<thead><tr><th>Symbol</th><th>First</th><th>Last</th><th>Min</th><th>Avg</th><th>Max</th><th>Growth</th>")
    f.write("<th>Range</th><th>Stability</th><th>Normalized<br>Slope</th><th>Linearity</th><th>Confident<br>Normalized<br>Slope</th>")
    f.write("<th>Period Start</th><th>Period Stop</th><th>Confidence</th></tr></thead>")
    for stock in sortedStockSummary:
        f.write("<tr><td>")
        f.write("<a href=\"https://robinhood.com/stocks/" + stock[0] + "?source=search\">" + stock[0] + "</a>")
        f.write("</td><td>")
        for i in range(1,12):
            f.write(f"{stock[i]:.3f}")
            f.write("</td><td>")
        f.write(stock[12])
        f.write("</td><td>")
        f.write(stock[13])
        f.write("</td><td>")
        f.write(f"{stock[14]:.0f}")
        f.write("</td></tr>\n")
    f.write("</table></body></html>")

#
        


