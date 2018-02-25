from boa.code.builtins import concat, list
from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash
from boa.blockchain.vm.Neo.Runtime import CheckWitness, Log
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Header import GetTimestamp, GetNextConsensus, GetHash


# Field identifiers
FIELD_BUSINESS_PROMISE_AMOUNT = 0x1

FIELD_PXID_USER_ID = 0x11
FIELD_PXID_BUSINESS_ID = 0x12
FIELD_PXID_CHARITY_ID = 0x13
FIELD_PXID_AMOUNT = 0x14
FIELD_PXID_PROMISE = 0x15
FIELD_PXID_TIME = 0x16

#  end field identifiers

#  Method identifiers
#  TODO
# End Method identifiers

#  other constants
MONTH = 2592000000

NEO_ASSET_ID = b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5'


def business_add_funds(business_pk, amount: int) -> bool:

    if not CheckWitness(business_pk):
        # business is not the one making transaction
        return False

    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    ctx = GetContext()
    current_value = Get(ctx, key)

    if not current_value:
        #  init current value
        current_value = 0

    current_value += amount
    Put(ctx, key, current_value)

    return True


def check_promise_funds(business_pk) -> int:
    ctx = GetContext()
    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    value = Get(ctx, key)

    if not value:
        return 0
    return value


def user_create_donation(user_pk, business_pk, charity_pk, amount: int, pxid)-> bool:
    if not CheckWitness(user_pk):
        return False

    ctx = GetContext()
    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    business_funds = Get(ctx, key)
    if amount > business_funds:
        return False

    field_user_id = concat(pxid, FIELD_PXID_USER_ID)
    field_business_id = concat(pxid, FIELD_PXID_BUSINESS_ID)
    field_charity_id = concat(pxid, FIELD_PXID_CHARITY_ID)
    field_amount_id = concat(pxid, FIELD_PXID_AMOUNT)
    field_promise_id = concat(pxid, FIELD_PXID_PROMISE)
    field_time_id = concat(pxid, FIELD_PXID_TIME)

    Put(ctx, field_user_id, user_pk)
    Put(ctx, field_business_id, business_pk)
    Put(ctx, field_charity_id, charity_pk)
    Put(ctx, field_amount_id, amount)
    Put(ctx, field_promise_id, amount)
    end_time = get_current_time() + MONTH
    Put(ctx, field_time_id, end_time)
    return True


# Return current time + a month
def get_current_time():
    height = GetHeight()
    header = GetHeader(height)
    current_time = GetTimestamp(header)
    return current_time


def get_neo_input_amount():
    return get_asset_input_amount(NEO_ASSET_ID)


def get_asset_input_amount(asset_id):
    tx = GetScriptContainer()
    script_hash = GetExecutingScriptHash()

    value = 0
    for output in GetOutputs(tx):
        if GetScriptHash(output) == script_hash and GetAssetId(output) == asset_id:
            value += GetValue(output)

    return value


def Main(business_pk, amount: int) -> int:
    Log("testing log messages")
    business_add_funds(business_pk, amount)
    return check_promise_funds(business_pk)
