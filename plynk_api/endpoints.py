""" All the URLs we will use to interact with Plynk """


def digital_url() -> str:
    return "https://www.digitalbrokerageservices.com"


def ecaap_url() -> str:
    return "https://ecaap.digitalbrokerageservices.com"


def authentication_url() -> str:
    return f"{ecaap_url()}/user/factor/password/authentication"


def login_url() -> str:
    return f"{ecaap_url()}/user/session/login"


def account_url() -> str:
    return f"{digital_url()}/gateway/restrict/portfolio/v1/customer/accounts"


def positions_url() -> str:
    return f"{digital_url()}/gateway/restrict/portfolio/v1/accounts/positions"


def stock_details_url() -> str:
    return f"{digital_url()}/gateway/restrict/market-data/v2/securities/details"


def place_order_url() -> str:
    return f"{digital_url()}/gateway/restrict/brokerage-order-entry/v5/accounts/orders/equities"


def build_headers(ecaap: bool = False, headers: dict = None) -> dict:
    """
    Builds default headers with the ability to specify custom headers to use on top of the default headers.

    :param ecaap: Whether the URL starts with ecaap as in: https://ecaap.digitalbrokerageservices.com.
    :param headers: Custom headers that will overwrite the default headers.
    :return: The headers
    """
    default_headers = {
        "host": "www.digitalbrokerageservices.com",
        "appid": "AP128920",
        "accept": "application/json",
        "appname": "Simplifid",
        "accept-token-location": "HEADER",
        "x-acf-sensor-data": "4,i,qMG9W1OFbObs5300s4c3USRKhJatHNMKfzxKSn2GLJYoGDjzqEmpZelg/6F6Vqo7O6K+c9g6WohHAr/oomyQL9Rhd/qk7xhIiCOXFGTT5WPIy3OVdSzLOgO5mTv3BkgXZ/JG6KMD0opGB/7IpYaG+lDCF2vZW486ASbJXfqEyH0=,GxzDvgnmfXikqi6fkl7Xcsy7wtOOVV4dGmvAc/TG0xGyvcCFVOXXSBZgsZxyhiz0xA7C0yKRv011fnpETUfIoCvd2bSnNHITi86Rd/ojNt9CMidFEEAD7vwOtc67CdB1SaRnn4IjBPwrc4qXWEFsFrxTWpiDkGu0M5gWLOAIbB8=$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$28,17,51",
        "accept-language": "en-US,en;q=0.5",
        "accept-encoding": "gzip, deflate, br",
        "content-type": "application/json",
        "user-agent": "Plynk/7803 CFNetwork/1335.0.3.4 Darwin/21.6.0",
        "connection": "keep-alive",
        "token-location": "HEADER",
        "accept-token-type": "ET",
    }
    if ecaap:
        default_headers["host"] = "ecaap.digitalbrokerageservices.com"
    if headers:
        default_headers = {**default_headers, **headers}  # Merge custom header's with default headers
    return default_headers
