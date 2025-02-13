import logging

from .data_manager.prepare_date import prepare_date
from .vizualization.show_chart import show_chart
from alor.ticker import Ticker


logger = logging.getLogger(__name__)


class Terminal:
    def __init__(self):
        self.__ticker = Ticker('SBER')

    def prepare(self):
        prepare_date(quotes=self.__ticker.quotes, ticker_config=self.__ticker.config)

    def show(self):
        show_chart(ticker_config=self.__ticker.config)
