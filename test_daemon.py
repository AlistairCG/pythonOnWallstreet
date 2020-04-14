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
import requests
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
import json
import subprocess
from stub_sftp import StubServer,  StubSFTPServer

host_key = paramiko.RSAKey(filename='test_rsa.key')
logzero.logfile("soupLogFile.log", maxBytes=1e6, backupCount=2)

   
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

def initDaemon():
	os.chdir('/')
	try:
		os.setsid()
	except:
		pass
	os.umask(0)
class Daemon(object):
    def __init__(self, pidfile,stdin='/dev/null',stdout='/dev/null',stderr='/dev/null'):
      self.stdin=stdin
      self.stdout=stdout
      self.stderr=stderr
      self.pidfile=pidfile
   
    def startService(self):
        try:           #first fork
            if os.fork()>0:
                raise SystemExit(0)
        except OSError as e:
            logger.info("First fork failed: %d (%s)"%(e.errno,e.strerror))
            
        initDaemon()
            
        try:        #2nd fork
            if os.fork()>0:
                raise SystemExit(0)
        except OSError as e:
            logger.info("2nd fork failed: %d (%s)"%(e.errno,e.strerror))
                
        sys.stdout.flush()
        sys.stderr.flush()
        si=open(self.stdin,'r')
        so=open(self.stdout,'a+')
        se=open(self.stderr,'a+')
        os.dup2(si.fileno(),sys.stdin.fileno())
        os.dup2(so.fileno(),sys.stdout.fileno())
        os.dup2(se.fileno(),sys.stderr.fileno())
        
        pid=str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(pid)
        
        atexit.register(lambda:os.remove(self.pidfile))
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        sock.bind(getBinds())
        sock.listen(100)
        signal.signal(signal.SIGCHLD,grimReaper)
        print('[+] Listening for connection ...')
        while True:
            try:
                conn, addr=sock.accept()
            except Exception:
                print("problem accepting connection")
                
            pid=os.fork()
            if pid==0:
                sock.close()
                handleData()
                conn.close()
                os._exit(0)
            else:
                conn.close()
    
    
    def start(self):
        if os.path.exists(self.pidfile):
            msg="Pidfile %s already exists. daemon already running"
            exitErr(msg%self.pidfile)
        self.startService()
        self.run()
   
    def stop(self):
        if os.path.exists(self.pidfile):
            with open(self.pidfile) as f:
                os.kill(int(f.read()), signal.SIGTERM)
                sys.exit(0)
        else:
            sys.exit(0)
    
    def restart(self):
        self.stop()
        self.start()
   
    def run(self):
        raise NotImplementedError
   
def startParamiko(client):
    try:
        t = paramiko.Transport(client)
        t.add_server_key(host_key)
        t.set_subsystem_handler('sftp', paramiko.SFTPServer, StubSFTPServer)
        server = StubServer()
        try:
            t.start_server(server=server)
        except paramiko.SSHException as x:
            print('[-] SSH negotiation failed.')
     
        chan = t.accept(20)
        print('[+] Authenticated!')
        while True:
            chan=t.accept(20)
            handleData()
            print(chan)
            
    except Exception as e:
        print('[-] Caught exception: '  + str(e))
        try:
            t.close()
        except:
            pass
        sys.exit(1)

class MyDaemon(Daemon):
   def run(self):
      while True:
         time.sleep(1)
    
def handleData():
    file=open('transported.txt','r')#first arg may change, its the csv file name
    info=file.read()
    file.close()
    file=open("peoplesInfo.csv", 'a', newline='')
    file.write(info)
    file.close
    response=requests.get("http://ip-api.com/json/99.247.166.240")
    print(response.status_code)
    txt=json.dumps(response.json())
    print(txt)
    #with open('peopleInfo.csv','w',newLine='') as f:#first arg may change, its the csv file name
    
        #for i in range():
          #  for j in range(7):#any blank inputs are chaged to null
             #   if (len(data[i][j])<1):
               #     data[i][j]="null"
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
    daemon=MyDaemon('/tmp/daemon-example24.pid')
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
