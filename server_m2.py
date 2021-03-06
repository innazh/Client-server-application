#!/usr/bin/python3
#==============================================================================
 #   Assignment:  Milestone 2
 #
 #       Author:  Inna Zhogova 
 #    StudentID:  116683160
 #     Language:  Python
 #   To Compile:  n/a
 #
 #        Class:  Python for Programmers: Sockets and Security (DPI912) 
 #    Professor:  Harvey Kaduri
 #     Due Date:  Friday, February 14, 5pm
 #    Submitted:  Friday, February 14, 8pm
 #
 #-----------------------------------------------------------------------------
 #
 #  Description:  This program consist of 2 files: a client and a server. Server waits for client's connection, then generates ticket numbers based on the paramenters supplied
 #                by the client and sends the ticket numbers in response. The arguments in the client are arbitrarily generated per each request.
 #
 #        Input:  There are no required inputs but there are 2 optional ones: -r number of clients running and -c for number of connections per client.
 #
 #       Output:  The program creates files with ticket numbers in /tmp directory. Files names are arbitrarily generated by the client.
 #
 #    Algorithm:  n/a.
 #
 #   Required Features Not Included:  n/a.
 #
 #   Known Bugs:  n/a.
 #
 #   Classification: n/a.
 #
#==============================================================================
import random
import errno
import socket
import signal
import os

serverAddress = (HOST, PORT) = '', 8888
requestQueueSize = 1024
#Function accepts two integers: the number of numbers it has to pick,
#and the size of the number pool. Returns a list of arbitrary picked numbers.
def pickArbitraryNumbers(quantity, poolSize):
    numberPool = list(range(1,poolSize+1))
    pickedNums = []
    for i in range(0, quantity):
        random.shuffle(numberPool)
        pickedNum = random.sample(numberPool, 1)
        for elem in numberPool:
            if elem == pickedNum[0]:
                numberPool.remove(elem)
        pickedNums.append(pickedNum[0])
    return pickedNums

def lottomax():
    firstSetOfNums=[]
    secondSetOfNums=[]
    thirdSetOfNums=[]

    firstSetOfNums = pickArbitraryNumbers(7,45)
    secondSetOfNums = pickArbitraryNumbers(7,50)
    thirdSetOfNums = pickArbitraryNumbers(7,50)
    
    httpResponse=f"{firstSetOfNums}:{secondSetOfNums}:{thirdSetOfNums}"
    return httpResponse


def lottario():
    firstSetOfNums=[]
    secondSetOfNums=[]
    
    firstSetOfNums = pickArbitraryNumbers(6,45)
    secondSetOfNums = pickArbitraryNumbers(6,45)

    httpResponse=f"{firstSetOfNums}:{secondSetOfNums}"
    return httpResponse

def sixFourtyNine(): 
    pickedNums = pickArbitraryNumbers(6,49) 
    return f"{pickedNums}"

def determineLottery(lotteryName, numberTickets):
    httpResponse=""
    if lotteryName=="649":
        for i in range(0, int(numberTickets)):
            httpResponse+=("Ticket#" + str(i+1) + ".")
            httpResponse+=sixFourtyNine()+";"

    elif (lotteryName).lower()=="lottario":
        for i in range(0, int(numberTickets)):
            httpResponse+=("Ticket#" + str(i+1) + ".")
            httpResponse+=lottario()+";"
    elif (lotteryName).lower()=="lottomax":
        for i in range(0, int(numberTickets)):
            httpResponse+=("Ticket#" + str(i+1) + ".")
            httpResponse+=lottomax()+";"

    return httpResponse

#Receive the data, decode it, put the ticket numbers in httpResponse and send it back to client
def handleRequest(clientConnection):
    request = clientConnection.recv(10240)
    data = request.decode()
    lotteryName, numTickets = data.split(',')

    httpResponse = determineLottery(lotteryName, numTickets)
    clientConnection.sendall(httpResponse.encode())

def grimReaper(signalNumber, frame):
    while True:
        try:
            pid, status = os.waitpid(
                -1,         #Wait for any child process
                os.WNOHANG  #Do not block and return EWOULDBLOCK error
            )
        except OSError:
            return

def serveForever():
    listenSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listenSocket.bind(serverAddress)
    listenSocket.listen(requestQueueSize)

    print(f"You're now connected to the Lottery Terminal #{PORT}")

    signal.signal(signal.SIGCHLD, grimReaper)

    while True:
        try:
            clientConnection, clientAddress = listenSocket.accept()
        except IOError as e:
            errorCode, message = e.args
            # restart 'accept' if it was interrupted
            if errorCode == errno.EINTR:
                continue
            else:
                raise
        
        #make a kid
        try:
            pid = os.fork()
        except OSError:
            sys.stderr.write("Couldnt create a child process \n")
            continue
        
        if pid == 0: #child
            listenSocket.close()
            handleRequest(clientConnection)
            clientConnection.close()
            os._exit(0)
        else: #parent
            clientConnection.close() # close parent copy and loop over

if __name__ == '__main__':
    serveForever()
