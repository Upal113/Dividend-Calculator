from cProfile import label
from pandas_datareader import data
import datetime
import numpy as np
import openpyxl
import pandas as pd
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title='Dividend Calculator', page_icon='📊', layout='wide')
tickers = st.text_input(label='Please enter the symbols of the stock you want to analyze', )

end = datetime.datetime.now()
start = datetime.datetime.now() - datetime.timedelta(weeks= 520)
final_data_sheet = []
all_devidents = []


if tickers:
  for ticker in tickers.split(','):
      ticker = ticker.strip()
      try:
        years = []
        days_taken = []
        target_days_under_10_days = []
        historical_data = data.get_data_yahoo(ticker, start, end).reset_index()
        devidents = yf.Ticker(ticker).dividends.loc[start:end].reset_index()
        devidents = devidents[devidents['Date'].dt.month.between(((datetime.datetime.now() - datetime.timedelta(days=10))).month, ((datetime.datetime.now() + datetime.timedelta(days=60))).month)]
        if len(devidents) != 0:
          st.title("Calculating dividends for " + str(ticker))
          all_devidents.append([ticker, devidents])
          for devident in devidents.values.tolist():
            years.append(devident[0].year)
            ten_days_earlier = devident[0] - datetime.timedelta(days=14)
            before_date = historical_data[historical_data['Date'] >= ten_days_earlier]['Date'].min()
            price_on_ten_days_before = historical_data[historical_data['Date'] == before_date].values.tolist()[0][3]
            target_price = price_on_ten_days_before + devident[1]
            filter = (historical_data['Date'] >= ten_days_earlier) & (historical_data['High'] >= target_price)
            date_to_reach_terget = historical_data[filter]['Date'].min()
            day_difference = date_to_reach_terget - before_date
            if day_difference.days == 0:
              days_taken.append(1)
            else:
              days_taken.append(day_difference.days)
              
          for day_taken in days_taken:
              if int(day_taken) <= 10:
                  target_days_under_10_days.append(int(day_taken))
          percentage = (len(target_days_under_10_days)/len(days_taken))*100
          days_calculation_df = pd.DataFrame(columns = ['Year', 'Days Taken'])
          days_calculation_df['Year'] = years
          days_calculation_df['Days Taken'] = days_taken
          st.write('Average days taken to reach target price over the 10 years : ')
          st.write(np.mean(days_calculation_df.groupby(['Year']).mean().reset_index()['Days Taken'].tolist()))
          final_data_sheet.append([ticker, historical_data.values.tolist()[-1][1], devidents.values.tolist()[-1][1],  devidents.values.tolist()[-1][0] , percentage, np.mean(days_calculation_df.groupby(['Year']).mean().reset_index()['Days Taken'].tolist()) ])
          years = []
          days_taken = []   
      except:
        st.write("You have entered the wrong symbol" + str(ticker))
  i = 0      
  for col in st.columns(len(all_devidents)):
    col.write(all_devidents[i][0])
    col.dataframe(all_devidents[i][1])
    i = i + 1
  st.dataframe(pd.DataFrame(final_data_sheet, columns = ['Symbol', 'Price', 'Current Dividend', 'Last Dividend Date', 'Percentage of Reaching Target', 'Average Days Taken to Reach Target']))
