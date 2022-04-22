import asyncio
import multidex
import argparse
import datetime
import calendar
from os import path

from pyrsistent import v

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--base", help = "Select base for chain")
    parser.add_argument("-i", "--input", help = "Select input token address (default base address)")
    parser.add_argument("-o", "--output", help = "Select output token address (default base address)")
    parser.add_argument("-r", "--routing", help = "Allow intermediate token address (default disabled, * = custom dex token)")
    parser.add_argument("-j", "--indecimals", help = "Set input token decimals (default 18)")
    parser.add_argument("-q", "--outdecimals", help = "Set output token decimals (default 18)")
    return parser.parse_args()

async def main():
    args = get_arguments()

    args.output = "0x818ec0a7fe18ff94269904fced6ae3dae6d6dc0b"
    args.outdecimals = 6
    args.base = "GLMR"
    #args.routing = "*"
    args.min_gap = 0.005
    args.max_priceimpact = 0.01

    values = {}
    for dex in multidex.__all__:
        if dex.base_symbol == args.base:
            input = args.input if args.input is not None else dex.base_address
            output = args.output if args.output is not None else dex.base_address
            if args.indecimals is not None:
                dex.decimals(input, fallback = int(args.indecimals))
            if args.outdecimals is not None:
                dex.decimals(output, fallback = int(args.outdecimals))
            intermediate = None
            if dex.exist(input, output):
                value = {
                    'price': dex.price(input, output, intermediate),
                    'reserves': dex.reserves(input, output, intermediate),
                    'reserve_ratio': dex.reserve_ratio(input, output, intermediate),
                    'liquidity': dex.liquidity(input, output)
                }
                if value['reserves'][0] > 1 and value['reserves'][1] > 1:
                    values[dex.platform] = value

            intermediate = dex.token
            if dex.exist(input, output, intermediate):
                value = {
                    'price': dex.price(input, output, intermediate),
                    'reserves': dex.reserves(input, output, intermediate),
                    'reserve_ratio': dex.reserve_ratio(input, output, intermediate),
                    'liquidity': dex.liquidity(input, output)
                }
                if value['reserves'][0] > 1 and value['reserves'][1] > 1:
                    values[dex.platform + "_dexcoin"] = value

    for k, v in values.items():
        for kk, vv in values.items():
            gap = (v['reserve_ratio'] - vv['reserve_ratio']) / v['reserve_ratio']
            if gap !=0 and gap > args.min_gap:
                now = datetime.datetime.now()
                out = {
                    "timestamp": calendar.timegm(now.utctimetuple()),
                    'gap': gap
                }
                out = {**out, **dex_output(k, v)}
                out = {**out, **dex_output(kk, vv)}
                list = out.values()
                text = ', '.join([str(x) for x in list])
                print(text)

def dex_output(platform, dex):
    return {        
        platform + '': platform,
        platform + '_reserve_ratio': dex['reserve_ratio'],
        platform + '_reserves0': dex['reserves'][0],
        platform + '_reserves1': dex['reserves'][1],
        platform + '_price': dex['price'] }


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())