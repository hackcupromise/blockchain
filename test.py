from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash

from boa.blockchain.vm.System.ExecutionEngine import GetScriptContainer, GetExecutingScriptHash
from boa.blockchain.vm.Neo.Transaction import Transaction, GetReferences, GetOutputs,GetUnspentCoins
from boa.blockchain.vm.Neo.Output import GetValue, GetAssetId, GetScriptHash

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

def Main():
   #context = GetContext()
   #print('context: ', context)
   #tx = GetScriptContainer()
   #print("tx: ", tx)
   #references = tx.References
   #print("past ref")
   #references = references[0]
   #print('references: ', references)

   #sender = GetScriptHash(reference)
   #print('sender: ', sender)
   #
   # reciever = GetExecutingScriptHash()
   # for output in tx.outputs:
   #     shash = GetScriptHash(output)
   #     print("Output: ", output)
   #     value = GetValue(output)
   #     print("value: ", value)
   attatchments = get_asset_attachments()
   print(attatchments)

   return False
