import monitor
import trade
import multidex
import os
import logging
import sys
import asyncio
import json

conf_dir = 'configs'
log_file = 'bot.log'

file_handler = logging.FileHandler(filename=log_file)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=handlers)

async def looper():
    while True:
        #try:
        await main()
        await asyncio.sleep(30)
        #except Exception as err:
        #    print("ERROR", err)
        #finally:
        #    await asyncio.sleep(30)

async def main():
    for filename in os.listdir(conf_dir):
        f = os.path.join(conf_dir, filename)
        if os.path.isfile(f) and filename.startswith('config_') and filename.endswith('.json'):
            conf = monitor.Config.read(f)
            gap = await monitorize(conf, filename)
            await trading(conf, gap)

async def monitorize(conf: monitor.Config, filename: str):
    gaps = await monitor.main(conf)
    logging.info("> {} {} gaps".format(filename, len(gaps)))
    if len(gaps) == 0:
        return None
    max = gaps[0]
    for gap in gaps:
        if gap['gap'] > max['gap']:
            max = gap
    logging.info("> {} gap: {} vs {}".format(max['gap'], max['dex0_platform'], max['dex1_platform']))
    logging.info("> {}".format(max))
    return max

async def trading(conf: monitor.Config, gap: dict):
    if gap is None:
        return
    filename = "wallet_" + conf.base.upper() + ".json"
    f = os.path.join(conf_dir, filename)
    if not os.path.isfile(f):
        logging.info("> {} not found".format(filename))
        return
    file = open(f)
    walletconf = json.loads(file.read())
    file.close()

    for dex in multidex.__all__:
        if dex.platform == gap['dex0_platform'].replace("_dexcoin", ""):
            dex0 = dex
        if dex.platform == gap['dex1_platform'].replace("_dexcoin", ""):
            dex1 = dex

    await trade.main(
        wallet_address = walletconf['wallet_address'],
        private_key = walletconf['private_key'],
        dex0 = dex0,
        dex1 = dex1,
        amount = walletconf['amount'],
        min_gap = walletconf['min_gap'],
        path0_inToken = conf.input,
        path0_outToken = conf.output,
        path0_middleToken = dex0.token if gap['dex0_platform'].endswith('_dexcoin') else None,
        path1_inToken = conf.input,
        path1_outToken = conf.output,
        path1_middleToken = dex1.token if gap['dex1_platform'].endswith('_dexcoin') else None,
        )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(looper())