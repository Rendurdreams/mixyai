import requests
import sqlite3
import json  # Add this import at the beginning of your file
from config import CMC_KEY  # Ensure this file exists and contains the API key

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
        return response.json()
    else:
        print("Failed to fetch data. Status Code:", response.status_code)
        return None

def update_database(crypto_data, connection):
    cursor = connection.cursor()
    try:
        # Iterate through each cryptocurrency data item
        for key, data in crypto_data.items():
            # Serialize 'tags' and 'platform' to JSON strings
            tags = json.dumps(data['tags']) if data['tags'] is not None else None
            platform = json.dumps(data['platform']) if data['platform'] is not None else None
            
            # Prepare data for insertion
            values = (
                data['id'], data['name'], data['symbol'], data['slug'], data['num_market_pairs'],
                data['date_added'], tags, data['max_supply'], data['circulating_supply'],
                data['total_supply'], data['is_active'], data['infinite_supply'], platform,
                data['cmc_rank'], data['is_fiat'], data['quote']['USD']['price'],
                data['quote']['USD']['percent_change_1h'], data['quote']['USD']['percent_change_24h'],
                data['quote']['USD']['percent_change_7d'], data['quote']['USD']['volume_24h']
            )
            
            # Execute SQL command
            cursor.execute('''
                INSERT INTO Coins (ucid, name, symbol, slug, num_market_pairs, date_added, tags, max_supply, 
                                   circulating_supply, total_supply, is_active, infinite_supply, platform, cmc_rank, 
                                   is_fiat, price, price_change_1h, price_change_24h, price_change_7d, volume_24h)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ucid) DO UPDATE SET
                    name=excluded.name,
                    symbol=excluded.symbol,
                    slug=excluded.slug,
                    num_market_pairs=excluded.num_market_pairs,
                    date_added=excluded.date_added,
                    tags=excluded.tags,
                    max_supply=excluded.max_supply,
                    circulating_supply=excluded.circulating_supply,
                    total_supply=excluded.total_supply,
                    is_active=excluded.is_active,
                    infinite_supply=excluded.infinite_supply,
                    platform=excluded.platform,
                    cmc_rank=excluded.cmc_rank,
                    is_fiat=excluded.is_fiat,
                    price=excluded.price,
                    price_change_1h=excluded.price_change_1h,
                    price_change_24h=excluded.price_change_24h,
                    price_change_7d=excluded.price_change_7d,
                    volume_24h=excluded.volume_24h;
            ''', values)
        
        connection.commit()
        print("Successfully updated the database.")
    except Exception as e:
        connection.rollback()
        print("Failed to update database:", e)
    finally:
        cursor.close()

def main():
    # List of UCIDs to update - adjust this list as necessary
    ucids = ['1','5426','24835','2354']  # These are example UCIDs; replace with actual UCIDs

    db_path = '/Users/jakeb/Projects/mixyai/app/db/coindata.db'
    connection = sqlite3.connect(db_path)

    crypto_data = fetch_crypto_data(CMC_KEY, ucids)
    if crypto_data and 'data' in crypto_data:
        update_database(crypto_data['data'], connection)
    else:
        print("No valid data received from API.")

    global_metrics = fetch_latest_global_metrics()
    if global_metrics and 'data' in global_metrics:
        update_global_metrics_db(connection, global_metrics['data'])
    else:
        print("No valid global metrics data received from API.")

    connection.close()

if __name__ == "__main__":
    main()

