from datetime import *
from dateutil.relativedelta import *
from Dates import *
from Constants import *

import pandas as pd

class CFormat():

    def __init__(self, inputs):

        self.IS_len = inputs.IS_len
        self.BS_len = inputs.BS_len
        self.IS_BS_columns = inputs.months_total

        TB_header = [kAccounts, kDR, kCR]


    def format_FS(self, file_path, FS_dfs):

        df_writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
        workbook = df_writer.book

        for FS_key in FS_dfs:
            FS_type = FS_key[:2]

            if FS_type == kBS:
                FS_length = self.BS_len
            elif FS_type == kIS:
                FS_length = self.IS_len
                # get a sum row from rows 2 to IS_len
            else:
                print("Format class error, FS type is incorrect.")

            df = FS_dfs[FS_key]

            #blank row for seperating account rows from total row
            pd.concat([df,pd.Series()])

            #get totals for bottom of columns
            sum = df.sum()
            sum = sum.transpose()
            sum.name = 'Sum'
            # Assign sum of all rows of DataFrame as a new Row
            pd.concat([df, sum])

            df.to_excel(df_writer, sheet_name = FS_key, index = False)

            worksheet = df_writer.sheets[FS_key]

            number_fmt = workbook.add_format({'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)', 'bold': False})
            bottom_fmt = workbook.add_format()
            bottom_fmt = number_fmt
            
            # 1st column is IS/BS category
            # 14 is std column width
            worksheet.set_column(0, self.IS_BS_columns+2, kStd_cat_columns, number_fmt)  # Set format for col 0.
            worksheet.set_column(1, self.IS_BS_columns+2, kStd_num_columns, number_fmt)  # Set format for col 1 - months projections.

            
            worksheet.set_row(FS_length, None, bottom_fmt)
            worksheet.set_row(FS_length+1, 6)
            worksheet.set_row(FS_length+2, None, bottom_fmt)

        df_writer.close()

# format header


# format $number row


# format number row


# format descriptive column(s)


                
