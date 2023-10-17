## -*- coding: utf-8 -*-

# General instructions to create a .zip deployment package:
    # https://docs.aws.amazon.com/lambda/latest/dg/services-rds-tutorial.html
# Must utilize psycopg2 library compiled for AWS Lambda which can be found at:
    # https://github.com/jkehler/awslambda-psycopg2
# For initially connecting to the AWS RDS PostgreSQL instance, need to specify db as 'postgres'

# import keys    # Passwords & keys for RDS & FRED APIs when running on local machine

import numpy as np
import pandas as pd
# import requests
import fredpy as fp
import psycopg2 as ps # needed to establish connection with AWS RDS
import os
import matplotlib.pyplot as plt
import statsmodels.api as sm
from datetime import datetime, timedelta
from time import sleep
import boto3
from botocore.exceptions import ClientError
import sys
import subprocess

# set the print options to display all columns and rows to assist with debugging
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

# Connect to S3 to download secrets and keys
s3 = boto3.client('s3')
bucket_name = 'econdaily-prod-app-config'
file_name = 'env.source'
local_filename = '/app/myfilefroms3'

s3.download_file(bucket_name, file_name, local_filename)

with open(local_filename, 'r') as f:
    secrets = {line.strip().split('=')[0]: line.strip().split('=')[1] for line in f}
# print('secrets are:', secrets) # for debugging

