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


def check_in_mempool(tx_id, token):
    return NetworkAPI.check_in_mempool(tx_id, token)


def get_transaction(hash_, token):
    transaction = NetworkAPI.get_transaction(hash_, token)
    return transaction

def get_last_block(token):
    block_number = NetworkAPI.get_last_block(token)
    return block_number
