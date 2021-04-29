from lit.network import NetworkAPI, satoshi_to_currency_cached


def get_balance(address, token, currency='LTC'):
    return NetworkAPI.get_balance(address, token)


def get_transactions(address, token):
    transactions = []
    """Fetches transaction history.

    :rtype: ``list`` of ``str`` transaction IDs
    """
    transactions[:] = NetworkAPI.get_transactions(address, token)
    return transactions
