# m3_agodwin.py

#==============================================================================
 #   Assignment:  Milestone 3
 #
 #       Author:  Alistair Godwin 
 #     Language:  Python 3
 #                      
 #   To Compile:  Ensure a dicrectory is available in /var/run/ called daemon with permissions 700 and owned by UID 1000 (AKA Lab)
 #
 #    Class:  DPI912 
 #    Professor:  Harvey Kaduri
 #    Due Date:  Mar 6th 2020 
 #    Submitted:  Mar 5th 2020
 #
 #-----------------------------------------------------------------------------
 #
 #  Description: This program acts as a non-blocking daemon that handles the generation of the lottery numbers and returns them to the client.
 #               It allows for multiple connections to occur at the same time and attempts to handle all of them together using forking.
 #               This program between client/server generates various lottery tickets per cmd args and outputs the results to the user.
 #               All work is completed using a double forked process that is handled behind the scenes for users. The server will run autonomously until told to stop
 #
 #      
 #        Input:  -init {stop/start} - The option to start or stop an initialized 
 #
 #       Output:  Ordered lists of lottery numbers returned to the client requesting it
 #
 #    Algorithm:  Using a numbered list with <1> to <n> numbers, generate random numbers using a list with poppings to create ticket lines of <c> numbers length
 #                based on game limits and how many computer generated lines are needed. Reapply the algorithm per ticket and per request receieved/
 #                Store the results to a list of lists and return to the requesting client when task completed.
 #                Handle the creation of a log file and PID file to store information relevant to starting/stopping the program. Log all events as needed.
 #                Ensure that each request is forked and handled seperatley and that those forked children are culled after their work is completed. 
 #                
 #      
 #
 #   Required Features Not Included: Semephore file in /var/run <-- requires root privilages which this program cannot take. File is located in /temp/daemon.pid instead.
 #
 #   Known Bugs:  N/A 
 #      
 #
 #   Classification: A - fully daemonized without errors
 #
#==============================================================================

import argparse
import random
import socket
import signal
import os
import sys
import atexit
import time
import fcntl
import logzero
from logzero import logger


lParse = argparse.ArgumentParser(description='Lottery Generation App Server')
lParse.add_argument('-init', type=str, help="Indicator to 'start' or 'stop' the server", required=True)


switches = lParse.parse_args()


#----Change as required---
maxTickets = 500 # maximum tickets to be played for a game
gamesPlayed = ("6/49", "lottoMax", "LOTTARIO") # Games with rules covered in this app
SERVICEQUEUE = 200
SERVINGPORT = 9000
acceptedArgs = ('start','stop') #can either start or stop
#-------------------------


def validateInput(tickets, gameType):
    '''
    validate input for tickets / type based on a ticket maximum and gamePlayed list
    On validation failed/bad input - return boolean result
    '''
    error = False
    try: 
        ticketCount = int(tickets)
        if (ticketCount < 1 or ticketCount > maxTickets):
            error = True
    except Exception:
        error = True
    try:
        lottoType = str(gameType)
        if not (lottoType in gamesPlayed): 
           error = True
    except Exception:
        error = True
    
    return error

def generateSequence(gameType):
    '''
        Generate a sequence of 1 to <n> based on gameType and returns it.
        param gameType - a string of the given game being played 
        return - tuple - a tuple containing all sequential numbers up to <n>
    '''
    low = 1
    high = 46 if (gameType == "LOTTARIO") else 50 if(gameType == "6/49")else 51 # +1 for inclusive
    strList = [str(x).zfill(2) for x in range(low,high)] # string conversion to support leading 0s
    return tuple(strList)
    
def lotteryDraw(numPool, limit):
    '''
        Simulate drawing numbers from the lottery pool with abritrariness
        param limit - an int of the maximum draw amount based on the game
        param numPool - a tuple containing the pool of numbers to sample from
        return - A list containing the line to be generated
    '''
    drawList = list(numPool)
    results = list() 
    while limit > 0:
      idx = random.randint(0, len(drawList)-1)
      results.append(drawList[idx])
      drawList.pop(idx)
      limit -= 1
    return results 
    
