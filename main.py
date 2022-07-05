from cProfile import label
from pandas_datareader import data
import datetime
import openpyxl
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title='Dividend Calculator', page_icon='📊', layout='wide')
ticker = st.text_input(label='Please enter the symbol of the stock you want to analyze', )

end = st.date_input(label='Please enter the end date when you want to stop the calculation' ,
                    value = datetime.datetime.now())
start = st.date_input(label='Please enter the starting date when you want the calculation to start' , 
                      value= (datetime.datetime.now() - datetime.timedelta(weeks= 520)))



if ticker:
    try:
        historical_data = data.get_data_yahoo(ticker, start, end).reset_index()
        devidents = yf.Ticker(ticker).dividends.loc[start:end]
        column1, column2 = st.columns(2)
        column1.dataframe(historical_data)
        column2.dataframe(devidents)
        for devident in devidents.reset_index().values.tolist():
            msg = "On " + str(devident[0]) + " devident was " +str(devident[1])
            st.write(msg + '\n')
            ten_days_earlier = devident[0] - datetime.timedelta(days=14)
            before_date = historical_data[historical_data['Date'] >= ten_days_earlier]['Date'].min()
            price_on_ten_days_before = historical_data[historical_data['Date'] == before_date].values.tolist()[0][3]
            st.write("10 days earlier price Date: " + str(before_date) + " Price: " + str(price_on_ten_days_before)  + '\n')
            target_price = price_on_ten_days_before + devident[1]
            st.write("Calculated target price  " + str(target_price))
            filter = (historical_data['Date'] >= ten_days_earlier) & (historical_data['High'] >= target_price)
            date_to_reach_terget = historical_data[filter]['Date'].min()
            st.write("Date it reached the target  " + str(date_to_reach_terget)  + '\n')
            day_difference = date_to_reach_terget - before_date
            if day_difference.days == 0:
                st.write("Days required to reach target: " + "Same date"  + '\n')
            else:  
                st.write("Days required to reach target: " + str(day_difference.days)  + '\n')
        fig = go.Figure(data=[go.Candlestick(x=historical_data['Date'],
                open=historical_data['Open'],
                high=historical_data['High'],
                low=historical_data['Low'],
                close=historical_data['Close'])])  
        st.title('Candelstick chart for the stock : ' + str(ticker))        
        st.plotly_chart(fig)      
    except:
        st.write("You have entered the wrong symbol")          
  
