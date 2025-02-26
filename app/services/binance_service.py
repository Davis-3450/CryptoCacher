from binance.client import Client
from binance.exceptions import BinanceAPIException
import os


class BinanceService:
    """
    Service for interacting with the Binance API.

    Handles cryptocurrency price queries and manages API credentials.
    """

    def __init__(self):
        api_key = os.getenv("BINANCE_API_KEY", "")
        api_secret = os.getenv("BINANCE_API_SECRET", "")
        self.client = Client(api_key, api_secret)

    def is_active(self) -> bool:
        """
        Check if the Binance API is accessible and the authentication is valid.
        Returns:
            bool: True if authentication succeeds, otherwise False.
        """
        try:
            # The ping method will raise an exception if authentication fails.
            self.client.ping()
            return True
        except BinanceAPIException as e:
            return False
        except Exception as e:
            return False

    def get_symbol_price(self, symbol: str) -> float:
        """
        Fetch current price for a given trading symbol.

        Args:
            symbol (str): Trading pair symbol (e.g., 'BTCUSDT', 'ETHUSDT')

        Returns:
            float: Current price of the trading pair

        Raises:
            ValueError: If symbol is invalid or API request fails
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol.upper())
            return float(ticker["price"])
        except BinanceAPIException as e:
            raise ValueError(f"Failed to get price for {symbol}: {str(e)}")
