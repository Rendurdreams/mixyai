import requests
import sqlite3
import json
from datetime import datetime
from config import CMC_KEY

# Configuration
DATABASE_PATH = '/Users/jakeb/Projects/mixyai/app/db/coindata.db'
CMC_API_KEY = CMC_KEY

def fetch_crypto_data(api_key, ucids):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {
        'id': ','.join(ucids),  # Convert list of UCIDs to a comma-separated string
        'convert': 'USD'
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }

    response = requests.get(url, headers=headers, params=parameters)
    if response.status_code == 200:
        print("Successfully fetched cryptocurrency data.")
        return response.json()
    else:
        print(f"Failed to fetch cryptocurrency data. Status Code: {response.status_code}")
        return None

def update_database(crypto_data, connection):
    cursor = connection.cursor()
    try:
        query = """INSERT OR REPLACE INTO Coins (
                    ucid, name, symbol, slug, num_market_pairs, date_added, tags,
                    max_supply, circulating_supply, total_supply, is_active,
                    infinite_supply, platform, cmc_rank, is_fiat, price,
                    price_change_1h, price_change_24h, price_change_7d,
                    volume_24h) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        for key, data in crypto_data.items():
            tags = json.dumps(data.get('tags')) if data.get('tags') is not None else None
            platform = json.dumps(data.get('platform')) if data.get('platform') is not None else None
            
            values = (
                data['id'], data['name'], data['symbol'], data['slug'], data['num_market_pairs'],
                data['date_added'], tags, data['max_supply'], data['circulating_supply'],
                data['total_supply'], data['is_active'], data['infinite_supply'], platform,
                data['cmc_rank'], data['is_fiat'], data['quote']['USD']['price'],
                data['quote']['USD']['percent_change_1h'], data['quote']['USD']['percent_change_24h'],
                data['quote']['USD']['percent_change_7d'], data['quote']['USD']['volume_24h']
            )
            cursor.execute(query, values)
        connection.commit()
        print("Successfully updated cryptocurrency data in the database.")
    except Exception as e:
        connection.rollback()
        print(f"Failed to update cryptocurrency data in the database: {e}")
    finally:
        cursor.close()

def update_global_metrics_db(connection, metrics):
    cursor = connection.cursor()
    try:
        query = """INSERT OR REPLACE INTO GlobalMetrics (
                    total_market_cap, total_volume_24h, btc_dominance,
                    active_cryptocurrencies, active_markets, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)"""
        
        values = (
            metrics['quote']['USD']['total_market_cap'], metrics['quote']['USD']['total_volume_24h'],
            metrics['btc_dominance'], metrics['active_cryptocurrencies'], 
            metrics.get('active_markets', 0),  # Use .get() to avoid KeyError
            datetime.now()
        )
        cursor.execute(query, values)
        connection.commit()
        print("Successfully updated global metrics in the database.")
    except Exception as e:
        connection.rollback()
        print(f"Failed to update global metrics in the database: {e}")
    finally:
        cursor.close()

def fetch_latest_global_metrics(api_key):
    url = "https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/latest"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("Successfully fetched global metrics data.")
        return response.json()
    else:
        print(f"Failed to fetch global metrics data. Status Code: {response.status_code}")
        return None

def main():
    ucids = ['1', '5426', '24835', '2354']  # Example UCIDs
    connection = sqlite3.connect(DATABASE_PATH)

    crypto_data = fetch_crypto_data(CMC_API_KEY, ucids)
    if crypto_data and 'data' in crypto_data:
        update_database(crypto_data['data'], connection)
    else:
        print("No valid cryptocurrency data received from API.")

    global_metrics = fetch_latest_global_metrics(CMC_API_KEY)
    if global_metrics and 'data' in global_metrics:
        update_global_metrics_db(connection, global_metrics['data'])
    else:
        print("No valid global metrics data received from API.")

    connection.close()

if __name__ == "__main__":
    main()
