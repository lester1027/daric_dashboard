import numpy as np


def calculate_gsc_ratios(capital_employed_all_cash_sub_1_yr, capital_employed_all_cash_sub_2_yr,
                         capital_employed_no_cash_sub_1_yr, capital_employed_no_cash_sub_2_yr,
                         operating_income_1_yr, operating_income_2_yr,
                         FCF_1_yr, FCF_2_yr,
                         BV_1_yr, BV_2_yr,
                         TBV_1_yr, TBV_2_yr,
                         fully_diluted_shares_1_yr, fully_diluted_shares_2_yr,
                         total_liabilities, market_cap, enterprise_value):
    # GSC return ROCE
    ROCE_all_cash_sub = operating_income_2_yr / capital_employed_all_cash_sub_2_yr
    ROCE_no_cash_sub = operating_income_2_yr / capital_employed_no_cash_sub_2_yr

    # GSC return FCFROCE
    FCFROCE_all_cash_sub = FCF_2_yr/capital_employed_all_cash_sub_2_yr
    FCFROCE_no_cash_sub = FCF_2_yr/capital_employed_no_cash_sub_2_yr

    # GSC growth d_OI_FDS_ratio
    d_OI_FDS_ratio = ((operating_income_2_yr/fully_diluted_shares_2_yr)-(operating_income_1_yr / fully_diluted_shares_1_yr))/(operating_income_1_yr/fully_diluted_shares_1_yr)

    # GSC growth d_FCF_FDS_ratio
    d_FCF_FDS_ratio = ((FCF_2_yr/fully_diluted_shares_2_yr) -(FCF_1_yr/fully_diluted_shares_1_yr))/(FCF_1_yr/fully_diluted_shares_1_yr)

    # GSC growth d_BV_FDS_ratio
    d_BV_FDS_ratio = ((BV_2_yr/fully_diluted_shares_2_yr)-(BV_1_yr/fully_diluted_shares_1_yr))/(BV_1_yr/fully_diluted_shares_1_yr)

    # GSC growth d_TBV_FDS_ratio
    d_TBV_FDS_ratio = ((TBV_2_yr/fully_diluted_shares_2_yr)-(TBV_1_yr/fully_diluted_shares_1_yr))/(TBV_1_yr/fully_diluted_shares_1_yr)

    # GSC le_ratio
    le_ratio = total_liabilities/BV_2_yr

    # GSC price MCAP_FCF_ratio
    MCAP_FCF_ratio = market_cap/FCF_2_yr

    # GSC price EV_OI_ratio
    enterprise_value = enterprise_value
    EV_OI_ratio = enterprise_value/operating_income_2_yr

    # GSC price MCAP_BV_ratio
    MCAP_FCF_ratio = market_cap/BV_2_yr

    # GSC price MCAP_TBV ratio
    MCAP_TBV_ratio = market_cap/TBV_2_yr

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
