# -*- coding: utf-8 -*-
"""forecasting.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XJ0o4AsrjZwR3UuEtZwoQMwyPIQAYHcq
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

df1 = pd.read_csv('/content/Transactional_data_retail_01.csv')
df2 = pd.read_csv('/content/Transactional_data_retail_02.csv')
df3 = pd.read_csv('/content/CustomerDemographics.csv')
df4 = pd.read_csv('/content/ProductInfo.csv')

"""1. Exploratory Data Analysis (EDA):
a. Perform customer, item, and transaction-level summary statistics.
b. Utilize SQL join queries to retrieve necessary data (e.g., customer and product
information) without explicit data merging.
c. Consolidate transactional data where necessary to ensure accurate summary metrics for
each level (customer, item, transaction).
d. Design and develop visualizations which should help to explain the data and summary
statistics
"""

df1.head()

df2.head()

df3.head()

df4.head()

!pip install sqlite3

import sqlite3

conn = sqlite3.connect('memory.db')

df1.to_sql('df1', conn, index=False, if_exists='replace')
df2.to_sql('df2', conn, index=False, if_exists='replace')
df3.to_sql('df3', conn, index=False, if_exists='replace')
df4.to_sql('df4', conn, index=False, if_exists='replace')

query = """
SELECT * FROM df1
UNION ALL
SELECT * FROM df2
"""
merged_transactions = pd.read_sql(query, conn)

merged_transactions.head()

query = """
SELECT t.*, c."Customer ID", c.Country
FROM (SELECT * FROM df1 UNION ALL SELECT * FROM df2) t
INNER JOIN df3 c
ON t."Customer ID" = c."Customer ID"  -- Enclose "Customer ID" in double quotes for both tables
"""
transactions_with_customers = pd.read_sql(query, conn)

transactions_with_customers

query = """
SELECT t.*, p.StockCode, p.Description
FROM (SELECT * FROM df1 UNION ALL SELECT * FROM df2) t
INNER JOIN df4 p
ON t."StockCode" = p."StockCode"
"""
transactions_with_products = pd.read_sql(query, conn)

transactions_with_products.head()

query = """
SELECT t.*, c."Country", p."Description"
FROM (SELECT * FROM df1 UNION ALL SELECT * FROM df2) t
INNER JOIN df3 c
ON t."Customer ID" = c."Customer ID"
INNER JOIN df4 p
ON t."StockCode" = p."StockCode"
"""
full_data = pd.read_sql(query, conn)

full_data.head()

full_data['Revenue'] = full_data['Quantity'] * full_data['Price']

full_data.drop_duplicates(inplace = True)

full_data.head()

"""lets observe different visualisations"""

# @title Revenue vs Last_Week_Demand

from matplotlib import pyplot as plt
full_data.plot(kind='scatter', x='Revenue', y='Last_Week_Demand', s=32, alpha=.8)
plt.gca().spines[['top', 'right',]].set_visible(False)

from matplotlib import pyplot as plt
import seaborn as sns
def _plot_series(series, series_name, series_index=0):
  palette = list(sns.palettes.mpl_palette('Dark2'))
  xs = series['InvoiceDate']
  ys = series['Revenue']

  plt.plot(xs, ys, label=series_name, color=palette[series_index % len(palette)])

fig, ax = plt.subplots(figsize=(10, 5.2), layout='constrained')
df_sorted = full_data.sort_values('InvoiceDate', ascending=True)
for i, (series_name, series) in enumerate(df_sorted.groupby('Country')):
  _plot_series(series, series_name, i)
  fig.legend(title='Country', bbox_to_anchor=(1, 1), loc='upper left')
sns.despine(fig=fig, ax=ax)
plt.xlabel('InvoiceDate')
_ = plt.ylabel('Revenue')

"""2. Top 10 Stock Codes: Use transactional data to identify the top 10 stock codes based on the total
quantity sold, ensuring the analysis reflects actual sale performance.
3. Top 10 High Revenue Products: Identify the top 10 products that generate the highest revenue
by considering both price and quantity sold.

