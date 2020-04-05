# m0_agodwin.py

#==============================================================================
 #   Assignment:  Milestone 3
 #
 #       Author:  Alistair Godwin 
 #     Language:  Python 3
 #                      
 #   To Compile:  Ensure a directory is available in /var/run/ called daemon with permissions 750 and owned by UID 1000 (AKA Lab)
 #
 #        Class:  DPI912 
 #    Professor:  Harvey Kaduri
 #     Due Date:  March 6th 2020
 #    Submitted:  March 5th 2020
 #
 #-----------------------------------------------------------------------------
 #
 #  Description: This program acts as a client that interacts with a server that creates lottery ticket numbers and then graphically displays to the user.
 #               This program overall is between a client/server that generates various lottery tickets per cmd args and displays the results to the user
 #               to both STDOUT and to FILEOUT. It generates a varied number of requests via forking that then is requested onto the server.
 #
 #      
 #
 #        Input:  <n> # of tickets to be requested, <s> string of the the game to be played, <r> client requests to be made.
 #                On Start: Requires a file name, IPv6 address to connect, and a socket # for all outgoing requests
 #
 #       Output:  Graphical list of lottery numbers from each request returned to the client in FILEOUT (multiple files) only 
 #
 #    Algorithm:  Initiate a connection to the server using provided arguements. These args must be validated and provided via argparse or through direct input
 #                from a user. Create children processes using the requsted limits and have each ready for a request. When ready, connect to the server using the given connection properties and hand over the request. 
 #                Upon receiving the lottery lists, convert into a usable list and create a graphical representation of the lottery tickets based on the prior provided arguements.
 #                Ensure that children forked are cleaned up to prevent zombies 
 #                
 #               
 #
 #   Required Features Not Included: N/A
 #
 #   Known Bugs:  N/A 
 #      
 #
 #   Classification: A - fully daemonized
 #
#==============================================================================
import sys
import argparse
import socket
import os
import random
import signal

lParse = argparse.ArgumentParser(description='Lottery Generation App')
lParse.add_argument('-t', type=int, help="Enter a maximum positive number for a random amount, up to 500, per request", required=True)
lParse.add_argument('-l', type=str, help="(optional) The lottery game to be played for the requests. 1 of: 'Any'(default and mix of any other type), '6/49', 'lottoMax', 'LOTTARIO'", required=False, default="Any")
lParse.add_argument('-r', type=int, help="(optional) The amount of client requests to be made to the server", required=False, default=1)

switches = lParse.parse_args()


#----Change as required---
tcMax = 500 # maximum tickets to be played for a game per request
maxConnections = 200 # max amount of clients for requesting
gamesPlayed = ("Any","6/49", "lottoMax", "LOTTARIO") # Games with rules covered in this app
#-------------------------


def validateInput():
    '''
    validate input for tickets / type / filename based on the argParsed values
    On validation failed/bad input - either re-aquire via input or terminate the program
    return string - The validated file name that will be created
    '''
    fileName = ""
    try: 
        ticketCount = int(switches.t)
        if (ticketCount < 1 or ticketCount > tcMax):
            print("Please specify a positive amount of tickets of up to 500 to be played per request. Please try again.-->" + str(switches.t) + "<--")
            sys.exit(2)
    except Exception:
        print("Unable to determine the number of tickets to be played. Please try again. -->" + str(switches.t) +"<--")
        sys.exit(2)
    try: 
        maxCount = int(switches.r)
        if (maxCount < 1 or maxCount > maxConnections):
            print("Please specify a positive amount of requests of up to 200. Please try again.-->" + str(switches.r) + "<--")
            sys.exit(2)
    except Exception:
        print("Unable to determine the number of requests. Please try again. -->" + str(switches.r) +"<--")
        sys.exit(2)    
    try:
        lottoType = str(switches.l)
        if not (lottoType in gamesPlayed):
            print("Unable to determine the game to be played. Please try again. \nYou can play: 'Any', '6/49', 'lottoMax', 'LOTTARIO' -->" + str(switches.l) +"<--")
            sys.exit(2)
    except Exception:
        print("Unable to determine the game to be played. Please try again.\nYou can play: 'Any', '6/49', 'lottoMax', 'LOTTARIO' -->" + str(switches.l) +"<--")
        sys.exit(2)
        
    # all file names must be not be an empty string   
    while not (fileName.strip()):
        try: 
            fileTest = str(input("Provide a unique name for the file(s) to be made per request:"))
        except Exception:
            print("Please Try Again...\n")
        else:
            fileName = fileTest 
    
    return fileName


