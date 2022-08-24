#Welcome to ELLevationUserDataBackup.py

#see variable 'welcomeInstructions' for description

from tkinter import *
from tkinter import messagebox
import csv, re, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#messages
welcomeInstructions = '''Welcome to ELLevationUserDataBackup.py!

This application will help you back up your ELLevation User data by splitting all users' names
into "First Name" & "Last Name" columns and creating a new line for each school associated with 
a given teacher. It will also split users into separate "Active" and "Inactive" user .csv files.

This application requires the installation of Firefox, the Selenium module for Python, and the 
appropriate version and configuration of Geckodriver for your operating system. If Geckodriver
is not added to your system's PATH, please add it before running this program.

Click "OK" when you you are ready to begin.'''
downloadInstructions = '''Once selenium has downloaded the file, copy and paste the file's file path below.
Your operating system may have a "copy as path" option in its file browsing application.


Please ensure that there are no quotation marks at the beginning or end of the pathname.'''
credentialsInstructions = '''Enter your ELLevation login credentials.

Click 'Ok' once you have entered them.'''
seleniumMessage = '''Please wait while the driver downloads data from the ELLevation users file.

Do not move the mouse or type anything while the program is working. It may interfere with the
program and cause it to fail.

Click 'Run' when you are ready to begin.'''
reformatInstructions = '''The file will now be reformatted. First, delete the first two columns of the .csv file.
Then, close the file. If the file is not closed, the program cannot open the file.

You will be alerted when the file is transformed.

Click 'Run' when you are ready to begin.'''

#variables
root_title = "ELLevation User Data Backup"
userCounter = 0
closeUserFilterXPATH = '/html/body/section/div[2]/content/router-view/div/div/div[1]/div/ell-people-filters/ell-filter-sets/div/div/ell-filter-set/div[1]/div/ell-filter-readable/div/div/button'
userDownloadXPATH = '/html/body/section/div[2]/content/router-view/div/div/div[2]/div[1]/ell-people-actions/div/div[4]/button'
processingBarXPATH = '/html/body/section/div[2]/content/router-view/div/div/div[2]/ell-processing-message/div'
loginPage = 'https://login.ellevationeducation.com'
homePage = 'https://app.ellevationeducation.com/'
peoplePage = 'https://app.ellevationeducation.com/people'
active_user_file = 'active_user_file' + str(datetime.date.today()) + '.csv'
inactive_user_file = 'inactive_user_file' + str(datetime.date.today()) + '.csv'
redBorder = '3px solid red'
addBorder = 'arguments[0].style.border = "' + redBorder + '"'

#lists/dictionaries
relevantRows = []
ELL_Users = []
ActiveUsers = []
InactiveUsers = []
ELL_UserKeys = [] #create class for keys?
ELL_UploadKeys = []
ELL_UserSchoolDuplicate = []
ELL_UserFullName = [] #create class for name lists?
LastFirstMiddle = []
LastName = []
FirstName = []
MiddleName = []
SchoolDict = []
Credentials = {}

driver = webdriver.Firefox()
standby = WebDriverWait(driver,10)

#tkinter Windows
root = Tk()
root.title(root_title)

top = Toplevel()
top.title('Welcome')

def WelcomeScreen(): #welcome Screen with instructions
    welcome.pack()
    exitwelcome.pack()

def SetCredentials(): #instructs user to download, 1st step in mapping folder path
    top.destroy()
    root_title = "Login Credentials"
    credentials.pack()
    username.pack()
    pw.pack()
    credentialsSubmit.pack()

def ConfirmCredentials(): #confirm that folder path is correct
    response = messagebox.askyesno("Confirm","Are you sure your credentials are correct?")
    if response == True:
        Credentials['Username'] = username.get() #add regex
        Credentials['Password'] = pw.get()
        Download()

def Download():
    credentials.destroy()
    username.destroy()
    pw.destroy()
    credentialsSubmit.destroy()
    root_title = 'Downloading ELLevation Data'
    seleniumInstructions.pack()
    runSelenium.pack()

#selenium
def loginInput(): #finds login fields and inputs username & pw
    userElem=driver.find_element(By.ID,'userName')
    userElem.send_keys(Credentials['Username'])
    passwordElem=driver.find_element(By.ID,'password')
    passwordElem.send_keys(Credentials['Password'])
    passwordElem.submit()
    standby.until(EC.url_matches(homePage))
    UserManagement()

