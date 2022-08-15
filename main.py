import asyncio
import web3dex
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--chain", help = "Select chain")
    parser.add_argument("-i", "--input", help = "Select input token address (default base address)")
    parser.add_argument("-o", "--output", help = "Select output token address (default base address)")
    parser.add_argument("-r", "--routing", help = "Allow intermediate token address (default disabled, * = custom dex token)")
    return parser.parse_args()

async def main():
    args = get_arguments()

    print("{:<12} {:<20} {:<20} {:<20} {:<20}".format('Dex','Price','Reserve','Liquidity In','Liquidity Out'))
    values = {}
    for dex in web3dex.all[args.chain.lower()]:
        input = args.input if args.input is not None else dex.base_address
        output = args.output if args.output is not None else dex.base_address
        intermediate = args.routing if args.routing is not None else None
        intermediate = dex.token if args.routing == "*" else intermediate
        if dex.exist(input, output, intermediate):
            value = {
                'price': dex.price(input, output, intermediate),
                'reserve_ratio': dex.reserve_ratio(input, output, intermediate, refresh = True),
                'liquidity_in': dex.liquidity_in(input, output, intermediate),
                'liquidity_out': dex.liquidity_out(input, output, intermediate)
            }
            values[dex.platform] = value
            print("{:<12} {:<20} {:<20} {:<20} {:<20}".format(
                dex.platform, 
                value['price'],
                value['reserve_ratio'],  
                value['liquidity_in'],
                value['liquidity_out']))
    print("")
    header = list(values.keys())
    header.insert(0, "")
    format_row = "{:<12}" * (len(header)+1)
    print(format_row.format("", *header))
    for k, v in values.items():
        gaps = [k]
        for kk, vv in values.items():
            gap = (v['reserve_ratio'] - vv['reserve_ratio']) / v['reserve_ratio']
            gaps.append(round(gap, 6))
        print(format_row.format("", *gaps))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())