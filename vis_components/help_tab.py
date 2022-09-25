import dash
from dash_extensions.enrich import Output, State, Input, html, ALL, dcc, dash_table

from main_dash import app

tab_help_layout = dcc.Markdown(
    '''

    ## What is Daric Dashboard?
    - It is a dashboard for calculating, screening and comparing stock metrics for value intesting. \n
    - It provides users with references for looking for high quality stocks in the long run.

    ## What is Daric Dashboard not?
    - It is not for the prediction of short- or long-term stock price fluctuation.

    ## Usage steps
    1. Select the stocks you are interested in from the drop-down list. \n
    2. Click the 'Refresh Data' button. \n
    3. Wait for the data update. \n
    4. Click the 'Data' tab and edit the 'long_term_growth_rate'. Press 'Enter' to confirm the change. \n
        (The API used by Daric does not support a valid growth rate yet.) \n
    5. Go back to the 'Visualization' tab to look at the metrics evaluation. \n
        The metrics in blue pass the screening and the ones in red fail. \n
        The line charts show the trends of the metrics.
    6. The data tables in the 'Metrics' and the 'Data' tabs are editable for matching customization needs. \n
        (Editing the entries in the 'Data' tab will modify the stock raw data and the metrics will be recalculated. \n
        Editing the entries in the 'Metrics' tab will only modify the stock metrics while leaving the raw data unchanged.)

    ## Metrics
    | Name | Symbol | Formula | Benchmark | Remark |
    |------|--------|---------|-----------|--------|
    |Discounted Intrinsic Value per Share|dis_intrinsic_value|$$\\frac{Present\ Value + Terminal\ Value + Cash - Debt}{Shares\ Outstanding} \\times (1 - safety\ margin)$$|> stock price|The core metric of a stock. It indicates the true value of the stock.|
    |Market Capitalization to Levered Free Cash Flow|MCAP_to_FCF|$$\\frac{Market\ Capitalization}{Levered\ Free\ Cash\ Flow}$$|<= 8|It weighs the price of the common stock against what cash accounting says comes out after interest and taxes.|
    |Market Capitalization to Book Value|MCAP_to_BV|$$\\frac{Market\ Capitalization}{Book\ Value}=\\frac{Market\ Capitalization}{Stockholders'\ Equity}$$|<= 3|The price relative to the value of the company dead.|
    |Market Capitalization to Tangible Book Value|MCAP_to_TBV|$$\\frac{Market\ Capitalization}{Tangible\ Book\ Value}=\\frac{Market\ Capitalization}{Book\ Value-Inangible\ Assets}$$|<= 3|The price relative to the value of the company dead. This is stricter than MCAP_to_BV.|
    |Return on Capital Employed|ROCE|$$\\frac{Operating\ Income}{Capital\ Employed}$$|>= 0.15|This shows how much money a business 'made' relative to the amount of capital it 'needed'.|
    |Free Cash Flow Return on Captial Employed|FCFROCE|$$\\frac{Levered\ Free\ Cash\ Flow}{Capital\ Employed}$$|>= 0.08|This shows how much money a business 'made' relative to the amount of capital it 'needed'. Unlike ROCE, it captures interest, tax, and the normal cash cycle.|
    |Growth in Operating Income per Fully Diluted Share|dOI_to_FDS|$$\\frac{\\frac{operating\ income}{fully\ diluted\ shares}_{2nd}-\\frac{operating\ income}{fully\ diluted\ shares}_{1st}}{\\frac{operating\ income}{fully\ diluted\ shares}_{1st}}$$|>= inflation rate|        |
    |Growth in Free Cash Flow per Fully Diluted Share|dFCF_to_FDS|$$\\frac{\\frac{levered\ free\ cash\ flow}{fully\ diluted\ shares}_{2nd}-\\frac{levered\ free\ cash\ flow}{fully\ diluted\ shares}_{1st}}{\\frac{levered\ free\ cash\ flow}{fully\ diluted\ shares}_{1st}}$$|>= inflation rate|        |
    |Growth in Book Value per Fully Diluted Share|dBV_to_FDS|$$\\frac{\\frac{book\ value}{fully\ diluted\ shares}_{2nd}-\\frac{book\ value}{fully\ diluted\ shares}_{1st}}{\\frac{book\ value}{fully\ diluted\ shares}_{1st}}$$|>= inflation rate|It shows the increase in worth over time from a strict accounting standpoint.|
    |Growth in Tangible Book Value per Fully Diluted Share|dTBV_to_FDS|$$\\frac{\\frac{tangible\ book\ value}{fully\ diluted\ shares}_{2nd}-\\frac{tangible\ book\ value}{fully\ diluted\ shares}_{1st}}{\\frac{tangible\ book\ value}{fully\ diluted\ shares}_{1st}}$$|>= inflation rate|        |
    |Liabilities-to-equity Ratio|liab_to_equity|$$\\frac{Liabilities}{Equity}$$|<= 2|It is a measure of the company\'s indebtedness.|
    |Enterprise Value to Operating Income|EV_to_OI|$$\\frac{Enterprise\ Value}{Operating\ Income}$$|<= 7|It weights the price of the whole company against what accrual accounting says comes out before interest and taxes.|
    ''',
    mathjax=True,
)