import asyncio
import multidex
import datetime
import calendar
import sys
import os
import json
import logging

class Config:
    def __init__(self, chain, input, output, routing, indecimals, outdecimals, min_gap, min_base_liquidity, timeout, daemon, dexes):
        self.chain = chain
        self.input = input
        self.output = output
        self.routing = routing
        self.indecimals = indecimals
        self.outdecimals = outdecimals
        self.min_gap = min_gap
        self.min_base_liquidity = min_base_liquidity
        self.timeout = timeout
        self.daemon = daemon
        self.dexes = dexes
    
    @staticmethod
    def read(conf_file):
        file = open(conf_file)
        conf = file.read()
        file.close()
        res = json.loads(conf, object_hook=Config.from_json)
        filename = os.path.basename(conf_file)
        res.log_file = f"{filename}.log"
        res.csv_file = f"{filename}.csv"
        return res

    @staticmethod
    def from_json(json):
      return Config(json['chain'],
                   json['input'], json['output'], json['routing'],
                   json['indecimals'], json['outdecimals'], json['min_gap'], json['min_base_liquidity'],
                   json['timeout'], json['daemon'], json['dexes'])

async def looper():
    config_file = "config.json"#sys.argv[1]
    conf = Config.read(config_file)
    file_handler = logging.FileHandler(filename=conf.log_file)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    while True:
        try:
            await main(conf)
        except Exception as err:
            print("ERROR", err)
        finally:
            if not conf.daemon:
                return
            await asyncio.sleep(conf.timeout)

async def main(conf):
    values = {}
    block_number = multidex.all[conf.chain.lower()][0].block_number()
    print ("block_number: {}".format(block_number))

    for dex in multidex.all[conf.chain.lower()]:
        if dex.platform in conf.dexes.split(','):
            input = conf.input if conf.input is not None else dex.base_address
            output = conf.output if conf.output is not None else dex.base_address
            intermediate = None
            if dex.exist(input, output):
                value = dex_read(dex, input, output)
                if value['liquidity_in'] > conf.min_base_liquidity and value['price'] != 0 and value['liquidity_out'] > conf.min_base_liquidity * value['price']:
                    values[dex.platform] = value
            #intermediate = dex.token
            #if dex.exist(input, output, intermediate):
            #    value = dex_read(dex, input, output, intermediate)
            #    if value['liquidity_in'] > conf.min_base_liquidity and value['price'] != 0 and value['liquidity_out'] > conf.min_base_liquidity * value['price']:
            #        values[dex.platform + "_dexcoin"] = value

    res = []
    for k, v in values.items():
        for kk, vv in values.items():
            gap = (v['reserve_ratio'] - vv['reserve_ratio']) / v['reserve_ratio']
            if gap !=0 and gap > conf.min_gap:
                now = datetime.datetime.now()
                out = {
                    "timestamp": calendar.timegm(now.utctimetuple()),
                    'gap': gap
                }
                dex0 = dict(map(lambda kv: ('dex0_' + kv[0], kv[1]), v.items()))
                dex1 = dict(map(lambda kv: ('dex1_' + kv[0], kv[1]), vv.items()))
                out = {**out, **dex0}
                out = {**out, **dex1}
                list_ = out.values()
                text = ', '.join([str(x) for x in list_])
                print(text)
                appendcsv(conf.csv_file, out)
                res.append(out)
    return res

def dex_read(dex, input, output, intermediate = None):
    return {
        'platform': dex.platform + ('' if intermediate is None else '_dexcoin'),
        'price': dex.price(input, output, intermediate),
        'reserve_ratio': dex.reserve_ratio(input, output, intermediate, refresh = True),
        'liquidity_in': dex.liquidity_in(input, output, intermediate),
        'liquidity_out': dex.liquidity_out(input, output, intermediate)
    }

def appendcsv(file, dict):
    exist = os.path.exists(file)
    file = open(file, 'a')
    if not exist:
        header = ', '.join([str(x) for x in dict.keys()])
        file.write(header + '\r\n')
    item = ', '.join([str(x) for x in dict.values()])
    file.write(item + '\r\n')
    file.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(looper())