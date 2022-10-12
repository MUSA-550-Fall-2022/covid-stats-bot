import os

from bs4 import BeautifulSoup
import pandas as pd
import requests
import tweepy as tw


def scrape_data():
    """Scrape COVID-19 case data from phila.gov."""

    url = "https://www.phila.gov/programs/coronavirus-disease-2019-covid-19/updates/"
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.37"

    result = requests.get(url, headers={"User-Agent": user_agent})
    soup = BeautifulSoup(result.content, "html.parser")

    # Get the case count
    selector = "#post-263624 > div.one-quarter-layout > div:nth-child(1) > div.medium-18.columns.pbxl > ul > li:nth-child(1)"
    case_count = int(soup.select_one(selector).text.split()[-1])

    # Get the last updated date
    selector = "#post-263624 > div.one-quarter-layout > div:nth-child(1) > div.medium-18.columns.pbxl > p:nth-child(3) > em"
    lines = soup.select_one(selector).text.splitlines()
    last_updated = pd.to_datetime(lines[0].split(":")[-1])

    # Return
    return case_count, last_updated


def tweet_data(data):
    """Tweet data."""

    # Load secret API credentials from the environment
    client = tw.Client(
        consumer_key=os.environ['TWITTER_API_KEY'],
        consumer_secret=os.environ['TWITTER_API_KEY_SECRET'],
        access_token=os.environ['TWITTER_ACCESS_TOKEN'],
        access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    )

    last_data = data.iloc[-1]
    dt = last_data['last_updated']
    count = last_data['case_count']

    # Format the data
    dt = dt.strftime("%B %-d, %Y")

    # Text
    tweet_text = f"As of {dt}, the average number of new cases per day was {count}"

    # Send the tweet
    client.create_tweet(text=tweet_text)



# Run the scraper
case_count, last_updated = scrape_data()

# Load existing data
data = pd.read_csv('./data.csv')
data['last_updated'] = pd.to_datetime(data['last_updated'])

# Do we have new data?
if not len(data) or data['last_updated'].iloc[-1] < last_updated:

    # Create the new dataframe
    new_data = pd.DataFrame.from_records([{"last_updated":last_updated, "case_count":case_count}])

    # Combine
    data = pd.concat([data, new_data])

    # Save it
    data.to_csv("./data.csv", index=False)

    # Tweet it!
    tweet_data(data)



    