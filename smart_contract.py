from boa.code.builtins import concat, list
from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash
from boa.blockchain.vm.Neo.Runtime import CheckWitness, Log, GetTrigger
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader
from boa.blockchain.vm.Neo.Header import GetTimestamp, GetNextConsensus, GetHash
from boa.blockchain.vm.Neo.Action import RegisterAction
from boa.blockchain.vm.Neo import TriggerType



transfer = RegisterAction('refund', 'to', 'amount')

# Field identifiers
FIELD_BUSINESS_PROMISE_AMOUNT = 0x1

FIELD_PXID_USER_ID = 0x11
FIELD_PXID_BUSINESS_ID = 0x12
FIELD_PXID_CHARITY_ID = 0x13
FIELD_PXID_AMOUNT = 0x14
FIELD_PXID_PROMISE = 0x15
FIELD_PXID_FULFILLED = 0x16
FIELD_PXID_TIME = 0x17

FIELD_ENTITY_TOKEN = 0x18

#  end field identifiers

#  Method identifiers
METHOD_BUSINESS_ADD_FUNDS = 0x1
METHOD_CHECK_PROMISE_FUNDS = 0x2
METHOD_USER_CREATE_DONATION = 0x3
METHOD_BUSINESS_MATCH_FUNDS = 0x4
METHOD_CHECK_DONATION_STRUCT = 0x5

METHOD_TOKEN_TRANSFER = 0x6
METHOD_TOKEN_SILLY_DEPLOY = 0x7

# End Method identifiers

#  other constants
MONTH = 2592000000

NEO_ASSET_ID = b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5'

OWNER = b'8`V8\x16\x0f\x02z\x89\x97!t\xd9\xa9\x8d\x19\x07\x8c\xdf\xca'


def get_balance(pk):
    ctx = GetContext()
    key = concat(pk, FIELD_ENTITY_TOKEN)
    value = Get(ctx, key)
    if not value:
        return 0
    return value


def token_transfer(from_pk, to_pk, amount):
    if not CheckWitness(from_pk):
        return False

    ctx = GetContext()
    from_key = concat(from_pk, FIELD_ENTITY_TOKEN)
    from_balance = Get(ctx, from_key)
    if not from_balance:
        from_balance = 0

    to_key = concat(to_pk, FIELD_ENTITY_TOKEN)
    to_balance = Get(ctx, to_key)
    if not to_balance:
        to_balance = 0

    if from_balance < amount:
        return False

    to_balance += amount
    from_balance -= amount

    Put(ctx, from_key, from_balance)
    Put(ctx, to_key, to_balance)
    return True


def token_silly_deploy(amount): # comment too little time too little care
    if not CheckWitness(OWNER):
        return False

    ctx = GetContext()
    owner_key = concat(OWNER, FIELD_ENTITY_TOKEN)

    Put(ctx, owner_key, amount)
    return True


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


def user_create_donation(user_pk, business_pk, charity_pk, amount)-> bool:
    if not CheckWitness(user_pk):
        Log("User CheckWitness failed")
        return False
    script_hash = GetExecutingScriptHash()
    pxid = generate_pxid(business_pk, user_pk, charity_pk)
    amount = amount

    ctx = GetContext()
    key = concat(business_pk, FIELD_BUSINESS_PROMISE_AMOUNT)
    business_funds = Get(ctx, key)
    if not business_funds or amount > business_funds:
        Log("User donation failed - user overcommitted:")
        Log(amount)
        Log("which is more than the business has:")
        Log(business_funds)
        return False

    token_transfer(user_pk, script_hash, amount)

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
    Log("The current header timestamp is:")
    Log(current_time)
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


def business_match_funds(business_pk, user_pk, charity_pk, amount):
    '''
    Inputs: business_pk: Public Key of business adding neo
    pxid: Identifier of transaction that the business is matching

    Will match a pledge specified by pxid if time has not run out. If Neo attached
    exceeds the promised amount, the transaction fails.
    If the Neo is less than or equal, the promise field is updated with the difference.
    '''
    if not CheckWitness(business_pk):
        Log("Business CheckWitness failed")
        return False
    script_hash = GetExecutingScriptHash()
    pxid = generate_pxid(business_pk, user_pk, charity_pk)
    committed_amount = amount
    ctx = GetContext()

    promise_key = concat(pxid, FIELD_PXID_PROMISE)

    promised_amount = Get(ctx, promise_key)
    diff = promised_amount - committed_amount
    if not promised_amount or diff < 0:
        # If promised amount doesn't exist or if the commited amount is more than promised
        return False

    time_key = concat(pxid, FIELD_PXID_TIME)
    current_time = get_current_time()
    end_time = Get(ctx, time_key)

    # If time has run out, transaction fails
    if current_time > end_time:
        return False

    fulfilled_key = concat(pxid, FIELD_PXID_FULFILLED)

    # Update promised amount
    Put(ctx, promise_key, diff)
    Put(ctx, fulfilled_key, promised_amount)
    # Do transaction
    token_transfer(business_pk, script_hash, diff)

    return True


