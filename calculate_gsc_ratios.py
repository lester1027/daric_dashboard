import numpy as np
epsilon = 9999999999


def calculate_gsc_ratios(capital_employed_all_cash_sub_1_yr, capital_employed_all_cash_sub_2_yr,
                         capital_employed_no_cash_sub_1_yr, capital_employed_no_cash_sub_2_yr,
                         operating_income_1_yr, operating_income_2_yr,
                         FCF_1_yr, FCF_2_yr,
                         BV_1_yr, BV_2_yr,
                         TBV_1_yr, TBV_2_yr,
                         fully_diluted_shares_1_yr, fully_diluted_shares_2_yr,
                         total_liabilities, market_cap, enterprise_value):
    # GSC return ROCE
    if capital_employed_all_cash_sub_2_yr == 0:
        print('[ERROR] ROCE_all_cash_sub: ZeroDivisionError')
        ROCE_all_cash_sub = epsilon
    elif operating_income_2_yr == epsilon or capital_employed_all_cash_sub_2_yr == epsilon or \
            type(operating_income_2_yr) == str or type(capital_employed_all_cash_sub_2_yr) == str:
        ROCE_all_cash_sub = epsilon
    else:
        ROCE_all_cash_sub = operating_income_2_yr / float(capital_employed_all_cash_sub_2_yr)

    if capital_employed_no_cash_sub_2_yr == 0:
        print('[ERROR] ROCE_no_cash_sub: ZeroDivisionError')
        ROCE_no_cash_sub = epsilon
    elif operating_income_2_yr == epsilon or capital_employed_no_cash_sub_2_yr == epsilon or \
            type(operating_income_2_yr) == str or type(capital_employed_no_cash_sub_2_yr) == str:
        ROCE_no_cash_sub = epsilon
    else:
        ROCE_no_cash_sub = operating_income_2_yr / float(capital_employed_no_cash_sub_2_yr)

    # GSC return FCFROCE
    if capital_employed_all_cash_sub_2_yr == 0:
        print('[ERROR] FCFROCE_all_cash_sub: ZeroDivisionError')
        FCFROCE_all_cash_sub = epsilon
    elif FCF_2_yr == epsilon or capital_employed_all_cash_sub_2_yr == epsilon or \
            type(FCF_2_yr) == str or type(capital_employed_all_cash_sub_2_yr) == str:
        FCFROCE_all_cash_sub = epsilon
    else:
        FCFROCE_all_cash_sub = FCF_2_yr / float(capital_employed_all_cash_sub_2_yr)

    if capital_employed_no_cash_sub_2_yr == 0:
        print('[ERROR] FCFROCE_no_cash_sub: ZeroDivisionError')
        FCFROCE_no_cash_sub = epsilon
    elif FCF_2_yr == epsilon or capital_employed_no_cash_sub_2_yr == epsilon or \
            type(FCF_2_yr) == str or type(capital_employed_no_cash_sub_2_yr) == str:
        FCFROCE_no_cash_sub = epsilon
    else:
        FCFROCE_no_cash_sub = FCF_2_yr/float(capital_employed_no_cash_sub_2_yr)

    # GSC growth d_OI_FDS_ratio

    if operating_income_2_yr == epsilon or fully_diluted_shares_2_yr == epsilon or \
            operating_income_1_yr == epsilon or fully_diluted_shares_1_yr == epsilon or \
            type(operating_income_2_yr) == str or type(fully_diluted_shares_2_yr) == str or \
            type(operating_income_1_yr) == str or type(fully_diluted_shares_1_yr) == str:
        d_OI_FDS_ratio = epsilon
    elif fully_diluted_shares_2_yr == 0 or fully_diluted_shares_1_yr == 0 or \
            (operating_income_1_yr/fully_diluted_shares_1_yr) == 0:
        print('[ERROR] d_OI_FDS_ratio: ZeroDivisionError')
        d_OI_FDS_ratio = epsilon
    else:
        d_OI_FDS_ratio = ((operating_income_2_yr/float(fully_diluted_shares_2_yr))-(
            operating_income_1_yr / float(fully_diluted_shares_1_yr)))/(operating_income_1_yr/float(fully_diluted_shares_1_yr))

    # GSC growth d_FCF_FDS_ratio

    if FCF_2_yr == epsilon or fully_diluted_shares_2_yr == epsilon or \
            FCF_1_yr == epsilon or fully_diluted_shares_1_yr == epsilon or \
            type(FCF_2_yr) == str or type(fully_diluted_shares_2_yr) == str or \
            type(FCF_1_yr) == str or type(fully_diluted_shares_1_yr) == str:
        d_FCF_FDS_ratio = epsilon
    elif fully_diluted_shares_2_yr == 0 or fully_diluted_shares_1_yr == 0 or \
            (operating_income_1_yr/fully_diluted_shares_1_yr) == 0:
        print('[ERROR] d_FCF_FDS_ratio: ZeroDivisionError')
        d_FCF_FDS_ratio = epsilon
    else:
        d_FCF_FDS_ratio = ((FCF_2_yr/float(fully_diluted_shares_2_yr)) -
                           (FCF_1_yr/float(fully_diluted_shares_1_yr)))/(FCF_1_yr/float(fully_diluted_shares_1_yr))

    # GSC growth d_BV_FDS_ratio

    if BV_2_yr == epsilon or fully_diluted_shares_2_yr == epsilon or \
            BV_1_yr == epsilon or fully_diluted_shares_1_yr == epsilon or \
            type(BV_2_yr) == str or type(fully_diluted_shares_2_yr) == str or \
            type(BV_1_yr) == str or type(fully_diluted_shares_2_yr) == str:
        d_BV_FDS_ratio = epsilon
    elif fully_diluted_shares_2_yr == 0 or fully_diluted_shares_1_yr == 0 or \
            (operating_income_1_yr/fully_diluted_shares_1_yr) == 0:
        print('[ERROR] d_BV_FDS_ratio: ZeroDivisionError')
        d_BV_FDS_ratio = epsilon
    else:
        d_BV_FDS_ratio = ((BV_2_yr/float(fully_diluted_shares_2_yr))-(
            BV_1_yr/float(fully_diluted_shares_1_yr)))/(BV_1_yr/float(fully_diluted_shares_1_yr))

    # GSC growth d_TBV_FDS_ratio

    if TBV_2_yr == epsilon or fully_diluted_shares_2_yr == epsilon or \
            TBV_1_yr == epsilon or fully_diluted_shares_1_yr == epsilon or \
            type(TBV_2_yr) == str or type(fully_diluted_shares_2_yr) == str or \
            type(TBV_1_yr) == str or type(fully_diluted_shares_2_yr) == str:
        d_TBV_FDS_ratio = epsilon
    elif fully_diluted_shares_2_yr == 0 or fully_diluted_shares_1_yr == 0 or \
            (operating_income_1_yr/fully_diluted_shares_1_yr) == 0:
        print('[ERROR] d_TBV_FDS_ratio: ZeroDivisionError')
        d_TBV_FDS_ratio = epsilon
    else:
        d_TBV_FDS_ratio = ((TBV_2_yr/float(fully_diluted_shares_2_yr))-(
            TBV_1_yr/float(fully_diluted_shares_1_yr)))/(TBV_1_yr/float(fully_diluted_shares_1_yr))

    # GSC le_ratio
    if BV_2_yr == 0:
        print('[ERROR] le_ratio: ZeroDivisionError')
        le_ratio = epsilon
    elif total_liabilities == epsilon or BV_2_yr == epsilon or \
            type(total_liabilities) == str or type(BV_2_yr) == str:
        le_ratio = epsilon
    else:
        le_ratio = total_liabilities/float(BV_2_yr)

    # GSC price MCAP_FCF_ratio
    if FCF_2_yr == 0:
        print('[ERROR] MCAP_FCF_ratio: ZeroDivisionError')
        MCAP_FCF_ratio = epsilon
    elif market_cap == epsilon or FCF_2_yr == epsilon or \
            type(market_cap) == str or type(FCF_2_yr) == str:
        MCAP_FCF_ratio = epsilon
    else:
        MCAP_FCF_ratio = market_cap/float(FCF_2_yr)

    # GSC price EV_OI_ratio
    if operating_income_2_yr == 0:
        print('[ERROR] EV_OI_ratio: ZeroDivisionError')
        EV_OI_ratio = epsilon
    elif enterprise_value == epsilon or operating_income_2_yr == epsilon or \
            type(enterprise_value) == str or type(operating_income_2_yr) == str:
        EV_OI_ratio = epsilon
    else:
        EV_OI_ratio = enterprise_value/float(operating_income_2_yr)

    # GSC price MCAP_BV_ratio
    if BV_2_yr == 0:
        print('[ERROR] MCAP_FCF_ratio: ZeroDivisionError')
        MCAP_FCF_ratio = epsilon
    elif market_cap == epsilon or BV_2_yr == epsilon or \
            type(market_cap) == str or type(BV_2_yr) == str:
        MCAP_FCF_ratio = epsilon
    else:
        MCAP_FCF_ratio = market_cap/float(BV_2_yr)

    # GSC price MCAP_TBV ratio
    if TBV_2_yr == 0:
        print('[ERROR] MCAP_TBV_ratio: ZeroDivisionError')
        MCAP_TBV_ratio = epsilon
    elif market_cap == epsilon or TBV_2_yr == epsilon or \
            type(market_cap) == str or type(TBV_2_yr) == str:
        MCAP_TBV_ratio = epsilon
    else:
        MCAP_TBV_ratio = market_cap/float(TBV_2_yr)

    ratio_dict = dict()

    ratio_dict['ROCE_all_cash_sub'] = ROCE_all_cash_sub
    ratio_dict['ROCE_no_cash_sub'] = ROCE_no_cash_sub
    ratio_dict['FCFROCE_all_cash_sub'] = FCFROCE_all_cash_sub
    ratio_dict['FCFROCE_no_cash_sub'] = FCFROCE_no_cash_sub
    ratio_dict['d_OI_FDS_ratio'] = d_OI_FDS_ratio
    ratio_dict['d_FCF_FDS_ratio'] = d_FCF_FDS_ratio
    ratio_dict['d_BV_FDS_ratio'] = d_BV_FDS_ratio
    ratio_dict['d_TBV_FDS_ratio'] = d_TBV_FDS_ratio
    ratio_dict['le_ratio'] = le_ratio
    ratio_dict['MCAP_FCF_ratio'] = MCAP_FCF_ratio
    ratio_dict['EV_OI_ratio'] = EV_OI_ratio
    ratio_dict['MCAP_FCF_ratio'] = MCAP_FCF_ratio
    ratio_dict['MCAP_TBV_ratio'] = MCAP_TBV_ratio

    return ratio_dict
