import multidex
import asyncio

def price_impact_base(dex: multidex.Dex, amount: float, inToken: str, outToken: str, middleToken: str):
    liquidity_in = dex.liquidity_in(inToken, outToken, middleToken)
    liquidity_out = dex.liquidity_out(inToken, outToken, middleToken)
    price = liquidity_out / liquidity_in
    new_liquidity_in = liquidity_in + amount
    new_liquidity_out = (liquidity_in * liquidity_out) / new_liquidity_in
    newprice = new_liquidity_out / new_liquidity_in
    price_impact = (newprice - price) / price
    print("price_impact_base: amount {} price {} newprice {} price_impact {}".format(amount, price, newprice, price_impact))
    return price_impact

def price_impact_token(dex: multidex.Dex, amount: float, inToken: str, outToken: str, middleToken: str):
    liquidity_in = dex.liquidity_in(inToken, outToken, middleToken)
    liquidity_out = dex.liquidity_out(inToken, outToken, middleToken)
    price = liquidity_out / liquidity_in
    new_liquidity_out = liquidity_out + amount
    new_liquidity_in = (liquidity_in * liquidity_out) / new_liquidity_out
    newprice = new_liquidity_out / new_liquidity_in
    price_impact = (newprice - price) / price
    print("price_impact_token: amount {} price {} newprice {} price_impact {}".format(amount, price, newprice, price_impact))
    return price_impact

def buy(dex: multidex.Dex, token: str, amount: float, middleToken: str, wallet_address: str, private_key: str):
    if not dex.check_approval(wallet_address, token):
        raise Exception("UnapprovedExpection: " + wallet_address)
    tx = dex.swapFromBaseToTokens(amount, token, wallet_address, middleToken)
    signed_tx = dex.signTransaction(transaction = tx, private_key = private_key)
    tx_hash = dex.hash(signed_tx)
    print("Transaction Hash = ", tx_hash)
    tx_hash = dex.sendTransaction(signed_transaction = signed_tx)
    if not dex.waitTransaction(tx_hash):
        raise Exception("TransactionExpection: " + tx_hash.hex())
    tx["hash"] = tx_hash.hex()
    return tx

def sell(dex: multidex.Dex, token: str, amount: float, middleToken: str, wallet_address: str, private_key: str):
    if not dex.check_approval(wallet_address, token):
        raise Exception("UnapprovedExpection: " + wallet_address)
    tx = dex.swapFromTokensToBase(amount, token, wallet_address, middleToken)
    signed_tx = dex.signTransaction(transaction = tx, private_key = private_key)
    tx_hash = dex.hash(signed_tx)
    print("Transaction Hash = ", tx_hash)
    tx_hash = dex.sendTransaction(signed_transaction = signed_tx)
    if not dex.waitTransaction(tx_hash):
        raise Exception("TransactionExpection: " + tx_hash.hex())
    tx["hash"] = tx_hash.hex()
    return tx

def approve(dex: multidex.Dex, token: str, wallet_address: str, private_key: str):
    tx = dex.approve(token=token, address=wallet_address)
    signed_tx = dex.signTransaction(transaction = tx, private_key = private_key)
    tx_hash = dex.hash(signed_tx)
    print("Transaction Hash = ", tx_hash)
    tx_hash = dex.sendTransaction(signed_transaction = signed_tx)
    if not dex.waitTransaction(tx_hash):
        raise Exception("TransactionExpection: " + tx_hash.hex())
    tx["hash"] = tx_hash.hex()
    return tx

async def demo():
    dex0 = multidex.Stellaswap()
    dex1 = multidex.Zenlink()
    await main(
        wallet_address = "",
        private_key = "",
        dex0 = dex0,
        dex1 = dex1,
        amount = 5,
        min_gap = 0.01,
        path0_inToken = None,
        path0_outToken =  "0x818ec0a7fe18ff94269904fced6ae3dae6d6dc0b",
        path0_middleToken = dex0.token,
        path1_inToken = None,
        path1_outToken =  "0x818ec0a7fe18ff94269904fced6ae3dae6d6dc0b",
        path1_middleToken = dex1.token,
        )