def generateTickets(ticketCount, gameType, numPool):
    '''
        Generate <n> # of tickets based on the gameType indicated
        param gameType - a string of the given game being played 
        param ticketCount - a int indicating <n> # of tickets to be played 
        param numPool - a tuple containing the pool of numbers to work from
        return - A list of lists containing the number lines generated
    '''
    line = []
    
    if (gameType == "LOTTARIO"):    
        limit = 6
        for i in range(1, ticketCount+1):
           #select random numbers via the drawing function
            line.append(lotteryDraw(numPool, limit)) 
            line.append(lotteryDraw(numPool, limit)) 

    elif (gameType == "6/49"):
        limit = 6
        for i in range(1, ticketCount+1):
            #select random numbers via the drawing function
            line.append(lotteryDraw(numPool, limit)) 
          
        
    elif (gameType == "lottoMax"):  
        limit = 7
        for i in range(1, ticketCount+1):
            #select random numbers via the drawing function
            line.append(lotteryDraw(numPool, limit)) 
            line.append(lotteryDraw(numPool, limit)) 
            line.append(lotteryDraw(numPool, limit)) 
         
    else:
        print("Unknown gameType encountered. Will not generate this list")
        
    return line 

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
def daemonizeSelf(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    ''''
    This function handles the intiial setup needed in order to start or stop the Daemon. 
    For stopping the program, it will find the PID file and remove it. Then, it will exit the daemon.
    For starting the program, it will check for an existing PID file and if not available, writes one and double forks to generate a daemonized daemon.
    Function will log as needed to the logfile which exist next to the file that was executed as dpi912logFile
    '''
    
    pidFile = '/var/run/daemon/daemon.pid' #instead of /var/run/ which requires root, which I dont have the pwd for.
    try:
        inits = str(switches.init)
        if not (inits in acceptedArgs): 
           print("This Daemon can only be given the arg: 'start' or 'stop'. Please try again")
           logger.error("This Daemon can only be given the arg: 'start' or 'stop'. Please try again")
           os._exit(1)
    except Exception:
            print("This Daemon can only be given the arg: 'start' or 'stop'. Please try again")
            logger.error("This Daemon can only be given the arg: 'start' or 'stop'. Please try again")
            os._exit(1)
        
    #if init start is passed, start the server
    if inits == "start":
        print("Attempting to start on ipv6 localhost via socket #9000 - see logs for further information")
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
            with open(stdin,  'rb', 0)  as f:
                os.dup2(f.fileno(),  sys.stdin.fileno())
            with open(stdout,  'ab',  0)  as f:
                os.dup2(f.fileno(),  sys.stdout.fileno())
            with open(stderr,  'ab',  0)  as f:
                os.dup2(f.fileno(),  sys.stderr.fileno())
            
            with open(pidFile,'w')  as f:
                print(os.getpid(),file=f)
                
            # PID is to be removed when this daemon stops
            atexit.register(lambda:  os.remove(pidFile))
            signal.signal(signal.SIGTERM,  sigterm_handler)
            
    #if init stop is passed, shutdown the server
    else:
        print("Attempting to stop Daemon - see logs for further information")
        if os.path.exists(pidFile):
            with open(pidFile) as f:
                os.kill(int(f.read()),  signal.SIGTERM)
                logger.info("Daemon PID removed, daemon stopped. Exiting...")
                sys.exit(0)
        else:
                logger.warning("Daemon PID file was not detected, is this Daemon running? Exiting...")
                sys.exit(0)
        
        
        
def sigterm_handler(signo,  frame):
    ''''
    This function handles the cleanup of the parent daemon when the stop command is passed
    param - sigNo 
    param - frames
    return - exit state
    '''
    raise  SystemExit(1)

def beginService():
    '''
     This function begins the process of creating and controlling the server to complete the program's description
     It starts the server on localhost(::1) on IPv6 as the requirements do not specify servers to be hosted on an inputted arg
     When connections arrive, it uses the handle function to generate and return each callers request.
     All requests are handled by forks from the parent
    '''
 
    daemonizeSelf() #setup the daemon before beginning to listen 
    
    listenSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    listenSocket.bind(getBinds())
    listenSocket.listen(SERVICEQUEUE)
    logger.info(f"Daemon Started and ready for IPv6 service on localhost using port 9000...")

    signal.signal(signal.SIGCHLD,endConnection) #estabish a zombie child killer
    
    while True:
        try:
            clientCon, clientAddr = listenSocket.accept()
        except Exception:
            logger.error("There was a problem accepting the connection, please try again")
            
        pid = os.fork()
        if pid == 0:
            #I am the child connection
            listenSocket.close() # do not listen to the parent
            handle(clientCon)
            clientCon.close()
            os._exit(0) #children are returning success to parent
        else:
            #I am a parent connection
            clientCon.close()

def handle(conn):
    '''
    This function handles the requests issued to this server from client applications
    It decodes, parses, and validates the incoming args and begins generation based on the indicated gametype 
    It then returns the results from its generation using a flat array string 
    param conn - A connection socket that contains messaging functions from a requester
    '''
    request = conn.recv(1024)
    res = request.decode()
    argList = res.split() # move result to a list
    
    res = validateInput(argList[0], argList[1])
    tickets = int(argList[0])
    gameType = str(argList[1])
    
    if not res:
        # Generate a nested list and then parse it into a flat string
        msg = generateTickets(tickets, gameType, generateSequence(argList[1]))
        msgStr = []
        for msgSub in msg:
            for msgItem in msgSub:
                msgStr.append(msgItem)      
        res = ','.join(msgStr)

        #Return to client 
        conn.sendall(res.encode('utf-8'))
        
    else:
        logger.warning("CHILD Handler Says: A message did not validate, please try again")
    
def getBinds():
    '''
    This function grabs the binding arguements for the connection
    In the servers case, this is the socket # only
    return tuple - The connection properties 
    '''
    sockNum = SERVINGPORT;
    
    return ("::1", sockNum)
    
if __name__ == '__main__':
    logzero.logfile("dpi912logFile.log", maxBytes=1e6, backupCount=3, disableStderrLogger=True)
    pid = os.getpid()
    logger.info(f"Program started with PID: {pid}")
    beginService()
   