def main():
    
    """Download important economic metrics from FRED - Federal Reserve Economic Data - 
    https://fred.stlouisfed.org/
    "This product uses the FRED® API but is not endorsed or certified by the 
    Federal Reserve Bank of St. Louis."""
    
    # FRED key availabe at https://fred.stlouisfed.org/docs/api/api_key.html
    fp.api_key = secrets['FRED_KEY']
    
    # Selecting dates to download monthly economic data ...
    # Setting up time delay to reduce API call rate

    secs = 31
    t = datetime.today()
    d = t - timedelta(days=31)
    days = [d.strftime('%Y-%m-%d'), t.strftime('%Y-%m-%d')]
    
    # Download economic metrics with time delay and custom API request to reduce API call rate
    # See "Custom API querries" here:
        # https://www.briancjenkins.com/fredpy/docs/build/html/fredpy_examples.html

    # Function for custom API request with economic series ID and dates as string inputs > 
    # ...returns df with dates and economic series values
    def series_df(series_id, period):

        # Specify the API path
        path = 'fred/series/observations'

        # API request and specify desired parameter values for the API query
        data = fp.fred_api_request(api_key=fp.api_key,
                                    path=path,
                                    parameters={'series_id':series_id,
                                                'observation_start':period[0],
                                                'observation_end':period[1],
                                                'file_type':'json'})

        # Return results in JSON format
        data = data.json()

        # # Load data, deal with missing values, format dates in index, and set dtype
        df = pd.DataFrame(data['observations'], columns =['date','value'])
        df = df.replace('.', np.nan)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')['value'].astype(float)
        return df
    
    # Download daily economic data

    # Dow Jones Industrial Average
    djia = series_df('DJIA', days)

    # NASDAQ Composite Index
    sleep(secs)
    nasdaq = series_df('NASDAQCOM', days)

    # S&P 500
    sleep(secs)
    sp500 = series_df('SP500', days)

    # Federal Funds Effective Rate (benchmark for U.S. interest rates)
    sleep(secs)
    dff = series_df('DFF', days)

    # 5-Year Breakeven Inflation Rate
    sleep(secs)
    infl = series_df('T5YIE', days)

    # US benchmark for crude oil prices using West Texas Intermediate
    sleep(secs)
    tex = series_df('DCOILWTICO', days)

    # 10 Year T-Note
    sleep(secs)
    Tnote = series_df('DGS10', days)
    
    # Selecting dates to download monthly economic data

    f = datetime.today()
    s = f - timedelta(days=75)
    month = [s.strftime('%Y-%m-%d'), f.strftime('%Y-%m-%d')]
    
    # Download monthly economic data

    # Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
    sleep(secs)
    CPI_i = series_df('CPIAUCSL', month)

    # Consumer Price Index for All Urban Consumers: 
        # Purchasing Power of the Consumer Dollar in U.S. City Average
    sleep(secs)
    CPI_p = series_df('CUUR0000SA0R', month)

    # Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
    sleep(secs)
    conf = series_df('CSCICP03USM665S', month)
    
    # Functions for adding missing dates to dfs, usually weekends/holidays, and returns updated dfs

    def missed_daily(series_id, col_name):

        # Set range of dates in accordance to prior API calls
        idx = pd.date_range(d.strftime('%Y-%m-%d'), t.strftime('%Y-%m-%d'))

        # Fill in missing dates and NaNs for their values
        series_id = pd.Series(series_id, name=col_name)
        series_id.index = pd.DatetimeIndex(series_id.index)
        # df = series_id.reindex(idx, method='ffill')
        df = series_id.reindex(idx)
        return df

    def missed_monthly(series_id, col_name):

        # Set range of dates in accordance to prior API calls
        idx = pd.date_range(d.strftime('%Y-%m-%d'), t.strftime('%Y-%m-%d'))

        # Fill in missing dates and NaNs for their values
        series_id = pd.Series(series_id, name=col_name)
        series_id.index = pd.DatetimeIndex(series_id.index)
        df = series_id.reindex(idx, method='ffill') 
            # forward fill into the days window for the monthly series
        return df
    
    # Add missing dates to current economic series dfs

    # Dow Jones Industrial Average
    dj = missed_daily(djia, 'Dow')

    # NASDAQ Composite Index
    n = missed_daily(nasdaq, 'NASDAQ')

    # S&P 500
    sp = missed_daily(sp500, 'SP500')

    # Federal Funds Effective Rate (benchmark for U.S. interest rates)
    ff = missed_daily(dff, 'Interest')

    # 5-Year Breakeven Inflation Rate
    inf = missed_daily(infl, 'Inflation_5yr')

    # US benchmark for crude oil prices using West Texas Intermediate
    oil = missed_daily(tex, 'Oil')

    # 10 Year T-Note
    tnote = missed_daily(Tnote, 'T_Note_10yr')

    # Consumer Price Index for All Urban Consumers: All Items in U.S. City Average
    cpi_i = missed_monthly(CPI_i, 'CPI_item_cost')

    # Consumer Price Index for All Urban Consumers: Purchasing Power 
    cpi_p = missed_monthly(CPI_p, 'CPI_purchase_power')

    # Consumer Price Index for All Urban Consumers: Purchasing Power 
    conf = missed_monthly(conf, 'Confidence')    
    
    # Using Pandas concat else dates with NaN values are dropped when creating df
    # Data that changes daily are on the left while monthly are on the right of df
    econ = pd.concat((dj, n, sp, inf, oil, ff, tnote, cpi_i, cpi_p, conf), axis=1)
    df_econ = pd.DataFrame(index=dj.index.union(n.index), data=econ)
    
    # # Forward fill prior to analysis or visualizing
    # df_econ = df_econ.fillna(method='ffill')
    
    # Set date as first column to ease export into PostgreSQL
    df_final = df_econ.reset_index()
    df_final = df_final.rename(columns={'index':'date'})
    df_final['CPI_item_cost'] = df_final['CPI_item_cost'].round(2)
    print("df with NaNs:", df_final)
    df_final = df_final.dropna().reset_index(drop=True)
    print("df with NaN rows dropped:", df_final)

    # Set up AWS SNS client
    sns = boto3.client('sns', region_name='us-east-1')
    topic_arn1 = 'arn:aws:sns:us-east-1:307103213532:econ_nulls'

    # Check for NaN values in the fianl DataFrame and send alert if so
    if df_final.isna().values.any():
        # send email alert
        try:
            response = sns.publish(
                TopicArn=topic_arn1,
                Message='NaN values detected in DataFrame'
            )
            print(f"Email alert sent with message ID: {response['MessageId']}")
        except ClientError as e:
            print(f"Failed to send email alert: {e.response['Error']['Message']}")
            # terminate the script if NaN values found and after sending SNS alert
            sys.exit()

    # Sends SNS alert if AWS RDS database hasn't updated in more than 10 days
    # Calculate the difference in days between today's date and the latest date in the database
    latest_date = df_final['date'].max()
    days_difference = (datetime.today() - latest_date).days
    print("# days DB not updated:", days_difference)

    # Check if the difference is greater than 10
    if days_difference > 10:
        # Set up AWS SNS client
        sns = boto3.client('sns', region_name='us-east-1')
        topic_arn2 = 'arn:aws:sns:us-east-1:307103213532:econ_daily_db'

        # Send email alert
        try:
            response = sns.publish(
                TopicArn=topic_arn2,
                Message='The database has not been updated for more than 10 days.'
            )
            print(f"Email alert sent with message ID: {response['MessageId']}")
        except ClientError as e:
            print(f"Failed to send email alert: {e.response['Error']['Message']}")
            
    # Define functions to establish connnection to AWS RDS and update db
    # Database table already created by a Lambda function
    # https://github.com/Strata-Scratch/api-youtube/blob/main/importing_df_to_db_final.ipynb
        
    def connect_to_db(dbname, user, password, host, port):
        try:
            conn = ps.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
        except ps.OperationalError as e:
            raise e
        else:
            print('Connected!')
            return conn

    def check_if_date_exists(cur, date): 
        query = ("""SELECT date FROM econ_metrics WHERE date = %s""")
        cur.execute(query, (date,))
        return cur.fetchone() is not None
        
    def insert_into_table(cur, date, Dow, NASDAQ, SP500, Inflation_5yr, Oil,
                          Interest, T_Note_10yr, CPI_item_cost, CPI_purchase_power, Confidence):
        insert_into_econ_metrics = ("""INSERT INTO econ_metrics (date, Dow, NASDAQ, SP500, 
        Inflation_5yr, Oil, Interest, T_Note_10yr, CPI_item_cost, CPI_purchase_power, Confidence)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""")
        row_to_insert = (date, Dow, NASDAQ, SP500, Inflation_5yr, Oil, 
                         Interest, T_Note_10yr, CPI_item_cost, CPI_purchase_power, Confidence)
        cur.execute(insert_into_econ_metrics, row_to_insert)

    def append_from_df_to_db(cur,df_final):
        for i, row in df_final.iterrows():
            insert_into_table(cur, row['date'],  row['Dow'],
                              row['NASDAQ'], row['SP500'], row['Inflation_5yr'], row['Oil'],
                              row['Interest'], row['T_Note_10yr'], row['CPI_item_cost'],
                              row['CPI_purchase_power'], row['Confidence'])

    def update_db(cur,df_final):
        tmp_df = pd.DataFrame(columns=['date', 'Dow', 'NASDAQ', 'SP500', 
                                       'Inflation_5yr', 'Oil', 'Interest', 'T_Note_10yr', 
                                       'CPI_item_cost', 'CPI_purchase_power', 'Confidence'])
        for i, row in df_final.iterrows():
            if check_if_date_exists(cur, row['date']): 
                pass    # If date exists then pass and check the next date
            else: # If date doesn't exist, add to a temp df and append it with append_from_df_to_db
                tmp_df = tmp_df.append(row)
        return tmp_df
    
    # Set the AWS RDS connection parameters
    # DB_NAME = 'postgres'    
        #default db name, connect using this to add new db or delete existing db
    # If using imported keys file python script
    # dbname=keys.DB_NAME
    # user=keys.DB_USER
    # password=keys.DB_PASSWORD
    # host=keys.DB_HOST
    # port=keys.DB_PORT
    # If using Environment variables
    dbname  = secrets['DB_NAME']
    user    = secrets['DB_USER']
    password= secrets['DB_PASSWORD']
    host    = secrets['DB_HOST']
    port    = secrets['DB_PORT']
    
    conn = connect_to_db(dbname, user, password, host, port)
    conn.set_isolation_level(ps.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    #update data for existing dates
    new_date_df = update_db(cur,df_final)
    conn.commit()

    #insert new dates into db table

    append_from_df_to_db(cur, new_date_df)
    conn.commit()

    #view data in db table

    cur.execute("SELECT * FROM econ_metrics")
    print("Data from AWS RDS PostgreSQL!")
    print(cur.fetchall())
    
    # Close the database connection
    conn.close()

    return {
        'statusCode': 200,
        'body': 'Database connection successful!'
    }

if __name__ == '__main__':
    main()
    sys.exit()