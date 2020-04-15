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


binds = ("::1",  9500)
host_key = paramiko.RSAKey(filename='test_rsa.key')
logzero.logfile("soupLogFile.log", maxBytes=1e6, backupCount=2)
def child():
    childWrites="in child"
    logger.info(f"Child: {os.getpid()} {childWrites} ")

def parent():
    logger.info(f"Parent: {os.getpid()} is logging")
    
def sigterm_handler(signo,  frame):
    ''''
    This function handles the cleanup of the parent daemon when the stop command is passed
    param - sigNo 
    param - frames
    return - exit state
    '''
    raise  SystemExit(1)
    
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

   
    def startService(self,  stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        ''''
        This function handles the intiial setup needed in order to start or stop the Daemon. 
        For stopping the program, it will find the PID file and remove it. Then, it will exit the daemon.
        For starting the program, it will check for an existing PID file and if not available, writes one and double forks to generate a daemonized daemon.
        Function will log as needed to the logfile which exist next to the file that was executed as dpi912logFile
        '''
        pidFile = '/var/run/daemon/daemon.pid'  #instead of /var/run/ which requires root, which I dont have the pwd for.
        self.pidfile= pidFile
        #if init start is passed, start the server
        
        if 'start'==sys.argv[1]:
            print("Attempting to start on ipv6 localhost via socket "+str(binds) +"- see logs for further information")
            if os.path.exists(pidFile):
                logger.warning("Daemon PID File exists, is this Daemon already running? Exiting...")
                sys.exit(0)
            else:
                try:
                    if os.fork() > 0:
                        raise SystemExit(0)
                except OSError as e:
                    logger.error("Unable to fork for fork #1")
                
                os.chdir('/var/run/daemon')
                try:
                    os.setsid()
                    os.setuid(1000) #so how exactly does this become root if you must be root to set this privilage?
                except Exception as e:
                    logger.warning("Could not change the GID and/or UID - is this process privilaged?")
                    logger.warning(str(e))
                    
                # End Leadership by double forking
                try:
                    if os.fork() > 0:
                        raise SystemExit(0)
                except OSError as e:
                    logger.error("Unable to fork for fork #2")
                    
                # Flush I/O  buffers  and lockdown stderr/out/in
                sys.stdout.flush() 
                sys.stderr.flush()
                
                with open(pidFile,'w')  as f:
                    print(os.getpid(),file=f)
                    
                # PID is to be removed when this daemon stops
                atexit.register(lambda:  os.remove(pidFile))
                signal.signal(signal.SIGTERM,  sigterm_handler)
        
    def delpid(self):
        os.remove(self.pidfile)
    
    def start(self):
        if getPid(self.pidfile):
            print("PID Exists - remove it")
            logger.info("pidfile exists. deamon is running")
        self.startService(self)
        self.run()
   
    def stop(self):
        pid=getPid(self.pidfile)
        if not pid:
            print("PID doesnt exist")
            logger.info("pidfile dont exist. deamon not running")
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
    try:
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(binds)
    except Exception as e:
        print("*** Bind failed: " + str(e))
        e.print_exc()
        sys.exit(1)
    try:
        sock.listen(100)
        print("Listening for connection ...")
        logger.info("Listening for connection...")
    except Exception as e:
            print("*** Listen/accept failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)
    while True:
        print("Waiting...")
        client, addr = sock.accept()

        print("Got a connection!")
        t = paramiko.Transport(client)
        t.set_gss_host(socket.getfqdn(""))
        t.add_server_key(host_key)
        server = Server()
        try:
            t.start_server(server=server)
        except paramiko.SSHException:
            print("*** SSH negotiation failed.")
            sys.exit(1)
        # wait for auth
        clientCon = t.accept(20)
        if clientCon is None:
            print("*** No channel ***")
            sys.exit(1)
        print("Authenticated!")
        print("Handling this connection...")
        pid = os.fork()
        if pid == 0:
            #child
            handle(clientCon)
            clientCon.close()
            os._exit(0)
        else:
            #parent
            clientCon.close()

def handle(conn):
    
    request = conn.recv(1024).decode()
    print("Got this ->" + str(request))
    res = "Hello World"
    conn.sendall(res.encode('utf-8'))
   
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
            
    print("Done!")
    return 0
    
    
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
    logzero.logfile("rotating-logfile.log",maxBytes=1e6, backupCount=3, disableStderrLogger=True)
    daemonPid=os.getpid()
    logger.info(f"Started {daemonPid}")
    daemon=MyDaemon('/var/run/daemon/daemon.pid')
    if len(sys.argv)==2:
        if 'start'==sys.argv[1]:
            daemon.stop()
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
