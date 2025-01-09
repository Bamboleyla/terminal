import logging
import os

from alor.config import AlorConfiguration

__all__ = "AlorDownloader"

logger = logging.getLogger(__name__)


class AlorDownloader:
    def __init__(self):
        self.__config = AlorConfiguration()

    def prepare(self):
        for ticker in self.__config.tickers:
            print(ticker)
