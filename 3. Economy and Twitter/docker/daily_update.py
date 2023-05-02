# General instructions to create a .zip deployment package:
    # https://docs.aws.amazon.com/lambda/latest/dg/services-rds-tutorial.html
# Must utilize psycopg2 library compiled for AWS Lambda which can be found at:
    # https://github.com/jkehler/awslambda-psycopg2
# For initially connecting to the AWS RDS PostgreSQL instance, need to specify db as 'postgres'

import tweepy
import keys    # Passwords & keys for RDS, Twitter & FRED APIs.
import numpy
import pandas as pd
from textblob import TextBlob
import re
import emoji
import fredpy as fp
import psycopg2 as ps # needed when deployed to AWS Lambda
import os

def main():

    # Function to clean tweets from emojis, links and line breaks and more
    # https://github.com/Coding-with-Adam/Dash-by-Plotly/blob/master/Dash_More_Advanced_Shit/NLP/nlpDash.py
        # He found it somewhere on Medium or online, I was unable to locate the source

    def clean_tweets(txt):
        txt = emoji.replace_emoji(txt, replace='')
        txt = txt.replace(r'[^\x00-\x7F]+', '')
        txt = re.sub(r"RT[\s]+", "", txt)
        txt = txt.replace("\n", " ")
        txt = re.sub(" +", " ", txt)
        txt = re.sub(r"https?:\/\/\S+", "", txt)
        txt = re.sub(r"(@[A-Za-z0–9_]+)|[^\w\s]|#", "", txt)
        txt.strip()
        return txt
    
    # search tweets with certain terms and analyze them

    client = tweepy.Client(bearer_token=keys.BEARER_TOKEN)
    query = '"US Economy" OR "U.S. economy" OR "American economy" -is:retweet lang:en'

    # search_recent_tweets has a max results limit of 100, using paginator to increase max
    # https://gist.github.com/mGalarnyk/5b251ea41c3626d6965ac7d5006da432
    tweets = tweepy.Paginator(client.search_recent_tweets,
                              query=query,
                              tweet_fields=['created_at'], 
                              max_results=100).flatten(limit=100000) # increase to 100K for production
    # tweets above is a generator object and can only be iterated through once
    # need to sort payload by dates

    all_tweets = []

    cleaned_tweets, polarity_scores = [], []
    for tweet in tweets:
        # Clean the tweet
        cleaned = clean_tweets(tweet.text)
        p = TextBlob(cleaned).sentiment.polarity
        polarity_scores.append(p)
        cleaned_tweets.append(cleaned) #used for troubleshooting payload transformation    

        # https://towardsdatascience.com/collect-data-from-twitter-a-step-by-step-implementation-using-tweepy-7526fff2cb31
        parsed_tweet = {}
        parsed_tweet['date'] = tweet.created_at
        parsed_tweet['text'] = cleaned
        parsed_tweet['Polarity'] = p
        all_tweets.append(parsed_tweet)

    df = pd.DataFrame(all_tweets)
    df['date'] = pd.to_datetime(df['date']).dt.date  # Strip time and leave date
    
    # This does not subtract from monthly tweet limit.
    counts = client.get_recent_tweets_count(query=query, granularity='day')

    from datetime import datetime

    dates = []
    tweets = []
    for count in counts.data:
        date = datetime.strptime(count['end'][:10], '%Y-%m-%d')
        # Tweet payload includes 2 end dates for the current date with the 1st 
        # being the full day so the last date needs to be ignored.
        if date in dates:
            break
        else:
            dates.append(date)
            tweets.append(count['tweet_count'])
    tups = tuple(zip(dates, tweets))    
    date_list = list(tups)
    # Dataframe with dates and # of mentions as columns
    df_mentions = pd.DataFrame(date_list, columns=['date', 'Mentions'])
    
    df_p = df.groupby('date', as_index=False).mean()
    df_p['date'] = pd.to_datetime(df_p['date'])  # convert to same dtype as df_mentions['date']
    
    df_dmp = df_mentions.merge(df_p, how='right', on='date')
    df_dmp = df_dmp.set_index(df.columns[0])
    
    # Delete first 2 and last dates since they don't capture full days of tweets
    df_dmp = df_dmp[2:-1]
    
    """Download important economic metrics from FRED - Federal Reserve Economic Data - 
    https://fred.stlouisfed.org/
    "This product uses the FRED® API but is not endorsed or certified by the 
    Federal Reserve Bank of St. Louis."""
    
    # FRED key availabe at https://fred.stlouisfed.org/docs/api/api_key.html
    fp.api_key = keys.FRED_KEY
    
    # Selecting dates to download monthly economic data ...
    #  limited to 8 days since current Twitter API access level allows 7 days search 
    # Setting up time delay to reduce API call rate

    from datetime import datetime, timedelta
    from time import sleep

    secs = 31
    t = datetime.today()
    d = t - timedelta(days=8)
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
    
    # Functions for adding missing dates to dfs, usually weekends/holidays, and returns updated dfs

    def missed_daily(series_id, col_name):

        # Set range of dates in accordance to prior API calls
        idx = pd.date_range(d.strftime('%Y-%m-%d'), t.strftime('%Y-%m-%d'))

        # Fill in missing dates and NaNs for their values
        series_id = pd.Series(series_id, name=col_name)
        series_id.index = pd.DatetimeIndex(series_id.index)
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
    
    # Using Pandas concat else dates with NaN values are dropped when creating df
    # Data that changes daily are on the left while monthly are on the right of df
    econ = pd.concat((dj, n, sp, inf, oil, ff, tnote, cpi_i, cpi_p), axis=1)
    df_econ = pd.DataFrame(index=dj.index.union(n.index), data=econ)
    
    # Forward fill prior to analysis or visualizing
    df_econ = df_econ.fillna(method='ffill')
    
    # Merge tweets dataframe with economic metrics dataframe
    df_final = df_dmp.join(df_econ, how='inner')
    
    # Set date as first column to ease export into PostgreSQL
    df_final = df_final.reset_index()
    df_final = df_final.rename(columns={'index':'date'})
    
    
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
        query = ("""SELECT date FROM tweets WHERE date = %s""")
        cur.execute(query, (date,))
        return cur.fetchone() is not None
        
    def insert_into_table(cur, date, Mentions, Polarity, Dow, NASDAQ, SP500, Inflation_5yr, Oil,
                          Interest, T_Note_10yr, CPI_item_cost, CPI_purchase_power):
        insert_into_tweets = ("""INSERT INTO tweets (date, Mentions, Polarity, Dow, NASDAQ, SP500, 
        Inflation_5yr, Oil, Interest, T_Note_10yr, CPI_item_cost, CPI_purchase_power)
                            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);""")
        row_to_insert = (date, Mentions, Polarity, Dow, NASDAQ, SP500, Inflation_5yr, Oil, 
                         Interest, T_Note_10yr, CPI_item_cost, CPI_purchase_power)
        cur.execute(insert_into_tweets, row_to_insert)

    def append_from_df_to_db(cur,df):
        for i, row in df.iterrows():
            insert_into_table(cur, row['date'], row['Mentions'], row['Polarity'],  row['Dow'],
                              row['NASDAQ'], row['SP500'], row['Inflation_5yr'], row['Oil'],
                              row['Interest'], row['T_Note_10yr'], row['CPI_item_cost'],
                              row['CPI_purchase_power'])

    def update_db(cur,df):
        tmp_df = pd.DataFrame(columns=['date', 'Mentions', 'Polarity', 'Dow', 'NASDAQ', 'SP500', 
                                       'Inflation_5yr', 'Oil', 'Interest', 'T_Note_10yr', 
                                       'CPI_item_cost', 'CPI_purchase_power'])
        for i, row in df.iterrows():
            if check_if_date_exists(cur, row['date']): 
                pass    # If date exists then pass and check the next date
            else: # If date doesn't exist, add to a temp df and append it with append_from_df_to_db
                tmp_df = tmp_df.append(row)
        return tmp_df    
    
    # Set the AWS RDS connection parameters
    # DB_NAME = 'postgres'    
        #default db name, connect using this to add new db or delete existing db
    # If using imported keys file python script
    dbname=keys.DB_NAME
    user=keys.DB_USER
    password=keys.DB_PASSWORD
    host=keys.DB_HOST
    port=keys.DB_PORT
    # If using Environment variables
    # dbname=os.environ['DB_NAME']
    # user=os.environ['DB_USER']
    # password=os.environ['DB_PASSWORD']
    # host=os.environ['DB_HOST']
    # port=os.environ['DB_PORT']
    
    conn = connect_to_db(dbname, user, password, host, port)
    conn.set_isolation_level(ps.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    #update data for existing dates
    new_date_df = update_db(cur,df)
    conn.commit()

    #insert new dates into db table

    append_from_df_to_db(cur, new_date_df)
    conn.commit()

    #view data in db table

    cur.execute("SELECT * FROM tweets")
    print(cur.fetchall())
    
    # Close the database connection
    conn.close()

    return {
        'statusCode': 200,
        'body': 'Database connection successful!'
    }

if __name__ == '__main__':
    main()