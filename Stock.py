import pandas as pd
from calculate import calculate_intrinsic_value
import requests


class Stock:
    API_KEY = 'df55e203f4c76c061a598aaf16ea454d'
    #a class variable to store all the URLs to be used
    URL_DICT = {'priceHistory':'https://financialmodelingprep.com/api/v3/historical-price-full/{}?serietype=line&apikey={}',
                'cashflowQuarter':'https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?period=quarter&apikey={}',
                'cashflow':'https://financialmodelingprep.com/api/v3/cash-flow-statement/{}?apikey={}',

                'companyQuote':'https://financialmodelingprep.com/api/v3/quote/{}?apikey={}',

                'financialGrowth':'https://financialmodelingprep.com/api/v3/financial-growth/{}?apikey={}',
                'profile':'https://financialmodelingprep.com/api/v3/profile/{}?apikey={}',
                'govBonds':'http://www.worldgovernmentbonds.com',
                'riskPremium':'http://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html',
                'financialRatios':'https://financialmodelingprep.com/api/v3/ratios/{}?apikey={}',
                'income':'https://financialmodelingprep.com/api/v3/income-statement/{}?apikey={}',
                'balance':'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?apikey={}',
                'balanceQuarter':'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{}?period=quarter&apikey={}',
                'gdpGrowthRate':'https://en.wikipedia.org/wiki/List_of_countries_by_real_GDP_growth_rate'}

    def __init__(self,symbol,startDate,endDate,margin):
        self.symbol=symbol
        self.startDate=startDate
        self.endDate=endDate
        self.safetyMargin=margin
        self.debtPremium=1.3
        #the number to indicate a financial figure that cannot be acquired successfully
        self.epsilon=9999999999

    #a private function to construct the URLs with the input symbol
    def _get_f_url(self, url, format=False):
        if format:
            return Stock.URL_DICT[url].format(self.symbol,Stock.API_KEY)
        else: 
            return Stock.URL_DICT[url]


    def update_source(self):
        #source of priceHistory
        self.url_priceHistory =self._get_f_url('priceHistory',format=True)

        #source of figures 1
        self.url_cashflowQuarter=self._get_f_url('cashflowQuarter',format=True)

        self.url_cashflow=self._get_f_url('cashflow',format=True)

        #source of figures 2
        self.url_companyQuote=self._get_f_url('companyQuote',format=True)

        #source of figure 3
        self.url_financialGrowth=self._get_f_url('financialGrowth',format=True)
        
        #source of figures 4,5,10
        self.url_profile=self._get_f_url('profile',format=True)

        #source of figure 6
        self.url_govBonds = self._get_f_url('govBonds',format=False)
        
        #source of figure 7
        self.url_riskPremium=self._get_f_url('riskPremium',format=False)
        

        #source of figure 8
        self.url_financialRatios=self._get_f_url('financialRatios',format=True)

        #source of figure 9
        self.url_income=self._get_f_url('income',format=True)
        self.url_balance=self._get_f_url('balance',format=True)


        #source of figure 11,12,13
        self.url_balanceQuarter=self._get_f_url('balanceQuarter',format=True)


        #source of figure 14
        self.url_gdpGrowthRate=self._get_f_url('gdpGrowthRate',format=False)
        


    def update_price(self):
        #price history
        self.response_priceHistory = requests.request("GET",self.url_priceHistory).json()['historical']
        self.priceHistory=pd.DataFrame(self.response_priceHistory)
        self.selectedPriceHistory=self.priceHistory[(self.priceHistory['date']>self.startDate)&(self.priceHistory['date']<self.endDate)]

    def update_data(self):
        #figure 1: TTM FCF
        try:
            self.response_cashflowQuarter=pd.DataFrame(requests.request('GET',self.url_cashflowQuarter).json(),dtype=float)
            self.response_cashflow=pd.DataFrame(requests.request('GET',self.url_cashflow).json(),dtype=float)

            #if the most recent annual cashflow statement is the mose recent cashflow statement
            if self.response_cashflow.loc[0,'date']==self.response_cashflowQuarter.loc[0,'date']:
                self.ttmFCF=self.response_cashflow.loc[0,'freeCashFlow']
            #if there are quarterly cashflow statements released after the latest annual cashflow statement
            else:
                #use the free cash flow in the most recent annual cashflow statement and add all those from more recently quarterly cashflow statement then minus those from corrseponding quarterly cashflow from the previous year
                self.offset=self.response_cashflowQuarter.index[self.response_cashflowQuarter['date']==self.response_cashflow.loc[0,'date']].tolist()[0]
                self.quarters_added=np.array(self.response_cashflowQuarter.loc[0:self.offset-1,'freeCashFlow']).astype(np.float).sum()
                self.quarters_dropped=np.array(self.response_cashflowQuarter.loc[4:self.offset+4-1,'freeCashFlow']).astype(np.float).sum()
                self.ttmFCF=np.array(self.response_cashflow.loc[0,'freeCashFlow']).astype(np.float)+self.quarters_added-self.quarters_dropped

        except:
            self.ttmFCF=self.epsilon

        #Figure 2: Total number of shares outstanding
        try:
            self.sharesOutstanding=float(requests.request('GET',self.url_companyQuote).json()[0]["sharesOutstanding"])
        except:
            self.sharesOutstanding=self.epsilon

            #Figure 3: Long term growth rate
        try:
            self.longTermGrowthRate=float(requests.request('GET',self.url_financialGrowth).json()[0]["dividendsperShareGrowth"])
        except:
            self.longTermGrowthRate=self.epsilon

        #Figure 4: Current share price
        try:
            self.currentSharePrice=float(requests.request('GET',self.url_profile).json()[0]['price'])
        except:
            self.currentSharePrice=self.epsilon



        #Figure 5: Stock beta
        try:
            self.stockBeta=float(requests.request('GET',self.url_profile).json()[0]['beta'])
        except:
            self.stockBeta=self.epsilon


        #Figure 6: Risk free rate
        #10-year government's bond
        try:
            self.response_risk_free=pd.read_html(self.url_govBonds)[0]
            self.riskFreeRate=float(self.response_risk_free[self.response_risk_free['Country']=='United States']['10Y Yield'].values[0].strip('%'))/100
        except:
            self.riskFreeRate=self.epsilon


        #Figure 7: Market risk premium
        try:
            self.response_riskPremium=pd.read_html(self.url_riskPremium,header=0)[0]
            self.riskPremium=float(self.response_riskPremium.loc[self.response_riskPremium['Country']=='United States','Equity Risk  Premium'].values[0].strip('%'))/100
        except:
            self.riskPremium=self.epsilon


        #Figure 8: Business tax rate
        try:
            self.taxRate=float(requests.request('GET',self.url_financialRatios).json()[0]['effectiveTaxRate'])
        except:
            self.taxRate=self.epsilon



        #Figure 9: Estimated long-term interest rate
        try:
            self.interestExpense=float(requests.request('GET',self.url_income).json()[0]['interestExpense'])
            
            self.longTermDebt=float(requests.request('GET',self.url_balance).json()[0]['longTermDebt'])
            
            self.longTermIntRate=self.interestExpense/self.longTermDebt
        except:
            self.longTermIntRate=self.epsilon


        #Figure 10: Market value of equity
        try:
            self.marketCap=float(requests.request('GET',self.url_profile).json()[0]['mktCap'])
        except:
            self.marketCap=self.epsilon


        #Figure 11: Market value of debt
        #use the most recent quarter
        try:
            self.totalDebt=float(requests.request('GET',self.url_balanceQuarter).json()[0]['totalDebt'])
            
            self.mvDebt=(self.totalDebt)*self.debtPremium
        except:
            self.mvDebt=self.epsilon


        #Figure 12: Total liabilities
        #use the most recent quarter
        try:
            self.totalLiab=float(requests.request('GET',self.url_balanceQuarter).json()[0]["totalLiabilities"])
        except:
            self.totalLiab=self.epsilon

        #Figure 13: Total cash and cash equivalents
        #use the most recent quarter
        try:
            self.cce=float(requests.request('GET',self.url_balanceQuarter).json()[0]["cashAndCashEquivalents"])
        except:
            self.cce=self.epsilon

        #Figure 14: GDP growth rate
        #the real GDP growth rate from 2013 to 2018
        try:
            self.response_gdpGrowthRate=pd.read_html(self.url_gdpGrowthRate)[1]
            self.gdpGrowthRate=	float(self.response_gdpGrowthRate[self.response_gdpGrowthRate['Country']=='United States']['Average GDP growthrate (%) 2013–2018'].values)/100
        except:
            self.gdpGrowthRate=self.epsilon




        #calculate the intrinsic value
        self.pvDiscountedFCF,self.terminalValue,self.wacc,self.intrinsicValuePerShare=calculate_intrinsic_value(
            self.ttmFCF,
            self.sharesOutstanding,
            self.longTermGrowthRate,
            self.currentSharePrice,
            self.stockBeta,
            self.riskFreeRate,
            self.riskPremium,
            self.taxRate,
            self.longTermIntRate,
            self.marketCap,
            self.mvDebt,
            self.totalLiab,
            self.cce,
            self.gdpGrowthRate)



        self.intrinsicValuePerShareSafe=self.intrinsicValuePerShare*(1-self.safetyMargin/100)

        #determine if the stock is over-valued or under-valued
        if self.currentSharePrice<=self.intrinsicValuePerShareSafe:
            self.comp='under'
        else:
            self.comp='over'

        self.df_figures=pd.DataFrame(
            data={  'Symbol':[self.symbol],
                    'Comparison':[self.comp],
                    'Intrinsic_Value_per_Share':[self.intrinsicValuePerShare],
                    'Intrinsic_Value_per_Share_with_Safety_Margin':[self.intrinsicValuePerShareSafe],
                    '1_TTM_Free_Cash_Flow':[self.ttmFCF],
                    '2_Shares_Outstanding':[self.sharesOutstanding],
                    '3_Long_Term_Growth_Rate':[self.longTermGrowthRate],
                    '4_Current_Share_Price':[self.currentSharePrice],
                    '5_Stock_Beta':[self.stockBeta],
                    '6_Risk_Free_Rate':[self.riskFreeRate],
                    '7_Market_Risk_Premium':[self.riskPremium],
                    '8_Business_Tax_Rate':[self.taxRate],
                    '9_Estimate_Interest_Rate':[self.longTermIntRate],
                    '10_Market_Value_of_Equity':[self.marketCap],
                    '11_Market_Value_of_Debt':[self.mvDebt],
                    '12_Total_Liabilities':[self.totalLiab],
                    '13_Cash_&_Cash_Equivalents':[self.cce],
                    '14_GDP_Growth_Rate':[self.gdpGrowthRate]})

        return self
