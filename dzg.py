import requests
import os
from dotenv import load_dotenv
import time
import hmac
import hashlib
from urllib.parse import quote


load_dotenv()  # Загружает переменные из .env

api_key: str = os.getenv("API_key")
secret_key: str = os.getenv("secret_key")
account_id: str = os.getenv("account_id")
url: str = os.getenv("url")


class Trade:
    def __init__(self, api_key: str, secret_key: str, url: str = url):
        """Инициализация класса Trade с API-ключами и выбором режима (демо или реальный)."""
        self.api_key = api_key
        self.secret_key = secret_key
        # self.url = "https://demo-api-adapter.dzengi.com/api/v2"
        self.url = url
        self.recv_window = 5000  
        self.account_id = account_id

    def _generate_signature(self, query_string: str):
        """Генерация подписи HMAC SHA256 для строки запроса."""
        return hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def AccountInfo(self):
        """Получение информации об аккаунте через GET-запрос к /api/v2/account."""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}&recvWindow={self.recv_window}"
        signature = self._generate_signature(query_string)
        url = f"{self.url}/account?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def CancelOrder(self, order_id:str, symbol:str):
        """Удаление ордера через DELETE-запрос к /api/v2/order."""
        timestamp = int(time.time() * 1000)
        query_params = [
            f"orderId={order_id}",
            f"symbol={self.GetSymbol(symbol)}",
            f"timestamp={timestamp}",
            f"recvWindow={self.recv_window}",
            f"accountId={self.account_id}"
        ]

        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/order?{query_string}&signature={signature}"

        headers  = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.delete(url, headers=headers)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def CreateOrder(
        self, 
        symbol: str, 
        side: str, 
        type_: str, 
        quantity: float, 
        resp_type: None|str=None, 
        leverage: None|int=None, 
        price: None|float=None, 
        stop_loss: None|float=None, 
        take_profit: None|float=None):
        """Создание ордера через POST-запрос к /api/v2/order. 
        side = BUY or SELL; 
        type = MARKET, LIMIT or STOP;
        take_profit цена продажи (напрмер покупка 100, продать, когда цена будет 105);
        leverage размер плеча int;
        """
        timestamp = int(time.time() * 1000)
        query_params = [
            f"symbol={self.GetSymbol(symbol)}",
            f"side={side}",
            f"type={type_}",
            f"quantity={quantity}",
            f"timestamp={timestamp}",
            f"recvWindow={self.recv_window}",
            f"accountId={self.account_id}"
        ]
        if resp_type:
            query_params.append(f"newOrderRespType={resp_type}")
        if price:
            query_params.append(f"price={price}")
        if leverage:
            query_params.append(f"leverage={leverage}")
        if stop_loss:
            query_params.append(f"stopLoss={stop_loss}")
        if take_profit:
            query_params.append(f"takeProfit={take_profit}")

        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/order?{query_string}&signature={signature}"

        headers  = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "url": url
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def EditOrder(
        self, 
        order_id: str, 
        symbol: str, 
        side: str, 
        type_: str, 
        quantity: float, 
        price: None|float=None, 
        stop_loss: None|float=None, 
        take_profit: None|float=None
        ):
        """Изменение ордера через POST-запрос к /api/v2/order. 
        side = BUY or SELL; 
        type = MARKET, LIMIT or STOP;
        take_profit цена продажи (напрмер покупка 100, продать, когда цена будет 105);
        leverage размер плеча int;
        """
        timestamp = int(time.time() * 1000)
        query_params = [
            f"orderId={order_id}",
            f"type={type_}",
            f"symbol={self.GetSymbol(symbol)}",
            f"side={side}",
            f"quantity={quantity}",
            f"timestamp={timestamp}",
            f"recvWindow={self.recv_window}",
            f"accountId={self.account_id}"
        ]
        if price:
            query_params.append(f"price={price}")
        if stop_loss:
            query_params.append(f"stopLoss={stop_loss}")
        if take_profit:
            query_params.append(f"takeProfit={take_profit}")

        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/order?{query_string}&signature={signature}"

        headers  = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ExchangeInfo(self):
        """Получение информации об актуальных курсах через GET-запрос к /api/v2/exchangeInfo."""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}&recvWindow={self.recv_window}"
        signature = self._generate_signature(query_string)
        url = f"{self.url}/exchangeInfo?{query_string}&signature={signature}"
      
        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "link": url,
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            } 

    def GetSymbol(self, name: str):
        """Получение информации о символе необходимом для открытия ордера."""
        try:
            response = self.ExchangeInfo()
            symbols_list = response.get("data").get("symbols")
            for element in symbols_list:
                if element.get("name") == name:
                    symbol = element.get("symbol")
                    break
            return symbol
        except Exception as ex:
            return {
                "error": f"HTTP error: {ex}",
            }

    def LeverageOrdersEdit(
        self, 
        order_id: str,
        exp_time: None|str=None, 
        guarant_stop_loss: bool=False, 
        new_price: None|float=None, 
        profit_distance: None|int=None,
        stop_distance: None|int=None,
        stop_loss: None|float=None,
        take_profit: None|float=None, 
        trailing_stop_loss: bool=False,        
        ):
        """Изменение ордера через POST-запрос к /api/v2/updateTradingOrder. 
        take_profit цена продажи (напрмер покупка 100, продать, когда цена будет 105);
        """
        timestamp = int(time.time() * 1000)
        query_params = [
            f"orderId={order_id}",
            f"timestamp={timestamp}",
            f"recvWindow={self.recv_window}",
            f"accountId={self.account_id}"
        ]
        if exp_time:
            query_params.append(f"expireTimestamp={exp_time}")
        if new_price:
            query_params.append(f"newPrice={new_price}")
        if take_profit:
            query_params.append(f"takeProfit={take_profit}")
        if guarant_stop_loss:
            query_params.append(f"guaranteedStopLoss={guarant_stop_loss}")
        if stop_loss:
            query_params.append(f"stopLoss={stop_loss}")
        if profit_distance:
            query_params.append(f"profitDistance={profit_distance}")
        if stop_distance:
            query_params.append(f"stopDistance={stop_distance}")
        if trailing_stop_loss:
            query_params.append(f"trailingStopLoss={trailing_stop_loss}")

        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/updateTradingOrder?{query_string}&signature={signature}"

        headers  = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "url": url
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def LeverageTradeEdit(
        self, 
        position_id: str,
        exp_time: None|str=None, 
        guarant_stop_loss: bool=False, 
        new_price: None|float=None, 
        profit_distance: None|int=None,
        stop_distance: None|int=None,
        stop_loss: None|float=None,
        take_profit: None|float=None, 
        trailing_stop_loss: bool=False,        
        ):
        """Изменение текущей сделки через POST-запрос к /api/v2/updateTradingPosition. 
        take_profit цена продажи (напрмер покупка 100, продать, когда цена будет 105);
        """
        timestamp = int(time.time() * 1000)
        query_params = [
            f"positionId={position_id}",
            f"timestamp={timestamp}",
            f"recvWindow={self.recv_window}",
            f"accountId={self.account_id}"
        ]
        if exp_time:
            query_params.append(f"expireTimestamp={exp_time}")
        if new_price:
            query_params.append(f"newPrice={new_price}")
        if take_profit:
            query_params.append(f"takeProfit={take_profit}")
        if guarant_stop_loss:
            query_params.append(f"guaranteedStopLoss={guarant_stop_loss}")
        if stop_loss:
            query_params.append(f"stopLoss={stop_loss}")
        if profit_distance:
            query_params.append(f"profitDistance={profit_distance}")
        if stop_distance:
            query_params.append(f"stopDistance={stop_distance}")
        if trailing_stop_loss:
            query_params.append(f"trailingStopLoss={trailing_stop_loss}")

        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/updateTradingPosition?{query_string}&signature={signature}"

        headers  = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "url": url
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfCurrencies(self):
        """Получение информации обо всех валютах GET-запрос к /api/v2/currencies."""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}&recvWindow={self.recv_window}"
        signature = self._generate_signature(query_string)
        url = f"{self.url}/currencies?{query_string}&signature={signature}"
      
        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfFees(self, symbol: str):
        """Получение информации обо всех системных сборах GET-запрос к /api/v2/tradingFees.
        symbol можно найти на ExchangeInfo"""
        url = f"{self.url}/tradingFees?symbol={self.GetSymbol(symbol)}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfHistoricalPositions(
        self, 
        from_: None| int = None, 
        symbol: None| str = None, 
        to: None| int = None, 
        limit: None| int = None
        ):
        """Получение информации обо всех закрытых сделках на аккаунте через GET-запрос к /api/v2/tradingPositionsHistory."""
        timestamp = int(time.time() * 1000)
        query_params = [f"timestamp={timestamp}", f"recvWindow={self.recv_window}"]
        if symbol:
            query_params.append(f"symbol={self.GetSymbol(symbol)}")
        if from_:
            query_params.append(f"from={from_}")
        if to:
            query_params.append(f"to={to}")
        if limit:
            query_params.append(f"limit={limit}")
        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/tradingPositionsHistory?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json(),
                "url": url,
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfLeverageTrades(self):
        """Получение информации обо всех открытых сделках на аккаунте через GET-запрос к /api/v2/tradingPositions."""
        timestamp = int(time.time() * 1000)
        query_string = f"timestamp={timestamp}&recvWindow={self.recv_window}"
        signature = self._generate_signature(query_string)
        url = f"{self.url}/account?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfLimits(self, symbol: str):
        """Получение информации обо всех системных ограничениях GET-запрос к /api/v2/tradingLimits.
        symbol можно найти на ExchangeInfo"""
        url = f"{self.url}/tradingLimits?symbol={self.GetSymbol(symbol)}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfOpenOrders(self, symbol: None|str = None):
        """Получение информации обо всех открытых заявках на аккаунте через GET-запрос к /api/v2/openOrders."""
        timestamp = int(time.time() * 1000)
        query_params = [f"timestamp={timestamp}", f"recvWindow={self.recv_window}"]
        if symbol:
            query_params.append(f"symbol={self.GetSymbol(symbol)}")
        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/openOrders?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def ListOfTrades(
        self, 
        symbol: str,
        start_time: None| int = None, 
        end_time: None| int = None,  
        limit: None| int = None
        ):
        """Получение информации обо всех сделках по symbol на аккаунте через GET-запрос к /api/v2/myTrades."""
        timestamp = int(time.time() * 1000)
        query_params = [f"timestamp={timestamp}", f"recvWindow={self.recv_window}", f"symbol={self.GetSymbol(symbol)}"]
        if start_time:
            query_params.append(f"startTime={start_time}")
        if end_time:
            query_params.append(f"endTime={end_time}")
        if limit:
            query_params.append(f"limit={limit}")
        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/myTrades?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def OrderBook(self, symbol: str):
        """Получение информации обо всех заявках на аккаунте через GET-запрос к /api/v2/depth"""
        timestamp = int(time.time() * 1000)
        query_params = [f"timestamp={timestamp}", f"recvWindow={self.recv_window}", f"symbol={self.GetSymbol(symbol)}"]
        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/depth?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }    

    def PriceChange(self, symbol: None|str = None):
        """Получение информации статистике изменения цен за последние 24ч через GET-запрос к /api/v2/ticker/24h"""
        timestamp = int(time.time() * 1000)
        query_params = [f"timestamp={timestamp}", f"recvWindow={self.recv_window}",]
        if symbol:
            query_params.append(f"symbol={self.GetSymbol(symbol)}")
        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/ticker/24hr?{query_string}&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }    

    def ServerTime(self):
        """Тест соединения с сервером и получение севрерного времени/api/v2/time."""
        url = f"{self.url}/time"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверяем, нет ли ошибок HTTP
            return {
                "status_code": response.status_code,
                "data": response.json()
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }

    def TradingPositionClose(self, position_id):
        """Закрытие позиции через запрос к /api/v2/closeTradingPosition"""
        timestamp = int(time.time() * 1000)
        query_params = [
            f"positionId={position_id}",
            f"timestamp={timestamp}",
            f"recvWindow={self.recv_window}",
            f"accountId={self.account_id}"
        ]

        query_string = "&".join(query_params)
        signature = self._generate_signature(query_string)
        url = f"{self.url}/closeTradingPosition?{query_string}&signature={signature}"

        headers  = {"X-MBX-APIKEY": self.api_key}
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            return {
                "status_code": response.status_code,
                "data": response.json(),
            }
        except requests.exceptions.HTTPError as http_err:
            return {
                "status_code": response.status_code,
                "error": f"HTTP error: {http_err}",
                "response_text": response.text
            }
        except requests.exceptions.RequestException as req_err:
            return {
                "status_code": None,
                "error": f"Request failed: {req_err}",
                "response_text": None
            }


trade = Trade(api_key, secret_key)

request = trade.PriceChange(symbol="Gold")
print(request)