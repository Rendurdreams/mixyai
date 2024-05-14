import sqlite3
import pandas as pd


# Configuration
DATABASE_PATH = '/Users/jakeb/Projects/mixyai/app/db/coindata.db'

def fetch_coin_list(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT name, symbol, cmc_rank, price, price_change_1h, price_change_24h, price_change_7d, volume_24h
        FROM Coins
        ORDER BY cmc_rank ASC
    """)
    coins = cursor.fetchall()
    cursor.close()
    return coins

def fetch_recent_global_metrics(connection, limit=3):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT total_market_cap, total_volume_24h, btc_dominance, last_updated
        FROM GlobalMetrics
        ORDER BY last_updated DESC
        LIMIT ?
    """, (limit,))
    metrics = cursor.fetchall()
    cursor.close()
    return metrics

def parse_and_print_data(coins, metrics):
    print("\nCoin List:")
    for coin in coins:
        name, symbol, rank, price, price_change_1h, price_change_24h, price_change_7d, volume_24h = coin
        print(f"Name: {name}, Symbol: {symbol}, Rank: {rank}, Price: {price}, "
              f"1h Change: {price_change_1h}%, 24h Change: {price_change_24h}%, 7d Change: {price_change_7d}%, "
              f"Volume (24h): {volume_24h}")

    print("\nMost Recent Global Metrics:")
    for metric in metrics:
        total_market_cap, total_volume_24h, btc_dominance, last_updated = metric
        print(f"Timestamp: {last_updated}, Total Market Cap: {total_market_cap}, "
              f"Total Volume (24h): {total_volume_24h}, BTC Dominance: {btc_dominance}")

def main():
    connection = sqlite3.connect(DATABASE_PATH)

    coins = fetch_coin_list(connection)
    metrics = fetch_recent_global_metrics(connection)

    parse_and_print_data(coins, metrics)

    connection.close()

if __name__ == "__main__":
    main()