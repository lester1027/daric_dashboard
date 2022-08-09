import numpy as np

def calc_ROCE(operating_income, capital_employed):
    return operating_income / capital_employed

def calc_FCFROCE(free_cash_flow, capital_employed):
    return free_cash_flow / capital_employed

def calc_dOI_to_FDS(operating_income_1, operating_income_2, fully_diluted_shares_1, fully_diluted_shares_2):
    OI_to_FDS_1 = (operating_income_1 / fully_diluted_shares_1)
    OI_to_FDS_2 = (operating_income_2 / fully_diluted_shares_2)
    return (OI_to_FDS_2 - OI_to_FDS_1) / OI_to_FDS_1

def calc_dFCF_to_FDS(levered_FCF_1, levered_FCF_2, fully_diluted_shares_1, fully_diluted_shares_2):
    FCF_to_FDS_1 = levered_FCF_1 / fully_diluted_shares_1
    FCF_to_FDS_2 = levered_FCF_2 / fully_diluted_shares_2
    return (FCF_to_FDS_2 - FCF_to_FDS_1) / FCF_to_FDS_1

def calc_dBV_to_FDS(book_value_1, book_value_2, fully_diluted_shares_1, fully_diluted_shares_2):
    BV_to_FDS_1 = book_value_1 / fully_diluted_shares_1
    BV_to_FDS_2 = book_value_2 / fully_diluted_shares_2

    return (BV_to_FDS_2 - BV_to_FDS_1) / BV_to_FDS_1

def calc_dTBV_to_FDS(tangible_book_value_1, tangible_book_value_2, fully_diluted_shares_1, fully_diluted_shares_2):
    TBV_to_FDS_1 = tangible_book_value_1 / fully_diluted_shares_1
    TBV_to_FDS_2 = tangible_book_value_2 / fully_diluted_shares_2

    return (TBV_to_FDS_2 - TBV_to_FDS_1) / TBV_to_FDS_1

def calc_liab_to_equity(liability, equity):
    return liability / equity

def calc_MCAP_to_FCF(market_capital, free_cash_flow):
    return market_capital / free_cash_flow

def calc_EV_to_OI(enterprise_value, operating_income):
    return enterprise_value / operating_income

def calc_MCAP_to_BV(market_capital, book_value):
    return market_capital / book_value

def calc_MCAP_to_TBV(market_capital, tangible_book_value):
    return market_capital / tangible_book_value