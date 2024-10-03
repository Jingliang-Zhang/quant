import mplfinance as mpl


def candle_stick(df, desc=None):
    note = ''
    if desc is not None:
        note = desc

    mpl.plot(df, type='candle', linecolor='#00ff00', volume=True, show_nontrading=False, figscale=1,
             figratio=[8, 5.75],
             title='{}\n[{} {}]\n{}'.format(note, df.index[0], df.index[-1], df['Name'][0]), ylabel='OHLC Candle',
             ylabel_lower='Shares\nTraded', style='mike', mav=[3, 6, 9])