def login(): #calls loginInput & loops until login is successful
    driver.get(loginPage)
    standby.until(EC.url_matches(loginPage))
    loginInput()


def UserManagement(): #opens User Management Page
    driver.get(peoplePage)
    standby.until(EC.url_matches(peoplePage))
    ReportPull()

def ReportPull(): #removes active filter and downloads .csv file
    standby.until(EC.element_to_be_clickable((By.XPATH,closeUserFilterXPATH)))
    downloadButton = driver.find_element(By.XPATH, userDownloadXPATH)
    filterButton = driver.find_element(By.XPATH, closeUserFilterXPATH)
    driver.execute_script(addBorder,filterButton)
    driver.execute_script('arguments[0].click()',filterButton)
    standby.until(EC.visibility_of_element_located((By.XPATH,processingBarXPATH)))
    standby.until_not(EC.visibility_of_element_located((By.XPATH,processingBarXPATH)))
    driver.execute_script(addBorder,downloadButton)
    driver.execute_script('arguments[0].click()',downloadButton)
    messagebox.showinfo('Close Firefox','You may close Firefox when the file has downloaded.')
    MapFile()


def MapFile(): #instructs user to download, 1st step in mapping file path
    seleniumInstructions.destroy()
    runSelenium.destroy()
    root_title = "Mapping"
    mapFileElement.pack()
    inputFP.pack()
    mappingSubmit.pack()

def ConfirmFP(): #confirm that file path is correct
    response = messagebox.askyesno("Confirm File Path","You have entered " + inputFP.get() + ". Is this correct?")
    if response == True:
        global filePath
        filePath = (inputFP.get())
        global ellevation_user_file
        ellevation_user_file = open(filePath)
        global dictReader
        dictReader = csv.DictReader(ellevation_user_file)
        messagebox.showinfo('Download File Mapping','File mapped successfully.')
        ReformatMenu()

def ReformatMenu(): #instructs user to delete first rows and then starts reformat process
    mapFileElement.destroy()
    inputFP.destroy()
    mappingSubmit.destroy()
    reformatMenu.pack()
    runReformat.pack()

#reformating data   
def ColumnDeletor(): #deletes irrelevant columns
    for users in dictReader:
        for key in users: #adds all experiment dict key names into ELL_UserKeys list
            ELL_UserKeys.append(key)
        ELL_Users.append({
            'Full Name': users[ELL_UserKeys[0]],
            'Staff ID': users[ELL_UserKeys[1]],
            'School': users[ELL_UserKeys[3]],
            ELL_UserKeys[4]: users[ELL_UserKeys[4]],
            ELL_UserKeys[5]: users[ELL_UserKeys[5]],
            ELL_UserKeys[11]: users[ELL_UserKeys[11]],
            })

def StoreKeys():
    for key in ELL_Users[0]: #adds all ELL_Users dict key names into ELL_UploadKeys list
        ELL_UploadKeys.append(key)

def NameSplit():
    userCounter = 0
    for name in ELL_Users: #splits last, first, & middle names into their respective lists
        spliterooni = re.split(r',\W',name['Full Name'])
        LastFirstMiddle.append(spliterooni)
        LastName.append(LastFirstMiddle[userCounter][0])
        FirstName.append(LastFirstMiddle[userCounter][1])
        #TODO middle name, may not exist
        userCounter += 1

def FullName_erator(): #deletes full name from dictionary entries
    userCounter = 0
    ELL_UploadKeys.insert(0,'Last Name')
    ELL_UploadKeys.insert(1,'First Name')
    ELL_UploadKeys.remove('Full Name')
    for dictionary in ELL_Users:
        dictionary[ELL_UploadKeys[0]] = LastName[userCounter]
        dictionary[ELL_UploadKeys[1]] = FirstName[userCounter]
        dictionary.pop('Full Name')
        userCounter += 1

