import openpyxl
import time
import pandas as pd

from datetime import *
from dateutil.relativedelta import *

from BaseProjections.Dates import *
from BaseProjections.Setup import *
from BaseProjections.TBEntry import *
from BaseProjections.Constants import *
from BaseProjections.TrialBalances import *
from BaseProjections.JournalEntry import *

from Compensation.CapExSw import *
from Compensation.Compensation import *

from Expenses.Expenses import *

from FSReports.FinancialStatements import *

from RevenueSaaS.Revenues import *
from RevenueSaaS.Collections import *
from RevenueSaaS.Products import *
from RevenueSaaS.Churn import *

InfoDict = {}
TBs = {}
FinStmts = {}
RevExpenseList = []
RevExpenseType = {}
RevExpenseFile = []
RevExpenseFiles = {}
RevExpenseLogs = {}

# Setup  varaibles & Data
absolute_path = os.path.dirname(__file__)
inputs = CSetup(absolute_path)
formats = CFormat(inputs)
InfoDict = inputs.SetupDict
products = CProducts(inputs.products_list)

# Calculate Forecasted Reveues and Expenses (?)
#dates = inputs.dates

# Needed for creating TB's
actuals_term = inputs.months_actuals
model_term = inputs.months_total
start_date = inputs.start_date
accounts = inputs.accounts
depts = inputs.depts
accountIndexs = inputs.accountIndexs
equity_account = inputs.equity_account
rev_expense_classes = {}
rev_expense_acs = {}

journal_entry = CJE()

# should switch to a list to iterate through
rev_acs_df = inputs.rev_exp_accounts_df
for i,row in inputs.rev_exp_types_df.iterrows():

    RevExpenseClass = row[kRevExpType]
    rev_expense_log = row[kRevExpLog]
    RevExpenseLogs[RevExpenseClass] = []
    print("RevExpenseClass: ", RevExpenseClass)
                    
    if RevExpenseClass == kClassExp:
        pass
        rev_expense_classes[RevExpenseClass] = CExpenses(inputs, journal_entry, formats, rev_expense_log)      #done
                        
    elif RevExpenseClass == kClassRev:
        pass
        rev_expense_classes[RevExpenseClass] = CRevenues(inputs, rev_acs_df, journal_entry, formats, products, rev_expense_log)      #done
                        
    elif RevExpenseClass == kClassEmpl:
        pass
        people = kEmplPeople
        comp = kEmplTypes
        comp_accounts = kEmplAccounts
        cap_accounts = kCapAc
        filename = kEmplFile
        employees = True                
        filenames = people, comp, comp_accounts, cap_accounts, filename
        employee_instance = CCompensation(inputs, filenames, employees, journal_entry, formats, rev_expense_log)     #done - needs JE
        rev_expense_classes[RevExpenseClass] = employee_instance
                        
    elif RevExpenseClass == kClassCont:
        pass
        people = kContPeople
        comp = kContTypes
        comp_accounts = kContAccounts
        cap_accounts = kCapAc
        filename = kContFile
        employees = False             
        filenames = people, comp, comp_accounts, cap_accounts, filename
        contractor_instance = CCompensation(inputs, filenames, employees, journal_entry, formats, rev_expense_log)   #done - needs JE
        rev_expense_classes[RevExpenseClass] = contractor_instance

    elif RevExpenseClass == kClassCapEx:
        pass
        compensation_instance = rev_expense_classes[kClassEmpl]
        contractor_instance = rev_expense_classes[kClassCont]
        rev_expense_classes[RevExpenseClass] = CCapExSW(inputs, journal_entry, formats, employee_instance, contractor_instance, rev_expense_log)         #done
         
    elif RevExpenseClass == kClassTB:
        pass
        rev_expense_classes[RevExpenseClass] = CTBEntry(inputs, journal_entry, formats, rev_expense_log)       #next

    else:
        print("Proj; The Revenue/Expense Class is undefined in Projections: ", RevExpenseClass, rev_expense_log)

# Add Forecasted Reveues and Expenses to TB's (and GL)
TrialBs = CTrialBalances(actuals_term, model_term, start_date, accounts, accountIndexs, equity_account, rev_expense_classes, rev_expense_acs, inputs, RevExpenseLogs)
TBs = TrialBs.TBDictOut

# Add TB's to the Financial Statements
fstatements = CFinStatements(depts, model_term, start_date, inputs, TBs)
fstatements.ActualsUpdate(model_term, start_date, inputs, formats)