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
FIELD_PXID_FULFILLED = 0x16
FIELD_PXID_TIME = 0x17

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
        Log("Business CheckWitness failed")
        return False

    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    ctx = GetContext()
    current_value = Get(ctx, key)

    if not current_value:
        Log("Creating new business fund")
        #  init current value
        current_value = 0

    current_value += amount
    Put(ctx, key, current_value)

    Log("Added funds (added, total)")
    Log(amount)
    Log(current_value)

    return True


def check_promise_funds(business_pk) -> int:
    ctx = GetContext()
    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    value = Get(ctx, key)

    Log("Checking promise with funds:")
    Log(value)

    if not value:
        return 0
    return value


def user_create_donation(user_pk, business_pk, charity_pk)-> bool:
    if not CheckWitness(user_pk):
        Log("User CheckWitness failed")
        return False
    pxid = generate_pxid(business_pk, user_pk, charity_pk)
    amount = get_neo_input_amount()

    ctx = GetContext()
    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    business_funds = Get(ctx, key)
    if not business_funds or amount > business_funds:
        Log("User donation failed - user overcommitted:")
        Log(amount)
        Log("which is more than the business has:")
        Log(business_funds)
        return False

    field_user_id = concat(pxid, FIELD_PXID_USER_ID)
    field_business_id = concat(pxid, FIELD_PXID_BUSINESS_ID)
    field_charity_id = concat(pxid, FIELD_PXID_CHARITY_ID)
    field_amount_id = concat(pxid, FIELD_PXID_AMOUNT)
    field_promise_id = concat(pxid, FIELD_PXID_PROMISE)
    field_fulfilled_id = concat(pxid, FIELD_PXID_FULFILLED)
    field_time_id = concat(pxid, FIELD_PXID_TIME)

    Put(ctx, field_user_id, user_pk)
    Put(ctx, field_business_id, business_pk)
    Put(ctx, field_charity_id, charity_pk)
    Put(ctx, field_amount_id, amount)
    Put(ctx, field_promise_id, amount)
    Put(ctx, field_fulfilled_id, 0)
    end_time = get_current_time() + MONTH
    Put(ctx, field_time_id, end_time)

    Log("NEW DONATION TO MATCH:")

    Log("user_id:")
    Log(user_pk)

    Log("business_id:")
    Log(business_pk)

    Log("charity_id:")
    Log(charity_pk)

    Log("user_neo_amount:")
    Log(amount)

    Log("promised_amount:")
    Log(amount)

    Log("fulfilled_amount:")
    Log(0)

    Log("end_time:")
    Log(end_time)

    return True


# Return current time + a month
def get_current_time():
    height = GetHeight()
    header = GetHeader(height)
    current_time = GetTimestamp(header)
    Log("The current header timestamp is:", current_time)
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

    Log("The tx inputs are:")
    Log(42)
    return value


def generate_pxid(business_pk, user_pk, charity_pk):
    return concat(business_pk, concat(user_pk, charity_pk))


def Main(operation, business_pk, user_pk, charity_pk, amount_promise) -> int:
    Log("testing log messages:")
    Log(42)

    business_add_funds(business_pk, amount_promise)
    return user_create_donation(user_pk, business_pk, charity_pk)
