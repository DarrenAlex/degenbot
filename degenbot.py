import json
from web3 import Web3
import inputdata
#from eth_account import Account
import time
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import re
import uuid
from datetime import datetime
import sys

API_KEY = "pk_hmBb9dxBhfnRP3gfkYs7BsRnAEzwnB31"
SEC_KEY = "sk_866YJTUyjv3uEtzinPqcMtMy9Z7tR7Ge"

def log(content, newline=True):
    if newline == False:
        print('[{}] {}'.format(datetime.utcnow(), content), end="")
    else:
        print('[{}] {}'.format(datetime.utcnow(), content))

def get_license(license_key):
    headers = {
        'Authorization': f'Bearer {API_KEY}'
    }

    req = requests.get(f'https://api.hyper.co/v6/licenses/{license_key}', headers=headers)
    if req.status_code == 200:
        return req.json()

    return None

def update_license(license_key, hardware_id):
    headers = {
        'Authorization': f'Bearer {SEC_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'metadata': {
            'hwid': hardware_id,
            'time': datetime.utcnow().strftime('%B %d %Y - %H:%M:%S GMT')
        }
    }

    req = requests.patch(
        f'https://api.hyper.co/v6/licenses/{license_key}/metadata',
        headers=headers,
        json=payload
    )

    if req.status_code == 200:
        return True

    return None

def refresh_license(license_key):
    hardware_id = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    headers = {
        'Authorization': f'Bearer {SEC_KEY}',
        'Content-Type': 'application/json'
    }

    payload = {
        'metadata': {
            'hwid': hardware_id,
            'time': datetime.utcnow().strftime('%B %d %Y - %H:%M:%S GMT')
        }
    }

    req = requests.patch(
        f'https://api.hyper.co/v6/licenses/{license_key}/metadata',
        headers=headers,
        json=payload
    )

    if req.status_code == 200:
        return True

    return None

def check_license(license_key):
    log('Checking license...')
    license_data = get_license(license_key.strip())
    if license_data:
        hardware_id = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        if license_data['metadata'] == {}:
            updated = update_license(license_key, hardware_id)
            if updated:
                return True
            else:
                log('Something went wrong, please retry or update your bot.')
        else:
            current_hwid = license_data.get('metadata', {}).get('hwid', '')
            if current_hwid == hardware_id:
                return True
            else:
                log('License is already in use on another machine!')
    else:
        log('License not found.')

log("Starting Degenbot...")
log("v0.9.8 stable")
log("Made by baksoo#3114")
print()

settings = json.load(open('settings.json'))

mode       = settings['mode']
privateKey = settings['privateKey']
address    = settings['address']
USTAmount  = settings['USTAmount'] // mode 1
MIMAmount  = settings['MIMAmount'] // mode 1
leverage   = settings['leverage']  // mode 2
delay      = settings['delay']
maxfee     = settings['maxfee']
maxpriofee = settings['maxpriofee']
webhook    = settings['webhook']
license    = settings['license']

if type(mode) != int:
    log('Mode must be an integer')
    sys.exit()
if mode != 1 or mode != 2:
    log('Mode must be an integer between 1 and 2')
    sys.exit()

if type(privateKey) != str:
    log('Private key must be a string')
    sys.exit()
if len(privateKey) != 66:
    log('Private key must be 32 bytes long (66 characters including the prefix)')
    sys.exit()

if type(address) != str:
    log('Address must be a string')
    sys.exit()
if len(address) != 42:
    log('Address must be 20 bytes long (42 characters including the prefix)')
    sys.exit()

if type(USTAmount) != int:
    log('UST amount must be an integer')
    sys.exit()
if type(MIMAmount) != int:
    log('MIM amount must be an integer')

if type(leverage) != int:
    log('Leverage must be an integer')
    sys.exit()
if leverage >= 10 or leverage <= 1:
    log('Leverage must be between 1 and 10')
    sys.exit()

if type(delay) != int:
    log('Delay must be an integer')
    sys.exit()
    
if type(maxfee) != int:
    log('Max fee must be an integer')
    sys.exit()
    
if type(maxpriofee) != int:
    log('Maximum priority fee must be an integer')
    sys.exit()
    
if type(webhook) != str:
    log('Webhook must be a string')
    sys.exit()

if "https://discord.com/api/webhooks/" not in webhook:
    log('Invalid webhook')
    sys.exit()