def ELL_UserSchoolDuplicator(): #creates duplicate lines for each school that a user is located
    for accounts in ELL_Users:
        ellUserSchoolList = re.split(r',\W',accounts['School'])
        SchoolCounter = 0
        for i in (ellUserSchoolList):
            ELL_UserSchoolDuplicate.append({
                ELL_UploadKeys[0]: accounts[ELL_UploadKeys[0]], #'Last Name'
                #TODO 'Middle Name': i['Middle Name']
                ELL_UploadKeys[1]: accounts[ELL_UploadKeys[1]], #'First Name'
                ELL_UploadKeys[2]: accounts[ELL_UploadKeys[2]], #'Staff ID'
                ELL_UploadKeys[3]: ellUserSchoolList[SchoolCounter], #'School'
                ELL_UploadKeys[4]: accounts[ELL_UploadKeys[4]], #'Account Type'
                ELL_UserKeys[5]: accounts[ELL_UserKeys[5]], #'Account Status'
                ELL_UploadKeys[6]: accounts[ELL_UploadKeys[6]] #'Email'
            })
            SchoolCounter += 1

def ActiveUserSeparator(): #separates all users into two lists: active and inactive
    for accounts in ELL_UserSchoolDuplicate:
        if accounts['Account Status'] == 'Active':
            ActiveUsers.append({
                    ELL_UploadKeys[0]: accounts[ELL_UploadKeys[0]], #'Last Name'
                    #TODO 'Middle Name': i['Middle Name']
                    ELL_UploadKeys[1]: accounts[ELL_UploadKeys[1]], #'First Name'
                    ELL_UploadKeys[2]: accounts[ELL_UploadKeys[2]], #'Staff ID'
                    ELL_UploadKeys[3]: accounts[ELL_UploadKeys[3]], #'School'
                    ELL_UploadKeys[4]: accounts[ELL_UploadKeys[4]], #'Account Type'
                    ELL_UploadKeys[6]: accounts[ELL_UploadKeys[6]] #'Email'
                })
        else:
            InactiveUsers.append({
                    ELL_UploadKeys[0]: accounts[ELL_UploadKeys[0]], #'Last Name'
                    #TODO 'Middle Name': i['Middle Name']
                    ELL_UploadKeys[1]: accounts[ELL_UploadKeys[1]], #'First Name'
                    ELL_UploadKeys[2]: accounts[ELL_UploadKeys[2]], #'Staff ID'
                    ELL_UploadKeys[3]: accounts[ELL_UploadKeys[3]], #'School'
                    ELL_UploadKeys[4]: accounts[ELL_UploadKeys[4]], #'Account Type'
                    ELL_UploadKeys[6]: accounts[ELL_UploadKeys[6]] #'Email'
                })
    ELL_UploadKeys.pop(5)

def WriteNewFile(): #writes two files, one for inactive and one for active
    with open(active_user_file, 'w', newline='') as activeFile:
        dictWriter = csv.DictWriter(activeFile, fieldnames=ELL_UploadKeys)
        dictWriter.writeheader()
        for person in ActiveUsers:
            dictWriter.writerow(person)
    with open (inactive_user_file, 'w', newline='') as inactiveFile:
        dictWriter = csv.DictWriter(inactiveFile, fieldnames=ELL_UploadKeys)
        dictWriter.writeheader()
        for person in InactiveUsers:
            dictWriter.writerow(person)

def ReformatUserFile(): #fuction that calls all other file-reformatting functions
    reformatMenu.destroy()
    runReformat.destroy()
    reformatRunning.pack()
    ColumnDeletor()
    StoreKeys()
    NameSplit()
    FullName_erator()
    ELL_UserSchoolDuplicator()
    ActiveUserSeparator()
    WriteNewFile()
    reformatRunning.destroy()
    done.pack()


#tkinter page elements
welcome = Label(top, text=welcomeInstructions)
exitwelcome = Button(top, text='Ok', command=SetCredentials)

credentials = Label(root,text=credentialsInstructions)
username = Entry(root, text="Enter ELLevation username here")
pw = Entry(root, text="Enter ELLevation password here", show='*')
credentialsSubmit = Button(root, text="Enter",command=ConfirmCredentials)

seleniumInstructions = Label(root, text=seleniumMessage)
runSelenium = Button(root, text='Run', command=login)

mapFileElement = Label(root,text=downloadInstructions)
inputFP = Entry(root, text="Enter file path here")
mappingSubmit = Button(root, text="Map File",command=ConfirmFP)

reformatMenu = Label(root,text=reformatInstructions)
runReformat = Button(root, text='Run', command=ReformatUserFile)
reformatRunning = Label(root,text='Please wait while the reformatting runs.')

done = Label(root, text="Complete! You may now close the program.")

#TODO align everything
#TODO add progress bar
#TODO delete first columns automatically

WelcomeScreen()
root.mainloop()
