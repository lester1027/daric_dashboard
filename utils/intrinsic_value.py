import numpy as np

def calc_intrinsic_value_per_share(market_capital, total_debt, r_f, beta,
                                        market_risk_premium, interest_expense, long_term_debt,
                                        effective_tax_rate_ttm, long_term_growth_rate, fcf_ttm,
                                        avg_gdp_growth, cce, total_liabilities, outstanding_shares,
                                        safety_margin):

    interest_rate = interest_expense / long_term_debt
    r_e = r_f + beta * market_risk_premium
    r_d = interest_rate * (1 - effective_tax_rate_ttm)
    mv_debt_equity = total_debt + market_capital

    wacc = (
        r_d * (total_debt / mv_debt_equity)
        + r_e * (market_capital / mv_debt_equity)
    )

    fcf_projected = np.array([fcf_ttm * (1 + long_term_growth_rate)**n for n in range(11)])
    discount_fact = np.array([1 / (1 + wacc)**n for n in range(11)])
    fcf_discounted = fcf_projected[1:] * discount_fact[1:]
    fcf_discounted_pv = fcf_discounted.sum()

    perpetuity_value = (
    (fcf_projected[-1] * (1 + avg_gdp_growth))
    / (wacc - avg_gdp_growth)
    )

    terminal_value = perpetuity_value * discount_fact[-1]

    intrinsic_value_per_share = (
        fcf_discounted_pv
        + terminal_value
        + cce
        - total_liabilities
    ) / outstanding_shares

    intrinsic_value_per_share = intrinsic_value_per_share * (1 - safety_margin)

    return intrinsic_value_per_share
