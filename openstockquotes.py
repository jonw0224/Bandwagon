########################################################################################################################
# Imports and includes
import csv
import time
import os
from collections import OrderedDict
import numpy as np
from scipy.stats import linregress, t
from operator import itemgetter, attrgetter

########################################################################################################################
# Global variables
# File paths
filepath = "stockQuotes.csv"
htmlpath = "stocks.html"

# Thirty two days into the past
now = time.time()
lookback_days = 32
querytime = now - 24*60*60*lookback_days
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
sortedStockSummary = [];

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
        # Calculate the linear regression and parameters
        slope, intercept, r_value, p_value, std_err = linregress(stockDate, stockPrice)
        # Calculate the critical value for a two-tailed test at 95% confidence level
        t_stat = slope / std_err
        # Calculate the critical value for the confidence interval
        critical_value = t.ppf(1 - 0.05, len(stockPrice) - 2)
        # Calculate the lower bound slope
        lower_bound_slope = slope - (std_err * critical_value)
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
    if len(stockPrice) == 0:
        avg_value = 0.0
    else:
        avg_value = sum(stockPrice) / len(stockPrice)
    
    first_value = stockPrice[0]
    
    if len(stockPrice) < 1:
        last_value = first_value
    else:
        last_value = stockPrice[len(stockPrice)-1]

    # Calculate the percent growth
    if first_value == 0:
        growth = 0.0
    else:
        growth = (last_value - first_value) / first_value
    
    # This is the slope of the linear regression scaled so that it is normalized by the average stock value over the period. 
    # You can think of this statistic as a percent slope in the period. For example a value of 0.5 means the stock price increased by 
    # 50% over the period, so this statistic is similar to the percent growth, except it is the percent growth of the linear 
    # regression trendline. Also calculate for the lower_bound_slope. The ranking criteria is the lower_bound_slope as a normalized value.
    if avg_value == 0:
        slp = 0.0
    else:
        slp = slope * (max_time - min_time) / avg_value
        lower_bound_slp = lower_bound_slope * (max_time - min_time) / avg_value 
    
    # Save the statistical analysis data. Also, saving the r^2 value for the linear regression and a "Confident Normalized Slope"
    # statistic, which is the linear regression trendline slope multiplied by the r^2 value. This statistic is the one used to sort
    # the stock list. The idea is that the r^2 value multiplied by the trendline slope gives a worst case approximation of the growth
    # or the growth that you could expect with the volatility removed from the data. It essentially measures "predictable growth"
    # of the stock or "consistent linear growth" of the stock over the period analyzed.
    if not(np.isnan(slp)) and not(np.isnan(r_value)):
        if slp > 0 and growth > 0:
            stockSummary.append([stock, first_value, last_value, min_value, avg_value, max_value, 
                growth*100, slp, r_value*r_value, lower_bound_slp, min_time_str, max_time_str, confidence])

# Sort the stock summary data by the "Confident Normalized Slope", which is the 10th column in the data
#sortedStockSummary = sorted(stockSummary, key=lambda x: x[11], reverse=True)
sortedStockSummary = sorted(stockSummary, key=itemgetter(9), reverse=True)

