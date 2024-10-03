import os
import pandas as pd
from progress.bar import Bar
import logging
import time


Global_DB = {}


def init_change_rate(db):
    for stock_type in db:
        for stock_id in db[stock_type]:
            db[stock_type][stock_id]['Change'] = db[stock_type][stock_id]['Close'].pct_change().fillna(0)
            db[stock_type][stock_id]['Change_Week'] = db[stock_type][stock_id]['Close'].pct_change(periods=7).fillna(0)
            db[stock_type][stock_id]['Change_Month'] = db[stock_type][stock_id]['Close'].pct_change(periods=30).fillna(0)


def add_stock_name(db):
    for stock_type in db:
        for stock_id in db[stock_type]:
            db[stock_type][stock_id]['Name'] = stock_id


def load_data(path):
    logging.info('Reading stock data files under directory {}'.format(path))
    stock_types = os.listdir(path)
    for stock_type in stock_types:
        if os.path.isdir(path + '\\' + stock_type):
            logging.info('Start loading {} stock data'.format(stock_type))
            Global_DB[stock_type] = {}
            start_time = time.time()
            stock_ids = os.listdir(path + '\\' + stock_type)
            stock_ids_cnt = len(stock_ids)

            progress_bar = Bar('Loading ' + stock_type + ' stock data', max=stock_ids_cnt)
            progress_bar.check_tty = False
            for stock_id in stock_ids:
                df = pd.read_csv(path + '\\' + stock_type + '\\' + stock_id, delimiter='	', encoding='latin_1', header=1, engine='python',
                                 skipfooter=2,
                                 names=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Volume_Amount'],
                                 index_col=0, parse_dates=True)
                Global_DB[stock_type][stock_id.replace('.txt', '')] = df
                progress_bar.next()
            progress_bar.finish()
            logging.info('End loading {} stock data, elapsed time {} seconds'.format(stock_type, round(time.time() - start_time)))

    logging.info('End reading stock data files under directory {}'.format(path))

    # Generate change rate based on 'Close'
    init_change_rate(Global_DB)
    add_stock_name(Global_DB)
