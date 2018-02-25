from boa.code.builtins import concat, list
from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash
from boa.blockchain.vm.Neo.Runtime import CheckWitness
from boa.blockchain.vm.Neo.Storage import GetContext, Get, Put, Delete
from boa.blockchain.vm.Neo.Blockchain import GetHeight, GetHeader

METHOD_USER_DONATE = 0x1
METHOD_BUSINESS_DONATE = 0x2
METHOD_START_BUSINESS_TRANSACTION = 0x3
METHOD_TRY_CHARITY_PAYOUT = 0x4
METHOD_TRY_REFUND_USER = 0x5
METHOD_TRY_REFUND_BUSINESS = 0x6

neo_asset_id = b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5'
gas_asset_id = b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`'

'''
Class copied from neo_ico_template:
https://github.com/neonexchange/neo-ico-template
'''

'''
class Attachments():
    """
    Container object ( struct ) for passing around information about attached neo and gas
    """
    neo_attached = 0

    gas_attached = 0

    sender_addr = 0

    receiver_addr = 0

    neo_asset_id = b'\x9b|\xff\xda\xa6t\xbe\xae\x0f\x93\x0e\xbe`\x85\xaf\x90\x93\xe5\xfeV\xb3J\\"\x0c\xcd\xcfn\xfc3o\xc5'

    gas_asset_id = b'\xe7-(iy\xeel\xb1\xb7\xe6]\xfd\xdf\xb2\xe3\x84\x10\x0b\x8d\x14\x8ewX\xdeB\xe4\x16\x8bqy,`'
    def get_neo_attached(self):
        return self.neo_attached


def get_asset_attachments() -> Attachments:
    """
    Gets information about NEO and Gas attached to an invocation TX

    :return:
        Attachments: An object with information about attached neo and gas
    """
    attachment = Attachments()

    tx = GetScriptContainer()  # type:Transaction
    references = tx.References
    attachment.receiver_addr = GetExecutingScriptHash()

    if len(references) > 0:

        reference = references[0]
        attachment.sender_addr = reference.ScriptHash

        sent_amount_neo = 0
        sent_amount_gas = 0

        for output in tx.Outputs:
            if output.ScriptHash == attachment.receiver_addr and output.AssetId == attachment.neo_asset_id:
                sent_amount_neo += output.Value

            if output.ScriptHash == attachment.receiver_addr and output.AssetId == attachment.gas_asset_id:
                sent_amount_gas += output.Value

        attachment.neo_attached = sent_amount_neo
        attachment.gas_attached = sent_amount_gas


    return attachment
'''
# Copied from LuckyNeo
def GetEndTime():
    #TWOWEEKS = 1209600000
    context = GetContext()
    currentHeight = GetHeight()
    currentHeader = GetHeader(currentHeight)
    #time = currentHeader.Timestamp + TWOWEEKS
    print('setting time')
    #print(time)
    #Put(context, "endTime", time)
    #return time
    return 0

#class Donation():
    '''
    def __init__(self, user_pk, business_pk, charity_pk, user_neo_amount):
        self.user_pk = user_pk
        self.business_pk = business_pk
        self.charity_pk = charity_pk
        self.user_neo = user_neo_amount
        self.required_match = user_neo_amount
        '''


def user_donate(user_pk, business_pk, charity_pk, amount_bigint, txid_hash) -> bool:
    '''
    :param user_pk: user's public key
    :param business_pk: business's public key
    :param charity_pk: charity's public key
    :param amount_bigint amount of NEO to donate
    :param txid_hash: Hash of tranaction id
    :return: true on success, false otherwise
    '''
    if not CheckWitness(user_pk):  # is the user making the call
        return False

    tx = GetScriptContainer()  # type:Transaction
    references = tx.References
    receiver_addr = GetExecutingScriptHash()

    sent_amount_neo = 0
    sent_amount_gas = 0

    if len(references) > 0:

        reference = references[0]
        sender_addr = reference.ScriptHash

        #o = tx.Outputs

        for output in tx.Outputs:
            if output.ScriptHash == receiver_addr and output.AssetId == neo_asset_id:
                sent_amount_neo += output.Value

            if output.ScriptHash == receiver_addr and output.AssetId == gas_asset_id:
                sent_amount_gas += output.Value

        neo_attached = sent_amount_neo
        gas_attached = sent_amount_gas

    # Get Neo from user - NOTE: This will be the hard part
    #attachment = get_asset_attachments()
    #if attachment.neo_attached != 0:
    if neo_attached != 0:
        # Create struct with info - LIST
        # Info to include: userpk, charitypk, businesspk, amount, amount promised, time, transaction ID - key
        ctx = GetContext() # Get context for storage
        # Check for existing shit I guess
        if Get(ctx, txid_hash) is None:
            print("Error: TXID exists already")
            return False
        # Create list
        # Check if neo_attached == amount?
        new_list = list(length=5)
        new_list[0] = user_pk
        new_list[1] = business_pk
        new_list[2] = amount_bigint
        new_list[3] = amount_bigint # same number - represents the amount pledged but not fullfilled
        new_list[4] = GetEndTime()

        # Now put the list in the context at the key val txid_hash
        Put(ctx, txid_hash, new_list)
        return True
    else:
        return False




#def business_donate(business_pk, amount_bigint, txid_hash):
def business_donate(user_pk, business_pk, charity_pk, amount_bigint, txid_hash):
    '''
    :param business_pk: business's public key
    :param amount_bigint:
    :param txid_hash: transaction identifier (byte array)
    :return: true on success, false otherwise
    '''
    # Get info from txid_hash
    # Add Neo to amount
    # Subtract Neo from the temp shit
    ctx = GetContext()
    info = Get(ctx, txid_hash)
    if info is None:
        return False

    # Info to include: userpk, charitypk, businesspk, amount, amount promised, time
    promised = info[4]
    if promised > 0:
        #
        return True


    return True


'''

    def try_charity_payout(charity_pk, txid_hash):
        pass


    def try_refund_user():
        pass


    def try_refund_business():
        pass

'''
def Main(method_byte, user_pk, business_pk, charity_pk, amount_bigint, txid_hash):
    #donate = Donation()
    '''
    METHOD_USER_DONATE = 0x1
    METHOD_BUSINESS_DONATE = 0x2
    METHOD_START_BUSINESS_TRANSACTION = 0x3
    METHOD_TRY_CHARITY_PAYOUT = 0x4
    METHOD_TRY_REFUND_USER = 0x5
    METHOD_TRY_REFUND_BUSINESS = 0x6
    '''
    #if method_byte == METHOD_USER_DONATE:
    #return donate.user_donate(user_pk, business_pk, charity_pk, amount_bigint, txid_hash)
    # There is still an error but what the hell ever I guess

    #return user_donate(user_pk, business_pk, charity_pk, amount_bigint, txid_hash)

    #elif method_byte == METHOD_BUSINESS_DONATE:
    return business_donate(user_pk, business_pk, charity_pk, amount_bigint, txid_hash)
    #return business_donate(business_pk, amount_bigint, txid_hash)
'''
    elif method_byte == METHOD_START_BUSINESS_TRANSACTION:

        return start_donation_transaction(user_pk, business_pk, charity_pk, amount_bigint, txid_hash)

    elif method_byte == METHOD_TRY_CHARITY_PAYOUT:

        return try_charity_payout(charity_pk, txid_hash)

    elif method_byte == METHOD_TRY_REFUND_USER:

        return try_refund_user()


    elif method_byte == METHOD_TRY_REFUND_BUSINESS:

        return try_refund_business()
'''
