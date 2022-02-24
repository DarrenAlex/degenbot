from eth_abi import encode_abi

cookFunctionId = "656f3d64"
watermark = "446567656e626f742062792062616b736f6f2333313134202d2068747470733a2f2f747769747465722e636f6d2f62616b736f6f333131340000000000000000"
wUST = "0xa47c8bf37f92aBed4A126BDA807A7b7498661acD"
uint256Limit = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffe
USTLevSwapper = "0x6B44d94ECDFaF0cb00dEF55212e226603BB68793"

def encode11():
    return encode_abi(['uint256', 'uint256', 'uint256'], [1, 0, 0])

def encode20(sender, amount):
    return encode_abi(['address', 'address', 'uint256', 'uint256'], [wUST, sender, amount, 0])

def encode10(sender):
    return encode_abi(['uint256', 'address', 'uint256'], [uint256Limit, sender, 0])

def encode5(expectedMIMAmount):
    return encode_abi(['uint256', 'address'], [expectedMIMAmount, USTLevSwapper])

def encode30(sender, expectedMIMAmount):
    shareToMin = int(expectedMIMAmount / 100 * 95)
    swapFunctionId = "9f1d0f59"
    # append functionID 9f1d0f59 to beginning of calldata
    calldata = swapFunctionId + str(encode_abi(["address", "uint256"], [sender, shareToMin]).hex())
    return encode_abi(["address", "bytes", "bool", "bool", "uint8"], [USTLevSwapper, bytes.fromhex(calldata), False, True, 2])

def getTxData(sender, amount, expectedMIMAmount):
    calldata = cookFunctionId + str(encode_abi(['uint8[]', 'uint256[]', 'bytes[]'], 
        [
            [11, 20, 10, 5, 30, 10], 
            [0, 0, 0, 0, 0, 0], 
            [
                encode11(), 
                encode20(sender, amount), 
                encode10(sender), 
                encode5(expectedMIMAmount), 
                encode30(sender, expectedMIMAmount), 
                encode10(sender)
            ]]).hex()) + watermark
    return bytes.fromhex(calldata)
