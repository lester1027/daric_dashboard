import numpy as np


def calculate_intrinsic_value(ttmFCF, sharesOutstanding, longTermGrowthRate, currentSharePrice, stockBeta, riskFreeRate, riskPremium, taxRate, longTermIntRate, marketCap, mvDebt, totalLiab, cce, gdpGrowthRate):
    # a function for calculating the intrinsic value
    # this is used later for both after acquiring financial figures and
    # after changing values in the interactive table

    r_e = riskFreeRate+stockBeta*riskPremium
    r_d = longTermIntRate*(1-taxRate)
    wacc = (marketCap)/(marketCap+mvDebt)*r_e+(mvDebt)/(marketCap+mvDebt)*r_d

    projectedFCF = np.array(
        [ttmFCF*(1+longTermGrowthRate)**n for n in range(11)])
    discountFact = np.array([1/(1+wacc)**n for n in range(11)])
    discountedFCF = projectedFCF[1:]*discountFact[1:]
    pvDiscountedFCF = discountedFCF.sum()
    perpetuityValue = (projectedFCF[-1]*(1+gdpGrowthRate))/(wacc-gdpGrowthRate)
    terminalValue = perpetuityValue*discountFact[-1]
    intrinsicValuePerShare = (
        pvDiscountedFCF+terminalValue+cce-totalLiab)/sharesOutstanding

    return pvDiscountedFCF, terminalValue, wacc, intrinsicValuePerShare
