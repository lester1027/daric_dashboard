import numpy as np
epsilon = 9999999999


def calculate_intrinsic_value(ttm_FCF, shares_outstanding, long_term_growth_rate, current_share_price,
                              stock_beta, risk_free_rate, risk_premium, tax_rate, long_term_int_rate,
                              market_cap, mv_debt, total_liabilities, cce, gdp_growth_rate):
    '''
    A function for calculating the intrinsic value.
    This is used later for both after acquiring financial figures and
    after changing values in the interactive table.
    '''
    try:
        r_e = risk_free_rate+stock_beta*risk_premium
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] r_e: ', e)
        r_e = epsilon

    try:
        r_d = long_term_int_rate*(1-tax_rate)
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] r_d: ', e)
        r_d = epsilon

    try:
        wacc = (market_cap)/(market_cap+mv_debt) * \
            r_e+(mv_debt)/(market_cap+mv_debt)*r_d
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] wacc: ', e)
        wacc = epsilon

    try:
        projected_FCF = np.array(
            [ttm_FCF*(1+long_term_growth_rate)**n for n in range(11)])
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] projected_FCF: ', e)
        projected_FCF = epsilon

    try:
        discount_fact = np.array([1/(1+wacc)**n for n in range(11)])
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] discount_fact: ', e)
        discount_fact = epsilon

    try:
        discounted_FCF = projected_FCF[1:]*discount_fact[1:]
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] discounted_FCF: ', e)
        discounted_FCF = epsilon

    try:
        pv_discounted_FCF = discounted_FCF.sum()
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] pv_discounted_FCF: ', e)
        pv_discounted_FCF = epsilon

    try:
        perpetuity_value = (
            projected_FCF[-1]*(1+gdp_growth_rate))/(wacc-gdp_growth_rate)
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] perpetuity_value: ', e)
        perpetuity_value = epsilon

    try:
        terminal_value = perpetuity_value*discount_fact[-1]
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] terminal_value: ', e)
        terminal_value = epsilon

    try:
        intrinsic_value_per_share = (
            pv_discounted_FCF+terminal_value+cce-total_liabilities)/shares_outstanding
    except (ZeroDivisionError, TypeError) as e:
        print('[ERROR] intrinsic_value_per_share: ', e)
        intrinsic_value_per_share = epsilon

    return pv_discounted_FCF, terminal_value, wacc, intrinsic_value_per_share
