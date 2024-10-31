# 💸 Plynk API 💸

<img src="https://github.com/user-attachments/assets/10817d69-fc8d-4251-b941-4b75243214e7" alt="cool dude" width="1000" height="500"/>

This is an *unofficial* API for Plynk. It is a simple Python wrapper around the Plynk backend API. **It is not affiliated with Plynk in any way**.

## Installation 🍇

```bash
pip install 'plynk-api'
```

## Logging In 🍅

```python
from plynk_api import Plynk

plynk = Plynk(
    username="USERNAME",
    password="PASSWORD",
    filename="plynk-creds.pkl",
    path="creds", 
    proxy_url=None,  # Takes "URL:PORT"
    proxy_auth=None # Takes ("USERNAME", "PASSWORD")
)
try:
    plynk.login()
except RuntimeError as e:
    print(f"Failed to login to Plynk: {e}")
```

## Get Account Number 🥑

```python
try:
    account_number = plynk.get_account_number()
    print(account_number)
except RuntimeError as e:
    print(f"Failed to get Plynk account number: {e}")
```

## Get Stock Holdings 🥭

```python
try:
    holdings = plynk.get_stock_holdings(account_number=account_number)
    for holding in holdings:
        stock_symbol = holding['security']['symbol']
        current_value = holding['currentValue']
        holding_quantity = holding['securityCount']
        print(f"Stock Symbol: {stock_symbol}, Quantity {holding_quantity}, Current Value: {current_value}")
except RuntimeError as e:
    print(f"Failed to get Plynk holdings: {e}")
```

## Placing Orders 🍉

There are two ways to place an order in Plynk, specifying a dollar amount to buy/sell, or specifying a quantity to buy/sell.

When buying stocks under $1 price, the user is required to specify a dollar amount instead of specifying a quantity.

### Placing orders by price 🥝
```python
try: 
    order = plynk.place_order_price(
        account_number=account_number, 
        ticker="AAPL", 
        quantity=350.50,  # Buy $350.50 worth of AAPL
        side="buy",  # Must be "buy" or "sell"
        price="market",  # Only market orders are supported for now
        dry_run=False # If True, will not actually place the order
    )
    print(order)
except RuntimeError as e:
    print(f"Failed to place price order: {e}")
```

### Placing orders by quantity 🥕
```python
try:
    order = plynk.place_order_quantity(
        account_number=account_number, 
        ticker="AAPL", 
        quantity=2,  # Sell 2 shares worth of AAPL
        side="sell",  # Must be "buy" or "sell"
        price="market",  # Only market orders are supported for now
        dry_run=False # If True, will not actually place the order
    )
    print(order)
except RuntimeError as e:
    print(f"Failed to place quantity order: {e}")
```

## Contributing  🌶️
Found or fixed a bug? Have a feature request? Feel free to open an issue or pull request!

Enjoying the project? Feel free to Sponsor me on GitHub or Buy Me a Coffee!

[![Sponsor](https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=GitHub-Sponsors&logoColor=#white)](https://github.com/sponsors/matthew55)
[![Buy Me A Coffee](https://img.shields.io/badge/buy%20me%20a%20coffee-30363D?style=for-the-badge&logo=buy-me-a-coffee&logoColor=ff4aaa)](https://buymeacoffee.com/matthew55)

[//]: # ([![Buy Me A Coffee]&#40;https://img.shields.io/badge/sponsor-30363D?style=for-the-badge&logo=buy-me-a-coffee&logoColor=fuchsia&#41;]&#40;https://buymeacoffee.com/matthew55&#41;)

## DISCLAIMER 🍆
DISCLAIMER: I am not a financial advisor and not affiliated with Plynk. Use this tool at your own risk. I am not responsible for any losses or damages you may incur by using this project. This tool is provided as-is with no warranty.
