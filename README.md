
<p align="center"><img width="300" height="300" style="border-radius: 25%;" alt="bandwagon" src="https://github.com/user-attachments/assets/aab3fb46-612a-43f8-90d9-436f79fa0ffe"></p>

<br/><br/>


# Purpose and Methodology

Bandwagon is a Python Script that uses the finnhub API (https://finnhub.io/ and https://github.com/Finnhub-Stock-API/finnhub-python) to record and analyze stock prices. The script uses the following steps:

1. Use the Finnhub API to get stock price and financial investor information for each US traded stock. You will need to get your own API key from Finnhub to run this script yourself. Since I'm using the free API, the number of request is throttled by Finnhub to one request per second. As a result, this step takes several hours to get daily stock price summary information for each stock. It is set up to run on weekdays at 5:00 PM EST via a cronjob. To set up the cron job:

```
sudo crontab -e
```

   Then add the line

```
0 17 * * 1-5 sh /[path to getstockquotes]/getStockQuotes.sh
```
<br/>

2. Creates CSV files with the stock prices for analysis and historical purposes. It creates and saves a CSV file for each stock in the PriceData directory. It also creates a rolling 180 day history in stockQuotes.csv. Lastly, it creates a stockQuotesYYYY.csv for each year of stock data consumed.

<br/>

3. Filters the stocks to analyze. The filtering parameters are as follows:

   (a) An investor grade of at least 20. The investor grade is calculated using investor grades from Finnhub. Finnhub provides a score for "Strong buy", "Buy", "Hold", "Sell", and "Strong Sell". A composite grade is calculated in the script using this equation:


    > [Investor Grade] = 2*[Strong Buy] + [Buy] - [Sell] - 2*[Strong Sell]


    (b) At least 40% of days in the past 32 days have a valid stock price. This avoids strange stock or stock with errors or missing data.

    (c) A positive lowerbound slope in stock price. In other words, a stock price that tends to be increasing in value over the past 32 days.

<br/>

4. Analyzes the stock. It'll record statistics using the daily high, low, opening, and prior day closing price. It performs a linear regression on these stock prices and calculates a regression line, confidence interval (95%), and a lower bond estimate of the slope of the regression line. For comparison purposes, the regression lines are normalized by the time period and by the stock price so that growth rate of the stocks can be compared to one another. Other statistics include the growth rate, R squared value, minimum price, maximum price, and average price over the period.

<br/>

5.  Generates a report as an HTML file with links to [Robinhood](https://robinhood.com) for each stock and links to the analysis images for each stock. The image includes a scatter plot of all of the prices, a line price of the opening stock price for each day, the linear regression line and the upperbound and lower bound regression line estimates, the confidence interval, and a shaded region between the highest price and lowest price each day of the stock. An example analysis image is below:

<br/>

<img width="1600" height="1200" alt="AAPL" src="https://github.com/user-attachments/assets/f30ddbb0-1c3c-4c55-804a-765c8b695240" />

<br/><br/>


I publish the report daily on my webserver. The included shell file includes lines for copying the report to a local webserver directory. You could modify the script to upload the files to a webserver via FTP as well. The report is accessible at https://stocks.jseeeweaver.cc

<br/>

# License

GPL 3.0
