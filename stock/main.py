import Common
from Common.LoadData import Global_DB
from Common.Similarity import find_similarity
from Common.CandleStick import candle_stick
import logging
import Config
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import sklearn


def init_logging():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def stock_find_similarity(df, db):
    # use last 30 days as answer and former 30 days as test input
    sample_a = df.tail(60).head(60)
    sample_a_ans = df.tail(30)
    # candle_stick(sample_a, 'TEST INPUT')
    # candle_stick(sample_a_ans, 'TEST OUTPUT')
    ret, ret_ans = find_similarity(sample_a, db, step=1000, n_similar=2)
    for key in ret.keys():
        candle_stick(ret[key], 'Similar match at ' + str(key))
        candle_stick(ret_ans[key], 'ANSWER ' + str(key))


def async_find_similarity():
    executor = ThreadPoolExecutor(max_workers=100)
    for _, stock_type in zip(np.arange(0, 2, 1), Global_DB):
        for _, stock_id in zip(np.arange(0, 2, 1), Global_DB[stock_type]):
            df = Global_DB[stock_type][stock_id]
            executor.submit(stock_find_similarity, df, Global_DB)


def main():
    init_logging()

    logging.info("Main Program is running")
    Common.load_data(Config.PATH)
    # Common.candle_stick('SH#600000', Common.Global_DB['sha']['SH#600000'])

    sample_a = Global_DB['sha']['SH#600000'].tail(60).head(30)
    n, sims = find_similarity(sample_a, Global_DB)
    for key in sims.keys():
        candle_stick('', sims[key])

    # async_find_similarity()


if __name__ == "__main__":
    main()
