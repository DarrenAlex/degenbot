license    (string) : found in https://degenbot.hyper.co/

privateKey (string) : use https://iancoleman.io/bip39/ to convert mnemonic into private key
address    (string) : your public address

USTAmount  (integer): amount of UST in your wallet (or willing to deposit)
MIMAmount  (integer): MIM amount to borrow (use discord bot or use frontend to get this value)

delay      (integer): delay to fetch available MIMs (recommended: ETH block time)
maxfee     (integer): max fee paid in ether (NOT GWEI) per txn
maxpriofee (integer): max priority fee to be paid to miners per txn (will generally use all)

webhook    (string) : set up discord webhook

example
{
    'license':    'DEGEN-XXXX-XXXX-XXXX-XXXX',

    'privateKey': '0x1234567890123456789012345678901234567890123456789012345678901234',
    'address':    '0x1234567890123456789012345678901234567890',

    'USTAmount':  15000,
    'MIMAmount':  91250,

    'delay':      13,
    'maxfee':     0.05,
    'maxpriofee': 3,

    'webhook':    'https://discord.com/api/webhooks/930491992302034955/307UEaIXqJtZVAwkaG9IeeaxVs2D6jqbe8nmO-uIDgm9TQKxQZ0X3GOPKfmLqUSejmRu'
}
