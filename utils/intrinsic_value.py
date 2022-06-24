from dis import dis
import numpy as np

def calc_r_d(debt_int_rate, tax_rate):
    return debt_int_rate * (1 - tax_rate)

def calc_r_e(r_f, beta, mkt_risk_prem):
    return r_f + beta * mkt_risk_prem

def calc_wacc(mv_debt, mv_equity, r_d, r_e):

    mv_debt_equity = mv_debt + mv_equity
    debt_ratio = mv_debt / mv_debt_equity
    equity_ratio = mv_equity / mv_debt_equity

    wacc = debt_ratio * r_d + equity_ratio * r_e

    return wacc

def calc_ttm_FCF(df_FCF_annual, df_FCF_quar):
    # if the most recent annual cashflow statement is the mose recent cashflow statement
    if df_FCF_annual.loc[0, 'date'] == df_FCF_quar.loc[0, 'date']:
        ttm_FCF = df_FCF_annual.loc[0, 'annual_free_cash_flow']
    # if there are quarterly cashflow statements released after the latest annual cashflow statement
    else:
        # use the free cash flow in the most recent annual cashflow statement
        # and add all those from more recently quarterly cashflow statement
        # then minus those from corrseponding quarterly cashflow from the previous year
        offset = df_FCF_quar.index[df_FCF_quar['date'] == df_FCF_annual.loc[0, 'date']].tolist()[0]
        quarters_added = np.array(
            df_FCF_quar.loc[0:offset-1, 'quarterly_free_cash_flow']).astype(np.float).sum()
        quarters_dropped = np.array(
            df_FCF_quar.loc[4:offset+4-1, 'quarterly_free_cash_flow']).astype(np.float).sum()
        ttm_FCF = np.array(df_FCF_annual.loc[0, 'annual_free_cash_flow']).astype(
            np.float) + quarters_added - quarters_dropped

        return ttm_FCF

def calc_projected_FCF(ttm_FCF, long_term_growth_rate):
    projected_FCF = np.array(
        [ttm_FCF * (1 + long_term_growth_rate)**n for n in range(11)]
    )
    return projected_FCF

def calc_discount_factor(wacc):
    discount_factor = np.array([1 / (1 + wacc)**n for n in range(11)])
    return discount_factor

def calc_discounted_FCF(projected_FCF, discount_factor):
    discounted_FCF = projected_FCF[1:] * discount_factor[1:]
    return discounted_FCF

def calc_pv_discounted_FCF(discounted_FCF):
    pv_discounted_FCF = discounted_FCF.sum()
    return pv_discounted_FCF

def calc_perpetuity_value(projected_FCF, wacc, gdp_growth_rate):
    perpetuity_value = (projected_FCF[-1] * (1 + gdp_growth_rate)) / (wacc - gdp_growth_rate)
    return perpetuity_value

def calc_terminal_Value(perpetuity_value, discount_factor):
    terminal_value = perpetuity_value * discount_factor[-1]
    return terminal_value

def calculate_intrinsic_value_per_share(debt_int_rate, tax_rate, r_f, beta, mkt_risk_prem,
                                        mv_debt, mv_equity, df_FCF_annual, df_FCF_quar,
                                        long_term_growth_rate, gdp_growth_rate,
                                        cce, debt, shares_outstanding):
    r_d = calc_r_d(debt_int_rate, tax_rate)
    r_e = calc_r_e(r_f, beta, mkt_risk_prem)
    wacc = calc_wacc(mv_debt, mv_equity, r_d, r_e)
    ttm_FCF = calc_ttm_FCF(df_FCF_annual, df_FCF_quar)
    projected_FCF = calc_projected_FCF(ttm_FCF, long_term_growth_rate)
    discount_factor = calc_discount_factor(wacc)
    discounted_FCF = calc_discounted_FCF(projected_FCF, discount_factor)
    pv_discounted_FCF = calc_pv_discounted_FCF(discounted_FCF)
    perpetuity_value = calc_perpetuity_value(projected_FCF, wacc, gdp_growth_rate)
    terminal_value = calc_terminal_Value(perpetuity_value, discount_factor)

    intrinsic_value_per_share = (pv_discounted_FCF + terminal_value + cce - debt) / shares_outstanding

    return intrinsic_value_per_share
