from src import plot as pl
pl.vnquant_candle_stick(data='TCB',
                        title='TCB symbol from 2022-01-01 to 2022-10-01',
                        xlab='Date', ylab='Price',
                        start_date='2022-01-01',
                        end_date='2022-10-01',
                        data_source='cafe',
                        show_advanced=['volume', 'macd'])