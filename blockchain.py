from boa.code.builtins import concat, list
from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash
from boa.blockchain.vm.Neo.Runtime import CheckWitness

METHOD_USER_DONATE = 0x1
METHOD_BUSINESS_DONATE = 0x2
METHOD_START_BUSINESS_TRANSACTION = 0x3
METHOD_TRY_CHARITY_PAYOUT = 0x4
METHOD_TRY_REFUND_USER = 0x5
METHOD_TRY_REFUND_BUSINESS = 0x6

class Donation:
    def __init__(self, user_pk, business_pk, charity_pk, user_neo_amount):
        self.user_pk = user_pk
        self.business_pk = business_pk
        self.charity_pk = charity_pk
        self.user_neo = user_neo_amount
        self.required_match = user_neo_amount



def user_donate(user_pk, business_pk, charity_pk):
    '''
    :param user_pk: user's public key
    :param business_pk: business's public key
    :param charity_pk: charity's public key
    :param amount_bigint amount of NEO to donate
    :return: true on success, false otherwise
    '''

    if not CheckWitness(user_pk):  # is the user making the call
        return False



    return True


def business_donate(business_pk, txid_hash):
    '''
    :param business_pk: business's public key
    :param amount_bigint:
    :param txid_hash: transaction identifier (byte array)
    :return: true on success, false otherwise
    '''
    pass


def start_donation_transaction(user_pk, business_pk, charity_pk, txid_hash, duration):
    pass


def try_charity_payout(charity_pk, txid_hash):
    pass


def try_refund_user():
    pass


def try_refund_business():
    pass


def Main(method_byte, user_pk, business_pk, charity_pk, amount_bigint, txid_hash):
    if method_byte == METHOD_USER_DONATE:

        return user_donate(user_pk, business_pk, charity_pk)

    elif method_byte == METHOD_BUSINESS_DONATE:

        return business_donate(business_pk, amount_bigint, txid_hash)

    elif method_byte == METHOD_START_BUSINESS_TRANSACTION:

        return start_donation_transaction(user_pk, business_pk, charity_pk, amount_bigint, txid_hash)

    elif method_byte == METHOD_TRY_CHARITY_PAYOUT:

        return try_charity_payout(charity_pk, txid_hash)

    elif method_byte == METHOD_TRY_REFUND_USER:

        return try_refund_user()


    elif method_byte == METHOD_TRY_REFUND_BUSINESS:

        return try_refund_business()

