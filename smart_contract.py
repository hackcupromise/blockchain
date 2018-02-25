from boa.code.builtins import concat, list
from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash
from boa.blockchain.vm.Neo.Runtime import CheckWitness
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader

# Field identifiers
FIELD_BUSINESS_PROMISE_AMOUNT = 0x1

#  end field identifiers

#  Method identifiers
#  TODO
# End Method identifiers


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


def Main(business_pk, amount: int) -> int:
    business_add_funds(business_pk, amount)
    return check_promise_funds(business_pk)
