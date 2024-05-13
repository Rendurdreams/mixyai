import requests
import sqlite3
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
        for ucid, data in crypto_data.items():
            # Extract and prepare data for insertion
            # Some data fields like tags and platform may need checks for None or conversion
            tags = ','.join(data['tags']) if data['tags'] else ''  # Convert list of tags to comma-separated string
            platform = data['platform']['name'] if data['platform'] else ''
            cursor.execute('''
                INSERT INTO Cryptocurrencies (
                    ucid, name, symbol, slug, num_market_pairs, date_added, tags, 
                    max_supply, circulating_supply, total_supply, is_active, infinite_supply, 
                    platform, cmc_rank, is_fiat
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(ucid) DO UPDATE SET
                    name=excluded.name, symbol=excluded.symbol, slug=excluded.slug, 
                    num_market_pairs=excluded.num_market_pairs, date_added=excluded.date_added,
                    tags=excluded.tags, max_supply=excluded.max_supply, 
                    circulating_supply=excluded.circulating_supply, total_supply=excluded.total_supply, 
                    is_active=excluded.is_active, infinite_supply=excluded.infinite_supply, 
                    platform=excluded.platform, cmc_rank=excluded.cmc_rank, is_fiat=excluded.is_fiat;
            ''', (
                data['id'], data['name'], data['symbol'], data['slug'], data.get('num_market_pairs', 0),
                data['date_added'].split('T')[0], tags, data.get('max_supply', 0), 
                data.get('circulating_supply', 0), data.get('total_supply', 0),
                data['is_active'], data.get('infinite_supply', False), 
                platform, data.get('cmc_rank', 0), data.get('is_fiat', False)
            ))
        
        connection.commit()
        print("Successfully updated the database.")
    except Exception as e:
        connection.rollback()
        print("Failed to update the database:", e)
    finally:
        cursor.close()


def main():
    # List of UCIDs to update - adjust this list as necessary
    ucids = ['1', '5', '5426','24835', '2354']  # These are example UCIDs; replace with actual UCIDs

    db_path = '/Users/jakeb/Projects/mixyai/app/db/maindatabase.db'
    connection = sqlite3.connect(db_path)

    crypto_data = fetch_crypto_data(CMC_KEY, ucids)
    if crypto_data and 'data' in crypto_data:
        update_database(crypto_data['data'], connection)
    else:
        print("No valid data received from API.")

    connection.close()

if __name__ == "__main__":
    main()

