from datetime import *
from dateutil.relativedelta import *
from Constants import *
#from utilities import *
import pandas as pd  # to replace csv

#fExpensePath = kInputPath
#fOutputPath =  kOutputPath

class CExpenses():

        def __init__(self, inputs, journal_entry, formats):

                self.Depts = []
                self.Expenses_list = []
                self.Expenses_dict ={}
                self.totalmonthexpenses = 0
                expense_counter = 0
                tempExpenses = []
                dates = inputs.dates
                self.journal_entry = journal_entry

                fExpenses = inputs.full_path_input+kExpensesXL

                try:
                        #This needs to be converted to a dataframe and excel
                        xls = pd.ExcelFile(fExpenses)
                        df = pd.read_excel(xls, kExpenses)
                        Expense_list = df.values.tolist()

                        for expense_row in Expense_list:

                                
                                expense_instance = CExpense_item(expense_row, dates)
                                self.Expenses_list.append(expense_instance)
                                self.Expenses_dict[expense_instance.description] = expense_instance
                                tempExpenses.append(expense_instance.expense_months)
                                description= self.Expenses_list[expense_counter].description
                                month_start_text = self.Expenses_list[expense_counter].start      
                                expenses_amount =self.Expenses_list[expense_counter].amount
                                expenses_dept = self.Expenses_list[expense_counter].dept
                                account_to_debit = self.Expenses_list[expense_counter].ac_dr
                                account_to_credit = self.Expenses_list[expense_counter].ac_cr
                               
                                expense_counter +=1

                        

                except FileNotFoundError:
                        print("Can't find or open accounts file", fExpenses)

        def CExpensesAddMonthsTransactions(self, month, TB):

                #getExpenseIndexes is replaced by:
                Expense_index = []
                self.totalmonthexpenses = 0

                for expense_item in self.Expenses_list:

                        amount = expense_item.expense_months[month] # months start at 1 not zero
                        dr = expense_item.ac_dr
                        cr = expense_item.ac_cr
                        
                        self.totalmonthexpenses = self.totalmonthexpenses + (amount)
                        self.journal_entry.performJE(month, TB, dr, cr, amount)
                                
                return TB

        def getExpenseIndexes(self, TB):

                Expense_index = []
                for TBrow in TB:
                        Expense_index.append(TBrow[kTBAcIndex])
                return Expense_index
            
class CExpense_item():
  
        def __init__(self, item_list, dates):

                expense_months = []
                temp_list = []

                # need to change the absolute references to references in 'Constants'
                self.Expense_item_list = item_list
                self.description = self.Expense_item_list[kExpensesDescription]
                self.start = self.Expense_item_list[kExpensesStart]
                self.end = self.Expense_item_list[kExpensesEnd]
                self.amount = self.Expense_item_list[kExpensesAmount]
                self.dept = self.Expense_item_list[kExpensesDept]
                self.ac_dr = self.Expense_item_list[kExpensesAcDr]
                self.ac_cr = self.Expense_item_list[kExpensesAcCr]
                        
                self.expense_tuple = (self.description,self.start,self.end,self.amount,self.dept,self.ac_dr,self.ac_cr)
                                
                self.expense_months = [0 for i in range(dates.model_term)]

                if pd.isnull(self.Expense_item_list[kExpensesStart]):
                        # Fill entire row with amount
  
                        self.expense_months = [self.amount for i in range(dates.model_term)]
                else:
                        self.start_date = self.Expense_item_list[kExpensesStart]
                              
                        #if  (self.Expense_item_list[kExpensesEnd] == pd.NaT):
                        if pd.isnull(self.Expense_item_list[kExpensesEnd]):
                                # Fill from start month to end of list
                                # get start month and calculate length to end of list
  
                                self.start_month = dates.GetMonthNum(self.start_date)
 
                                for i in range(dates.model_term):
                                        if i >= self.start_month:
                                                self.expense_months[i] = self.amount
                        else:
                                # Fill from start month to end month
                                # get start month and end month
                                self.end_date = self.Expense_item_list[kExpensesEnd]

                                self.start_month = dates.GetMonthNum(self.start_date)
                                self.end_month = dates.GetMonthNum(self.end_date)
 
                                for i in range(dates.model_term):
                                        if i >= self.start_month and i <= self.end_month:
                                                self.expense_months[i] = self.amount
                                                        
 
        
          

                

