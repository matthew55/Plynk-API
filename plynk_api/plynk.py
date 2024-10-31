import os
import pickle
from curl_cffi import requests
from typing import Optional

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
        self.path = path
        self.proxy_url = proxy_url
        self.proxy_auth = proxy_auth
        self._set_session(proxy_url, proxy_auth)
        self.account_number: Optional[str] = None
        self.logged_in = False

        self._load_credentials()

    def _set_session(self, proxy_url: str, proxy_auth: Optional[tuple[str, str]] = None) -> None:
        """
        Sets the request session and handles the proxy.

        :param proxy_url: String of "PROXY_URL:PROXY_PORT"
        :param proxy_auth: Tuple of (PROXY_USERNAME, PASSWORD)
        :return: None
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

        :return: None
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

        :return: None
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

        :return: None
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

    def login(self) -> bool:
        """
        This handles authenticating the user's session.
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :return: Whether the login completed successfully.
        """
        # If creds exist, check if they are valid/try to refresh
        if self._verify_login():
            self.logged_in = True
            return True

        # Make initial authentication request
        payload = {
            "username": f"{self.username}",
            "requestBaseInfo": None,
            "password": f"{self.password}"
        }
        response = self.session.post(endpoints.authentication_url(), headers=endpoints.build_headers(ecaap=True), json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Authentication request failed with status code {response.status_code}: {response.text}")

        # Make login request
        payload = {}  # Yes this is required, I don't know why.
        response = self.session.post(endpoints.login_url(), json=payload, headers=endpoints.build_headers(ecaap=True))
        if response.status_code != 200:
            raise RuntimeError(f"Login request failed with status code {response.status_code}: {response.text}")

        self._save_credentials()
        self.account_number = self._fetch_account_number()
        self.logged_in = True
        return True

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

    def _fetch_account_number(self) -> str:
        """
        Fetches the user's, as specified in the credentials, account number.
        Login is not required for this function because this is used to determine if the user is logged in.

        :return: The user's account number.
        """
        account_number = None
        response = self.session.get(endpoints.account_url(), headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Account number request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "accounts" in response:
            account_number = response["accounts"][0]["accountNumber"]
        if not account_number:
            raise RuntimeError("Unable to get account number")
        return account_number

    @check_login
    def get_account_number(self) -> str:
        """
        Returns the user's account number if it is already cached, otherwise fetches it.

        :return: The user's account number.
        """
        return self.account_number if self.account_number is not None else self._fetch_account_number()

    @check_login
    def get_stock_holdings(self, account_number: str) -> dict:
        payload = {"accounts": [
            {
                "accountNumber": f"{account_number}",
                "registrationType": "I"
            }
        ]}
        response = self.session.post(endpoints.positions_url(), json=payload, headers=endpoints.build_headers())
        if response.status_code != 200:
            raise RuntimeError(f"Holdings request failed with status code {response.status_code}: {response.text}")
        response = response.json()
        if "accounts" not in response:
            raise RuntimeError("Fetched holdings details missing information")
        return response['accounts'][0]['positionsSummary']['positions']

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
            raise RuntimeError(f"Securities details request failed with status code {response.status_code}: {response.text}")
        return response.json()

    @check_login
    def is_stock_tradable(self, ticker: str) -> bool:
        """
        Return whether a stock is a tradable
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param ticker: Ticker of the stock
        :return: Whether the stock is tradable
        """
        details = self.get_stock_details(ticker)
        if "security" in details:
            # TODO: Look into this. Is this important? Also typo or not?
            return bool(details["security"]["tradable"])  # Can be None which means False
        else:
            raise RuntimeError("Fetched securities details missing information")

    @check_login
    def get_stock_price(self, ticker: str) -> float:
        """
        Returns the last price of a stock
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param ticker: Ticker of the stock
        :return: Last price of the stock
        """
        details = self.get_stock_details(ticker)
        if "security" in details:
            try:
                return float(details["security"]["lastPrice"])
            except Exception as e:
                raise RuntimeError(f"Unable to get float value fo stock price: {e}")
        else:
            raise RuntimeError("Fetched securities details missing information")

    @check_login
    def get_stock_logo(self, ticker: str) -> str:
        """
        Returns the URL to the logo of a stock
        When unsuccessful, this will throw a RuntimeError with details elaborating what failed.

        :param ticker: Ticker of the stock
        :return: URL to the logo of the stock
        """
        details = self.get_stock_details(ticker)
        if "security" not in details:
            raise RuntimeError("Fetched stock details missing information")
        return details["security"]["logo"]

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
