Hello,

This app is a subset of an overall financial projection app designed to forecast the future financial results of a company, while integrating in actual results.  Thus, providing a proper set of financials from a given month into the future.  

This subset is designed to provide a future view of revenue and the related schedules that arise in a b2b SaaS company.

To run the app, download the zip file, extract all the files into a folder and open 'Projections.py'.  Run Build.

There are three components to this app:

	Current invoices
	Future contracts (already signed)
	New business - aggregated as we cannot know the future clients

	The app currently allows for 5 products, but that is wholly data-driven - changing the inputs can accommodate as many products as necessary.

	The output of the app is a full set of 'revenue recognition sheets', as well as the revenue, by product, for each of the products in the list.

	Note: The Future contracts and New business are both continued through the end of the projections.  They are continually churned each renewing contract as follows: (1-churn)^renewal(n) where n is the number of times the contract has renewed from its initial start.

	Note in the inputs-product tab there are percentages for each product.  Those are for allocating the total forecast new booking amongst the products.  Thus, the total percentages should add up to 100%. (It will work with other totals, but it does not make sense)

Each of the sheets provides monthly figures.

The sheets on the revenue recognition files are:

	Revenue
	Invoices
	Deferred
	Accrual
	Collections
	Commissions

The Revenue Product sheets:
	Product 1
	...
	Product 5  (can be product 'n')

The revenues per month for the product will add up to the monthly revenues for each component.  Existing monthly = Product monthly for Products 1-5)

For every item (row) in the components existing/contract each month the sum of revenue, invoice, deferred & accrual equals zero.

Note in this model a debit has a positive value and a credit has a negative value (similar to under the hood in most accounting systems).

An accrual is a contract where the revenue starts before invoicing.  In a deferral, the invoicing occurs before or at the start of the revenue.

The model is atomic down to the month.  A contract starting on the 1st of the end of the month will be counted as one month’s revenue.  Same with any other transaction in the larger model.

The mechanics of the app:

There are currently 3 input files.  I suggest leaving the file "RevAccounts.xlsx" alone.  It controls the accounting entries for the monthly transactions, which are unnecessary in this section.  

The other two files are:
	Inputs
	RevenueInputs

Inputs has three sheets of note (the others are for the wider products, including chart of accounts and related accounts for specific transactions).  The commission table is described further below.

The Input sheet has individual parameters.  The dates are the start of the projections, the end of the actuals to be incorporated (not really used in this app), and the end of the projections.  I suggest you set the start of the projections and the actuals to be the same date and a month before the term of the revenue projections.  

The rest of the inputs are:
	Default churn - if there is no product transaction history - so a churn cannot be calculated
	Client Collection Days	- if there is no collection history for a specific client, this is the default day from invoice to payment.
	Term for New - the number of months in a 'New' contract	
	Churn Months Lookback - how many months from start of the projections should be used to calculate churn.

Other calculations:

Collections - if there is a historical list of invoices, including payment and collection dates, as well as the amount you can calculate the weighted average days to payment.  The days to payment then can be used to forecast future payments.

Churn - if there is a history of invoices as noted above you can calculate the churn.  We have included a product churn, not a client churn as we believe it is more insightful.  If there is no history, or history for a specific product, then a default percentage is used - from inputs.

Commissions - the amount of commissions for a specific contract is calculated for the three revenue components based on the table in the inputs file - 'RevCommissions'.  This has three rows - one for each component.  It also provides a choice on how the commissions are calculated - when collect, by mmr, or when invoiced.  There is also a percentage for the initial contract (higher usually) and for renewals.  Note there is no initial percentage for Existing contracts - we assume the commission has already been paid.

Churn - Churn examines the last 'n' months (n is set in Churn Months Lookback and its default is 24 months).  It calculates the product churn for that period.  Churn is defined as the loss of a client for 2 or more months for a specific client-product pair.  Churn output is calculated on a yearly basis.  Thus, the calculated percentage is scaled to "Churn Months Lookback/12".  If no churn is calculated the churn of a specific contract uses the "Default churn" percentage (which is assumed to be a yearly percentage).
	
	All churn items for future contracts and new contracts are annualized.

The above calculations are found in the Outputs folder.
	
	Churn.xlsx
	Collections.xlsx
	The commissions tab is found in each of the revenue components; Existing, Renewals and New.

To modify the data:

	There is a Python file named "Constants.py" detailing all the numbers and names found in the app, organized by category or by Excel sheet position or Sheet Name.

	The 'Inputs' file implemented in Python as a list.  This means it has a row and column orientation.  Since there is only one row, an input location is based on its column (starting with 0 for column A).  You can change to order of the list, but it MUST be reflected in Constants.  You can change the column headings to be whatever is better for your team, it has no effect on the app.  The inputs section of Constants starts at line 50.

	The 'RevenueInputs' file is used in Python as a Pandas dataframe.  This means the opposite of a list --> the Column Names are how the data is located, and the column number is irrelevant. You can change the names of the column headings if the corresponding change is made in Constants.py.  The sheet names are also critical and are located at the top of the data table listing.
		Existing starts at line 189
		Contracts starts at line 205
		New starts at line 229
