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
            if i == 49:
                FINAL_PAGE_DATA.clear()
                text = page.extract_text()
                headerlist = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER', 'EXPENSES', 'CHARGES_FOR_SERVICES', 'OPERATING GRANTS AND CONTRIBUTIONS', 'CAPITAL GRANTS AND CONTRIBUTIONS']
                #------------------Filters-----------------
                county_filter = re.compile(r'county|COUNTY|County$')
                statementOfActivitiesFilter = re.compile(r'Statement of Activities|statement of activities|STATEMENT OF ACTIVITIES')
                #CHECK DATE FILTER --> NEXT STEP
                dateFilter = re.compile(r'^Year Ended')
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
                        date = fullPagetext[lineIndex]
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
                            print("here")
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
                print(FINAL_PAGE_DATA)
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
                dateFilter = re.compile(r'^Year Ended')
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
                    GrantsFound = fullPagetext[lineIndex].find(GrantsRowSplit)
                    propertyTaxFound = fullPagetext[lineIndex].find(propertyTaxSplit)
                    totalGenRevTransferFound = fullPagetext[lineIndex].find(totalGenRevTransferSplit)
                    ChangeinNetPosFound = fullPagetext[lineIndex].find(ChangeinNetPosSplit)
                    if countyFound:
                        county = fullPagetext[lineIndex]
                        print('_______________________________________________________________________')
                    elif statementOfActivitiesFound:
                        header = fullPagetext[lineIndex]
                        print('_______________________________________________________________________')
                    elif dateFound:
                        date = fullPagetext[lineIndex].replace('Year Ended ', '')
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
                print(FINAL_PAGE_DATA)
                fillDF(FINAL_PAGE_DATA, headerlist)
                print("---------------------DONE PAGE 51----------------------\n\n\n")
        conv_to_csv()
# WRite to CSV ----UPDATE THIS!
file_parse('C:/Users/Maitra/Documents/CIS 4951/WashtenawCountyFY18_annotated nb edits.pdf')