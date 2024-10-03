import numpy as np
import pandas as pd
import os
import logging
from progress.bar import Bar
import time
import matplotlib.pyplot as plt

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

RESULT_DIR = 'C:\\export\\result_sha_9_deg'
period = 20

orig_result = {}

stocks = os.listdir(RESULT_DIR)
progress_bar = Bar('Loading stocks', max=len(stocks))
progress_bar.check_tty = False
samples_cnt = 0
answers_cnt = 0
start_time = time.time()
for stock in stocks:

    result_files = os.listdir('{}\\{}'.format(RESULT_DIR, stock))

    orig_result[stock] = {}
    orig_result[stock]['answer'] = []

    for result_file in result_files:

        if result_file.startswith('sample'):
            orig_result[stock]['sample'] = pd.read_csv('{}\\{}\\{}'.format(RESULT_DIR, stock, result_file))
            samples_cnt += 1
        elif result_file.startswith('answer'):
            orig_result[stock]['answer'].append(pd.read_csv('{}\\{}\\{}'.format(RESULT_DIR, stock, result_file)))
            answers_cnt += 1

    progress_bar.next()

progress_bar.finish()
logging.info(
    '{} stock results loaded, including {} samples and {} answers'.format(len(stocks), samples_cnt, answers_cnt))
logging.info(
    'average answers per sample is {}, {} seconds elapsed'.format(answers_cnt / samples_cnt, time.time() - start_time))

len(orig_result)

columns = ['sample_change',
           'ans_change_list', 'ans_cnt', 'ans_mean', 'ans_std']
result_df = pd.DataFrame(columns=columns)
progress_bar = Bar('Parsing origin result', max=len(stocks))
progress_bar.check_tty = False

for stock_id in sorted(orig_result.keys()):

    sample_df = orig_result[stock_id]['sample']
    sample_name = sample_df['Name'][0]

    if sample_name == 'SH#600802':
        print(sample_name)


    sample_df_part1 = sample_df.head(period)
    sample_df_part2 = sample_df.tail(sample_df.shape[0] - period)

    sample_change = (sample_df_part2['Close'].iloc[-1] - sample_df_part2['Close'].iloc[0]) / sample_df_part2['Close'].iloc[0]

    ans_change_list = []
    for ans_df in orig_result[stock_id]['answer']:
        ans_df_part1 = ans_df.head(period)
        # print('ans_df_part1 = {}'.format(ans_df_part1))
        ans_df_part2 = ans_df.tail(ans_df.shape[0] - period)
        # print('ans_df_part2 = {}'.format(ans_df_part2))
        # total change rate
        first_close = ans_df_part2['Close'].iloc[0]
        last_close = ans_df_part2['Close'].iloc[-1]
        total_change = (last_close - first_close) / first_close
        # print('{} {} {}'.format(first_close, last_close, total_change))
        ans_change_list.append(total_change)

    np_ans_change_list = np.array(ans_change_list)
    # print(np_ans_change_list)

    # new row for per stock sample
    row = pd.Series({
        'sample_change': sample_change,
        'ans_change_list': np_ans_change_list,
        'ans_cnt': np_ans_change_list.shape[0],
        'ans_mean': np_ans_change_list.mean(),
        'ans_std': np_ans_change_list.std()
    },
        name=sample_name)

    # print(row)
    # append row to result_df
    result_df = result_df.append(row)

    progress_bar.next()
progress_bar.finish()

result_df

