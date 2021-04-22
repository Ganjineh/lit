import requests

from lit.network import currency_to_satoshi
from lit.network.meta import Unspent
from lit.utils import Decimal

DEFAULT_TIMEOUT = 1000


def set_service_timeout(seconds):
    global DEFAULT_TIMEOUT
    DEFAULT_TIMEOUT = seconds


class InsightAPI:
    MAIN_ENDPOINT = ''
    MAIN_ADDRESS_API = ''
    MAIN_BALANCE_API = ''
    MAIN_UNSPENT_API = ''
    MAIN_TX_PUSH_API = ''
    TX_PUSH_PARAM = ''

    @classmethod
    def get_balance(cls, address):
        r = requests.get(cls.MAIN_BALANCE_API.format(
            address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()

    @classmethod
    def get_transactions(cls, address):
        r = requests.get(cls.MAIN_ADDRESS_API + address,
                         timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return r.json()['transactions']

    @classmethod
    def get_unspent(cls, address):
        r = requests.get(cls.MAIN_UNSPENT_API.format(
            address), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:  # pragma: no cover
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['amount'], 'btc'),
                    tx['confirmations'],
                    tx['scriptPubKey'],
                    tx['txid'],
                    tx['vout'])
            for tx in r.json()
        ]

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        r = requests.post(cls.MAIN_TX_PUSH_API, data={
                          cls.TX_PUSH_PARAM: tx_hex}, timeout=DEFAULT_TIMEOUT)
        return True if r.status_code == 200 else False


class TatumAPI:
    MAIN_ENDPOINT = 'https://api-eu1.tatum.io/v3/litecoin/'
    MAIN_ADDRESS_API = MAIN_ENDPOINT + 'address/balance'
    MAIN_TRANSACTIONS = MAIN_ENDPOINT + 'transaction/address'
    MAIN_TRANSACTIONS_UNSPENT = MAIN_ENDPOINT + 'get_tx_unspent'
    MAIN_TRANSACTION_SEND = MAIN_ENDPOINT + 'send_tx/'

    @classmethod
    def _get_balance(cls, network, address, token):
        url = "{endpoint}/{address}".format(
            endpoint=cls.MAIN_ADDRESS_API,
            address=address
        )
        r = requests.get(url, timeout=DEFAULT_TIMEOUT,
                         headers={'x-api-key': token})
        if r.status_code != 200:
            raise ConnectionError
        print(Decimal(r.json()['incoming']) - Decimal(r.json()['outgoing']))
        return (Decimal(r.json()['incoming']) - Decimal(r.json()['outgoing']))

    @classmethod
    def get_balance(cls, address, token):
        return cls._get_balance('LTC', address, token)

    @classmethod
    def _get_transactions(cls, network, address,token):
        url = "{endpoint}/{address}?pageSize=30&offset=0".format(
        endpoint=cls.MAIN_TRANSACTIONS,
        address=address
        )
        r = requests.get(url, timeout=DEFAULT_TIMEOUT,
                        headers={'x-api-key': token})
        if r.status_code != 200:
            raise ConnectionError
        data = r.json()
        return data

    @classmethod
    def get_transactions(cls, address, token):
        return cls._get_transactions('LTC', address, token)

    @classmethod
    def _get_unspent(cls, network, address):
        url = "{endpoint}/{address}".format(
            endpoint=cls.MAIN_TRANSACTIONS_UNSPENT,
            address=address
        )
        r = requests.get(url, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            raise ConnectionError
        return [
            Unspent(currency_to_satoshi(tx['value'], 'ltc'),
                    tx['confirmations'],
                    tx['script_hex'],
                    tx['txid'],
                    tx['output_no'])
            for tx in r.json()['data']["txs"]
        ]

    @classmethod
    def get_unspent(cls, address):
        return cls._get_unspent('LTC', address)

    @classmethod
    def _broadcast_tx(cls, network, tx_hex):
        url = "{endpoint}{network}/".format(
            endpoint=cls.MAIN_TRANSACTION_SEND,
            network=network
        )
        r = requests.post(url, timeout=DEFAULT_TIMEOUT,
                          data={'tx_hex': tx_hex})
        return True if r.status_code == 200 else False

    @classmethod
    def broadcast_tx(cls, tx_hex):
        return cls._broadcast_tx('LTC', tx_hex)


class NetworkAPI:
    IGNORED_ERRORS = (ConnectionError,
                      requests.exceptions.ConnectionError,
                      requests.exceptions.Timeout,
                      requests.exceptions.ReadTimeout)

    GET_BALANCE_MAIN = [TatumAPI.get_balance, ]
    GET_TRANSACTIONS_MAIN = [TatumAPI.get_transactions, ]
    GET_UNSPENT_MAIN = [TatumAPI.get_unspent, ]
    BROADCAST_TX_MAIN = [TatumAPI.broadcast_tx, ]

    @classmethod
    def get_balance(cls, address, token):
        """Gets the balance of an address in satoshi.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``int``
        """

        for api_call in cls.GET_BALANCE_MAIN:
            try:
                return api_call(address, token)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_transactions(cls, address, token):
        """Gets the ID of all transactions related to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of ``str``
        """

        for api_call in cls.GET_TRANSACTIONS_MAIN:
            try:
                return api_call(address, token)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def get_unspent(cls, address):
        """Gets all unspent transaction outputs belonging to an address.

        :param address: The address in question.
        :type address: ``str``
        :raises ConnectionError: If all API services fail.
        :rtype: ``list`` of :class:`~bit.network.meta.Unspent`
        """

        for api_call in cls.GET_UNSPENT_MAIN:
            try:
                return api_call(address)
            except cls.IGNORED_ERRORS:
                pass

        raise ConnectionError('All APIs are unreachable.')

    @classmethod
    def broadcast_tx(cls, tx_hex):  # pragma: no cover
        """Broadcasts a transaction to the blockchain.

        :param tx_hex: A signed transaction in hex form.
        :type tx_hex: ``str``
        :raises ConnectionError: If all API services fail.
        """
        success = None

        for api_call in cls.BROADCAST_TX_MAIN:
            try:
                success = api_call(tx_hex)
                if not success:
                    continue
                return
            except cls.IGNORED_ERRORS:
                pass

        if success is False:
            raise ConnectionError('Transaction broadcast failed, or '
                                  'Unspents were already used.')

        raise ConnectionError('All APIs are unreachable.')