async def main(
    wallet_address: str, private_key:str,
    dex0: multidex.Dex, dex1: multidex.Dex, 
    amount: float, min_gap: float,
    path0_inToken: str, path0_outToken: str, path0_middleToken,
    path1_inToken: str, path1_outToken: str, path1_middleToken):

    print("{}: liquidity_in {}".format(dex0.platform, dex0.liquidity_in(path0_inToken, path0_outToken, path0_middleToken)))
    print("{}: liquidity_out {}".format(dex0.platform, dex0.liquidity_out(path0_inToken, path0_outToken, path0_middleToken)))
    print("{}: liquidity_in {}".format(dex1.platform, dex1.liquidity_in(path1_inToken, path1_outToken, path1_middleToken)))
    print("{}: liquidity_out {}".format(dex1.platform, dex1.liquidity_out(path1_inToken, path1_outToken, path1_middleToken)))

    reserve0 = dex0.reserve_ratio(path0_inToken, path0_outToken, path0_middleToken)
    reserve1 = dex1.reserve_ratio(path1_inToken, path1_outToken, path1_middleToken)
    if reserve0 < reserve1:
        (dex_low, dex_high) = (dex0, dex1)
        (reserve_low, reserve_high) = (reserve0, reserve1)
        (path_low_inToken, path_low_outToken, path_low_middleToken) = (path0_inToken, path0_outToken, path0_middleToken)
        (path_high_inToken, path_high_outToken, path_high_middleToken) = (path1_inToken, path1_outToken, path1_middleToken)
    else:
        (dex_low, dex_high) = (dex1, dex0)
        (reserve_low, reserve_high) = (reserve1, reserve0)
        (path_low_inToken, path_low_outToken, path_low_middleToken) = (path1_inToken, path1_outToken, path1_middleToken)
        (path_high_inToken, path_high_outToken, path_high_middleToken) = (path0_inToken, path0_outToken, path0_middleToken)

    # calculte gap
    gap = (reserve_high - reserve_low) / reserve_high
    print("gap {}".format(gap))
    if gap <= 0 and gap <= min_gap:
        raise Exception("gap {} <= 0 , min_gap".format(gap, min_gap))

    # calculate price impact
    price_impact_high = price_impact_base(dex_high, amount, path_high_inToken, path_high_outToken, path_high_middleToken)
    amount_token = amount * dex_high.reserve_ratio(path_high_inToken, path_high_outToken, path_high_middleToken)
    price_impact_low = price_impact_token(dex_low, amount_token, path_low_inToken, path_low_outToken, path_low_middleToken)
    print("filter {}".format(gap - price_impact_low - price_impact_high))
    filter = gap - abs(price_impact_low) - abs(price_impact_high) 
    #if filter >= min_gap:
    #    print("filter {} >= min_gap {}".format(filter, min_gap))
    #    return

    # check approvals
    dex_high_token = path_high_outToken if path_high_inToken is None or path_high_inToken == dex0.base_address else path_high_inToken
    if not dex_high.check_approval(wallet_address, dex_high_token):
        print("approve token {} on {}".format(dex_high_token, dex_high.platform))
        approve(dex_high, dex_high_token, wallet_address, private_key)
    dex_low_token = path_low_outToken if path_low_inToken is None or path_low_inToken == dex1.base_address else path_low_inToken
    if not dex_low.check_approval(wallet_address, dex_low_token):
        print("approve token {} on {}".format(dex_low_token, dex_low.platform))
        approve(dex_low, dex_low_token, wallet_address, private_key)

    # check amount in balance
    inBalance = dex0.balance(wallet_address, path0_inToken)
    outBalance = dex0.balance(wallet_address, path0_outToken)
    baseBalance = dex0.balance(wallet_address, dex0.base_address)
    print("{}: inBalance {}".format(path0_inToken, inBalance))
    print("{}: outBalance {}".format(path0_outToken, outBalance))
    print("{}: baseBalance {}".format(dex0.base_address, baseBalance))

    if amount >= inBalance:
        raise Exception("amount {} >= balance {}".format(amount, inBalance))

    # swap from base to token
    print("{}: swap base to token: amount {}".format(dex_high.platform, amount))
    tx = buy(dex_high, dex_high_token, amount, path_high_middleToken, wallet_address, private_key)
    print(tx)

    print("{}: inBalance {}".format(path_high_inToken, dex_high.balance(wallet_address, path_high_inToken)))
    print("{}: outBalance {}".format(path_high_outToken, dex_high.balance(wallet_address, path_high_outToken)))

    # swap from token to base
    last_outBalance = dex0.balance(wallet_address, path_high_outToken)
    amount = last_outBalance - outBalance
    print("{}: swap token to base: amount {}".format(dex_low.platform, amount))
    tx = sell(dex_low, dex_low_token, amount, path_low_middleToken, wallet_address, private_key)
    print(tx)

    print("{}: inBalance {}".format(path_low_inToken, dex0.balance(wallet_address, path_low_inToken)))
    print("{}: outBalance {}".format(path_low_outToken, dex0.balance(wallet_address, path_low_outToken)))

    # profit / loss
    last_inBalance = dex0.balance(wallet_address, path_low_inToken)
    last_outBalance = dex0.balance(wallet_address, path_low_outToken)
    print("earn {}: {}".format(path_low_inToken, last_inBalance - inBalance))
    print("earn {}: {}".format(path_low_outToken, last_outBalance - outBalance))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(demo())