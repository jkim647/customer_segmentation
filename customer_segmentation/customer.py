#!/usr/bin/env python
# coding: utf-8



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import plotly.offline as po
import plotly.graph_objs as gobj

url = '/Users/jskim/PycharmProjects/data.csv'

Rtl_data = pd.read_csv(url, encoding='unicode_escape')

# Customer distribution by country
country_cust_data = Rtl_data[['Country', 'CustomerID']].drop_duplicates()
country_cust_data.groupby(['Country'])['CustomerID'].aggregate('count').reset_index().sort_values('CustomerID',ascending=False)

# Keep only United Kingdom data
Rtl_data = Rtl_data.query("Country=='United Kingdom'").reset_index(drop=True)

# Check for missing values in the dataset
Rtl_data.isnull().sum(axis=0)

# Remove missing values from CustomerID column, can ignore missing values in description column
Rtl_data = Rtl_data[pd.notnull(Rtl_data['CustomerID'])]

# Validate if there are any negative values in Quantity column
Rtl_data.Quantity.min()

# Validate if there are any negative values in UnitPrice column
Rtl_data.UnitPrice.min()

# Filter out records with negative values
Rtl_data = Rtl_data[(Rtl_data['Quantity'] > 0)]

# Convert the string date field to datetime
Rtl_data['InvoiceDate'] = pd.to_datetime(Rtl_data['InvoiceDate'])

# Add new column depicting total amount
Rtl_data['TotalAmount'] = Rtl_data['Quantity'] * Rtl_data['UnitPrice']


# Set Latest date 2011-12-10 as last invoice date was 2011-12-09. This is to calculate the number of days from recent purchase
Latest_Date = dt.datetime(2011, 12, 10)

# Create RFM Modelling scores for each customer
RFMScores = Rtl_data.groupby('CustomerID').agg(
    {'InvoiceDate': lambda x: (Latest_Date - x.max()).days, 'InvoiceNo': lambda x: len(x),
     'TotalAmount': lambda x: x.sum()})

# Convert Invoice Date into type int
RFMScores['InvoiceDate'] = RFMScores['InvoiceDate'].astype(int)

# Rename column names to Recency, Frequency and Monetary
RFMScores.rename(columns={'InvoiceDate': 'Recency',
                          'InvoiceNo': 'Frequency',
                          'TotalAmount': 'Monetary'}, inplace=True)


x = RFMScores['Recency']

ax = sns.distplot(x)



# Descriptive Statistics (Monetary)
RFMScores.Monetary.describe()

# Monateray distribution plot, taking observations which have monetary value less than 10000

# Split into four segments using quantiles
quantiles= RFMScores.quantile(q = [0.2,0.4,0.6,0.8])
quantiles = quantiles.to_dict()





# Functions to create R, F and M segments
def RScoring(x, p, d):
    if x <= d[p][0.20]:
        return 1
    elif x <= d[p][0.40]:
        return 2
    elif x <= d[p][0.60]:
        return 3
    elif x <= d[p][0.80]:
        return 4
    else:
        return 5



def FnMScoring(x, p, d):
    if x <= d[p][0.20]:
        return 5
    elif x <= d[p][0.40]:
        return 4
    elif x <= d[p][0.60]:
        return 3
    elif x <= d[p][0.80]:
        return 2
    else:
        return 1



# Calculate Add R, F and M segment value columns in the existing dataset to show R, F and M segment values
RFMScores['R'] = RFMScores['Recency'].apply(RScoring, args=('Recency', quantiles,))
RFMScores['F'] = RFMScores['Frequency'].apply(FnMScoring, args=('Frequency', quantiles,))
RFMScores['M'] = RFMScores['Monetary'].apply(FnMScoring, args=('Monetary', quantiles,))
RFMScores.head()

# Calculate and Add RFMGroup value column showing combined concatenated score of RFM
RFMScores['RFMGroup'] = RFMScores.R.map(str) + RFMScores.F.map(str) + RFMScores.M.map(str)

# Calculate and Add RFMScore value column showing total sum of RFMGroup values
RFMScores['RFMScore'] = RFMScores[['R', 'F', 'M']].sum(axis=1)
RFMScores.head()
print(RFMScores.head())
