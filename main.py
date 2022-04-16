import asyncio
import multidex
import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--base", help = "Select base for chain")
    parser.add_argument("-i", "--input", help = "Select input token address (default base address)")
    parser.add_argument("-o", "--output", help = "Select output token address (default base address)")
    parser.add_argument("-j", "--indecimals", help = "Set input token decimals (default 18)")
    parser.add_argument("-q", "--outdecimals", help = "Set output token decimals (default 18)")
    return parser.parse_args()


async def main():
    args = get_arguments()
    print("{:<12} {:<20} {:<20} {:<20}".format('Dex','Price','Reserve','Liquidity'))
    values = {}
    for dex in multidex.__all__:
        if dex.base_symbol == args.base:
            input = args.input if args.input is not None else dex.base_address
            output = args.output if args.output is not None else dex.base_address
            if args.indecimals is not None:
                dex.decimals(input, fallback = int(args.indecimals))
            if args.outdecimals is not None:
                dex.decimals(output, fallback = int(args.outdecimals))
            if dex.exist(input, output):
                value = {
                    'price': dex.price(input, output),
                    'reserve_ratio': dex.reserve_ratio(input, output),
                    'liquidity': dex.liquidity(input, output)
                }
                values[dex.platform] = value
                print("{:<12} {:<20} {:<20} {:<20}".format(
                    dex.platform, 
                    value['price'],
                    value['reserve_ratio'], 
                    value['liquidity']))
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