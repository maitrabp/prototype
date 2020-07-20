import re
import pdfplumber
import pandas as pd
from collections import namedtuple

mainDF = pd.DataFrame()

#if there is next, then get (else return current) --UNUSED
def getNext(index, fullPagetext):
    if((index+1) < range(fullPagetext)):
        return fullPagetext[index+1]
    else:
        return fullPagetext[index]

#write to CSV func, manipulates with the dataframe
#Usage Example: fillDF(FINAL_PAGE_DATA, ['Date', 'Subheader'])..
def fillDF(PAGE_DATA, PAGE_DATA_COLUMNS):
    pageDF = pd.DataFrame(PAGE_DATA, columns=PAGE_DATA_COLUMNS)
    global mainDF
    if mainDF.empty:
        mainDF = mainDF.append(pageDF)
    else:
        mainDF = pd.concat([mainDF, pageDF])
    print(mainDF)
    print("__________________________DATAFRAME UPDATED______________________")

def conv_to_csv():
    global mainDF
    saveCSVfilepath = r'./parseRESULT2.csv'
    mainDF.to_csv(saveCSVfilepath, index=False)
    print("\n\nMESSAGE: Your csv file is ready, go to " + saveCSVfilepath + " to take a look at!")
    return saveCSVfilepath

def file_parse(file):
    with pdfplumber.open(file) as pdf:
        pages = pdf.pages
        FINAL_PAGE_DATA = []
        for i, page in enumerate(pdf.pages):
            if i == 48:
                FINAL_PAGE_DATA.clear()
                text = page.extract_text()
                headerlist = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER', 'GOV_ACTIVITIES', 'BUS_ACTIVITY', 'TOTAL']
                #------------------Filters-----------------
                county_filter = re.compile(r'county|COUNTY|County$')
                statementOfNetPositionFilter = re.compile(r'Statement of Net Position|statement of net position|STATEMENT OF NET POSITION')
                dateFilter = re.compile(r'[a-zA-Z]+\s\d\d[,]\s\d\d\d\d')
                #--------------------------------------UNUSED(approach not found yet)-----------------------------------
                # expensesFilter = re.compile(r'Expenses|EXPENSES|expenses')
                # chargesForServicesFilter = re.compile(r'(Charges for)(Services)|(Charges)(for Services)|(Charges)(for)(Services)')
                # operatingGrantsAndContributionsFilter = re.compile(r'(Operating)(Grants and)(Contributions)|(Operating Grants)(and Contributions)|(Operating Grants)(and)(Contributions)')
                # capitalGrantsAndContributionsFilter = re.compile(r'(Capital)(Grants and)(Contributions)|(Capital Grants)(and Contributions)|(Capital)(Grants)(and Contributions)|(Capital)(Grants)(and)(Contributions)')
                
                #--------------------------------------------------DATA FILLER LINE-------------------------------------------------------------------
                dfLine = namedtuple('dfLine', 'date county header pageheader govActivityData busActivityData totalData')
                #--------------------------------------------------Split Lines based on /n and store into list----------------------------------------
                fullPagetext = text.split('\n')
                #--------------------------------------------------Flags to look for in lines---------------------------------------------------------
                #-------------------ASSETS-----------------------------
                cashAndPooledInvestmentsSplit = "Cash and pooled investments"
                #-------------ISSUE (Assets being matched, it's only one word LEFT OFF HERE)-----------------------
                capitalAssetsNotBeingDepricatedSplit = "Capital assets not being depreciated | Capital assets not subject to depreciation"
                capitalAssetsBeingDepcricatedSplit = "Capital assets being depreciated, net | Capital assets being depreciated - net |  Capital assets subject to depreciation, net | Capital assets subject to depreciation - net | Capital assets net of accumulated depreciation | Assets subject to depreciation, net | Assets subject to depreciation - net"
                totalAssetsSplit = "Total assets | Total Assets"
                #-------------------LIABILITIES-----------------------------
                longTermDebtSplit = "Long-term debt: | Long-Term Debt: | Long-term debt"
                # if long term debt meets, then
                dueWithinOneYearSplit = "Due within one year | current portion | current maturities"
                dueInMoreThanOneYearSplit = "Due in more than one year | noncurrent portion | noncurrent maturities"
                netPensionLiabilitySplit = "Net pension liability | Net Pension Liability"
                netOtherPostEmploymentBenefitsLiabilitySplit = "Net other postemployment benefits liability"
                totalLiabilitiesSplit = "Total liabilities | Total Liabilities"
                #------------------NET POSITION ----------------------------
                netInvestmentInCapitalAssetsSplit = "Net investment in capital assets | Net Investment In Capital Assets"
                unrestrictedSplit = "Unrestricted | Unrestricted (deficit)"
                totalNetPositionSplit = "Total net position | Total Net Position"
                #Temp Storage variables
                county = ''
                date = ''
                header = ''

                #each line will be manipulated using index, index starts at 0
                lineIndex = 0
                while lineIndex in range(len(fullPagetext)):
                    #Get rid of $ signs
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", " ")
                    #Look for these flags within the page (as we go line by line), if found return true, otherwise false
                    countyFound = county_filter.search(fullPagetext[lineIndex])
                    headerFound = statementOfNetPositionFilter.search(fullPagetext[lineIndex])
                    dateFound = dateFilter.search(fullPagetext[lineIndex])
                    cashAndPooledInvestmentsFound = cashAndPooledInvestmentsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    capitalAssetsNotBeingDepricatedFound = capitalAssetsNotBeingDepricatedSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    capitalAssetsBeingDepcricatedFound = capitalAssetsBeingDepcricatedSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalAssetsFound = totalAssetsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    longTermDebtFound = longTermDebtSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    netPensionLiabilityFound = netPensionLiabilitySplit.find(fullPagetext[lineIndex].split("  ")[0])
                    netOtherPostEmploymentBenefitsLiabilityFound = netOtherPostEmploymentBenefitsLiabilitySplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalLiabilitiesFound = totalLiabilitiesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    netInvestmentInCapitalAssetsFound = netInvestmentInCapitalAssetsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    unrestrictedFound = unrestrictedSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalNetPositionFound = totalNetPositionSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    
                    #If found, then store them into a list
                    if countyFound:
                        county = fullPagetext[lineIndex]
                    elif dateFound:
                        date = fullPagetext[lineIndex].replace("Year Ended", "")
                    elif headerFound:
                        header = fullPagetext[lineIndex]
                    elif cashAndPooledInvestmentsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if cashAndPooledInvestmentsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] + " - ASSETS"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " - ASSETS"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif capitalAssetsNotBeingDepricatedFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if capitalAssetsNotBeingDepricatedSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] + " - ASSETS"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " - ASSETS"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif capitalAssetsBeingDepcricatedFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if capitalAssetsBeingDepcricatedSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] + " - ASSETS"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " - ASSETS"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif totalAssetsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalAssetsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " - ASSETS"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif longTermDebtFound != -1:
                        nextLine = fullPagetext[lineIndex + 1].split("  ")
                        nextNextLine = fullPagetext[lineIndex + 2].split("  ")
                        mainpageHeader = fullPagetext[lineIndex].split("  ")[0]
                        if dueWithinOneYearSplit.find(nextLine[0]) != -1:
                            if len(nextLine) > 3:
                                pageHeader = mainpageHeader  + " " + nextLine[0] + " - LIABILITIES"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))

                        if dueInMoreThanOneYearSplit.find(nextNextLine[0]) != -1:
                            if len(nextNextLine) > 3:
                                pageHeader = mainpageHeader + " " + nextNextLine[0] + " - LIABILITIES"
                                #Keep data, remove header
                                fullPagetext[lineIndex+2] = fullPagetext[lineIndex+2].replace(nextNextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+2] = fullPagetext[lineIndex+2].replace("$", "")
                                fullPagetext[lineIndex+2] = fullPagetext[lineIndex+2].replace("-", "0")
                                fullPagetext[lineIndex+2] = fullPagetext[lineIndex+2].replace("(", "-")
                                fullPagetext[lineIndex+2] = fullPagetext[lineIndex+2].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+2].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                        lineIndex += 2
                    elif netPensionLiabilityFound != -1:
                         #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if netPensionLiabilitySplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] + " (noncurrent due in one year) - LIABILITIES"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " (noncurrent due in one year) - LIABILITIES"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif netOtherPostEmploymentBenefitsLiabilityFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if netOtherPostEmploymentBenefitsLiabilitySplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif totalLiabilitiesFound != -1:
                         #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalLiabilitiesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif netInvestmentInCapitalAssetsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if netInvestmentInCapitalAssetsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] + " - NET POSITION"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + "- NET POSITION"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif unrestrictedFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if unrestrictedSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] + " - NET POSITION"
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + "- NET POSITION"
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    elif totalNetPositionFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalNetPositionSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    lineIndex+=1   
                fillDF(FINAL_PAGE_DATA, headerlist)
                print("---------------------DONE PAGE 49----------------------\n\n\n")
            elif i == 49:
                FINAL_PAGE_DATA.clear()
                text = page.extract_text()
                headerlist = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER', 'EXPENSES', 'CHARGES_FOR_SERVICES', 'OPERATING GRANTS AND CONTRIBUTIONS', 'CAPITAL GRANTS AND CONTRIBUTIONS']
                #------------------Filters-----------------
                county_filter = re.compile(r'county|COUNTY|County$')
                statementOfActivitiesFilter = re.compile(r'Statement of Activities|statement of activities|STATEMENT OF ACTIVITIES')
                #CHECK DATE FILTER --> NEXT STEP
                dateFilter = re.compile(r'[a-zA-Z]+\s\d\d[,]\s\d\d\d\d')
                #--------------------------------------UNUSED(approach not found yet)-----------------------------------
                # expensesFilter = re.compile(r'Expenses|EXPENSES|expenses')
                # chargesForServicesFilter = re.compile(r'(Charges for)(Services)|(Charges)(for Services)|(Charges)(for)(Services)')
                # operatingGrantsAndContributionsFilter = re.compile(r'(Operating)(Grants and)(Contributions)|(Operating Grants)(and Contributions)|(Operating Grants)(and)(Contributions)')
                # capitalGrantsAndContributionsFilter = re.compile(r'(Capital)(Grants and)(Contributions)|(Capital Grants)(and Contributions)|(Capital)(Grants)(and Contributions)|(Capital)(Grants)(and)(Contributions)')
                
                #--------------------------------------------------DATA FILLER LINE-------------------------------------------------------------------
                dfLine = namedtuple('dfLine', 'date county header pageheader expenses chargesForServices operatingGrantsAndContributions capitalGrantsAndContributions')
                #--------------------------------------------------Split Lines based on /n and store into list----------------------------------------
                fullPagetext = text.split('\n')
                #--------------------------------------------------Flags to look for in lines---------------------------------------------------------
                totalGovActSplit = "Total governmental activities"
                totalBusActSplit = "Total business-type activities"
                totalPrimaryGovSplit = "Total primary government"

                #Temp Storage variables
                county = ''
                date = ''
                header = ''

                #each line will be manipulated using index, index starts at 0
                lineIndex = 0
                while lineIndex in range(len(fullPagetext)):
                    #Look for these flags within the page (as we go line by line), if found return true, otherwise false
                    countyFound = county_filter.search(fullPagetext[lineIndex])
                    headerFound = statementOfActivitiesFilter.search(fullPagetext[lineIndex])
                    dateFound = dateFilter.search(fullPagetext[lineIndex])
                    totalGovActSplitFound = fullPagetext[lineIndex].find(totalGovActSplit)
                    totalBusActSplitFound = fullPagetext[lineIndex].find(totalBusActSplit)
                    totalPrimaryGovSplitFound = fullPagetext[lineIndex].find(totalPrimaryGovSplit)

                    #If found, then store them into a list
                    if countyFound:
                        county = fullPagetext[lineIndex]
                    elif dateFound:
                        date = fullPagetext[lineIndex].replace("Year Ended", "")
                    elif headerFound:
                        header = fullPagetext[lineIndex]
                    elif totalGovActSplitFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")[0]
                        if totalGovActSplit.find(nextLine) != -1:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            
                            #Keep data, remove header
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")

                            #Replace or remove these items and only keep numbers
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")

                            #Split numerical data by , based on space detected between each
                            row = fullPagetext[lineIndex+1].split()
                            
                            #Store data into a list
                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 5], row[len(row) - 4], row[len(row) - 3], row[len(row - 2)]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) and $
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                            
                            #Keep data, remove header
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(nextLine, "")
                            
                            #Split numerical data by, based on space detected between each
                            row = fullPagetext[lineIndex].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 5], row[len(row) - 4], row[len(row) - 3], row[len(row)  - 2]))
                            

                    elif totalBusActSplitFound != -1:
                        nextLine = fullPagetext[lineIndex + 1].split("  ")[0]
                        if totalBusActSplit.find(nextLine) != -1:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            
                            #Keep data, remove header
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")

                            #Replace or remove these items and only keep numbers
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")

                            #Split numerical data by , based on space detected between each
                            row = fullPagetext[lineIndex+1].split()

                            #Store data into a list
                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 5], row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) and $
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                            
                            #Keep data, remove header
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(nextLine, "")
                            
                            #Split numerical data by, based on space detected between each
                            row = fullPagetext[lineIndex].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 5], row[len(row) - 4], row[len(row) - 3], row[len(row)  - 2]))
                            

                    elif totalPrimaryGovSplitFound != -1:
                        nextLine = fullPagetext[lineIndex + 1].split("  ")[0]
                        if totalPrimaryGovSplit.find(nextLine) != -1:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            
                            #Keep data, remove header
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")

                            #Replace or remove these items and only keep numbers
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")

                            #Split numerical data by , based on space detected between each
                            row = fullPagetext[lineIndex+1].split()

                            #Store data into a list
                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 5], row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) and $
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                            
                            #Keep data, remove header
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(nextLine, "")
                            
                            #Split numerical data by, based on space detected between each
                            row = fullPagetext[lineIndex].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 5], row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            

                    #Move to the next line
                    lineIndex+=1 
                #end of while loop iteration of page
                fillDF(FINAL_PAGE_DATA, headerlist)
                print("---------------------DONE PAGE 50----------------------\n\n\n")
            elif i == 50: 
                text = page.extract_text()
                FINAL_PAGE_DATA.clear()
                headerlist = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER', 'GOV_ACTIVITIES', 'BUS_ACTIVITY', 'TOTAL']
                #Filter County on this page
                county_filter = re.compile(r'county|COUNTY|County$')
                #Filter statementOfActivities on this page
                statementOfActivities = re.compile(r'Statement of Activities|statement of activities|STATEMENT OF ACTIVITIES')
                #Filter date
                dateFilter = re.compile(r'[a-zA-Z]+\s\d\d[,]\s\d\d\d\d')
                #------------------------------------------------------------------HEADER FILTERS (UNUSED)------------------------------------------------------
                #Filter governmental activities
                govActivityFilter = re.compile(r'(Governmental) (Activities)')
                #Filter Business-type activities
                busActivityFilter = re.compile(r'(Business-type) (Activities)')
                #Filter Total
                totalFilter = re.compile(r'Total')
                #Filter Component Units
                componentUnitFilter = re.compile(r'(Component) (Units)')
                county  = ''
                header = ''
                date = ''
                pageHeader = ''
                dfLine = namedtuple('dfLine', 'date county header pageheader govActivityData busActivityData totalData')
                govActivityData = 'Government Activities Data'
                busActivityData = ''
                #gets full page split using \n
                fullPagetext = text.split('\n')
                #To fetch the following data (which sometimes are also referred to split by |)
                GrantsRowSplit = "Grants and contributions not restricted to specific programs | Unrestricted state shared revenues | State-shared revenue | State-shared revenue | State grants"
                propertyTaxSplit = "Property taxes"
                totalGenRevTransferSplit = "Total general revenues and transfers"
                ChangeinNetPosSplit = "Change in net position"
                #each line will be accessed using index
                lineIndex = 0
                while lineIndex in range(len(fullPagetext)):
                    countyFound = county_filter.search(fullPagetext[lineIndex])
                    statementOfActivitiesFound = statementOfActivities.search(fullPagetext[lineIndex])
                    dateFound = dateFilter.search(fullPagetext[lineIndex])
                    #See if this line has any data type close to what's in  GrantsFound..
                   #See if this line has any data type close to what's in  GrantsFound..
                    GrantsFound = GrantsRowSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    propertyTaxFound = propertyTaxSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalGenRevTransferFound = totalGenRevTransferSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    ChangeinNetPosFound = ChangeinNetPosSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    if countyFound:
                        county = fullPagetext[lineIndex]
                        print('_______________________________________________________________________')
                    elif statementOfActivitiesFound:
                        header = fullPagetext[lineIndex]
                        print('_______________________________________________________________________')
                    elif dateFound:
                        date = fullPagetext[lineIndex].replace("Year Ended", "")
                        print('_______________________________________________________________________')
                    elif GrantsFound != -1:
                        #See if next line also matches (this means double line subheader formatting issue)
                        nextLine = fullPagetext[lineIndex+1].split("  ")[0]
                        if(GrantsRowSplit.find(nextLine) != -1):
                            #Split both lines at more than one space and concatenate them together to make a header
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            #get rid of the subheader (Ex: Property Tax and only keep numericals)
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")
                            #get rid of ( ) and $
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")

                            #Split numerical data by , based on space space
                            row = fullPagetext[lineIndex+1].split()
                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) and $
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                            row = fullPagetext[lineIndex].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))

                    elif propertyTaxFound != -1:
                        #See if next line also matches (this means double line subheader formatting issue)
                        nextLine = fullPagetext[lineIndex+1].split("  ")[0]
                        if(propertyTaxSplit.find(nextLine) != -1):
                            #Split both lines at more than one space and concatenate them together to make a header
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")
                            #get rid of ( ) and $
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")

                            row = fullPagetext[lineIndex+1].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) and $
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")

                            row = fullPagetext[lineIndex].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))

                    elif totalGenRevTransferFound != -1:
                        #See if next line also matches (this means double line subheader formatting issue)
                        nextLine = fullPagetext[lineIndex+1].split("  ")[0]
                        if(totalGenRevTransferSplit.find(nextLine) != -1):
                            #Split both lines at more than one space and concatenate them together to make a header
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")
                            #get rid of ( ) and $
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")

                            row = fullPagetext[lineIndex+1].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) and $
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")

                            row = fullPagetext[lineIndex].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))

                    elif ChangeinNetPosFound != -1:
                        #See if next line also matches (this means double line subheader formatting issue)
                        nextLine = fullPagetext[lineIndex+1].split("  ")[0]
                        if(ChangeinNetPosSplit.find(nextLine) != -1):
                            #Split both lines at more than one space and concatenate them together to make a header
                            pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine, "")
                            #get rid of ( ) and $
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                            fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")


                            row = fullPagetext[lineIndex+1].split()

                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                            lineIndex += 1
                        else:
                            pageHeader = fullPagetext[lineIndex].split("   ")[0]
                            #get rid of ( ) with - and $ with empty
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                            fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")

                            row = fullPagetext[lineIndex].split()
                            FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))

                    #Move to the next line
                    lineIndex+=1 
                fillDF(FINAL_PAGE_DATA, headerlist)
                print("---------------------DONE PAGE 51----------------------\n\n\n")
            elif i == 65:
                FINAL_PAGE_DATA.clear()
                text = page.extract_text()
                headerlist = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER','Business-type Activities - Enterprise Funds - TOTAL']
                #------------------Filters-----------------
                county_filter = re.compile(r'county|COUNTY|County$')
                proprietaryFundsSplit = re.compile(r'Proprietary Funds$')
                statementOfNetPositionFilter = re.compile(r'Statement of Net Position|statement of net position|STATEMENT OF NET POSITION')
                dateFilter = re.compile(r'[a-zA-Z]+\s\d\d[,]\s\d\d\d\d')
                #--------------------------------------UNUSED(approach not found yet)-----------------------------------
                # expensesFilter = re.compile(r'Expenses|EXPENSES|expenses')
                # chargesForServicesFilter = re.compile(r'(Charges for)(Services)|(Charges)(for Services)|(Charges)(for)(Services)')
                # operatingGrantsAndContributionsFilter = re.compile(r'(Operating)(Grants and)(Contributions)|(Operating Grants)(and Contributions)|(Operating Grants)(and)(Contributions)')
                # capitalGrantsAndContributionsFilter = re.compile(r'(Capital)(Grants and)(Contributions)|(Capital Grants)(and Contributions)|(Capital)(Grants)(and Contributions)|(Capital)(Grants)(and)(Contributions)')
                
                #--------------------------------------------------DATA FILLER LINE-------------------------------------------------------------------
                dfLine = namedtuple('dfLine', 'date county header pageheader totalData')
                #--------------------------------------------------Split Lines based on /n and store into list----------------------------------------
                fullPagetext = text.split('\n')
                #--------------------------------------------------Flags to look for in lines---------------------------------------------------------
                #-------------------ASSETS-----------------------------
                cashAndPooledInvestmentsSplit = "Cash and pooled investments | Cash and cash equivalents"
                nonCurrentAssetsCapitalAssetsSplit = "Noncurrent assets - capital assets, net | Noncurrent assets - capital assets - net"
                totalAssetsSplit = "Total assets | Total Assets"
                #-------------------LIABILITIES-----------------------------
                totalCurrentLiabilitiesSplit = "Total current liabilities | Total Current Liabilities"
                netPensionLiabilitySplit = "Net pension liability | Net OPEB liability"
                totalNonCurrentLiabilitiesSplit = "Total noncurrent liabilities | Total Noncurrent Liabilities"
                totalLiabilitiesSplit = "Total liabilities | Total Liabilities"
                #------------------NET POSITION ----------------------------
                investmentInCapitalAssetsSplit = "Investment in capital assets | Investment In Capital Assets"
                unrestrictedSplit = "Unrestricted | Unrestricted (deficit)"
                totalNetPositionSplit = "Total net position | Total Net Position"
                #Temp Storage variables
                county = ''
                date = ''
                header = ''
                propFund = ''
                #each line will be manipulated using index, index starts at 0
                lineIndex = 0
                while lineIndex in range(len(fullPagetext)):
                    #Get rid of $ signs
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", " ")
                    #Look for these flags within the page (as we go line by line), if found return true, otherwise false
                    countyFound = county_filter.search(fullPagetext[lineIndex])
                    headerFound = statementOfNetPositionFilter.search(fullPagetext[lineIndex])
                    dateFound = dateFilter.search(fullPagetext[lineIndex])
                    proprietaryFundsFound = proprietaryFundsSplit.search(fullPagetext[lineIndex])
                    cashAndPooledInvestmentsFound = cashAndPooledInvestmentsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    nonCurrentAssetsCapitalAssetsFound =  nonCurrentAssetsCapitalAssetsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalAssetsFound = totalAssetsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalCurrentLiabilitiesFound = totalCurrentLiabilitiesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    netPensionLiabilityFound = netPensionLiabilitySplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalNonCurrentLiabilitiesFound = totalNonCurrentLiabilitiesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalLiabilitiesFound = totalLiabilitiesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    investmentInCapitalAssetsFound = investmentInCapitalAssetsSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    unrestrictedFound = unrestrictedSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalNetPositionFound = totalNetPositionSplit.find(fullPagetext[lineIndex].split("  ")[0])

                    #If found, then store them into a list
                    if countyFound:
                        county = fullPagetext[lineIndex]
                    elif dateFound:
                        date = fullPagetext[lineIndex].replace("Year Ended", "")
                    elif headerFound:
                        header = fullPagetext[lineIndex]
                    elif proprietaryFundsFound:
                        propFund = fullPagetext[lineIndex]
                        header = propFund + " - " + header
                    elif cashAndPooledInvestmentsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if cashAndPooledInvestmentsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif nonCurrentAssetsCapitalAssetsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if nonCurrentAssetsCapitalAssetsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif  totalAssetsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalAssetsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif totalCurrentLiabilitiesFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalCurrentLiabilitiesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    
                    elif netPensionLiabilityFound != -1:
                         #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if netPensionLiabilitySplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0] 
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif totalNonCurrentLiabilitiesFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalNonCurrentLiabilitiesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif totalLiabilitiesFound != -1:
                         #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalLiabilitiesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif investmentInCapitalAssetsFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if investmentInCapitalAssetsSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif unrestrictedFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if unrestrictedSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif totalNetPositionFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalNetPositionSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    lineIndex+=1
                fillDF(FINAL_PAGE_DATA, headerlist)
                print("---------------------DONE PAGE 66----------------------\n\n\n")
            elif i == 66:
                FINAL_PAGE_DATA.clear()
                text = page.extract_text()
                headerlist = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER','Business-type Activities - Enterprise Funds - TOTAL']
                #------------------Filters-----------------
                county_filter = re.compile(r'county|COUNTY|County$')
                proprietaryFundsSplit = re.compile(r'Proprietary Funds$')
                statementOfNetPositionFilter = re.compile(r'Statement of Revenues, Expenses and Changes in Fund Net Position|statement of revenues, expenses and changes in fund net position|STATEMENT OF REVENUES, EXPENSES AND CHANGES IN FUND NET POSITION')
                dateFilter = re.compile(r'[a-zA-Z]+\s\d\d[,]\s\d\d\d\d')
                #--------------------------------------UNUSED(approach not found yet)-----------------------------------
                # expensesFilter = re.compile(r'Expenses|EXPENSES|expenses')
                # chargesForServicesFilter = re.compile(r'(Charges for)(Services)|(Charges)(for Services)|(Charges)(for)(Services)')
                # operatingGrantsAndContributionsFilter = re.compile(r'(Operating)(Grants and)(Contributions)|(Operating Grants)(and Contributions)|(Operating Grants)(and)(Contributions)')
                # capitalGrantsAndContributionsFilter = re.compile(r'(Capital)(Grants and)(Contributions)|(Capital Grants)(and Contributions)|(Capital)(Grants)(and Contributions)|(Capital)(Grants)(and)(Contributions)')
                
                #--------------------------------------------------DATA FILLER LINE-------------------------------------------------------------------
                dfLine = namedtuple('dfLine', 'date county header pageheader totalData')
                #--------------------------------------------------Split Lines based on /n and store into list----------------------------------------
                fullPagetext = text.split('\n')
                #--------------------------------------------------Flags to look for in lines---------------------------------------------------------
                #-------------------ASSETS-----------------------------
                totalOperatingRevenuesSplit = "Total operating revenues | Total Operating Revenues"
                totalOperatingExpensesSplit = "Total operating expenses | Total Operating Revenues"
                totalNonOperatingRevenuesSplit = "Total nonoperating revenues | Total nonoperating (expenses) revenues | Total nonoperating revenues (expenses) | Total nonoperating expense"
                changeInNetPositionSplit = "Change in net position | Change In Net Position"
                #Temp Storage variables
                county = ''
                date = ''
                header = ''
                propFund = ''
                #each line will be manipulated using index, index starts at 0
                lineIndex = 0
                while lineIndex in range(len(fullPagetext)):
                    #Get rid of $ signs
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", " ")
                    #Look for these flags within the page (as we go line by line), if found return true, otherwise false
                    countyFound = county_filter.search(fullPagetext[lineIndex])
                    headerFound = statementOfNetPositionFilter.search(fullPagetext[lineIndex])
                    dateFound = dateFilter.search(fullPagetext[lineIndex])
                    proprietaryFundsFound = proprietaryFundsSplit.search(fullPagetext[lineIndex])
                    totalOperatingRevenuesFound = totalOperatingRevenuesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalOperatingExpensesFound = totalOperatingExpensesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    totalNonOperatingRevenuesFound = totalNonOperatingRevenuesSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    changeInNetPositionFound = changeInNetPositionSplit.find(fullPagetext[lineIndex].split("  ")[0])
                    #If found, then store them into a list
                    if countyFound:
                        county = fullPagetext[lineIndex]
                    elif dateFound:
                        date = fullPagetext[lineIndex].replace("Year Ended", "")
                    elif headerFound:
                        header = fullPagetext[lineIndex]
                    elif proprietaryFundsFound:
                        propFund = fullPagetext[lineIndex]
                        header = propFund + " - " + header
                    elif totalOperatingRevenuesFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalOperatingRevenuesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif totalOperatingExpensesFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalOperatingExpensesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif  totalNonOperatingRevenuesFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if totalNonOperatingRevenuesSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    elif changeInNetPositionFound != -1:
                        #Check if next line also matches with what we are looking for, if so data falls on second line not first
                        nextLine = fullPagetext[lineIndex+1].split("  ")
                        if changeInNetPositionSplit.find(nextLine[0]) != -1:
                            if(len(nextLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0] + " " + nextLine[0]
                                #Keep data, remove header
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(nextLine[0], "")
                                #Replace or remove these items and only keep numbers
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("$", "")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("-", "0")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace("(", "-")
                                fullPagetext[lineIndex+1] = fullPagetext[lineIndex+1].replace(")", "")
                                #Split numerical data by , based on space detected between each
                                row = fullPagetext[lineIndex+1].split()
                                #Store data into a list
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                                lineIndex += 1
                        else:
                            thisLine = fullPagetext[lineIndex].split("  ")
                            if(len(thisLine) > 3):
                                pageHeader = fullPagetext[lineIndex].split("   ")[0]
                                #get rid of ( ) and $
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                                #Keep data, remove header
                                fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(thisLine[0], "")
                                #Split numerical data by, based on space detected between each
                                row = fullPagetext[lineIndex].split()
                                FINAL_PAGE_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 2]))
                    lineIndex+=1
                fillDF(FINAL_PAGE_DATA, headerlist)
                print("---------------------DONE PAGE 67----------------------\n\n\n")
    
    #Convert when while loop is done (outside of while loop)
    csvPath = conv_to_csv()
    return csvPath