# Write the HTML file
with open(htmlpath, "w") as f:
    # Write the HTML head and stylesheet
    f.write("<html><head>\n")
    f.write("<title>Bandwagon Stock List</title>\n")
    f.write("<meta charset=\"UTF-8\">\n")
    f.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
    f.write("<meta name=\"author\" content=\"Jonathan Weaver\">\n")
    f.write("<meta name=\"description\" content=\"A daily listing of stocks sorted by the growth rate and linearity of growth over the past 30 days.\">\n")
    f.write("<meta name=\"keywords\" content=\"finnhub stock robinhood\">\n")
    f.write("<style>\n")
    f.write("   html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: left; line-height: 1.4 }\n")
    f.write("   body { background-color: #fff; color: #333; }\n")
    f.write("   a { font-weight: bold; } \n")
    f.write("   tr:nth-child(odd) { background-color: #f2f2f2; color: #333;}\n")
    f.write("   tr:nth-child(even) { background-color: #ffffff; color: #333;}\n")
    f.write("   th { background-color: #375a7f; color: white; position: sticky; top: 0; z-index: 1; }\n")
    f.write("   th, td {\n")
    f.write("       padding-top: 5px;\n")
    f.write("       padding-right: 15px;\n")
    f.write("       padding-bottom: 5px;\n")
    f.write("       padding-left: 15px;\n")
    f.write("   }\n")
    f.write("   @media (prefers-color-scheme: dark) {\n") 
    f.write("       body { background-color: #333; color: #fff; }\n")
    f.write("       a:link { color: #628bd1; font-weight: bold; }\n")
    f.write("       a:visited { color: #8027d1; font-weight: bold; }\n")
    f.write("       tr:nth-child(odd) { background-color: #222; color: #fff;}\n")
    f.write("       tr:nth-child(even) { background-color: #333; color: #fff;}\n")
    f.write("   }\n")
    f.write("</style></head>\n")
    # Write the HTML body
    f.write("<body>\n")
    f.write("<center><table width=1500>\n")
    f.write("<tr><td>\n")
    f.write("<h1 align=\"left\">Bandwagon Stock List</h1>\n")
    f.write("<h2 align=\"left\">Join the Bandwagon</h2>\n")
    f.write("<p align=\"left\">When deciding which stocks to buy in <a href=\"https://robinhood.com\">Robinhood</a>, you’d find an API to get current prices, log historical data, use statistics to identify top-performing stocks from the past month, and automate the process with a script. Isn’t that what you’d do? If not, here’s the resulting list of top-performing stocks from the past month, sorted by growth. Use this list to quickly identify stocks with strong investor support and enhance your investment strategy.</p>\n")
    f.write("<p align=\"left\">Stocks were filtered to have a minimum investor grade of 20 points, analyzed using linear regression, and sorted by the minimum trendline slope. The minimum trendline slope has been normalized by the average stock price and calculated using a 95% confidence interval. This statistic gives a low estimate of stock price percent growth, considering both the trends and volatility of the stock price over the past month. With these details, you can easily compare stocks by their historical performance.</p>\n")
    f.write("<h2 align=\"left\">Designed for Robinhood Users</h2>\n")
    f.write("<p align=\"left\">The Bandwagon Stock List is designed for use with <a href=\"https://robinhood.com\">Robinhood</a>, a popular online brokerage platform offering commission-free trading. With this tool, you can easily find and research top-performing stocks on the list, then quickly place trades through your Robinhood account.</p>\n")
    f.write("<h2 align=\"left\">Important Disclaimer</h2>\n")
    f.write("<p align=\"left\">The information presented on this list is for informational purposes only and should not be considered investment advice. Past performance is not indicative of future gains. Investing in the stock market carries risks, and it's possible that any or all of these stocks could decline in value. It's essential to do your own research, set clear goals, and consider your risk tolerance before making any investment decisions.</p>\n")
    f.write("<h2 align=\"left\">Learn More</h2>\n")
    f.write("<p align=\"left\">Learn more at <a href=\"https://github.com/jonw0224/Bandwagon\">https://github.com/jonw0224/Bandwagon</a>.</p>\n")
    # Write the stock table
    f.write("<table width=100%>\n")
    # Write the table header
    f.write("<thead><tr><th>Symbol</th><th>First</th><th>Last</th><th>Min</th><th>Avg</th><th>Max</th><th>Percent<br>Growth</th>")
    f.write("<th>Normalized<br>Slope</th><th>R<sup>2</sup> Value</th><th>Minimal<br>Normalized<br>Slope<br>95% Confidence</th>")
    f.write("<th>Period Start</th><th>Period Stop</th><th>Investor Grade</th></tr></thead>")
    # Write the table values
    for stock in sortedStockSummary:
        print(stock[9])
        f.write("<tr><td>")
        f.write("<a href=\"https://robinhood.com/stocks/" + stock[0] + "?source=search\" target=\"_blank\">" + stock[0] + "</a>")
        f.write("</td><td style=\"text-align: right;\">")
        for i in range(1,6):
            f.write(f"{stock[i]:.3f}")
            f.write("</td><td style=\"text-align: right;\">")
        f.write(f"{stock[6]:.1f}")
        f.write("</td><td style=\"text-align: right;\">")
        for i in range(7,9):
            f.write(f"{stock[i]:.3f}")
            f.write("</td><td style=\"text-align: right;\">")
        f.write(f"<b>{stock[9]:.3f}</b>")
        f.write("</td><td style=\"text-align: right;\">")
        f.write(stock[10])
        f.write("</td><td style=\"text-align: right;\">")
        f.write(stock[11])
        f.write("</td><td style=\"text-align: right;\">")
        f.write(f"{stock[12]:.0f}")
        f.write("</td></tr>\n")
    # Finish the table
    f.write("</table>\n")
    # Footer
    f.write("<p align=\"left\" style=\"font-size: small\">Table generated on " + time.strftime("%Y-%m-%d", time.localtime()) + "</p>")
    f.write("<p align=\"left\" style=\"font-size: small\">Copyright (C) 2025 Jonathan Weaver</p>")
    f.write("<p align=\"left\" style=\"font-size: small\">Bandwagon is free software licensed under GPL v3.0</p>")
    f.write("</table></center>\n")
    # Finish the HTML body
    f.write("</body></html>")


#
        