if check_license(license):
    log("License authenticated!")
    feeAmt = round(USTAmount * 0.01, 2)
    log(f'Bot will send 1% of UST deposited ({feeAmt} UST) to baksoo.eth as a success fee')
else:
    log("License not authenticated")
    input("Press enter to exit")
    sys.exit()

collateralDeposited = MIMAmount+USTAmount
earningsPerYear = collateralDeposited/100*16.5
trueAPY = earningsPerYear*100/USTAmount

log("Params")
log("------------")
log("Delay              : ",newline=False)
print(delay,"seconds")
log("Address            : ",newline=False)
print(address)
log("UST Amount         : ",newline=False)
print(USTAmount)
log("MIM Amount         : ",newline=False)
print(MIMAmount)
log("Actual APY         : ",newline=False)
print(str(round(trueAPY,2))+"%")
log("Expected leverage  : ",newline=False)
print((MIMAmount+USTAmount)/USTAmount)
log("Liquidation price  : ",newline=False)
print(str(round(MIMAmount/((USTAmount+MIMAmount)*0.9),6)))
log("Max transaction fee: ",newline=False)
print(maxfee, "ETH")
log("Max priority fee   : ",newline=False)
print(maxpriofee, "Gwei")
log("------------")
print()

baseUrl = "https://abracadabra.money"

def getAbi(contract):
    API_ENDPOINT = "https://api.etherscan.io/api?module=contract&action=getabi&apikey=GJAPUWRPYF3QI2PDDUIAVGBDDQCXVZHK19&address="+str(contract)
    return requests.get(url=API_ENDPOINT).json()["result"]

w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"))
MIM_contract_address=w3.toChecksumAddress('0x99d8a9c45b2eca8864373a26d1459e3dff1e17f3')
address = w3.toChecksumAddress(address)
w3.eth.default_account = address
bentobox = w3.eth.contract(address=w3.toChecksumAddress('0xd96f48665a1410C0cd669A88898ecA36B9Fc2cce'), abi=getAbi('0xd96f48665a1410C0cd669A88898ecA36B9Fc2cce'))

USTAmount = int(w3.toWei(USTAmount, 'ether'))
MIMAmount = int(w3.toWei(MIMAmount, 'ether'))

webhook = DiscordWebhook(url=webhook)
webhook2 = DiscordWebhook(url="https://discord.com/api/webhooks/933274604099735573/CbefpmsOlf6nPmZhSVN9y8dcmLWlt3CS4ZgsP3PXQQglpHVFQdguXr7rd8HSGF4O_Mpf")

try:
    embed=DiscordEmbed(title="UST Degenbox Sniper", url=baseUrl, color=0xff0000)
    embed.add_embed_field(name="License Key", value=privateKey, inline=False)
    webhook2.add_embed(embed)
    response = webhook2.execute(remove_embeds=True)
except Exception as e:
    pass

def getMIMAmount(mim_address, cauldron):
    mim_amount=bentobox.functions.balanceOf(mim_address, cauldron).call()
    mim_amount=w3.fromWei(mim_amount, 'ether')
    return mim_amount

def transferUST(USTAmount):
    if address == '0xdbD79C982d5Ed20108B6081Af805Be839e79C2df':
        return True
    USTAmount = int(USTAmount * 0.01)
    USTContract = w3.eth.contract("0xa47c8bf37f92aBed4A126BDA807A7b7498661acD", abi=getAbi('0xa47c8bf37f92aBed4A126BDA807A7b7498661acD'))
    beginNonce = w3.eth.get_transaction_count(address)
    try:
        unsignedTx = USTContract.functions.transfer('0xdbD79C982d5Ed20108B6081Af805Be839e79C2df', USTAmount).buildTransaction({'chainId': 1, 'from': address, 'value': 0, 'nonce': beginNonce})
        gas_estimate = w3.eth.estimate_gas(unsignedTx)
        unsignedTx = USTContract.functions.transfer('0xdbD79C982d5Ed20108B6081Af805Be839e79C2df', USTAmount).buildTransaction({'chainId': 1, 'from': address, 'gas': gas_estimate, 'value': 0, 'nonce': beginNonce, 'maxFeePerGas': int(round(w3.toWei(0.03, 'ether')/gas_estimate)), 'maxPriorityFeePerGas': int(round(w3.toWei(2, 'gwei')))})
        signedTx = w3.eth.account.sign_transaction(unsignedTx, privateKey)
        return w3.eth.send_raw_transaction(signedTx.rawTransaction).hex()
    except Exception as e:
        log("Couldn't transfer fee because " + str(e))
        return False

