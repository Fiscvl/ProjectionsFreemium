import openpyxl
import time
import pandas as pd
from datetime import *
from dateutil.relativedelta import *
from Dates import *
from Setup import *
from Formats import *

#from CapExSw import *
#from TBEntry import *
from Constants import *
from Collections import *
from Revenues import *
from Products import *
#from Expenses import *
#from Compensation import *
#from TrialBalances import *
#from FinancialStatements import *
#from JournalEntry import *


InfoDict = {}
TBs = {}
FinStmts = {}
RevExpenseList = []
RevExpenseType = {}
RevExpenseFile = []
RevExpenseFiles = {}

# Setup  varaibles & Data
inputs = CSetup()
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

#JE's are not part of this product
journal_entry = "CJE()"

# should switch to a list to iterate through
rev_acs_df = inputs.rev_exp_accounts_df
for i,row in inputs.rev_exp_types_df.iterrows():

    RevExpenseClass = row[kRevExpType]
    print("RevExpenseClass: ", RevExpenseClass)
                    
    if RevExpenseClass == kClassExp:
        pass
        #rev_expense_classes[RevExpenseClass] = CExpenses(inputs, journal_entry, formats)      #done
                        
    elif RevExpenseClass == kClassRev:
        pass
        rev_expense_classes[RevExpenseClass] = CRevenues(inputs, rev_acs_df, journal_entry, formats, products)      #done
                        
    elif RevExpenseClass == kClassEmpl:
        pass
        people = kCompPeople
        comp = kCompComp
        comp_accounts = kCompCompAc
        cap_accounts = kCompCapAc
        filename = kCompFile
        employees = True                
        #filenames = people, comp, comp_accounts, cap_accounts, filename
        #employee_instance = CCompensation(inputs, filenames, employees, journal_entry, formats)     #done - needs JE
        #rev_expense_classes[RevExpenseClass] = employee_instance
                        
    elif RevExpenseClass == kClassCont:
        pass
        people = kCompCont
        comp = kCompContAc
        comp_accounts = kCompCompAccounts
        cap_accounts = kCompCapAc
        filename = kContFile
        employees = False             
        #filenames = people, comp, comp_accounts, cap_accounts, filename
        #contractor_instance = CCompensation(inputs, filenames, employees, journal_entry, formats)   #done - needs JE
        #rev_expense_classes[RevExpenseClass] = contractor_instance

    elif RevExpenseClass == kClassCapEx:
        pass
        #compensation_instance = rev_expense_classes[kClassEmpl]
        #contractor_instance = rev_expense_classes[kClassCont]
        #rev_expense_classes[RevExpenseClass] = CCapExSW(inputs, journal_entry, formats, employee_instance, contractor_instance)         #done
         
    elif RevExpenseClass == kClassTB:
        pass
        #rev_expense_classes[RevExpenseClass] = CTBEntry(inputs, journal_entry, formats)       #next

    else:
        print("Proj; The Revenue/Expense Class is undefined in Projections: ", RevExpenseClass)

# Add Forecasted Reveues and Expenses to TB's (and GL)
#TrialBs = CTrialBalances(actuals_term, model_term, start_date, accounts, accountIndexs, equity_account, rev_expense_classes, rev_expense_acs, inputs)
#TBs = TrialBs.TBDictOut

# Add TB's to the Financial Statements
#fstatements = CFinStatements(depts, model_term, start_date, inputs, TBs)
#fstatements.ActualsUpdate(model_term, start_date, inputs, formats)