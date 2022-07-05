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
tickers = st.text_input(label='Please enter the symbol of the stock you want to analyze', )

end = st.date_input(label='Please enter the end date when you want to stop the calculation' ,
                    value = datetime.datetime.now())
start = st.date_input(label='Please enter the starting date when you want the calculation to start' , 
                      value= (datetime.datetime.now() - datetime.timedelta(weeks= 520)))



if tickers:
  for ticker in tickers.split(','):
    st.write("Calculating dividends for " + str(ticker))
    try:
        years = []
        days_taken = []
        historical_data = data.get_data_yahoo(ticker, start, end).reset_index()
        devidents = yf.Ticker(ticker).dividends.loc[start:end]
        devidents = devidents[devidents['Date'].dt.month == datetime.datetime.today().month]
        column1, column2, column3 = st.columns(3)
        column1.dataframe(historical_data)
        column2.dataframe(devidents)
        for devident in devidents.reset_index().values.tolist():
            years.append(devident[0].year)
            msg = "On " + str(devident[0]) + " devident was " +str(devident[1])
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
        days_calculation_df = pd.DataFrame(columns = ['Year', 'Days Taken'])
        days_calculation_df['Year'] = years
        days_calculation_df['Days Taken'] = days_taken
        column3.dataframe(days_calculation_df)
        for day_cal in days_calculation_df.groupby(['Year']).mean().reset_index().values.tolist():
          st.write("Average days taken to reach target price in the year : " + str(day_cal[0]))
          if day_cal[1]==0:
            st.write(1)
          else:  
            st.write(day_cal[1])
        st.write('Average days taken to reach target price over the 10 years : ')
        st.write(np.mean(days_calculation_df.groupby(['Year']).mean().reset_index()['Days Taken'].tolist()))
        years = []
        days_taken = []
    except:
        st.write("The stock either did not have dividend this month or you have entered a wrong symbol")          
  