def generate_pxid(business_pk, user_pk, charity_pk):
    user_charity = concat(user_pk, charity_pk)
    return concat(business_pk, user_charity)


def check_donation_struct(user_pk, business_pk, charity_pk):
    pxid = generate_pxid(business_pk, user_pk, charity_pk)
    ctx = GetContext()

    field_user_id = concat(pxid, FIELD_PXID_USER_ID)
    field_business_id = concat(pxid, FIELD_PXID_BUSINESS_ID)
    field_charity_id = concat(pxid, FIELD_PXID_CHARITY_ID)
    field_amount_id = concat(pxid, FIELD_PXID_AMOUNT)
    field_promise_id = concat(pxid, FIELD_PXID_PROMISE)
    field_time_id = concat(pxid, FIELD_PXID_TIME)
    field_fulfilled = concat(pxid, FIELD_PXID_FULFILLED)

    user_id = Get(ctx, field_user_id)
    business_id = Get(ctx, field_business_id)
    charity_id = Get(ctx, field_charity_id)
    amount = Get(ctx, field_amount_id)
    promise = Get(ctx, field_promise_id)
    time = Get(ctx, field_time_id)
    fulfilled = Get(ctx, field_fulfilled)

    data = list(length=7)
    data[0] = user_id
    data[1] = business_id
    data[2] = charity_id
    data[3] = amount
    data[4] = promise
    data[5] = time
    data[6] = fulfilled
    output = build_csv_list(data)

    return output


def build_csv_list(data):
    output = ""
    for d in data:
        entry = concat(d, ",")
        output = concat(output, entry)
    return output


def transfer_funds(uid, amount):
    if not CheckWitness(uid):
        return False
    transfer(uid, amount)
    return True


def charity_transfer_completed_contracts(charity_id, pxid):
    if not CheckWitness(charity_id):
        return False

    script_hash = GetExecutingScriptHash()

    ctx = GetContext()
    time_key = concat(pxid, FIELD_PXID_TIME)
    time_out = Get(ctx, time_key)
    current_time = get_current_time()

    if time_out<current_time: # Contract has expired
        promise_key = concat(pxid, FIELD_PXID_PROMISE)
        promised = Get(ctx, promise_key)

        if promised == 0: # Pay out to charity
            # Get total data
            fulfilled_key = concat(pxid, FIELD_PXID_FULFILLED)
            amount_key = concat(pxid, FIELD_PXID_AMOUNT)

            fulfilled = Get(ctx, fulfilled_key)
            amount = Get(ctx, amount_key)
            tot = fulfilled+amount
            # Transfer to charity
            token_transfer(script_hash, charity_id, tot)
        else:
            # Promise was not fulfilled
            fulfilled_key = concat(pxid, FIELD_PXID_FULFILLED)
            amount_key = concat(pxid, FIELD_PXID_AMOUNT)
            user_key = concat(pxid, FIELD_PXID_USER_ID)
            business_key = concat(pxid, FIELD_PXID_BUSINESS_ID)

            fulfilled = Get(ctx, fulfilled_key)
            amount = Get(ctx, amount_key)
            user_pk = Get(ctx, user_key)
            business_pk = Get(ctx, business_key)

            token_transfer(script_hash, user_pk, amount)
            token_transfer(script_hash, business_pk, fulfilled)

        return True


def handle_verifications():
    return False


def handle_application(operation, args):
    if operation == METHOD_BUSINESS_ADD_FUNDS:
        #  business_add_funds
        business_pk = args[0]
        amount = args[1]
        return business_add_funds(business_pk, amount)

    elif operation == METHOD_BUSINESS_MATCH_FUNDS:
        #  business_match_funds
        business_pk = args[0]
        user_pk = args[1]
        charity_pk = args[2]
        amount = args[3]
        return business_match_funds(business_pk, user_pk, charity_pk, amount)

    elif operation == METHOD_CHECK_DONATION_STRUCT:
        # check_donation_struct
        user_pk = args[0]
        business_pk = args[1]
        charity_pk = args[2]
        return check_donation_struct(user_pk, business_pk, charity_pk)

    elif operation == METHOD_CHECK_PROMISE_FUNDS:
        # check_promise_funds
        business_pk = args[0]
        return check_promise_funds(business_pk)

    elif operation == METHOD_USER_CREATE_DONATION:
        # user_create_donation
        user_pk = args[0]
        business_pk = args[1]
        charity_pk = args[2]
        amount = args[3]
        return user_create_donation(user_pk, business_pk, charity_pk, amount)

    elif operation == METHOD_TOKEN_SILLY_DEPLOY:
        #  token_silly_deploy
        amount = args[0]
        return token_silly_deploy(amount)

    elif operation == METHOD_TOKEN_TRANSFER:
        #  token_transfer
        from_pk = args[0]
        to_pk = args[1]
        amount = args[2]
        return token_transfer(from_pk, to_pk, amount)

    return False


def Main(operation, args) -> int:
    trigger = GetTrigger()
    if trigger == b'\x10':
        return handle_application(operation, args)
    else:
        return handle_verifications()