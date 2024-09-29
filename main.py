from curl_cffi import requests
# import requests

session = requests.Session(impersonate="safari_ios")
# session = requests.Session()

# Globals
plynk_accounts = []
username = ""
password = ""


def merge_two_dicts(initial, modifier):
    merged_dictionary = initial.copy()   # start with keys and values of initial
    merged_dictionary.update(modifier)    # modifies merged_dictionary with keys and values of modifier
    return merged_dictionary


def build_headers(headers=None):
    transform_headers = {
        "host": "www.digitalbrokerageservices.com",
        "appid": "AP128920",
        "accept": "application/json",
        "appname": "Simplifid",
        "accept-token-location": "HEADER",
        "x-acf-sensor-data": "2,i,s+fma3BdJDzJCunpm2Og2Vrfiq5FePjOLVogA60RVJ7f5Qr4JKfGm2ru5AcEDlWrW48xer3Kg8s3Ymb2iZJBCjeBiosvcZDGWN5whG6VclEsD/YANaDaQflYKqe1JS4s/T8+g+4FZm339ufaA/snJ0487QNvNmuZKlaPQ+R6B50=,sXRZF2S+12IKRo7JOZEHzo8P1GnILREEQHVeu2geHXXqup+R2vu/dxtnSMTPWc14wvWghh8LZyFyiWIx5PwmZRNmJpN04LCeE8wqmbZBXG0Lqxqfu+iY+UwmvsY50irUYCTiedYcLh6j9UfDeaVw6tOj18YgL9E2NAqcRaFZCGw=$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$26,13,47$",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "user-agent": "Plynk/7803 CFNetwork/1335.0.3.4 Darwin/21.6.0",
        # "fsreqid": "475be22356481862a95e87152c89",
        "connection": "keep-alive",
        "token-location": "HEADER",
        "accept-token-type": "ET",
        # "cookie": "MC=43_vpu4RwGEZxls7oimwoFwrAC0SAmb0qpGc5GjynjjW4j7uqjMGBAAKADIGBWb473UABgkAAAABBwoABQUFABMN7mZxCFIKiDDbIAACiQABqjMDEYALG2RmLmNoZi5yYQIcAAAAAAAAAyYBAyoHAAAAAAAAP03"
    }
    if headers:
        transform_headers = merge_two_dicts(transform_headers, headers)
    return transform_headers


def login():
    url = "https://ecaap.digitalbrokerageservices.com/user/factor/password/authentication"
    payload = {
        "username": f"{username}",
        "requestBaseInfo": None,
        "password": f"{password}"
    }
    headers = build_headers({"host": "ecaap.digitalbrokerageservices.com"})
    response = session.post(url, json=payload, headers=headers)
    print(response.text)

    url = "https://ecaap.digitalbrokerageservices.com/user/session/login"
    payload = {}
    headers = build_headers({"host": "ecaap.digitalbrokerageservices.com"})
    # headers = build_headers({"eventtype": "LOGIN", "session_ctx": "c1be59629cf642f78e2ea258fca1c96f", "sub_eventtype": "login_analyze"})
    # "x-acf-sensor-data": "2,i,s+fma3BdJDzJCunpm2Og2Vrfiq5FePjOLVogA60RVJ7f5Qr4JKfGm2ru5AcEDlWrW48xer3Kg8s3Ymb2iZJBCjeBiosvcZDGWN5whG6VclEsD/YANaDaQflYKqe1JS4s/T8+g+4FZm339ufaA/snJ0487QNvNmuZKlaPQ+R6B50=,sXRZF2S+12IKRo7JOZEHzo8P1GnILREEQHVeu2geHXXqup+R2vu/dxtnSMTPWc14wvWghh8LZyFyiWIx5PwmZRNmJpN04LCeE8wqmbZBXG0Lqxqfu+iY+UwmvsY50irUYCTiedYcLh6j9UfDeaVw6tOj18YgL9E2NAqcRaFZCGw=$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$48,7,28$$",
    response = session.post(url, json=payload, headers=headers)
    print(response.text)


# https://www.digitalbrokerageservices.com/gateway/restrict/portfolio/v1/accounts/balance # Might be important for getting cash allocations
def holdings():
    url = "https://www.digitalbrokerageservices.com/gateway/restrict/portfolio/v1/customer/accounts"
    # "dbs-log-parameters": "{\"deviceId\":\"AC6180F0-8EB2-4863-AC97-6665136D4046\"}",
    account_number = None
    response = session.get(url, headers=build_headers()).json()
    if "accounts" in response:
        account_number = response["accounts"][0]["accountNumber"]
    if not account_number:
        raise Exception("Unable to get account number")
    plynk_accounts.append(account_number)

    url = "https://www.digitalbrokerageservices.com/gateway/restrict/portfolio/v1/accounts/positions"
    payload = {"accounts": [
        {
            "accountNumber": f"{account_number}",
            "registrationType": "I"
        }
    ]}
    response = session.post(url, json=payload, headers=build_headers()).json()
    if "accounts" in response:
        for account in response['accounts']:
            positions = account['positionsSummary']['positions']
            for position in positions:
                security_symbol = position['security']['symbol']
                current_value = position['currentValue']
                print(f"Security Symbol: {security_symbol}, Current Value: {current_value}")


