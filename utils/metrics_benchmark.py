import operator

def compare_with_benchmark(stock_value, symb, benchmark):
    op = {
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        '==': operator.eq,
        '!=': operator.ne,
    }
    flag = op[symb](stock_value, benchmark)
    diff = stock_value - benchmark

    return flag, stock_value, benchmark, diff

def compare_instrinsic_value(intrinsic_value_per_share, current_share_price):

    stock_value = intrinsic_value_per_share
    benchmark = current_share_price
    symb = '>'

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_ROCE(ROCE):

    stock_value = ROCE
    benchmark = 0.15
    symb = '>='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_FCFROCE(FCFROCE):

    stock_value = FCFROCE
    benchmark = 0.08
    symb = '>='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_dOI_to_FDS(dOI_to_FDS):

    stock_value = dOI_to_FDS
    benchmark = 0.03
    symb = '>='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_dFCF_to_FDS(dFCF_to_FDS):

    stock_value = dFCF_to_FDS
    benchmark = 0.03
    symb = '>='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_dBV_to_FDS(dBV_to_FDS):

    stock_value = dBV_to_FDS
    benchmark = 0.03
    symb = '>='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_dTBV_to_FDS(dTBV_to_FDS):

    stock_value = dTBV_to_FDS
    benchmark = 0.03
    symb = '>='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_liab_to_equity(liab_to_equity):

    stock_value = liab_to_equity
    benchmark = 2
    symb = '<='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_MCAP_to_FCF(MCAP_to_FCF):

    stock_value = MCAP_to_FCF
    benchmark = 8
    symb = '<='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_EV_to_OI(EV_to_OI):

    stock_value = EV_to_OI
    benchmark = 7
    symb = '<='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_MCAP_to_BV(MCAP_to_BV):

    stock_value = MCAP_to_BV
    benchmark = 3
    symb = '<='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb, benchmark)

    return flag, stock_value, symb, benchmark, diff

def compare_MCAP_to_TBV(MCAP_to_TBV):

    stock_value = MCAP_to_TBV
    benchmark = 3
    symb = '<='

    flag, stock_value, benchmark, diff = compare_with_benchmark(stock_value, symb , benchmark)

    return flag, stock_value, symb, benchmark, diff

comp = {
    'ROCE': compare_ROCE,
    'FCFROCE': compare_FCFROCE,
    'dOI_to_FDS': compare_dOI_to_FDS,
    'dFCF_to_FDS': compare_dFCF_to_FDS,
    'dBV_to_FDS': compare_dBV_to_FDS,
    'dTBV_to_FDS': compare_dTBV_to_FDS,
    'liab_to_equity': compare_liab_to_equity,
    'MCAP_to_FCF': compare_MCAP_to_FCF,
    'EV_to_OI': compare_EV_to_OI,
    'MCAP_to_BV': compare_MCAP_to_BV,
    'MCAP_to_TBV': compare_MCAP_to_TBV,
}