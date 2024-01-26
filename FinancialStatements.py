import pandas as pd

from datetime import *
from dateutil.relativedelta import *
from Constants import *
from Formats import *
from xlsxwriter.utility import xl_rowcol_to_cell

# create FS files:
    #   Open IS Standard File - accounts in IS
    #   Open Department File - departments in IS, including consolidated
    #   Create IS files  - all departments

    #   Open BS Standard File - accounts in BS
    #   Open Department File - just consolidated
    #   Create BS files  - just consolidated

    #   get number of depts

    #   get list of FS lines

    #   loop thru BS FS lines, select just BS lines and then loop thru every month
    #   in the projection, creating a list of FS with months +1 columns

class CFinStatements():

    def __init__(self, Depts, months, start_date, inputs, TBs):



        fInputPath =    'C:/Users/mcbreslin/Dropbox (Personal)/Fiscvl/Models & other/Python/Data/Input/'
        self.fOutputPath =   'C:/Users/mcbreslin/Dropbox (Personal)/Fiscvl/Models & other/Python/Data/Output/'
        self.fTBPath =       'C:/Users/mcbreslin/Dropbox (Personal)/Fiscvl/Models & other/Python/Data/Trial Balances/'
        
        self.ISIndex = []
        self.BSIndex = []
        self.FS_Dict = {}
        self.FS_Outputs = {}
        self.BS_type = {}
        self.IS_totals = {}
        self.IS_prior_month = 0
        self.Accounts = []
        self.AccountIndexs = []
        self.Depts = []
        self.TBs = TBs

        fAccounts = fInputPath+'Accounts.csv'
        fBS = fInputPath+'BS.csv'
        fIS = fInputPath+'IS.csv'

        self.Accounts = inputs.accounts
        
        self.AccountIndexs = []
        self.AccountIndexs = self.GetListIndex(self.Accounts,self.AccountIndexs)

        depts = inputs.depts

        for dept in depts:
            deptStr = str(dept)
            deptStr = deptStr.replace('[', "")
            deptStr = deptStr.replace("'", "")
            deptStr = deptStr.replace(']', "")
            IS_string = kIS_string + "_" + deptStr
            self.FS_Outputs[IS_string] = self.CreateFSlist(months, fIS, IS_string,  start_date, inputs)
            self.IS_totals[IS_string] = 0    

        self.ISIndex = self.GetListIndex(inputs.IS,self.ISIndex)
        self.IS_totals[kIS_string] = 0
        self.FS_Outputs[kIS_string] = self.CreateFSlist(months, fIS, kIS_string, start_date, inputs)
        
        self.BSIndex = self.GetListIndex(inputs.BS,self.BSIndex)
        self.FS_Outputs[kBS_string] =  self.CreateFSlist(months, fBS, kBS_string, start_date, inputs)

        self.BS_type[kAssets] = 0
        self.BS_type[kLiabilities] = 0
        self.BS_type[kEquity] = 0


    def CreateFSlist(self, months, file_out, FS_type, start_date, inputs):

        counter = 0 

        if FS_type == kBS:
            FS_rows = inputs.BS
            

        elif FS_type[:2] == kIS:
            FS_rows = inputs.IS          

        else:
            print("A incorrect FS type was sent to Financial Statements 'CreateFSlist' module", FS_type)

        self.FS_output = [[0 for x in range(months+1)] for y in range(len(FS_rows))]
        
        counter = 0
        for FS_account in FS_rows:
            self.FS_output[counter][0] = str(FS_rows[counter])[1:-1]
            counter += 1

        header = []
        a_month = relativedelta(months=1)
        projections_date = start_date
        header.append(kFS_line)

        counter = 0
        while counter < months :
            header.append(projections_date.strftime("%Y-%m"))
            projections_date = projections_date + a_month
            counter += 1

        return self.FS_output

    def ActualsUpdate(self, model_term, start_date, inputs, formats):

        month_counter = 1
        month_number = 1
        current_date = start_date
        prior_date = current_date
        current_month = ""
        prior_month = ""
        a_month = relativedelta(months=1)
        TB_Statistics = []  #0 is PL total to equity
        current_TB = []
        prior_TB = []
        prior_TB_index = 0

        while month_counter <= model_term:
                month_number = current_date.month
                
                self.ClearTotals()
                
                if month_number == 1:
                        current_month = current_date.strftime("%Y-%m")
                        current_TB = self.TBs[current_month]
                        Feb_Dec_month = False
                        self.UpdateFS(current_TB, prior_TB, prior_TB_index, month_counter, Feb_Dec_month, inputs)
 
                else:
                        
                        current_month = current_date.strftime("%Y-%m")
                        prior_date = current_date - a_month
                        prior_month = prior_date.strftime("%Y-%m")
                        
                        current_TB = self.TBs[current_month]
                        prior_TB = self.TBs[prior_month]
                        prior_TB_indexs = []
                        prior_TB_indexs = self.GetListIndex(prior_TB, prior_TB_indexs)
                        Feb_Dec_month = True
                        self.UpdateFS(current_TB, prior_TB, prior_TB_indexs, month_counter,Feb_Dec_month, inputs)

                current_date += a_month        
                self.UpdateCheckBS(month_counter)
                
                month_counter += 1

        self.MonthActualsWrite(inputs, formats) #mMonthActualsWrite

    def UpdateFS(self, current_TB, prior_TB, prior_TB_indexs, month_counter, Feb_Dec_month, inputs):

        TB_row = 0

        for row in current_TB:

                #AccountIndexs.index(row[0])
                # assumes the TB account is in the chart of accounts
                Acc_index = self.AccountIndexs.index(row[kTBAccountIndex])
                # tuple for account info: ac#, FS line identifier, BS/IS, Dept if "IS" or Type if "BS"
                Account_set  = (self.Accounts[Acc_index][kTBAccountIndex],self.Accounts[Acc_index][kFSAcc],self.Accounts[Acc_index][kBSorIS],self.Accounts[Acc_index][kDept])

                if row[kDRIndex] == 0:
                        Account_valueDR = 0
                else:
                        Account_valueDR = float(row[kDRIndex])

                if row[kCRIndex] == 0:
                        Account_valueCR = 0
                else:
                        Account_valueCR = float(row[kCRIndex])

                Account_value = Account_valueDR - Account_valueCR

                if Account_set[2] == kIS:

                        # Adjust the current account value by subtracting prior months value
                        # Not done in Jan, as TB resets every 1st month in a fiscvl year

                        # Add to Dept IS
                        # Add to Consolidate IS
                        IS_index_num = self.ISIndex.index(Account_set[1])

                        if Feb_Dec_month:
                            Prior_account_value = 0

                            try:

                                Prior_acc_Index = prior_TB_indexs.index(row[kTBAccountIndex])

                                if prior_TB[Prior_acc_Index][kDRIndex] == 0:
                                    Prior_account_valueDR = 0
                                else:
                                    Prior_account_valueDR = float(prior_TB[Prior_acc_Index][kDRIndex])

                                if prior_TB[Prior_acc_Index][kCRIndex] == 0 :
                                    Prior_account_valueCR = 0
                                else:
                                    Prior_account_valueCR = float(prior_TB[Prior_acc_Index][kCRIndex])

                                Prior_account_value = Prior_account_valueDR - Prior_account_valueCR

                            except:
                                pass
                                    
                            Account_value = Account_value - Prior_account_value
                                
                        IS_value = round(Account_value,2)
                        
                        FS_index = "IS_"+Account_set[3]
                        self.FS_Outputs[FS_index][IS_index_num][month_counter] = round(float(self.FS_Outputs[FS_index][IS_index_num][month_counter]) + Account_value,2)
                        self.IS_totals[FS_index] = round(IS_value + self.IS_totals[FS_index],2)
                        
                        FS_index = kIS
                        self.FS_Outputs[FS_index][IS_index_num][month_counter] = round(float(self.FS_Outputs[FS_index][IS_index_num][month_counter]) + Account_value,2)
                        self.IS_totals[FS_index] = round(IS_value + self.IS_totals[FS_index],2)

                elif Account_set[2] == kBS:
                       
                        #Add to BS
                        
                        BS_index_num = self.BSIndex.index(Account_set[1])
                        FS_index = kBS
                    
                        prior_value = float(self.FS_Outputs[FS_index][BS_index_num][month_counter])
                            
                        self.FS_Outputs[FS_index][BS_index_num][month_counter] = round(prior_value + Account_value,2)

                
                        if Account_set[3] == kAssets:
                                self.BS_type[kAssets] = round(Account_value + self.BS_type[kAssets],2)

                        elif Account_set[3] == kLiabilities:
                                self.BS_type[kLiabilities] = round(Account_value + self.BS_type[kLiabilities],2)

                        elif Account_set[3] ==kEquity:
                                self.BS_type[kEquity] = round(Account_value + self.BS_type[kEquity],2)

                        else:
                                print("BS type in Accounts is wrong")
                else: 

                        print("Error in TB, account isn't classified as a BS or IS account")

                TB_row += 1

    def OpenTBcsv(self, month_file):

        TB_file = self.fTBPath + month_file

        try:

                with open(TB_file, 'r') as read_obj:
                        csv_reader = reader(read_obj)
                        month_TB = list(csv_reader)

        except FileNotFoundError:
                print(f"Can't find or open file {month_file}")

        return  month_TB

    def ClearTotals(self):

        for BS_key in self.BS_type:
             self.BS_type[BS_key] = 0

        for IS_key in self.IS_totals:
             self.IS_totals[IS_key] = 0

    def GetListIndex(self, List, ListIndex):

        for row in List:
                List_name = row[0]
                ListIndex.append(List_name)
        
        return ListIndex

    def UpdateCheckBS(self, month_counter):

        IS_key = kIS
        equityValueMonth = self.IS_totals[IS_key]        

        BS_index_num = self.BSIndex.index(kRetainedEarnings)  # Don't change the value of 'Retained Earnings' in .csv
        FS_index = kBS
        self.FS_Outputs[FS_index][BS_index_num][month_counter] = self.FS_Outputs[FS_index][BS_index_num][month_counter] + equityValueMonth + self.IS_prior_month
        

        BS_month_values =self.FS_Outputs[FS_index]
        BS_total_check = 0
        row_counter = 1
        
        for row in BS_month_values:

                if row_counter >= 1:
                        BS_total_check = round(BS_total_check + float(row[month_counter]),2)
                        
                row_counter += 1

        #Feb - Dec ,

        if BS_total_check != 0:
            print(f"BS totals are not zero {BS_total_check}")

        self.BS_type[kEquity] = round(self.BS_type[kEquity] + equityValueMonth + self.IS_prior_month,2)

        BS_balance_check = round(self.BS_type[kAssets] + self.BS_type[kLiabilities] + self.BS_type[kEquity],2)

        if BS_balance_check != 0:
                print(f"Assets {self.BS_type[kAssets]}")
                print(f"Liabilities {self.BS_type[kLiabilities]}")
                print(f"Equity after {self.BS_type[kEquity]}")
                print("BS DOES NOT Balance")
                        

        if month_counter%12 == 0:
                self.IS_prior_month = 0
        else:
                self.IS_prior_month = equityValueMonth + self.IS_prior_month

    def MonthActualsWrite(self, inputs, formats):

        #This needs to be rewritten to output Excel
        sheet_header = [kAccounts]
        sheet_header.extend(inputs.months_header)
        file_path = inputs.full_path_output + kFSOut
        FS_dfs = {}
        
        for FS_key in self.FS_Outputs:    
                FS_to_write = self.FS_Outputs[FS_key]

                df = pd.DataFrame(FS_to_write, columns = sheet_header)
                FS_dfs[FS_key] = df             

        FS_keys = self.FS_Outputs.keys()
        formats.format_FS(file_path, FS_dfs)

    def format_FS(self, inputs):

        writer = pd.ExcelWriter('fancy.xlsx', engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='report')

        #df.save()
        df.close()

    