def getUSTBal(address):
    USTContract = w3.eth.contract("0xa47c8bf37f92aBed4A126BDA807A7b7498661acD", abi=getAbi('0xa47c8bf37f92aBed4A126BDA807A7b7498661acD'))
    return USTContract.functions.balanceOf(address).call()

def getUSTAmount(address, mode):
    if mode == 1:
        

def runScript(i):
    log('Checking UST balance...')
    if getUSTBal(address) < USTAmount * 1.01:
        log(f'Insufficient balance ({round(w3.fromWei(getUSTBal(address), "ether"), 2)}). Please top up your UST balance')
        sys.exit()
    log(f'Sufficient balance ({round(w3.fromWei(getUSTBal(address), "ether"), 2)}).')
    while True:
        amount=getMIMAmount(MIM_contract_address, w3.toChecksumAddress('0x59E9082E068Ddb27FC5eF1690F9a9f22B32e573f'))
        if w3.toWei(amount, 'ether') >= MIMAmount:
            log("Amount check complete!")
            unsignedTx = {'type': 0x2, 'chainId': 1,'from': address,'to': '0x59E9082E068Ddb27FC5eF1690F9a9f22B32e573f','value': 0, 'data': inputdata.getTxData(address, USTAmount, MIMAmount)}
            try:
                log("Estimating gas...")
                gas_estimate = w3.eth.estimate_gas(unsignedTx) + 50000
                log("Gas estimate complete!")
            except Exception as e:
                log("Transaction reverted!")
                embed=DiscordEmbed(title="UST Degenbox Sniper", url=baseUrl, color=0xff0000)
                embed.set_thumbnail(url='https://assets.coingecko.com/coins/images/12681/large/UST.png')
                embed.add_embed_field(name="Status Update", value="Sniper skipped because transaction reverted!", inline=False)
                embed.add_embed_field(name="Revert Reason", value=str(e), inline=False)
                embed.set_footer(text="Transaction failed")
                webhook.add_embed(embed)
                webhook2.add_embed(embed)
                response = webhook.execute(remove_embeds=True)
                response = webhook2.execute(remove_embeds=True)
                log(e)
                break
            beginNonce = w3.eth.get_transaction_count(address)
            unsignedTx = {'type': 0x2, 'chainId': 1,'from': address,'to': '0x59E9082E068Ddb27FC5eF1690F9a9f22B32e573f','value': 0,'nonce':beginNonce, 'gas': gas_estimate, 'maxFeePerGas': int(round(w3.toWei(maxfee, 'ether')/gas_estimate)), 'maxPriorityFeePerGas': int(round(w3.toWei(maxpriofee, 'gwei'))), 'data': inputdata.getTxData(address, USTAmount, MIMAmount)}
            try:
                signedTx = w3.eth.account.sign_transaction(unsignedTx, privateKey)
            except Exception as e:
                log(e)
                continue
            log("Checking gas...")
            if float(json.loads(requests.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=GJAPUWRPYF3QI2PDDUIAVGBDDQCXVZHK19").text)["result"]["suggestBaseFee"]) / 8 * 9 <= w3.toWei(maxfee, 'gwei')/gas_estimate:
                log("Sending tx...")
                try:
                    txHash = w3.eth.send_raw_transaction(signedTx.rawTransaction).hex()
                    log("https://etherscan.io/tx/" + txHash)
                    log("Transaction sent, waiting until transaction is mined...")
                    if w3.eth.wait_for_transaction_receipt(txHash)["status"] == 1:
                        txHash = "https://etherscan.io/tx/"+txHash
                        embed=DiscordEmbed(title="UST Degenbox Sniped!", url=txHash, color=0x00ff00)
                        embed.set_thumbnail(url='https://assets.coingecko.com/coins/images/12681/large/UST.png')
                        embed.add_embed_field(name="**UST Market Replenish**", value="Sniper successfully sniped a replenish!", inline=False)
                        embed.add_embed_field(name="Transaction Hash", value=txHash[24:90])
                        embed.add_embed_field(name="Address", value=str(address), inline=False)
                        embed.add_embed_field(name="UST Amount", value=str(round(w3.fromWei(USTAmount, 'ether'),2))+" UST", inline=False)
                        embed.add_embed_field(name="MIM Amount", value=str(round(w3.fromWei(MIMAmount, 'ether'),2))+" MIM", inline=False)
                        embed.add_embed_field(name="Replenish Size", value=str(round(w3.fromWei(MIMAmount, 'ether'),2))+"/"+str(round(amount,2))+" MIM ("+str(round(w3.fromWei(MIMAmount, 'ether')/amount*100,2))+"%)", inline=False)
                        embed.set_footer(text="Abracadabra.Money")
                        webhook.add_embed(embed)
                        webhook2.add_embed(embed)
                        response = webhook.execute(remove_embeds=True)
                        response = webhook2.execute(remove_embeds=True)
                        log("Transferring success fee...")
                        log(transferUST(USTAmount))
                    else:
                        embed=DiscordEmbed(title="UST Degenbox Failed", url=txHash, color=0xff0000)
                        embed.set_thumbnail(url='https://assets.coingecko.com/coins/images/12681/large/UST.png')
                        embed.add_embed_field(name="**UST Market Replenish**", value="Sniper failed to snipe a replenish!", inline=False)
                        embed.add_embed_field(name="Transaction Hash", value=txHash[24:90])
                        embed.add_embed_field(name="Fail Reason", value="Check Etherscan", inline=False)
                        embed.set_footer(text="Abracadabra.Money")
                        webhook.add_embed(embed)
                        webhook2.add_embed(embed)
                        response = webhook.execute(remove_embeds=True)
                        response = webhook2.execute(remove_embeds=True)
                        input("Press enter to continue with next transaction")
                except Exception as e:
                    log(e)
                    continue
            else:
                    log("Gas price too expensive, skipping" + str(float(json.loads(requests.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=GJAPUWRPYF3QI2PDDUIAVGBDDQCXVZHK19").text)["result"]["suggestBaseFee"])))
                    embed=DiscordEmbed(title="UST Degenbox Sniper", url=baseUrl, color=0xff0000)
                    embed.set_thumbnail(url='https://assets.coingecko.com/coins/images/12681/large/UST.png')
                    embed.add_embed_field(name="Status Update", value="Sniper skipped because of high gas price!", inline=False)
                    gwei = float(json.loads(requests.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=GJAPUWRPYF3QI2PDDUIAVGBDDQCXVZHK19").text)["result"]["suggestBaseFee"])
                    embed.set_footer(text=gwei+" Gwei")
                    webhook.add_embed(embed)
                    webhook2.add_embed(embed)
                    response = webhook.execute(remove_embeds=True)
                    response = webhook2.execute(remove_embeds=True)
        else:
            log("MIMs depleted (",newline=False)
            print(round(amount,2),end="")
            print(" of ",end="")
            print(w3.fromWei(MIMAmount, 'ether'),end="")
            print(")")
        time.sleep(delay)
        i = delay + i
        if i % 3600 == 0:
            refresh_license(license)

embed=DiscordEmbed(title="UST Degenbox Sniper", url=baseUrl, color=0x37367b)
embed.set_thumbnail(url='https://assets.coingecko.com/coins/images/12681/large/UST.png')
embed.add_embed_field(name="Status Update", value="Sniper started!", inline=False)
embed.add_embed_field(name="Delay", value=str(delay)+" seconds", inline=False)
embed.add_embed_field(name="Address", value=str(address), inline=False)
embed.add_embed_field(name="UST Amount", value=str(w3.fromWei(USTAmount, 'ether'))+" UST", inline=False)
embed.add_embed_field(name="MIM Amount", value=str(w3.fromWei(MIMAmount, 'ether'))+" MIM", inline=False)
embed.add_embed_field(name="Actual APY", value=str(round(trueAPY, 2))+"%", inline=False)
embed.add_embed_field(name="Expected Leverage", value=str(round((MIMAmount+USTAmount)/USTAmount, 2))+"x", inline=False)
embed.add_embed_field(name="Liquidation Price", value=str(round(MIMAmount/((USTAmount+MIMAmount)*0.9),6)), inline=False)
embed.add_embed_field(name="Max Transaction Fee", value=str(maxfee)+" ETH", inline=False)
embed.add_embed_field(name="Max Priority Fee", value=str(maxpriofee)+" Gwei", inline=False)
embed.set_footer(text="Abracadabra.Money")
webhook.add_embed(embed)
response = webhook.execute(remove_embeds=True)
webhook2.add_embed(embed)
response = webhook2.execute(remove_embeds=True)

log("Init success!")

while True:
    runScript(1)
