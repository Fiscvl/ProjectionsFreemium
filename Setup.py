from datetime import *
from dateutil.relativedelta import *
from Dates import *
from Constants import *

import pandas as pd
import os




# 0: Account
# 1: Account Number
# 2: Category
# 3: BS or IS
# 4: Department
# 5: Category + Department

class CSetup():
    
    def __init__(self):

        self.depts = []
        self.accounts = []
        self.revExpTypes = []
        self.accountIndexs = []
        self.SetupDict = {}
        self.months_header = []
        internal_accounts = []

        
        absolute_path = os.path.dirname(__file__)
        input_relative_path = kInputPath
        output_relative_path = kOutputPath
        #path to b
        self.full_path_input = os.path.join(absolute_path, input_relative_path)
        self.full_path_output = os.path.join(absolute_path, output_relative_path)
        blank_account_row = [None]*kAccountFields

 
# New - all encompassing XL file for all input-data
        try:
            excel_book = (self.full_path_input + kInputs_file)
            inputs_df = pd.read_excel(excel_book, kInputs)
            accounts_df = pd.read_excel(excel_book, kAccounts)
            products_df = pd.read_excel(excel_book, kProducts)
            self.rev_exp_accounts_df = pd.read_excel(excel_book, kRevExpAccounts)
            self.rev_exp_types_df = pd.read_excel(excel_book, kRevExpTypes)

            # The green is hardcoded column names - need to be converted to Constants

            BS_df = accounts_df.copy()
            BS_df = BS_df.loc[:, [kFSAccName, kBSorISName]]
            #this needs to be redone with field name and field 
            BS_df = BS_df.query(f"`{kBSorISName}` ==  @kBS_string")
            #df.query('team == @team_name')
            #subframe = fooframe.query(f"`{myvar}` == 'Large'")
            BS_df = BS_df.drop_duplicates([kFSAccName])
            BS_df = BS_df.loc[:, [kFSAccName]]
            self.BS_len = len(BS_df)

            IS_df = accounts_df.copy()
            IS_df = IS_df.loc[:, [kFSAccName, kBSorISName]]
            #this needs to be redone with field name and field 
            IS_df = IS_df.query(f"`{kBSorISName}` ==  @kIS_string")
            IS_df = IS_df.drop_duplicates([kFSAccName])
            IS_df = IS_df.loc[:, [kFSAccName]]
            self.IS_len = len(IS_df)
            
            depts_df = accounts_df.copy()
            depts_df = depts_df.loc[:, ['Department', 'Statement']]
            depts_df = depts_df.query("Statement == 'IS'")
            depts_df = depts_df.drop_duplicates(["Department"])
            depts_df = depts_df.loc[:, ['Department']]

            self.accounts = accounts_df.values.tolist()
            self.SetupDict[kAccounts] = self.accounts
            self.BS = BS_df.values.tolist()
            self.IS = IS_df.values.tolist()
            self.depts = depts_df.values.tolist()

            for row in self.accounts:
                account_name = row[kTBAccountIndex]
                self.accountIndexs.append(account_name)

            internal_accounts_df = accounts_df.copy()
            internal_accounts_df = internal_accounts_df.query("Statement == 'IS'")
            internal_accounts_df = internal_accounts_df.drop_duplicates(["Combined: FS Account and Dept"])
            internal_accounts = internal_accounts_df.values.tolist()

            for i,row in enumerate(internal_accounts):

                row[kTBAccountIndex] = kInternalAccount + row[kFSAcc] + "-" + row[kDept]
                row[kAccNum] = ""
                #internal_account_row[kFSAcc] = IS_row[kFirst]
                #internal_account_row[kBSorIS] = kIS
                #internal_account_row[kDept] = Dept_row[kFirst]
                row[kCombined] = ""
                row[kExternal] = False
                #print(row)
                internal_accounts[i] = row
                self.accounts.append(row)
            
            'check the output'

            self.SetupDict[kAccIndex] = self.accountIndexs

            self.depts = depts_df.values.tolist()
            self.SetupDict[kDepts] = self.depts

            self.products_list = products_df.values.tolist()
            self.SetupDict[kProducts] = self.products_list

            inputs_row = inputs_df.values.tolist()
            self.SetupDict[kInputs] = inputs_row

        except FileNotFoundError:
                print("Input Excel file/sheet not found")  
                
            #   get all the variables to  create the durations of the projection
                            
        self.start_date = inputs_row[kFirst][kInStartDateIndex]

        self.end_date = inputs_row[kFirst][kInEndDateIndex]
       
        self.projections_date = inputs_row[kFirst][kInActualsDateIndex]

        self.dates = CMonths(self.start_date, self.end_date, self.projections_date)

        start_month = self.dates.GetMonth(self.start_date)
        end_month = self.dates.GetMonth(self.end_date)
        
        projections_month = self.dates.GetMonth(self.projections_date)
        self.months_actuals = projections_month + 1 - start_month
        self.months_projections = end_month - projections_month
        self.months_total =  self.months_actuals +  self.months_projections
        self.projections_start =   projections_month - start_month + 1
        # plus 2 = 1 month to switch from 0 to 1 counter and 1 month past end of actuals

        self.equity_account =(inputs_row[kFirst][kInIncomeAcIndex])
        self.cash_account =(inputs_row[kFirst][kInCashAcIndex])

        self.FICA_rate = (inputs_row[kFirst][kInSSRateIndex])
        self.FICA_cap = (inputs_row[kFirst][kInSSCapIndex])
        self.Medicare_rate = (inputs_row[kFirst][kInMedicareIndex])
        self.SUI_rate = (inputs_row[kFirst][kInSUIRateIndex])
        self.SUI_cap = (inputs_row[kFirst][kInSUICapIndex])
        self.FUTA_rate = (inputs_row[kFirst][kInFUTARateIndex])
        self.FUTA_cap = (inputs_row[kFirst][kInFUTACapIndex])
        self.churn = (inputs_row[kFirst][kInChurnIndex])
        self.amort_balance_term = (inputs_row[kFirst][kInCapSWBalTermIndex])
        self.amort_comp_term = (inputs_row[kFirst][kInCapSWAmortTermIndex])
        self.new_client_days = (inputs_row[kFirst][kInNewClientDaysIndex])
        self.new_client_term = (inputs_row[kFirst][kInNewContractLength])

        column_date = pd.to_datetime(self.start_date)
        
        for i in range(self.months_total):
            date_string = column_date.strftime("%Y-%m")
            self.months_header.append(date_string)
            column_date = column_date + relativedelta(months=1)

        self.zero_row = [0 for x in range(self.months_total)]

    def getBSorIS(self, account):

        try:
            acc_index = self.AccountIndexs.index(account)
            BSorIS = self.Accounts[acc_index][kBSorIS]

        except:
            print(f"Can't find the account in Accounts {account}")

        return BSorIS
    
    def getDept(self, account):
        try:
            acc_index = self.AccountIndexs.index(account)
            Dept_name = self.Accounts[acc_index][kDept]

        except:
            print(f"Can't find the accounts in Accounts {account}")

        return Dept_name    


    def getFSCategory(self, account):
        
        try:
            acc_index = self.AccountIndexs.index(account)
            Category_name = self.Accounts[acc_index][kAccNum]

        except:
            print(f"Can't find the accounts in Accounts {account}")

        return Category_name

       
    #def input__init__(self):
        

    def get_dates(self):
        return self.dates

