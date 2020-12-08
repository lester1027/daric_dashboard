import numpy as np


def calculate_intrinsic_value(ttm_FCF, shares_outstanding, long_term_growth_rate, current_share_price, stock_beta, risk_free_rate, risk_premium, tax_rate, long_term_int_rate, market_cap, mv_debt, total_liab, cce, gdp_growth_rate):
    # a function for calculating the intrinsic value
    # this is used later for both after acquiring financial figures and
    # after changing values in the interactive table

    r_e = risk_free_rate+stock_beta*risk_premium
    r_d = long_term_int_rate*(1-tax_rate)
    wacc = (market_cap)/(market_cap+mv_debt)*r_e+(mv_debt)/(market_cap+mv_debt)*r_d

    projected_FCF = np.array(
        [ttm_FCF*(1+long_term_growth_rate)**n for n in range(11)])
    discount_fact = np.array([1/(1+wacc)**n for n in range(11)])
    discounted_FCF = projected_FCF[1:]*discount_fact[1:]
    pv_discounted_FCF = discounted_FCF.sum()
    perpetuity_value = (projected_FCF[-1]*(1+gdp_growth_rate))/(wacc-gdp_growth_rate)
    terminal_value = perpetuity_value*discount_fact[-1]
    intrinsic_value_per_share = (
        pv_discounted_FCF+terminal_value+cce-total_liab)/shares_outstanding

    return pv_discounted_FCF, terminal_value, wacc, intrinsic_value_per_share
