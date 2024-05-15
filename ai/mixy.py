from config import OPENAI_KEY
import sqlite3
import json
import os
from openai import OpenAI
from datetime import datetime, timedelta

DATABASE_PATH = '/Users/jakeb/Projects/mixyai/db/coindata.db'
API_KEY = OPENAI_KEY
client = OpenAI(api_key=API_KEY)  # Set up the OpenAI API key

# Function to fetch data from the database
def fetch_data():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()
    try:
        # Fetch current coins data
        cursor.execute("""
            SELECT name, symbol, cmc_rank, price, price_change_1h, price_change_24h, price_change_7d, volume_24h
            FROM Coins
            ORDER BY price_change_24h ASC
        """)
        coins = cursor.fetchall()

        # Fetch global metrics
        cursor.execute("""
            SELECT total_market_cap, total_volume_24h, btc_dominance, last_updated
            FROM GlobalMetrics
            ORDER BY last_updated DESC
            LIMIT 3
        """)
        metrics = cursor.fetchall()

        # Fetch historical data for the last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(days=1)
        cursor.execute("""
            SELECT ucid, name, symbol, price, price_change_1h, price_change_24h, price_change_7d, volume_24h, timestamp
            FROM CoinHistory
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (twenty_four_hours_ago,))
        history = cursor.fetchall()

        print("Successfully fetched coins data, global metrics, and historical data.")
    except sqlite3.Error as e:
        print(f"An error occurred while fetching data: {e}")
    finally:
        cursor.close()
        connection.close()
    return coins, metrics, history

# Function to load text files
def load_file(filepath):
    with open(filepath, 'r') as file:
        return file.read().strip()

# Function to analyze data using OpenAI
def analyze_data(coins, metrics, history, sentiment, strategy):
    print("Mixy is analyzing the data, hold a sec and let the homie cook...")
    # Convert data to JSON strings for analysis
    coins_data = json.dumps(coins)
    metrics_data = json.dumps(metrics)
    history_data = json.dumps(history)

    # Load sentiment and strategy prompts
    sentiment_prompt = load_file(f'prompts/{sentiment}.txt')
    strategy_prompt = load_file(f'strats/{strategy}.txt')

    # Create a dynamic prompt for GPT-4o
    prompt = f"""
    Yo bro, welcome to your ultimate crypto trading wingman! 
    I'm here to analyze market prices, global metrics, and all the juicy data from your database.
    We're on the lookout for trends, volume surges, and those wild price moves.
    
    ### Current Sentiment: {sentiment.capitalize()}
    - {sentiment_prompt}
    
    ### Strategy: {strategy.capitalize()}
    - {strategy_prompt}

    ### Data Inputs:
    - Market Prices: {coins_data}
    - Global Metrics: {metrics_data}
    - Historical Data (last 24 hours): {history_data}

    Let's get to work and make those trades count. Remember, it's all about staying sharp, adapting to the market, and having a blast while doing it. Let's roll, bro!
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "You are a helpful assistant analyzing cryptocurrency data."},
                      {"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None

def main():
    # Fetch data from the database
    coins, metrics, history = fetch_data()

    # Specify sentiment and strategy
    sentiment = "bullish"  # or "bearish", "neutral"
    strategy = "strat1"  # or "strategy2", "strategy3"

    # Analyze data using GPT-4o
    analysis = analyze_data(coins, metrics, history, sentiment, strategy)
    if analysis:
        print("GPT-4o Analysis:")
        print(analysis)
    else:
        print("No analysis available.")

if __name__ == "__main__":
    main()