# This can be used to get the price of stocks, so you can sell any extra shares you maybe needed to buy in order to
# fulfill the $1 minimum order requirement.
def get_stock_market_price(ticker):
    url = "https://www.digitalbrokerageservices.com/gateway/restrict/market-data/v2/securities/details"
    querystring = {
        "quoteType": "R",
        "symbol": f"{ticker}",
        "proIndicator": "N",
        "contextLevel": "2"
    }
    response = session.get(url, headers=build_headers(), params=querystring).json()
    if "security" in response:
        # TODO: Look into this. Is this important?
        tradable = response["security"]["tradable"]
        # I am just pulling this one for fun. It might be fun to send to this Discord for the memes.
        logo = response["security"]["logo"]
        price = response["securityDetails"]["lastPrice"]
        print(f"{ticker} price: {price}")
        return price

    return None


def transaction_price(ticker, action, quantity):
    action = action.upper()
    plynk_account = plynk_accounts[0]
    quantity_formatted = f"{float(quantity):.2f}"
    if action != "BUY" and action != "SELL":
        raise Exception("Invalid transaction! Please use BUY or SELL")

    url = "https://www.digitalbrokerageservices.com/gateway/restrict/brokerage-order-entry/v5/accounts/orders/equities"
    # This buys it based off a quantity
    payload = {
        "account": {
            "accountNumber": f"{plynk_account}",
            "accountType": "CASH"
        },
        "orderCondition": {"orderType": "MARKET"},
        "intermediary": {"branchOfficeNumber": "D4K"},
        "typeOfOrder": "EQUITY_REQUEST",
        "order": {
            "orderOrigin": "YE",
            "quantityType": "DOLLARS",
            "orderAction": f"{action}",
            "preview": False,
            "timeInForce": "DAY",
            "quantity": f"{quantity_formatted}"
        },
        "security": {
            "securityIdentifierType": "SYMBOL",
            "securityIdentifier": f"{ticker.upper()}"
        }
    }
    response = session.post(url, json=payload, headers=build_headers()).json()
    if "messages" in response:
        if response["messages"]["status"] == "FAILURE":
            message_list = response["messages"]["messageList"]
            error_message = message_list[len(message_list) - 1]["messageContent"]
            raise Exception(f"Error: Unable to {action} {quantity} {ticker}: {error_message}")
        print(f"Successfully {action} {quantity} {ticker}")


def transaction_quantity(ticker, action, quantity):
    #
    action = action.upper()
    plynk_account = plynk_accounts[0]
    quantity_formatted = f"{float(quantity):.3f}"
    if action != "BUY" and action != "SELL":
        raise Exception("Invalid transaction! Please use BUY or SELL")

    url = "https://www.digitalbrokerageservices.com/gateway/restrict/brokerage-order-entry/v5/accounts/orders/equities"
    # This buys it based off a quantity
    payload = {
        "account": {
            "accountNumber": f"{plynk_account}",
            "accountType": "CASH"
        },
        "orderCondition": {"orderType": "MARKET"},
        "intermediary": {"branchOfficeNumber": "D4K"},
        "typeOfOrder": "EQUITY_REQUEST",
        "order": {
            "orderOrigin": "YE",
            "quantityType": "SHARES",
            "orderAction": f"{action}",
            "preview": False,
            "timeInForce": "DAY",
            "quantity": f"{quantity_formatted}"
        },
        "security": {
            "securityIdentifierType": "SYMBOL",
            "securityIdentifier": f"{ticker.upper()}"
        }
    }
    response = session.post(url, json=payload, headers=build_headers()).json()
    if "messages" in response:
        if response["messages"]["status"] == "FAILURE":
            message_list = response["messages"]["messageList"]
            error_message = message_list[len(message_list) - 1]["messageContent"]
            raise Exception(f"Error: Unable to {action} {quantity} {ticker}: {error_message}")
        else:
            print(f"Successfully {action} {quantity} {ticker}")


def main():
    login()
    holdings()
    # transaction_price("CNET", "SELL", 1)
    # get_stock_market_price("CNET")
    transaction_quantity("CNET", "BUY", 1)


if __name__ == '__main__':
    main()