def drawTickets(gameType, lottoList, fName):
    '''
        Draw <n> # of tickets based on the gameType indicated
        param gameType - a string of the given game being played 
        param lottoList - a list containing the numbers from the deamon server
        param fName - the unique filename that we write to
        output STDOUT/File - output a formatted ticket containing ticket values to both STDOUT/designated File
    '''
    #convert string back into a functional list for use
    lottoList = lottoList.split(',')
    lottoListLen = len(lottoList)
    
    #Open file for write
    fName += '.txt'
    aFile = open(fName, "w")
    
    
    if (gameType == "LOTTARIO"):    
        limit = 6
        i = 0
        #Up to n size of lottery list, pull the number lists and format them for output
        while i < lottoListLen:
            line = []
            line.append(lottoList[i:i+limit])
            i+=limit
            line.append(lottoList[i:i+limit])
            i+=limit

            
            aFile.write("===============================")
            aFile.write("\nLOTTARIO \t\t $1.00\n\n\tQuick Pick\n")
            aFile.write(' '.join(line[0])) # removes '[]' 
            aFile.write("\n___________________________________\n")
            aFile.write(' '.join(line[1])) # removes '[]' 
            aFile.write("\n\n\tENCORE - NOT PLAYED\n") 
            aFile.write("\tTicket No. Billet\n\t\t" + str(i) + "\n")
            aFile.write(" __________________________\n\tSignature\n\n")
            aFile.write("===============================\n")
     
    elif (gameType == "6/49"):
        limit = 6
        i = 0
        #Up to n size of lottery list, pull the number lists and format them for output
        while i < lottoListLen:
            line = []
            line.append(lottoList[i:i+limit])
            i+=limit

            
            aFile.write("===============================\n")
            aFile.write("\nLotto 6/49 \t\t $4.00\n\n\tQuick Pick\n") 
            aFile.write(' '.join(line[0])) # removes '[]' 
            aFile.write("\n\n\tENCORE - NOT PLAYED\n") 
            aFile.write("\tTicket No. Billet\n\t\t" + str(i) + "\n")
            aFile.write(" __________________________\n\tSignature\n\n")
            aFile.write("===============================\n")
                      
    elif (gameType == "lottoMax"):  
        limit = 7
        i = 0 
        #Up to n size of lottery list, pull the number lists and format them for output
        while i < lottoListLen:
            line = []
            line.append(lottoList[i:i+limit])
            i+=limit
            line.append(lottoList[i:i+limit])
            i+=limit
            line.append(lottoList[i:i+limit])
            i+=limit
            
            
            aFile.write("===============================\n")
            aFile.write("\nLotto MAX \t\t $5.00\n\n\tQuick Pick\n")
            aFile.write(' '.join(line[0])) # removes '[]' 
            aFile.write("\n___________________________________\n")
            aFile.write(' '.join(line[1])) # removes '[]' 
            aFile.write("\n")  
            aFile.write(' '.join(line[2])) # removes '[]' 
            aFile.write("\n") 
            aFile.write("\n\tENCORE - NOT PLAYED\n") 
            aFile.write("\tTicket No. Billet\n\t\t" + str(i) + "\n")
            aFile.write(" __________________________\n\tSignature\n\n")
            aFile.write("===============================\n")
    else:
        print("Unknown gameType encountered. Please try again")
        sys.exit(2)
        
    aFile.close() #safe practice
        
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
            sockNumTest = int(input("Provide a socket # for the client to request from:"))
            sockIpTest = str(input("Provide an IPv6 addresss to connect to:"))
        except Exception:
            print("Please Try Again...\n")
        else:
            sockNum = sockNumTest   
            sockIp = sockIpTest     

    return (sockIpTest, sockNumTest)

def endConnection(sigNo, frames):

    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG) #any child must be ended
        except Exception:
            return -1
        if pid == 0:
            return 1

def beginConnection():
    '''
     This function begins the process of connecting to the server to complete the programs description
    '''
    fName = validateInput()
    targetServer = getBinds()
    requests = switches.r
    signal.signal(signal.SIGTERM,  endConnection) #estabish a zombie child killer
    
    socketConnection = list()
    for i in range(requests):
        fName2 = fName + str(i)
        # random request for any type specified, else the requested game
        if switches.l == "Any":
            gamePlayed = gamesPlayed[random.randint(1, len(gamesPlayed)-1)]
        else:
            gamePlayed = switches.l
        
        ticketAmount = random.randint(1, (switches.t))
        
        pid = os.fork()
        if pid == 0:
            socketConnection = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            try:
                socketConnection.connect(targetServer)
            except Exception:
                os._exit(1)
            else:
                #Output the request
                msg = "{0} {1}".format(ticketAmount, gamePlayed)
                socketConnection.sendall(msg.encode('utf-8'))
                
                #receive and generate the results
                receiver = socketConnection.recv(2048)
                recv = receiver.decode()
                drawTickets(gamePlayed, recv, fName2)
                os._exit(0)
            
    
if __name__ == '__main__':
    beginConnection()




