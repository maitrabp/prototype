import re
import pdfplumber
import pandas as pd
from collections import namedtuple

#Make method to detect the headers which go into second line. If not header, then return false (NOT IMPLEMENTED YET, UNUSED)

def getNext(index, fullPagetext):
    if((index+1) < range(fullPagetext)):
        return fullPagetext[index+1]
    else:
        return fullPagetext[index]

def file_parse(file):
    with pdfplumber.open(file) as pdf:
        page = pdf.pages[50]
        text = page.extract_text()
        headerlist = ['DATE', 'COUNTY','MAIN_PAGE_HEADER', 'DATA_DESCRIPTION'] 
        #Filter County on this page
        county_filter = re.compile(r'county|COUNTY|County$')
        #Filter statementOfActivities on this page
        statementOfActivities = re.compile(r'Statement of Activities|statement of activities|STATEMENT OF ACTIVITIES')
        #Filter date
        dateFilter = re.compile(r'^Year Ended');
#------------------------------------------------------------------HEADER FILTERS (UNUSED)------------------------------------------------------
        #Filter governmental activities
        govActivityFilter = re.compile(r'(Governmental) (Activities)')
        #Filter Business-type activities
        busActivityFilter = re.compile(r'(Business-type) (Activities)')
        #Filter Total
        totalFilter = re.compile(r'Total')
        #Filter Component Units
        componentUnitFilter = re.compile(r'(Component) (Units)')
#--------------------------------------------------------------------------------------------------------------------------------------
        county  = ''
        header = ''
        date = ''
        pageHeader = ''
        dfLine = namedtuple('dfLine', 'date county header pageheader govActivityData busActivityData totalData')
        FINAL_DATA = []
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
            GrantsFound = GrantsRowSplit.find(fullPagetext[lineIndex].split("  ")[0])
            propertyTaxFound = propertyTaxSplit.find(fullPagetext[lineIndex].split("  ")[0])
            totalGenRevTransferFound = totalGenRevTransferSplit.find(fullPagetext[lineIndex].split("  ")[0])
            ChangeinNetPosFound = ChangeinNetPosSplit.find(fullPagetext[lineIndex].split("  ")[0])
            print("LINE BEING TREATED:  \n" + fullPagetext[lineIndex])
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
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    lineIndex += 1
                else:
                    pageHeader = fullPagetext[lineIndex].split("   ")[0]
                    #get rid of ( ) and $
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                    row = fullPagetext[lineIndex].split()
                    
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))

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
                    
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    lineIndex += 1
                else:
                    pageHeader = fullPagetext[lineIndex].split("   ")[0]
                    #get rid of ( ) and $
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")
                    
                    row = fullPagetext[lineIndex].split()
                   
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                   
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
                    
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    lineIndex += 1
                else:
                    pageHeader = fullPagetext[lineIndex].split("   ")[0]
                    #get rid of ( ) and $
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")

                    row = fullPagetext[lineIndex].split()
                   
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    
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
                    
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    lineIndex += 1
                else:
                    pageHeader = fullPagetext[lineIndex].split("   ")[0]
                    #get rid of ( ) with - and $ with empty
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("-", "0")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("$", "")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace("(", "-")
                    fullPagetext[lineIndex] = fullPagetext[lineIndex].replace(")", "")

                    row = fullPagetext[lineIndex].split()
                    FINAL_DATA.append(dfLine(date, county, header, pageHeader, row[len(row) - 4], row[len(row) - 3], row[len(row) - 2]))
                    
            #Move to the next line
            lineIndex+=1      
    return FINAL_DATA
        
def conv_to_csv(FINAL_DATA):
    df = pd.DataFrame(FINAL_DATA)
    df.columns = ['DATE', 'COUNTY', 'PAGE_HEADER', 'SUB_DATA_HEADER', 'GOV_ACTIVITIES', 'BUS_ACTIVITY', 'TOTAL']

    for col in df.columns[-3: ]:
        df[col] = df[col].map(lambda x: float(str(x).replace(',', '')))
    saveCSVfilepath = r'./parseRESULT.csv'
    df.to_csv(saveCSVfilepath, index=False, header=True)
    print("\n\nMESSAGE: Your csv file is ready, go to " + saveCSVfilepath + " to take a look at!")
    return saveCSVfilepath



#Page51