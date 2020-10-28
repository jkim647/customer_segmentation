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

print(type(Rtl_data))


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

print(RFMScores)

x = RFMScores['Recency']
print(x)
ax = sns.distplot(x)
RFMScores.reset_index().head()


# Descriptive Statistics (Monetary)
RFMScores.Monetary.describe()
test = RFMScores
print(test)
# Monateray distribution plot, taking observations which have monetary value less than 10000

# Split into four segments using quantiles
quantiles= RFMScores.quantile(q = [0.2,0.4,0.6,0.8])
quantiles = quantiles.to_dict()
print(quantiles)



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
RFMScores['R'] = RFMScores['Recency'].apply(FnMScoring, args=('Recency', quantiles,))
RFMScores['F'] = RFMScores['Frequency'].apply(RScoring, args=('Frequency', quantiles,))
RFMScores['M'] = RFMScores['Monetary'].apply(RScoring, args=('Monetary', quantiles,))
RFMScores.head()

# Calculate and Add RFMGroup value column showing combined concatenated score of RFM
RFMScores['RFMGroup'] = RFMScores.R.map(str) + RFMScores.F.map(str) + RFMScores.M.map(str)
RFMScores['loyalty'] = ''

# Calculate and Add RFMScore value column showing total sum of RFMGroup values
RFMScores['RFMScore'] = RFMScores[['R', 'F', 'M']].sum(axis=1)
RFMScores.head()
print(RFMScores.head())
#4 1 1
#Assign customer characteristics to each customer
def find_loyalty(Recency,Frequency,Monetory,id):
    if Recency >=4 and Frequency >=4 and Monetory >=4:
        RFMScores.at[id, 'loyalty'] = 'Champion'
    elif 2<=Recency<=4 and 3<=Frequency<=4 and 4<=Monetory<=5:
        RFMScores.at[id, 'loyalty'] = 'Loyal Customer'
    elif 3<=Recency<=5 and 2<=Frequency<=3 and 2<=Monetory<=3:
        RFMScores.at[id, 'loyalty'] = 'Potential Loyalist'
    elif 4<=Recency<=5 and Frequency<2 and Monetory <2:
        RFMScores.at[id, 'loyalty'] = 'New Customer'
    elif 3 <= Recency <= 4 and Frequency < 2 and Monetory <2:
        RFMScores.at[id, 'loyalty'] = 'Promising'
    elif 3 <= Recency <= 4 and 3 <= Frequency <= 4 and 3 <= Monetory <= 4:
        RFMScores.at[id, 'loyalty'] = 'Need attention'
    elif 2 <= Recency <= 3 and Frequency < 3 and Monetory < 3:
        RFMScores.at[id, 'loyalty'] = 'About to sleep'
    elif Recency < 3 and 2 <=Frequency <= 5 and 2 <= Monetory <= 5:
        RFMScores.at[id, 'loyalty'] = 'At Risk'
    elif Recency < 2 and 4 <= Frequency <= 5 and 4<= Monetory <= 5:
        RFMScores.at[id, 'loyalty'] = 'Cannot lose them'
    elif Recency<2 and Frequency < 2 and Monetory < 2:
        RFMScores.at[id, 'loyalty'] = 'Lost'

    #elif 1 <= Recency <= 2 and 1 <= Frequency <= 2 and 1 <= Monetory <= 2:
       # RFMScores.at[id, 'loyalty'] = 'Hibernating'





for ind in RFMScores.index:
    R = RFMScores['R'][ind]
    F = RFMScores['F'][ind]
    M = RFMScores['M'][ind]
    id = ind
    find_loyalty(R,F,M,id)

print(RFMScores)

RFMScores.dropna()
RFMScores.to_csv('/Users/jskim/PycharmProjects/rfm4.csv', index=False, header=True)









character = ['Champion', 'Loyal_Customer', 'Potential_loyalist', 'New_customer', 'Promising', 'Need_attention',
             'At_risk', 'cannot_lose_them', 'Hibernating', 'Lost']







#Assign customer characteristics to each customer

