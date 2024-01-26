import openpyxl
import pandas as pd
import copy

from datetime import *
from dateutil.relativedelta import *
from Constants import *
from Formats import *

from copy import deepcopy

class CTrialBalances():

    def __init__(self, actuals_term, model_term, start_date, accounts, accountIndexs, equity_account ,rev_expense_classes, rev_expense_acs, inputs):

        TBDict = {}
        self.TBDictOut = {}
        month_counter = 1
        TB_index = 0
        current_date = start_date
        a_month = relativedelta(months=1)
        stop_TB = False

        # need to try except for errors
        excel_book = (inputs.full_path_input + kTB_file)

        try:
            xls = pd.ExcelFile(excel_book)

        except:
            print("Couldn't find or open the TB's Excel File. TB process halted", excel_book)
            stop_TB = True
                
        while month_counter <= model_term and not(stop_TB):
            
            current_month = current_date.strftime("%Y-%m")
            
            if month_counter <= actuals_term:
                temp_df = pd.read_excel(xls, current_month, header = None)
                # this should replace nan (empty value, nothing or blank) with zero
                temp_df = temp_df.fillna(0)
                temp_TB = temp_df.values.tolist()
                current_TB = temp_TB.copy()
                TB_index += 1
                TBDict[current_month] = current_TB
    
            else:           
                # Add to existing TB, for each revenue expense type
                # and if the new TB is Jan of any year, strip off the IS and add the IS total to Retained Earnings
                temp_TB = self.getNewTB(current_date, accounts, accountIndexs, equity_account, TBDict)
                current_TB = copy.deepcopy(temp_TB)
                for rev_expense_class in rev_expense_classes:                   

                    if rev_expense_class == "CExpenses":
                        current_TB = rev_expense_classes[rev_expense_class].CExpensesAddMonthsTransactions(month_counter-1, current_TB)
                    elif rev_expense_class == "CRevenues":
                        current_TB = rev_expense_classes[rev_expense_class].CRevenuesAddMonthsTransactions(month_counter-1, current_TB, inputs)
                    elif rev_expense_class == "CCapExSW":
                        current_TB = rev_expense_classes[rev_expense_class].CCapExSWAddMonthsTransactions(month_counter-1, current_TB, inputs)
                    elif rev_expense_class == "CEmployees":
                        CapSW_type = "none"
                        current_TB = rev_expense_classes[rev_expense_class].CCompensationAddMonthsTransactions(month_counter-1, current_TB, CapSW_type)
                    elif rev_expense_class == "CContractors":
                        CapSW_type = "none"
                        current_TB = rev_expense_classes[rev_expense_class].CCompensationAddMonthsTransactions(month_counter-1, current_TB, CapSW_type)
                    elif rev_expense_class == "CTBEntry":
                        current_TB = rev_expense_classes[rev_expense_class].CTBEntryAddMonthsTransactions(month_counter-1, current_TB)
                    else:
                        print("The Revenue/Expense Class is undefined: {rev_expense_class}")

                TBDict[current_month] = current_TB
                       
            current_date = current_date + a_month
            month_counter += 1
        
        self.writeTBs(start_date, TBDict, inputs)
        self.TBDictOut = TBDict


    def writeTBs(self, start_date, TBDict, inputs):

            TB_file = inputs.full_path_output + kTBOut
            try:
                TB_file = inputs.full_path_output + kTBOut
                df_writer = pd.ExcelWriter(TB_file, engine='xlsxwriter')

            except:
                print("Failed to write the Excel TB file to the folder", TB_file)
                
            for month_key in TBDict:

                current_month_csv = month_key + ".csv"

                TB = TBDict[month_key]
                df = pd.DataFrame(TB) #, columns = kTBHeader
                df.to_excel(df_writer, sheet_name = month_key, index = False, header = False)
                TB_file_csv = inputs.full_path_output + month_key + ".csv"

            df_writer.close()

    def getTBIndex(self, csv_date, account):

        try:

            #If found
            TBIndex = TBIndexes.index(account)
        
        except:
            # otherwise return a -1 to signify it's not found
            TBIndex = -1

        return TBIndex

    def getNewTB(self, csv_date, accounts, accountIndexs, equity_account, TBDict):  # accounts the chart of accounts 
    
        a_month = relativedelta(months=1)
        previous_date = csv_date - a_month
        previous_month = previous_date.strftime("%Y-%m")

        current_month_num = csv_date.month
        newTB = []
        tempTB = TBDict[previous_month]
        acct_total = 0

        # Add the new BS/IS entries to the current first
        
        # if the csv month is Jan then add up all the IS accounts and add to Retained Earnings for the prior year.
        # then strip (pop) off all the IS accounts

        if current_month_num == 1:

            for row in tempTB:

                acc_name = row[kTBAcIndex]
                BSorIS = ""

                try:
                    #If found
                    TBIndex = accountIndexs.index(acc_name)
                    BSorIS = accounts[TBIndex][kBSorIS]
                
                except:
                    # otherwise return a -1 to signify it's not found
                    TBIndex = -1


                #### fix this ####
                
                if BSorIS == "BS":
                    #then append to newTB
                    newTB.append(row)

                elif BSorIS == "IS":
                    if row[kDRIndex]:
                        # element non blank
                        acct_total = float(acct_total) + float(row[kDRIndex])

                    if row[2]:
                        # element non blank
                        acct_total = float(acct_total) - float(row[kCRIndex])

                else:
                    print("The BS/IS varaible is invalid in month: ", current_month_num)           

            # add the the designated Retained Earnings Account
            # if the RE account doesn't exist, add it

            RE_account_index = self.getTBIndex(csv_date, equity_account)

            if RE_account_index == -1:

                # determine if the Retained Earnings amount is a Debit or Credit
                if acct_total > 0:
                    # Debit
                    RE_row = [equity_account, acct_total,0]

                else:
                    # Credit
                    RE_row = [equity_account, 0,-acct_total]
                    
                newTB.append(RE_row)
                
            else:
                if acct_total > 0:
                    # Debit
                    newTB[RE_account_index][kDRIndex] = float(newTB[RE_account_index][kDRIndex]) + acct_total
                    newTB[RE_account_index][kCRIndex] = 0
                else:
                    # Credit
                    newTB[RE_account_index][kCRIndex] = float(newTB[RE_account_index][kCRIndex]) - acct_total
                    newTB[RE_account_index][kDRIndex] = 0

        else:
            #otherwise Feb-Dec, just use the prior month's csv to start
            newTB = tempTB       

        return newTB    