"""

# Customer-level summary
customer_summary = full_data.groupby('Customer ID').agg(
    total_transactions=('Invoice', 'nunique'),
    total_quantity=('Quantity', 'sum'),
    total_revenue=('Revenue', 'sum')
).reset_index()

print("Customer-Level Summary:")
print(customer_summary.head())

# Item-level summary
item_summary = full_data.groupby('StockCode').agg(
    total_quantity=('Quantity', 'sum'),
    total_revenue=('Revenue', 'sum'),
    total_transactions=('Invoice', 'nunique')
).reset_index()

# Merging with product details for better understanding

item_summary = item_summary.merge(full_data, left_on='StockCode', right_on='StockCode', how='left') # Changed 'Stock_Code' to 'StockCode' in right_on

print("Item-Level Summary:")
print(item_summary[['StockCode', 'total_quantity', 'total_revenue']].head())

# Transaction-level summary
transaction_summary = full_data.groupby('Invoice').agg(
    total_quantity=('Quantity', 'sum'),
    total_revenue=('Revenue', 'sum')
).reset_index()

print("Transaction-Level Summary:")
print(transaction_summary.head())

full_data.plot(kind='scatter', x='Quantity', y='Revenue', alpha=0.5)
plt.title('Quantity vs Revenue')
plt.show()

full_data.info()

from dateutil import parser

full_data['InvoiceDate'] = full_data['InvoiceDate'].apply(lambda x: parser.parse(x))

full_data['InvoiceDate'] = pd.to_datetime(full_data['InvoiceDate'])

full_data.columns

# Group by Stock_Code/Product_ID and sum the Quantity_Sold
top_10_quantity = full_data.groupby('StockCode')['Quantity'].sum().nlargest(10).reset_index()
top_10_quantity = top_10_quantity.merge(full_data[['StockCode', 'Description']], left_on='StockCode', right_on='StockCode', how='left')

print("Top 10 Products by Quantity Sold:")
print(top_10_quantity[['Description', 'Quantity']])

# Group by Stock_Code/Product_ID and sum the revenue
top_10_revenue = full_data.groupby('StockCode')['Revenue'].sum().nlargest(10).reset_index()
top_10_revenue = top_10_revenue.merge(full_data[['StockCode', 'Description']], left_on='StockCode', right_on='StockCode', how='left')

print("Top 10 Products by Revenue:")
print(top_10_revenue[['Description', 'Revenue']])

full_data.info()

"""4. Time Series Analysis (TS):
a. Develop and compare various time series models, such as ARIMA, Exponential
Smoothing (ETS), Prophet, and advanced models like LSTM
Note: The modeling will focus on the top 10 products based on quantity sold or revenue
to ensure detailed and accurate forecasting (Explain your reasoning how and why use
selected top 10 products)
"""

## lets prepare data for time series analysis

product_data = full_data[full_data['StockCode'] == top_10_quantity['StockCode'][0]]

# Resample the data by week and sum the quantities sold
weekly_demand = product_data.resample('W', on='InvoiceDate')['Quantity'].sum()

# Ploting the data to visualize the demand over time
weekly_demand.plot()

##lets apply arima model here
from statsmodels.tsa.arima.model import ARIMA

model_arima = ARIMA(weekly_demand, order=(5, 1, 0))  # ARIMA(p, d, q) parameters
model_arima_fit = model_arima.fit()
forecast_arima = model_arima_fit.forecast(steps=15)
print(forecast_arima)

##lets apply exponential smoothing
from statsmodels.tsa.holtwinters import ExponentialSmoothing

model_ets = ExponentialSmoothing(weekly_demand, seasonal='add', seasonal_periods=52)
model_ets_fit = model_ets.fit()
forecast_ets = model_ets_fit.forecast(15)
print(forecast_ets)

#lets apply fbprophet
from prophet import Prophet # Change import statement to 'prophet'

# Prepare data for Prophet
prophet_data = weekly_demand.reset_index().rename(columns={'InvoiceDate': 'ds', 'Quantity': 'y'}) # Assuming 'InvoiceDate' is the correct column name

model_prophet = Prophet()
model_prophet.fit(prophet_data)

future = model_prophet.make_future_dataframe(periods=15, freq='W')
forecast_prophet = model_prophet.predict(future)
print(forecast_prophet[['ds', 'yhat']])

from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense
import numpy as np

# Scale the data
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(weekly_demand.values.reshape(-1, 1))

def create_dataset(data, time_step=1):
    X, y = [], []
    for i in range(len(data)-time_step-1):
        X.append(data[i:(i+time_step), 0])
        y.append(data[i + time_step, 0])
    return np.array(X), np.array(y)

time_step = 5
X, y = create_dataset(scaled_data, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Build LSTM model
model_lstm = Sequential()
model_lstm.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model_lstm.add(LSTM(50))
model_lstm.add(Dense(1))

model_lstm.compile(loss='mean_squared_error', optimizer='adam')
model_lstm.fit(X, y, epochs=100, batch_size=1, verbose=2)

import numpy as np
predictions = []
input_data = X[-1].reshape(1, time_step, 1)

# Predict for the next 'n_steps' time steps
n_steps = 15
for _ in range(n_steps):
    prediction = model_lstm.predict(input_data)
    predictions.append(prediction[0, 0])
    input_data = np.roll(input_data[0, :, 0], -1)
    input_data[-1] = prediction[0, 0]
    input_data = input_data.reshape(1, time_step, 1)

lstm_forecast = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))

print(lstm_forecast)

from sklearn.metrics import mean_squared_error

rmse_arima = mean_squared_error(weekly_demand[-15:], forecast_arima, squared=False)
rmse_ets = mean_squared_error(weekly_demand[-15:], forecast_ets, squared=False)
rmse_prophet = mean_squared_error(weekly_demand[-15:], forecast_prophet['yhat'][-15:], squared=False)

print(f"ARIMA RMSE: {rmse_arima}, ETS RMSE: {rmse_ets}, Prophet RMSE: {rmse_prophet}")

"""5. Non-Time Series Techniques: Apply machine learning models (e.g., DecisionTree, XGBoost) that
leverage non-time series features, such as customer demographics and product features, to
predict demand
"""

##non time  series
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

full_data['Last_Week_Demand'] = full_data.groupby('StockCode')['Quantity'].shift(1)

# Drop rows with NaN values (from shifting)
model_data = full_data.dropna()

# Prepare X (features) and y (target - Quantity)
X = model_data[['Price', 'Last_Week_Demand']]
y = model_data['Quantity']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.tree import DecisionTreeRegressor

dt_model = DecisionTreeRegressor()
dt_model.fit(X_train, y_train)
dt_predictions = dt_model.predict(X_test)

import xgboost as xgb

xgb_model = xgb.XGBRegressor(objective='reg:squarederror')
xgb_model.fit(X_train, y_train)
xgb_predictions = xgb_model.predict(X_test)

## evaluate models
from sklearn.metrics import mean_absolute_error

mae_dt = mean_absolute_error(y_test, dt_predictions)
mae_xgb = mean_absolute_error(y_test, xgb_predictions)

print(f"Decision Tree MAE: {mae_dt}, XGBoost MAE: {mae_xgb}")

"""6. Training and Validation Strategy: Define robust training and validation strategies, such as timebased cro"""

##cross validation for time series model
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_index, test_index in tscv.split(weekly_demand):
    train, test = weekly_demand.iloc[train_index], weekly_demand.iloc[test_index]

from sklearn.model_selection import cross_val_score

# Cross-validation for XGBoost or Decision Trees
scores = cross_val_score(xgb_model, X, y, cv=5, scoring='neg_mean_absolute_error')
print(f"Cross-Validation Scores: {-scores.mean()}")

from sklearn.metrics import mean_squared_error
min_len = min(len(test), len(forecast_arima))
rmse_arima = mean_squared_error(test[:min_len], forecast_arima[:min_len], squared=False)
print(f"ARIMA RMSE: {rmse_arima}")

from sklearn.metrics import mean_absolute_error
mae_xgb = mean_absolute_error(y_test, xgb_predictions)
print(f"XGBoost MAE: {mae_xgb}")

full_data.head()

8. Error and Evaluation Metrics: Use appropriate error metrics (e.g., RMSE, MAE) and evaluation
criteria to assess model performance.
9. ACF and PACF Plots: Analyze Auto-Correlation Function (ACF) and Partial Auto-Correlation
Function (PACF) plots to identify trends, seasonality, and lags in time series data.

from statsmodels.tsa.stattools import adfuller
data_for_adf = full_data['Quantity'].astype(float)

# Perform ADF test on the selected numeric column
result = adfuller(data_for_adf)
print(f'ADF Statistic: {result[0]}')
print(f'p-value: {result[1]}')

if result[1] < 0.05:
    print("The data is stationary (no trend).")
else:
    print("The data is non-stationary (trend present).")

import pandas as pd
import matplotlib.pyplot as plt

#  lets Assume we have a time series of weekly sales data
# Replacing with our actual time series data
dates = pd.date_range(start='2022-01-01', periods=104, freq='W')
sales_data = pd.Series([120 + (i % 10)*10 for i in range(104)], index=dates)

# Plot the time series
plt.figure(figsize=(10, 6))
plt.plot(sales_data, label="Weekly Sales")
plt.title('Time Series Plot of Weekly Sales')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.legend()
plt.show()

from statsmodels.tsa.seasonal import seasonal_decompose
decomposition = seasonal_decompose(sales_data, model='additive', period=52)

# Plot the decomposition
decomposition.plot()
plt.show()

import statsmodels.api as sm

# Plotting ACF and PACF
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# ACF Plot
sm.graphics.tsa.plot_acf(sales_data, lags=30, ax=axes[0])
axes[0].set_title('ACF Plot')

# PACF Plot
sm.graphics.tsa.plot_pacf(sales_data, lags=30, ax=axes[1])
axes[1].set_title('PACF Plot')

plt.tight_layout()
plt.show()

# Seasonal differencing (e.g., 12 for monthly seasonality or 52 for weekly data with yearly seasonality)
seasonally_differenced = sales_data.diff(52).dropna()

# Plot the seasonally differenced series
plt.figure(figsize=(10, 6))
plt.plot(seasonally_differenced, label='Seasonally Differenced Sales')
plt.title('Seasonally Differenced Series')
plt.xlabel('Date')
plt.ylabel('Sales')
plt.legend()
plt.show()



pip install streamlit

!pip install pyngrok