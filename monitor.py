import asyncio
import multidex
import datetime
import calendar
import sys
import os
import json
import logging

class Config:
    def __init__(self, base, input, output, routing, indecimals, outdecimals, min_gap, timeout, daemon):
        self.base = base
        self.input = input
        self.output = output
        self.routing = routing
        self.indecimals = indecimals
        self.outdecimals = outdecimals
        self.min_gap = min_gap
        self.timeout = timeout
        self.daemon = daemon
    
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
      return Config(json['base'],
                   json['input'], json['output'], json['routing'],
                   json['indecimals'], json['outdecimals'], json['min_gap'],
                   json['timeout'], json['daemon'])

async def looper():
    config_file = sys.argv[1]
    conf = Config.read(config_file)
    file_handler = logging.FileHandler(filename=conf.log_file)
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers = [file_handler, stdout_handler]
    while True:
        try:
            await main(conf)
        except Exception as err:
            print("ERROR {err}")
        finally:
            if not conf.daemon:
                return
            await asyncio.sleep(conf.timeout)

async def main(conf ):
    values = {}
    for dex in multidex.__all__:
        if dex.base_symbol == conf.base:
            input = conf.input if conf.input is not None else dex.base_address
            output = conf.output if conf.output is not None else dex.base_address
            if conf.indecimals is not None:
                dex.decimals(input, fallback = int(conf.indecimals))
            if conf.outdecimals is not None:
                dex.decimals(output, fallback = int(conf.outdecimals))
            intermediate = None
            if dex.exist(input, output):
                value = dex_read(dex, input, output)
                if value['reserves'][0] > 1 and value['reserves'][1] > 1:
                    values[dex.platform] = value
            intermediate = dex.token
            if dex.exist(input, output, intermediate):
                value = dex_read(dex, input, output, intermediate)
                if value['reserves'][0] > 1 and value['reserves'][1] > 1:
                    values[dex.platform + "_dexcoin"] = value

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
                list = out.values()
                text = ', '.join([str(x) for x in list])
                print(text)
                appendcsv(conf.csv_file, out)

def dex_read(dex, input, output, intermediate = None):
    return {
        'platform': dex.platform,
        'price': dex.price(input, output, intermediate),
        'reserves': dex.reserves(input, output, intermediate, refresh = True),
        'reserve_ratio': dex.reserve_ratio(input, output, intermediate),
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