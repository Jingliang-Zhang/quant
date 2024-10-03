from scipy.spatial import distance
import time
from progress.bar import Bar
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import logging
import pytz


def chebyshev_fit(series, deg):
    x = np.arange(0, series.shape[0], 1)
    y = series

    p = np.polynomial.Chebyshev.fit(x, y, deg)
    y_fit = p(x)

    return y_fit


def sort_and_truncat(result, result_ans, n_similar):
    ret = {}
    ret_ans = {}
    for n, key in zip(np.arange(0, n_similar, 1), sorted(result.keys())):
        ret[key] = result[key]
        ret_ans[key] = result_ans[key]

    logging.info('return {} most similar samples'.format(len(ret)))
    return ret, ret_ans


def find_similarity(sample_a, db, step=1, n_similar=10, reg=True, deg=9, lcr_threshold=0.005):
    sample_a_name = sample_a['Name'][0]
    logging.info(
        'Find similarity for {} in period [{} {}]'.format(sample_a_name, sample_a.index[0], sample_a.index[-1]))
    period = sample_a.shape[0]

    change_a = sample_a['Change']
    fit_a = chebyshev_fit(change_a, deg)

    close_a = sample_a['Close']
    linear_fit_a = chebyshev_fit(close_a, 1)
    lcr_a = (linear_fit_a[-1] - linear_fit_a[0]) / linear_fit_a[0]

    result = {}
    result_ans = {}

    for stock_type in db:
        start_time = time.time()
        # logging.info('Find similarity in {} for {}'.format(stock_type, sample_a_name))

        stock_ids_cnt = len(db[stock_type])
        progress_bar = Bar('Find similarity in {} for {}'.format(stock_type, sample_a_name), max=stock_ids_cnt)
        progress_bar.check_tty = False

        for stock_id in db[stock_type]:

            df = db[stock_type][stock_id]

            idx = df.shape[0] - period
            for i in np.arange(0, idx, step):
                sample_b = df.iloc[i: i + period]

                # calculate linear change rate, ignore exceeds +-0.5%
                close_b = sample_b['Close']
                linear_fit_b = chebyshev_fit(close_b, 1)
                lcr_b = (linear_fit_b[-1] - linear_fit_b[0]) / linear_fit_b[0]

                if lcr_b < lcr_a - lcr_threshold or lcr_b > lcr_a + lcr_threshold:
                    continue

                # get another sample_b, which start from row i and contains period rows
                change_b = sample_b['Change']
                fit_b = chebyshev_fit(change_b, deg)

                # chebyshev distance
                dist = distance.chebyshev(fit_a, fit_b)
                result[dist] = sample_b

                sample_b_ans_end = i + 2 * period
                if sample_b_ans_end > df.shape[0]:
                    sample_b_ans_end = df.shape[0]
                sample_b_ans = df.iloc[i + period: sample_b_ans_end]
                result_ans[dist] = sample_b_ans
            progress_bar.next()
        progress_bar.finish()

        logging.info('Find similarity in {} for {} end, time elapse {} seconds'.format(stock_type, sample_a_name,
                                                                                       time.time() - start_time))
        # HACK: tmp break to only use sha
        break

    logging.info('result length is {}'.format(len(result)))

    return sort_and_truncat(result, result_ans, n_similar)

