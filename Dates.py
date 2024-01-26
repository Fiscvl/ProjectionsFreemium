from datetime import *
import pandas as pd

class CMonths():

	# Calculate the serial number a Month represents
	# starting from Jan, 2016 as the 1st month
	# So it returns a 1 if you send a date between1/1/16 thru 1/31/16




    def __init__(self, start_date, end_date, projections_date):
        
        self.start_date = start_date  #date(start_date.year, start_date.month, start_date.day)
        self.end_date = end_date  #date(end_date.year, end_date.month, end_date.day)
        self.start_month = self.GetMonth(start_date)
        self.end_month = self.GetMonth(end_date)
        self.projections_date = projections_date  #date(projections_date.year, projections_date.month, projections_date.day)
        self.projections_month = self.GetMonth(projections_date)
        self.model_term = self.end_month - self.start_month + 1
        self.actuals_term = self.projections_month - self.start_month + 1
        self.projections_term = self.end_month - self.projections_month + 1
        self.projections_start = self.projections_month - self.start_month

        print(f"  ** start month  ** : { self.start_month}")
        print(f"  ** end month  ** : { self.end_month}")
        print(f"  ** projections_start  ** : { self.projections_start}")
        
    def GetMonthNum(self, in_date):
         self.MonthNum = self.GetMonth(in_date)-self.start_month
         return self.MonthNum

    def GetMonth(self, in_date):
        kStartYear = 2016
        kMonthsinYear = 12        
        
        temp_date = pd.to_datetime(in_date)
        vYear = temp_date.year
        vYear = vYear - kStartYear
        self.MonthNum2016 = kMonthsinYear * vYear + temp_date.month
        return self.MonthNum2016
