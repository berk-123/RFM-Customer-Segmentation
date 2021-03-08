'''''''''''''''''''''''''''
# Variables
# InvoiceNo: Invoice number. The unique number for each transaction.
# IMPORTANT NOTE: If İnvoiceNo code starts with C, it indicates that the transaction has been canceled.
# StockCode: Product code. Unique number for each product.
# Description: Product name
# Quantity: Number of items. It expresses how many products in the invoices are sold.
# InvoiceDate: Invoice date and time.
# UnitPrice: Product price (in Pounds)
# CustomerID: Unique customer number
# Country: Country name. The country where the customer lives.
'''''''''''''''''''''''''''''
import datetime as dt
import pandas as pd
pd.set_option("display.max_columns",None)
df = pd.read_excel("dataset/online_retail_II.xlsx",sheet_name="Year 2010-2011")
df = df_.copy()

## Data overview
df.head()
df.tail()
df.info()
df.isnull().values.any()
df.isnull().sum()

# What is the unique number of products?
df["Description"].nunique()

# how many of which product do you have?
df["Quantity"].value_counts()

# Which is the most ordered product?
df.groupby(df["Description"]).agg({"Quantity":"sum"})


# How do we sort the above output?
df.groupby(df["Description"]).agg({"Quantity":"sum"}).sort_values("Quantity",ascending=False)


# how many invoices have been issued?
df["Invoice"].nunique()


df = df[~df["Invoice"].str.contains("C", na=False)]

# How much money is earned on average per invoice?
df["Total_price"] = df["Price"]* df["Quantity"]

# what are the most expensive products?
df.sort_values("Price",ascending=False).head()

# How many orders came from which country?
df["Country"].value_counts()

# which country made how much?
df.groupby("Country").agg({"TotalPrice": "sum"}).sort_values("TotalPrice", ascending=False).head()

# Data Preparation
df.isnull().sum()
df.dropna(inplace=True)

df.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T

# Recency, Frequency, Monetary

# Recency: Time elapsed since the last purchase of the customer
# In other words, it is the "time elapsed since the last contact of the customer".

# Today's date - Last purchase
df["InvoiceDate"].max()

today_date = dt.datetime(2011, 12, 9)

rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                                     'Invoice': lambda num: len(num),
                                     'Total_price': lambda Total_price: Total_price.sum()})

rfm.columns = ['Recency', 'Frequency', 'Monetary']

rfm = rfm[(rfm["Monetary"]) > 0 & (rfm["Frequency"] > 0)]

# Calculating RFM Scores
# Recency

rfm["RecencyScore"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])

rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])

rfm["MonetaryScore"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])


rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) +
                    rfm['FrequencyScore'].astype(str) +
                    rfm['MonetaryScore'].astype(str))


rfm[rfm["RFM_SCORE"] == "555"].head()

rfm[rfm["RFM_SCORE"] == "111"]

# Naming & Analysing RFM Segments

# Naming Analysis
seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}
rfm.head()

rfm['Segment'] = rfm['RecencyScore'].astype(str) + rfm['FrequencyScore'].astype(str)

rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)
df[["Customer ID"]].nunique()
rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean", "count"])

new_df = pd.DataFrame()

new_df["Loyal_Customers"] = rfm[rfm["Segment"] == "Loyal_Customers"].index

new_df.to_excel("Loyal_Customers.xlsx")

