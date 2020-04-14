# test_daemon.py

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
 #  Description: This program is a skeleton daemon that acts as an ssh server using paramiko. It awaits connections and prompts on a connection to execute shell commands onto the target client.
 #      
 #        Input:  N/A
 #
 #       Output:  Outputs to console results of command executed
 #
 #    Algorithm:  Invokes the Paramiko supplied functions to create and manage an SSH server. Continously request new commands and then send them to the target client. Await for 
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

import csv
import errno
import random
import os
import time
import atexit
import logzero
from logzero import logger
from signal import SIGTERM
import socket
import paramiko
import threading
import sys
import signal
from stub_sftp import StubServer,  StubSFTPServer

host_key = paramiko.RSAKey(filename='test_rsa.key')
logzero.logfile("soupLogFile.log", maxBytes=1e6, backupCount=2)
def child():
    childWrites="in child"
    logger.info(f"Child: {os.getpid()} {childWrites} ")

def parent():
    logger.info(f"Parent: {os.getpid()} is logging")
   
def grimReaper(signalNumber,frame):
   while True:
        try:
            pid,status=os.waitpid(-1,os.WNOHANG)
        except OSError:
            return
        
        if pid==0:
            return
         
def exitErr(msg,status=1):
   print(msg)
   sys.exit(status)
   
def getPid(pidfile,default=None):
    try:
        with open(pidfile) as f:
            return int(f.read().strip())
    except IOError:
        return default

class Daemon(object):
    def __init__(self, pidfile,stdin='/dev/null',stdout='/dev/null',stderr='/dev/null'):
      self.stdin=stdin
      self.stdout=stdout
      self.stderr=stderr
      self.pidfile=pidfile
   
    def startService(self):
        try:
            try:
                if os.fork() > 0:
                   raise SystemExit(0)
            except OSError as e:
                    logger.error("Unable to fork for fork #1")
            
            os.chdir('/')
            try:
                os.setsid()
            except Exception as e:
                logger.warning("Could not change the GID and/or UID - is this process privilaged?")
                logger.warning(str(e))
                
            # End Leadership by double forking
            try:
                if os.fork() > 0:
                    raise SystemExit(0)
            except OSError as e:
                logger.error("Unable to fork for fork #2")
         
            sys.stdout.flush()
            sys.stderr.flush()
                
           # PID is to be removed when this daemon stops
            atexit.register(lambda:  os.remove(self.pidFile))
            signal.signal(signal.SIGTERM,  grimReaper)
        except Exception as e:
            print('[-] Listen/bind/accept failed: '+str(e))
            sys.exit(1)
    def delpid(self):
        os.remove(self.pidfile)
    
    def start(self):
        if getPid(self.pidfile):
            msg="Pidfile %s already exists. daemon already running"
            exitErr(msg%self.pidfile)
        self.startService()
        self.run()
   
    def stop(self):
        pid=getPid(self.pidfile)
        if not pid:
            msg="pidfile dont exist. deamon not running"
            print(msg%self.pidfile)
            return
        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as e:
            error=e.strerror
            if 'No such process' in error:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                exitErr(error)

    def restart(self):
        self.stop()
        self.start()
   
    def run(self):
        print("Error - Invoked Base class RUN")
            
   
def startParamiko(client):
  return -1

def endConnection(sigNo, frames):
    '''
    This function handles the cleanup of zombie children after their work has been completed
    param - sigNo 
    param - frames
    return - exit state
    '''
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG) #any child must be ended
        except Exception:
            return -1
        if pid == 0:
            return 1
        
class MyDaemon(Daemon):
   def run(self):
    client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.bind(getBinds())
    client.listen(200)
    logger.info(f"Daemon Started and ready for IPv6 service on localhost using port 9000...")

    signal.signal(signal.SIGCHLD,endConnection) #estabish a zombie child kille        
    while True:
            try:
                clientCon, clientAddr = client.accept()
            except Exception:
                logger.error("There was a problem accepting the connection, please try again")
            pid = os.fork()
            if pid == 0:
                #I am the child connection
                client.close() # do not listen to the parent
                handle(clientCon)
                clientCon.close()
                os._exit(0) #children are returning success to parent
            else:
                #I am a parent connection
                clientCon.close()

    
#def handleData(data):
   # if os.path.exists("peopleInfo.csv"):
      #  with open('peopleInfo.csv','w',newLine='') as f:#first arg may change, its the csv file name
        #    writer=csv.writer(f)
          #  thewriter.writerow(['First Name','Last Name','IP','Location','Email','Domain','Postal Code')
        #here we'll recv the info being sent back by the client assuming its an array as of now
    #with open('peopleInfo.csv','w',newLine='') as f:#first arg may change, its the csv file name
        #writer=csv.writer(f)
        #for i in range():
            #for j in range(7):#any blank inputs are chaged to null
               # if (len(data[i][j])<1):
                    #data[i][j]="null"
            #thewriter.writerow([data1[i][0],data1[i][1],data1[i][2],data1[i][3],data1[i][4],data1[i][5],data1[i][6]])
            #Alistairs signUp function called here with each row of data
            #signUp(data1[i])

def getBinds():
    '''
    This function grabs the binding arguements for the connection
    In the clients case, this is the IPv6 address and the socket #
    return tuple - The connection properties 
    '''
    sockNum = -1
    sockIp = ""
    while sockNum < 0 and not sockIp:
        try: 
            sockNumTest = int(input("Provide a socket # for the daemon to host:"))
            sockIpTest = str(input("Provide an IPv6 addresss to host on:"))
        except Exception:
            print("Please Try Again...\n")
        else:
            sockNum = sockNumTest   
            sockIp = sockIpTest     

    return (sockIpTest, sockNumTest)

class Server (paramiko.ServerInterface):
    host_key = paramiko.RSAKey(filename='test_rsa.key')
    def _init_(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == 'root') and (password == 'toor'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED



if __name__=="__main__":
    logzero.logfile("/tmp/rotating-logfile.log",maxBytes=1e6, backupCount=3, disableStderrLogger=True)
    daemonPid=os.getpid()
    logger.info(f"Started {daemonPid}")
    daemon=MyDaemon('/tmp/daemon-example3.pid')
    if len(sys.argv)==2:
        if 'start'==sys.argv[1]:
            daemon.start()
        elif 'stop'==sys.argv[1]:
                daemon.stop()
        elif 'restart'==sys.argv[1]:
            daemon.restart()
        else:
            print('command not recognized')
            sys.exit(2)
        sys.exit(0)
    else:
        print('usage: %s start|stop|restart'%sys.argv[0])
        sys.exit(2)
