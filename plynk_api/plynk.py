import json
import os
import pickle
import pytz

from datetime import datetime
from curl_cffi import requests
from typing import Optional, Callable

from plynk_api import endpoints


def check_login(func):
    """
    Decorator that ensures that the client is logged in before executing the targeted function.

    :param func: The function targeted by the decorator.
    :return: The nested wrapper function.
    """
    def wrapper(self, *args, **kwargs):
        if self.logged_in is False:
            raise RuntimeError("Plynk not logged in. Please login first.")
        return func(self, *args, **kwargs)

    return wrapper


class Plynk:
    def __init__(self, username: str, password: str, filename: str = "plynk_credentials.pkl", path: Optional[str] = None, proxy_url: Optional[str] = None, proxy_auth: Optional[tuple[str, str]] = None) -> None:
        """
        Builder for Plynk API. Provides support for cookie locations as well as proxy support.

        :param username: Plynk username.
        :param password: Plynk password.
        :param filename: Cookie filename.
        :param path: Path cookie file will be saved in. Default is current directory.
        :param proxy_url: String of "PROXY_URL:PROXY_PORT"
        :param proxy_auth: Tuple of (PROXY_USERNAME, PASSWORD)
        """
        self.username: str = username
        self.password: str = password
        self.filename: str = filename
        self.path: Optional[str] = path
        self.proxy_url: Optional[str] = proxy_url
        self.proxy_auth: Optional[tuple[str, str]] = proxy_auth
        self._set_session(proxy_url, proxy_auth)
        self.account_number: Optional[str] = None
        self.logged_in: bool = False

        self._load_credentials()

    def _set_session(self, proxy_url: str, proxy_auth: Optional[tuple[str, str]] = None) -> None:
        """
        Sets the request session and handles the proxy.

        :param proxy_url: String of "PROXY_URL:PROXY_PORT"
        :param proxy_auth: Tuple of (PROXY_USERNAME, PASSWORD)
        :return: None.
        """
        if proxy_url is not None and proxy_auth is not None:
            self.session: requests.Session = requests.Session(impersonate="safari_ios", proxy=proxy_url, proxy_auth=proxy_auth, timeout=10)
        elif proxy_url is not None:
            self.session: requests.Session = requests.Session(impersonate="safari_ios", proxy=proxy_url, timeout=10)
        else:
            self.session: requests.Session = requests.Session(impersonate="safari_ios", timeout=10)

    def _load_credentials(self) -> None:
        """
        Attempts to load the previously saved session cookies from the specified cookie file and path.

        :return: None.
        """
        filename = self.filename
        if self.path is not None:
            filename = os.path.join(self.path, filename)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                credentials = pickle.load(f)
            # noinspection PyProtectedMember
            self.session.cookies.jar._cookies.update(credentials)

    def _save_credentials(self) -> None:
        """
        Saves the current session cookies to the specified cookie file and path.

        :return: None.
        """
        filename = self.filename
        if self.path is not None:
            filename = os.path.join(self.path, filename)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        with open(filename, "wb") as f:
            # noinspection PyTypeChecker,PyProtectedMember
            pickle.dump(self.session.cookies.jar._cookies, f)

    def _clear_credentials(self) -> None:
        """
        Clears the session cookies and removes the existing cookie file.

        :return: None.
        """
        filename = self.filename
        if self.path is not None:
            filename = os.path.join(self.path, filename)
            if not os.path.exists(self.path):
                os.makedirs(self.path)
        if os.path.exists(filename):
            os.remove(filename)
        # # noinspection PyProtectedMember
        # self.session.cookies.jar._cookies.clear()
        self._set_session(self.proxy_url, self.proxy_auth)  # The code above causes authentication issues for whatever reason, so we use this.
        self.logged_in = False

    def login(self, otp_callback: Optional[Callable[[], str]] = None) -> bool:
        """
        This handles authenticating the user's session.
        This will throw a RuntimeError when authenticating fails.

        :param otp_callback: A custom function that returns a string that the user can specify to get SMS OTP codes.
        :return: Whether the login completed successfully.
        """
        # If creds exist, check if they are valid/try to refresh
        if self._verify_login():
            self.logged_in = True
            return True

        # Make authentication request
        response = self._authenticate()

        if "messages" in response:
            message = response["messages"]["messageList"][0]["messageContent"]
            if message == "Authentication Not Completed":
                self._authenticate(True, otp_callback)

        self.account_number = self._fetch_account_number()
        self.logged_in = True
        self._save_credentials()
        return True

    def _authenticate(self, otp: bool = False, otp_callback: Optional[Callable[[], str]] = None) -> dict:
        """
        This handles authentication with Plynk. It can handle OTP passcode authentication when requested too.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param otp: Whether to attempt OTP authentication.
        :param otp_callback: A custom function that returns a string that the user can specify to get SMS OTP codes.
        :return: Dict of login request.
        """
        if otp:
            self._request_sms_code()
            otp = otp_callback() if otp_callback else input("Please enter the OTP you received: ")
            payload = {
                "securityCode": otp
            }
        else:
            payload = {
                "username": f"{self.username}",
                "requestBaseInfo": None,
                "password": f"{self.password}"
            }
        response = self.session.post(endpoints.authentication_url(), json=payload, headers=endpoints.build_headers(ecaap=True))
        if response.status_code != 200:
            raise RuntimeError(
                f"Authentication request failed with status code {response.status_code}: {response.text}")
        payload = {}  # Yes this is required, I don't know why.
        response = self.session.post(endpoints.login_url(), json=payload, headers=endpoints.build_headers(ecaap=True))
        if response.status_code != 200:
            raise RuntimeError(f"Login request failed with status code {response.status_code}: {response.text}")
        return response.json()

    def _fetch_phone_number(self) -> str:
        """
        Fetches the last 4 digits of the user's, as specified in the credentials, phone number.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :return: The last for digits of the user's phone number.
        """
        response = self.session.get(endpoints.phone_url(), headers=endpoints.build_headers(ecaap=True))
        if response.status_code != 200:
            raise RuntimeError(f"Phone number request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "phone" in response:
            for phone in response["phone"]:
                # Make sure the phone number is active before returning it.
                value = phone["value"]
                try:
                    enabled = bool(phone["enabled"])
                except KeyError | TypeError:
                    raise RuntimeError("Unable to get bool value of enabled")
                if enabled:
                    return value
                raise RuntimeError("Unable to get phone number")
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched phone number missing information! Message from server: {message}")


    def _request_sms_code(self) -> dict:
        """
        Requests Plynk send an SMS code to the user.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :return: Dict of SMS code request.
        """

        # Get the last four digits of the user's phone number.
        phone_last_four = self._fetch_phone_number()

        payload = {
            "template": "Plynk: Your code is $$CODE$$. It expires in 30 minutes. Thank you.",
            "phone": phone_last_four
        }
        response = self.session.post(endpoints.authentication_url(), json=payload, headers=endpoints.build_headers(ecaap=True))
        if response.status_code != 200:
            raise RuntimeError(f"SMS code request failed with status code {response.status_code}: {response.text}")
        if "messages" not in response:
            raise RuntimeError(f"Fetched SMS code message missing information!")
        return response.json()

    def _fetch_account_number(self) -> str:
        """
        Fetches the user's, as specified in the credentials, account number.
        Login is not required for this function because this is used to determine if the user is logged in.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :return: The user's account number.
        """
        response = self.session.get(endpoints.account_url(), headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Account number request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "accounts" in response:
            account_number = response["accounts"][0]["accountNumber"]
            if not account_number:
                raise RuntimeError("Unable to get account number")
            return account_number
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched account number missing information! Message from server: {message}")

    def _verify_login(self) -> bool:
        """
        Test login by attempting to request Account IDs

        :return: Whether account info fetched successfully.
        """
        # noinspection PyBroadException
        try:
            self._fetch_account_number()
            return True
        except Exception:
            self._clear_credentials()
            return False

    @check_login
    def get_account_number(self) -> str:
        """
        Returns the user's account number if it is already cached, otherwise fetches it.
        This will throw a RuntimeError when fetching the account number fails.

        :return: The user's account number.
        """
        return self.account_number if self.account_number is not None else self._fetch_account_number()

    @check_login
    def get_positions(self, account_number: str) -> dict:
        """
        This fetches the user' user's positions info.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param account_number: The user's account number.
        :return: A dict of the user's positions info.
        """
        payload = {"accounts": [
            {
                "accountNumber": f"{account_number}",
                "registrationType": "I"
            }
        ]}
        response = self.session.post(endpoints.positions_url(), json=payload, headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Positions request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "accounts" in response:
            return response
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched holdings details missing information! Message from server: {message}")

    @check_login
    def get_account_holdings(self, account_number: str) -> dict:
        """
        Fetches the positions of the user.
        This will throw a RuntimeError when fetching account positions fails.

        :param account_number: The user's account number.
        :return: A list of the holdings in the user's account.
        """
        result = self.get_positions(account_number)
        return result["accounts"][0]["positionsSummary"]["positions"]

    @check_login
    def get_account_total(self, account_number: str) -> float:
        """
        Obtains the total value of the user's portfolio
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param account_number: The user's account number.
        :return: A float value of the total value of the user's portfolio.
        """
        payload = {"accounts": [
            {
                "accountNumber": f"{account_number}",
                "registrationType": "I"
            }
        ]}
        response = self.session.post(endpoints.balance_url(), json=payload, headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Account total request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "accounts" in response:
            try:
                return float(response["accounts"][0]["balanceSummary"]["totalAssets"])
            except Exception as e:
                raise RuntimeError(f"Unable parse float account total value: {e}")
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched account total details missing information! Message from server: {message}")


    @check_login
    def is_stock_market_open(self) -> bool:
        """
        Returns whether the stock market is currently open.

        :return: Bool of whether the stock market is currently open.
        """

        # Get current time in EST for the format
        eastern = pytz.timezone('US/Eastern')
        eastern_time = datetime.now(eastern)
        formatted_time = eastern_time.strftime('%Y-%m-%dT%H:%M:%S')
        fid_fbt_application_data_header = {"FID-FBT-APPLICATION-DATA": json.dumps({"calendarDateTime": formatted_time, "timezone": "ET", "countryCode": "US", "businessPartyCode": None, "isBankIndicator": None, "isIgnoreTime": None, "offsetDays": 6})}

        response = self.session.get(endpoints.market_open_url(), headers=endpoints.build_headers(headers=fid_fbt_application_data_header))
        if response.status_code != 200:
            raise RuntimeError(f"Is stock market open request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "businessDates" in response:
            try:
                return bool(response["businessDates"][0]["isOpen"])
            except Exception as e:
                raise RuntimeError(f"Unable parse boolean is market open value: {e}")
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched market open details missing information! Message from server: {message}")


    @check_login
    def get_stock_details(self, ticker: str) -> dict:
        """
        Fetches a dictionary object of stock details.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param ticker: Ticker of the stock
        :return: Dictionary object of stock details
        """
        querystring = {
            "quoteType": "R",
            "symbol": f"{ticker}",
            "proIndicator": "N",
            "contextLevel": "2"
        }
        response = self.session.get(endpoints.stock_details_url(), headers=endpoints.build_headers(), params=querystring)
        if response.status_code != 200:
            raise RuntimeError(f"Stock details request failed with status code {response.status_code}: {response.text}")
        return response.json()

    @check_login
    def get_stock_search(self, query:  str, exact: bool = False) -> dict:
        """
        Searches for a stock based off inputted text.

        :param query: The input to search. If exact=True, query MUST be a valid security ticker.
        :param exact: This will return an exact match of your ticker otherwise throw an error.
        :return: A dictionary containing a list of the search results for the stock.
        """
        response = self.session.get(endpoints.stock_search_url(query), headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Stock search request failed with status code {response.status_code}: {response.text}")

        response = response.json()

        if not exact:
            return response

        if "securities" in response:
            for stock in response["securities"]:
                if query.upper() == stock["symbol"]:
                    return stock
            raise RuntimeError(f"Unable to find exact match for ticker: {query}")
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched stock search missing information! Message from server: {message}")

    @check_login
    def is_stock_tradable(self, ticker: str) -> bool:
        """
        Return whether a stock is a tradable
        This will throw a RuntimeError when fetching the companies' details fails.

        :param ticker: Ticker of the stock
        :return: Whether the stock is tradable
        """

        search_results = self.get_stock_search(query=ticker, exact=True)
        try:
            return bool(search_results["tradable"])
        except Exception as e:
            raise RuntimeError(f"Unable parse boolean tradable value: {e}")

    @check_login
    def get_stock_price(self, ticker: str) -> float:
        """
        Returns the last price of a stock
        This will throw a RuntimeError when fetching the companies' details fails.

        :param ticker: Ticker of the stock
        :return: Last price of the stock
        """
        response = self.get_stock_details(ticker)
        if "security" in response:
            try:
                return float(response["securityDetails"]["lastPrice"])
            except Exception as e:
                raise RuntimeError(f"Unable to get float value fo stock price: {e}")
        else:
            message = "Message not found"
            if "messages" in response:
                message = response["messages"]["messageList"][0]["messageContent"]
            raise RuntimeError(f"Fetched securities details missing information! Message from server: {message}")

    @check_login
    def get_stock_logo(self, ticker: str) -> Optional[str]:
        """
        Returns the URL to the logo of a stock. It is possible for the URL to be None meaning there is no logo.
        This will throw a RuntimeError when fetching the companies' details fails.

        :param ticker: Ticker of the stock
        :return: URL to the logo of the stock
        """
        search_result = self.get_stock_search(query=ticker, exact=True)
        try:
            return search_result["logo"]
        except Exception as e:
            raise RuntimeError(f"Unable parse logo URL: {e}")


    @check_login
    def place_order_price(self, account_number: str, ticker: str, quantity: float, side: str, price: str = "market", dry_run: bool = False) -> dict:
        """
        This uses a dollar amount in the quantity to place a trade worth the specified amount of dollars.
        This will order fractional shares to ensure the exact amount of the quantity specified is ordered.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param account_number: Account number.
        :param ticker: The ticker of the stock.
        :param quantity: The dollar amount for the trade.
        :param side: buy or sell.
        :param price: Market or the price you would like to buy at.
        :param dry_run: Returns a sample dictionary with the information provided.
        :return: Either a sample dictionary if dry_run specified, or the dictionary of the order response.
        """
        if side.upper() not in ["BUY", "SELL"]:
            raise RuntimeError("Side must be either 'BUY' or 'SELL'")

        # Check if market is open
        market_open = self.is_stock_market_open()
        if not market_open:
            raise RuntimeError(f"Stock market is not open")

        # Check if stock is tradable
        can_trade = self.is_stock_tradable(ticker)
        if not can_trade:
            raise RuntimeError(f"Stock {ticker} is not tradable")

        if dry_run:
            return {
                "account_id": account_number,
                "ticker": ticker,
                "quantity": quantity,
                "side": side,
                "price": price,
                "dry_run_success": True,
            }

        # This buy a stock based off dollar amount quantity specified.
        payload = {
            "account": {
                "accountNumber": f"{account_number}",
                "accountType": "CASH"
            },
            "orderCondition": {"orderType": "MARKET"},
            "intermediary": {"branchOfficeNumber": "D4K"},
            "typeOfOrder": "EQUITY_REQUEST",
            "order": {
                "orderOrigin": "YE",
                "quantityType": "DOLLARS",
                "orderAction": f"{side.upper()}",
                "preview": False,
                "timeInForce": "DAY",
                "quantity": f"{float(quantity):.2f}"
            },
            "security": {
                "securityIdentifierType": "SYMBOL",
                "securityIdentifier": f"{ticker.upper()}"
            }
        }
        response = self.session.post(endpoints.place_order_url(), json=payload, headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Order Request failed with status code {response.status_code}: {response.text}")
        return response.json()

    @check_login
    def place_order_quantity(self, account_number: str, ticker: str, quantity: float, side: str, price: str | float = "market", dry_run: bool = False) -> dict:
        """
        This uses a numerical quantity to place a trade.
        This will not work for stock's under $1 price.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param account_number: Account number.
        :param ticker: The ticker of the stock.
        :param quantity: The dollar amount for the trade.
        :param side: buy or sell.
        :param price: Market or the price you would like to buy at.
        :param dry_run: Returns a sample dictionary with the information provided.
        :return: Either a sample dictionary if dry_run specified, or the dictionary of the order response.
        """
        if side.upper() not in ["BUY", "SELL"]:
            raise RuntimeError("Side must be either 'BUY' or 'SELL'")

        # Check if market is open
        market_open = self.is_stock_market_open()
        if not market_open:
            raise RuntimeError(f"Stock market is not open")

        # Check if stock is tradable
        can_trade = self.is_stock_tradable(ticker)
        if not can_trade:
            raise RuntimeError(f"Stock {ticker} is not tradable")

        stock_price = self.get_stock_price(ticker)
        if stock_price < 1:
            raise RuntimeError(f"Stock {ticker}'s is under $1. You must use price quantities for stock's priced under $1")

        if dry_run:
            return {
                "account_id": account_number,
                "ticker": ticker,
                "quantity": quantity,
                "side": side,
                "price": price,
                "dry_run_success": True,
            }

        # This buy a stock based off dollar amount quantity specified.
        payload = {
            "account": {
                "accountNumber": f"{account_number}",
                "accountType": "CASH"
            },
            "orderCondition": {"orderType": "MARKET"},
            "intermediary": {"branchOfficeNumber": "D4K"},
            "typeOfOrder": "EQUITY_REQUEST",
            "order": {
                "orderOrigin": "YE",
                "quantityType": "SHARES",
                "orderAction": f"{side.upper()}",
                "preview": False,
                "timeInForce": "DAY",
                "quantity": f"{float(quantity):.2f}"
            },
            "security": {
                "securityIdentifierType": "SYMBOL",
                "securityIdentifier": f"{ticker.upper()}"
            }
        }
        response = self.session.post(endpoints.place_order_url(), json=payload, headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Order Request failed with status code {response.status_code}: {response.text}")
        return response.json()
