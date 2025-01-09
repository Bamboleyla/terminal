import logging

from settings import alor
from datetime import datetime, date, timedelta

__all__ = "AlorConfiguration"

logger = logging.getLogger(__name__)


class AlorConfiguration:
    def __init__(self) -> None:
        self.contract: str = alor['contract']  # Alor contract
        self.token: str = alor['token']  # Alor token
        self.ttl_jwt: int = alor['ttl_jwt']  # Time to live JWT
        self.url_oauth: str = alor['url_oauth']  # Alor OAuth URL
        self.open: int = alor['open']  # Open time of Alor
        self.close: int = alor['close']  # Close time of Alor
        self.work_days: list = alor['work_days']  # List of work days
        self.websocket_url: str = alor['websocket_url']  # Alor WebSocket URL
        self.https_url: str = alor['https_url']  # Alor HTTPS URL
        self.stock_market: str = alor['stock_market']  # Alor stock market
        self.tickers: list = alor['tickers']  # List of tickers
