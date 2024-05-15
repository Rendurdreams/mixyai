from dotenv import load_dotenv
import os

load_dotenv()  # This line loads the environment variables from the .env file.

CMC_KEY = os.getenv('COIN_MARKET_CAP_API_KEY')
NEWS_KEY = os.getenv('CRYPTO_PANIC_API_KEY')
OPENAI_KEY = os.getenv('OPEN_AI_API_KEY')