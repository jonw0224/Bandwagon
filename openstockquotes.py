########################################################################################################################
# Imports and includes
import csv
import time
import os
from collections import OrderedDict
import numpy as np
from scipy.stats import linregress

########################################################################################################################
# Global variables
# File paths
filepath = "stockQuotes.csv"
htmlpath = "stocks.html"

# Thirty two days into the past
now = time.time()
querytime = now - 24*60*60*32
queryRows = [];

# Perform some analysis of historical data
if os.path.exists(filepath):
    # If file exists
     with open(filepath, 'r', newline='') as csvfile:
        # Read in the CSV data
        reader = csv.reader(csvfile)
        # Process each row
        for row in reader:
            # Handle errors
            try:
                # Only consider the most recent 32 days
                if(float(row[0]) > querytime):
                    # Calculate an investor confidence statistic based on the data from finnhub
                    confidence = float(row[8])*2 + float(row[9]) - float(row[11]) - float(row[12])*2
                    # Only consider stocks with an investor confidence more than 20
                    if confidence > 20:
                        # Add the row to the query
                        queryRows.append(row)
            # Respond to the errors
            except ValueError:
                print(f"Error: Unable to convert '{row[0]}' to a float.")

# Remove duplicate stocks from the query list
unique_stocks_dict = OrderedDict((row[2], None) for row in queryRows)
unique_stocks = list(unique_stocks_dict.keys())

# Create a list to store stock summary information and staticial analysis results
stockSummary = [];

# Analyze each stock and store the results
for stock in unique_stocks:
    # Create a history of stock dates and stock prices for a linear analysis
    stockDate = [];
    stockPrice = [];
    # Recalculate the confidence. It wasn't saved in the data before when used to select data, but we want to put it in the analysis results
    confidence = 0
    # Save the data stock dates and stock price for the linear analysis
    for row in queryRows:
        if row[2] == stock:
            # Scale the stock date by day
            stockDate.append(float(row[0])/60/60/24)
            # Save the stock price
            stockPrice.append(float(row[5]))
            # Calculate the confidence
            confidence = float(row[8])*2 + float(row[9]) - float(row[11]) - float(row[12])*2
    # Perform the linear regression, print error message in the event of an error
    try:
        slope, intercept, r_value, p_value, std_err = linregress(stockDate, stockPrice)
    except ValueError:
        print("Cannot calculate linear regression for " + stock)

    # Calculate statistical data
    # Beginning of period analyzed as a number
    min_time = min(stockDate)
    # Beginning of period analyzed as a readable string
    local_struct_min_time = time.localtime(min_time*60*60*24)
    min_time_str = time.strftime("%Y-%m-%d", local_struct_min_time)
    # End of period analyzed as a number
    max_time = max(stockDate)
    # End of period analyzed as a readable string
    local_struct_max_time = time.localtime(max_time*60*60*24)
    max_time_str = time.strftime("%Y-%m-%d", local_struct_max_time)

    # Stock price minimum, maximum, average, price at beginning and end of period analyzed
    min_value = min(stockPrice)
    max_value = max(stockPrice)
    avg_value = sum(stockPrice) / len(stockPrice)
    first_value = stockPrice[0]
    last_value = stockPrice[len(stockPrice)-1]

    # Calculate the percent growth
    growth = (last_value - first_value) / first_value
    # Calculate the "range" as a ratio of differnce of the maximum value and the minimum value normalized by the average value
    rng = (max_value - min_value) / avg_value
    # Calculate a "risk" as the ratio of the percent growth to the normalized range. 
    # This gives an idea of how the growth compares to the range or how volatile the stock was over the period compared to the growth.
    risk = growth / rng
    # This is the slope of the linear regression scaled so that it is normalized by the average stock value over the period. 
    # You can think of this statistic as a percent slope in the period. For example a value of 0.5 means the stock price increased by 
    # 50% over the period, so this statistic is similar to the percent growth, except it is the percent growth of the linear 
    # regression trendline.
    slp = slope*(max_time - min_time)/avg_value
    
    # Save the statistical analysis data. Also, saving the r^2 value for the linear regression and a "Confident Normalized Slope"
    # statistic, which is the linear regression trendline slope multiplied by the r^2 value. This statistic is the one used to sort
    # the stock list. The idea is that the r^2 value multiplied by the trendline slope gives a worst case approximation of the growth
    # or the growth that you could expect with the volatility removed from the data. It essentially measures "predictable growth"
    # of the stock or "consistent linear growth" of the stock over the period analyzed.
    stockSummary.append([stock, first_value, last_value, min_value, avg_value, max_value, 
        growth, rng, risk, slp, r_value*r_value, slp*r_value*r_value, min_time_str, max_time_str, confidence])

# Sort the stock summary data by the "Confident Normalized Slope", which is the 11th column in the data
sortedStockSummary = sorted(stockSummary, key=lambda x: x[11], reverse=True)

# Write the HTML file
with open(htmlpath, "w") as f:
    # Write the HTML head and stylesheet
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
    f.write("</style></head>\n")
    # Write the HTML body
    f.write("<body>\n")
    # Write the stock table
    f.write("<table>\n")
    # Write the table header
    f.write("<thead><tr><th>Symbol</th><th>First</th><th>Last</th><th>Min</th><th>Avg</th><th>Max</th><th>Growth</th>")
    f.write("<th>Range</th><th>Stability</th><th>Normalized<br>Slope</th><th>Linearity</th><th>Confident<br>Normalized<br>Slope</th>")
    f.write("<th>Period Start</th><th>Period Stop</th><th>Confidence</th></tr></thead>")
    # Write the table values
    for stock in sortedStockSummary:
        f.write("<tr><td>")
        f.write("<a href=\"https://robinhood.com/stocks/" + stock[0] + "?source=search\">" + stock[0] + "</a>")
        f.write("</td><td style=\"text-align: right;\">")
        for i in range(1,12):
            f.write(f"{stock[i]:.3f}")
            f.write("</td><td style=\"text-align: right;\">")
        f.write(stock[12])
        f.write("</td><td style=\"text-align: right;\">")
        f.write(stock[13])
        f.write("</td><td style=\"text-align: right;\">")
        f.write(f"{stock[14]:.0f}")
        f.write("</td></tr>\n")
    # Finish the table
    f.write("</table>\n")
    # Finish the HTML body
    f.write("</body></html>")

#
        


