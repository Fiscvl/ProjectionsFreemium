import pandas as pd # to replace csv
import openpyxl
from Constants import *

from datetime import *
from dateutil.relativedelta import *

# kTBaccountIndex = 0
# kTBcreditIndex = 1
# kTBCreditIndex = 2

class CJE():

    def __init__(self):

        pass

    def performJE(self, month, TB, DR_acct, CR_acct, amount):              
        
        if amount == 0:
            #no need for a JE for a zero amount
            return TB
       
        i = 0
        TBindex = -1
                        
        for row in TB:
        # see if DR item exists in TB
            if DR_acct == row[kTBAcIndex]: #kTBAcIndex
                TBindex = i
                break
            i += 1

        if TBindex != -1:

            if TB[TBindex][kDRIndex] != "":
                TB[TBindex][kDRIndex] = (TB[TBindex][kDRIndex]) + (amount)
            else:
                TB[TBindex][kDRIndex] = (amount)
                
        else:
            TB.append([DR_acct, (amount),0])
                        
        i = 0
        TBindex = -1
                        
        for row in TB:
        # see if CR item exists in TB
            if CR_acct == row[kTBAcIndex]:                   
                TBindex = i
                break
            i += 1

        if TBindex != -1:


            if TB[TBindex][kCRIndex] != "":
                TB[TBindex][kCRIndex] = (TB[TBindex][kCRIndex]) + (amount)
                    
            else:
                TB[TBindex][kCRIndex] = (amount)
       
        else:
            TB.append([CR_acct,0, (amount)])

        return TB


    
