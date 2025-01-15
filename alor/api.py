import logging
import uuid
import websockets
import json
import pandas as pd

from datetime import datetime, timezone, timedelta
from alor.token import AlorToken
from alor.config import AlorConfiguration

__all__ = "AlorAPI"

logger = logging.getLogger(__name__)


class AlorAPI:
    def __init__(self):
        token = AlorToken()  # Load token service
        config = AlorConfiguration()  # Load configuration

        self.ws_url = config.websocket_url  # Get websocket url
        self.access_token = token.get_access_token()['access_token']  # Get access token

    async def get_ticker_data(self, ticker: str, start_date: datetime) -> pd.DataFrame:

        df = pd.DataFrame(columns=['TICKER', 'DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME'],
                          dtype=[object, object, float, float, float, float, float])  # Create quotes DataFrame

        try:
            async with websockets.connect(self.ws_url) as websocket:  # connect to websocket
                message = {
                    "opcode": "BarsGetAndSubscribe",
                    "code": ticker,
                    "tf": "300",
                    "from": start_date.timestamp(),
                    "delayed": False,
                    "skipHistory": False,
                    "exchange": "MOEX",
                    "format": "Simple",
                    "frequency": 100,
                    "guid": uuid.uuid4().hex,
                    "token": self.access_token
                }
                await websocket.send(json.dumps(message))  # send message
                # receive response
                while True:
                    try:
                        response = await websocket.recv()  # receive response
                        response_dict = json.loads(response)  # convert response to dictionary

                        if 'httpCode' in response_dict:  # check if response contains 'httpCode'
                            return df  # return responses because httpCode is last field in response

                        json_item = json.loads(response)['data']  # convert item to json
                        date = datetime.fromtimestamp(json_item['time'], timezone.utc).astimezone(
                            timezone(offset=timedelta(hours=3))).strftime('%Y%m%d %H:%M:%S')  # convert timestamp to datetime, then to local time (UTC+3)

                        df.loc[len(df)] = [ticker, date, json_item["open"],
                                           json_item["high"], json_item["low"],
                                           json_item["close"], json_item["volume"]]  # add row to df

                        # responses.append(response)  # append response to list
                    except websockets.ConnectionClosed:
                        break

        except Exception as e:
            logger.error(f'Error connecting to websocket with {ticker}: {e}')

        return df
