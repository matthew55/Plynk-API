from curl_cffi import requests

# okhttp4_android10_ja3 = ",".join(
#     [
#         "771",
#         "4865-4866-4867-49195-49196-52393-49199-49200-52392-49171-49172-156-157-47-53",
#         "0-23-65281-10-11-35-16-5-13-51-45-43-21",
#         "29-23-24",
#         "0",
#     ]
# )
#
# okhttp4_android10_akamai = "4:16777216|16711681|0|m,p,a,s"
#
# extra_fp = {
#     "tls_signature_algorithms": [
#         "ecdsa_secp256r1_sha256",
#         "rsa_pss_rsae_sha256",
#         "rsa_pkcs1_sha256",
#         "ecdsa_secp384r1_sha384",
#         "rsa_pss_rsae_sha384",
#         "rsa_pkcs1_sha384",
#         "rsa_pss_rsae_sha512",
#         "rsa_pkcs1_sha512",
#         "rsa_pkcs1_sha1",
#     ]
#     # other options:
#     # tls_min_version: int = CurlSslVersion.TLSv1_2
#     # tls_grease: bool = False
#     # tls_permute_extensions: bool = False
#     # tls_cert_compression: Literal["zlib", "brotli"] = "brotli"
#     # tls_signature_algorithms: Optional[List[str]] = None
#     # http2_stream_weight: int = 256
#     # http2_stream_exclusive: int = 1
#
#     # See requests/impersonate.py and tests/unittest/test_impersonate.py for more examples
# }
#
#
# session = requests.Session(
#     ja3=okhttp4_android10_ja3, akamai=okhttp4_android10_akamai, extra_fp=extra_fp
# )

session = requests.Session(impersonate="safari_ios")
# session = requests.Session()

# Globals
plynk_accounts = []
username = ""
password = ""


def merge_two_dicts(initial, modifier):
    merged_dictionary = initial.copy()  # start with keys and values of initial
    merged_dictionary.update(modifier)  # modifies merged_dictionary with keys and values of modifier
    return merged_dictionary


def count_fits_into_one(value):
    if value <= 0:
        raise ValueError("The input must be a positive float.")
    return float(1 / value)  # Better to use int() if fractional share weren't needed to be accounted for


def build_headers(headers=None):
    transform_headers = {
        "host": "www.digitalbrokerageservices.com",
        "appid": "AP128920",
        "accept": "application/json",
        "appname": "Simplifid",
        "accept-token-location": "HEADER",
        # "x-acf-sensor-data": "2,i,s+fma3BdJDzJCunpm2Og2Vrfiq5FePjOLVogA60RVJ7f5Qr4JKfGm2ru5AcEDlWrW48xer3Kg8s3Ymb2iZJBCjeBiosvcZDGWN5whG6VclEsD/YANaDaQflYKqe1JS4s/T8+g+4FZm339ufaA/snJ0487QNvNmuZKlaPQ+R6B50=,sXRZF2S+12IKRo7JOZEHzo8P1GnILREEQHVeu2geHXXqup+R2vu/dxtnSMTPWc14wvWghh8LZyFyiWIx5PwmZRNmJpN04LCeE8wqmbZBXG0Lqxqfu+iY+UwmvsY50irUYCTiedYcLh6j9UfDeaVw6tOj18YgL9E2NAqcRaFZCGw=$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$26,13,47$",
        "x-acf-sensor-data": "4,i,qMG9W1OFbObs5300s4c3USRKhJatHNMKfzxKSn2GLJYoGDjzqEmpZelg/6F6Vqo7O6K+c9g6WohHAr/oomyQL9Rhd/qk7xhIiCOXFGTT5WPIy3OVdSzLOgO5mTv3BkgXZ/JG6KMD0opGB/7IpYaG+lDCF2vZW486ASbJXfqEyH0=,GxzDvgnmfXikqi6fkl7Xcsy7wtOOVV4dGmvAc/TG0xGyvcCFVOXXSBZgsZxyhiz0xA7C0yKRv011fnpETUfIoCvd2bSnNHITi86Rd/ojNt9CMidFEEAD7vwOtc67CdB1SaRnn4IjBPwrc4qXWEFsFrxTWpiDkGu0M5gWLOAIbB8=$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$28,17,51",
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
                security_count = position['securityCount']
                print(f"Security Symbol: {security_symbol}, Holdings {security_count}, Current Value: {current_value}")


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
    # Buy
    # for stock in ["uavs", "agba", "ncnc", "dlpn", "mgrx", "stss", "me"]:
    #     try:
    #         transaction_price(stock, "BUY", 1)
    #         price = get_stock_market_price(stock)
    #         print(f"Price of {stock}: {price}")
    #         fits_into_one = count_fits_into_one(float(price))
    #         print(f"Fits_into_one: {fits_into_one}")
    #         amount_to_sell = fits_into_one - 1
    #         print(f"Amount to sell: {amount_to_sell}")
    #         if not amount_to_sell <= 0:
    #             transaction_quantity(stock, "SELL", amount_to_sell)
    #     except Exception as e:
    #         print(f"Error during trading loop: {e}")
    #         continue

    # Sell
    # for stock in ["KWE"]:
    #     try:
    #         transaction_quantity(stock, "SELL", 1)
    #     except Exception as e:
    #         print(f"Error during trading loop: {e}")
    #     continue


if __name__ == '__main__':
    main()
