import socket 
from NodeClass import Node
from NodeClass import NewTransaction
from _thread import *
import threading
import json
import time
import pickle

lock=0
ListOfClients = {}
InitMessage = "InitialConnection"
UpdateListMessage = "SendUpdatedList"
GetObjectFromRecv = "SendObject"
BecomeReceiver = "BecomeReceiver"
UpdateClientList = "UpdateClientList"
UpdateLedger = "UpdateLedger"
NewNode = "NewNode"
SendLedger = "SendLedger"

def BroadcastUpdatedClientList(ClientList,node_id):
    for key in ClientList:
        if key!=node_id:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ClientList[key].split(':')[0],int(ClientList[key].split(':')[1])))
            s.send(pickle.dumps(UpdateClientList))
            #below message is received just to keep a continuity of send recv order
            message = pickle.loads(s.recv(1024))
            s.sendall(pickle.dumps(ClientList))
            s.close()
    print('In BCCL\n')        

def BroadcastLedger(ClientList,node,message):
    #1. node has a member named Inout_tx which is a ledger (List of all transaction)
    #2. It is a dictionary with id as key and a list of it's transactions as value
    #3. may refer above to see the working 
    print(node.Input_TX)
    print('In BCL\n')
    if message == NewNode:
        for key in ClientList:
            if key!=node.id:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ClientList[key].split(':')[0],int(ClientList[key].split(':')[1])))
                s.send(pickle.dumps(NewNode))
                #below message is received just to keep a continuity of send recv order
                message = pickle.loads(s.recv(1024))
                s.sendall(pickle.dumps(node.Input_TX))
                s.close()
        #Break loop if successfully connected to one of the node
        #Else continue till it is connected atmost one node
        #Handle try-catch
        for key in ClientList:
            if key!=node.id:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect((ClientList[key].split(':')[0],int(ClientList[key].split(':')[1])))
                except ConnectionRefusedError:
                    continue    
                s.send(pickle.dumps(SendLedger))
                NewLedgerDetails =  pickle.loads(s.recv(1024))
                node.Input_TX = NewLedgerDetails
                s.close()
                break
        print("\nFinal List:\n")
        print(node.Input_TX)                        

def threaded_Receiver(nodeInfo,node):
    #Forever open if I were to become the receiver
    node_id = nodeInfo.split(':')[0]
    node_ip = nodeInfo.split(':')[1]
    node_port = nodeInfo.split(':')[2]

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((node_ip, int(node_port)))
    print(node_ip)
    print(node_port)
    print("socket binded to post", node_port) 
  
    # put the socket into listening mode 
    s.listen(50) 
    print("socket is listening")
    while True:
        c, addr = s.accept()
        print(addr[1])
        message = pickle.loads(c.recv(1024))
        print(message+'\n')
        if message == GetObjectFromRecv:
            c.send(pickle.dumps(str(node.isBusy)))
            reply = pickle.loads(c.recv(1024))
            if reply == BecomeReceiver:
                node.setBusy(True)
        elif message == UpdateClientList:
            c.send(pickle.dumps(UpdateClientList))
            UpdatedClients = pickle.loads(c.recv(1024))
            node.updateBroadcastList(UpdatedClients)
            print(UpdatedClients)
            print('\n')
        elif message == NewNode:
            c.send(pickle.dumps(NewNode))
            NewLedgerEntry =  pickle.loads(c.recv(1024))
            for key in NewLedgerEntry:
                #Will have only one value....For value used ot fetch the key
                if key in node.Input_TX:
                    node.Input_TX[key].append(NewLedgerEntry[key])
                else:
                    lst = []
                    lst.extend(NewLedgerEntry[key])
                    node.Input_TX[key] = lst
        elif message == SendLedger:
            c.sendall(pickle.dumps(node.Input_TX))            
        elif message == UpdateLedger:
            NewLedger =  pickle.loads(c.recv(1024))
            node.updateLedger(NewLedger[0])  
            print(NewLedger)
            print('\n')       
    s.close()
    

def threaded_Sender(node):
    print("Hi2")
    receiver = input('Enter ID of the receiver from the above broadcast list:')
    print("Hi3")
    recv_ip = (node.BroadcastList[receiver]).split(":")[0]
    recv_port = (node.BroadcastList[receiver]).split(":")[1]
    recv_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print(recv_ip)
    print(recv_port)
    recv_sock.connect((recv_ip,int(recv_port)))
    recv_sock.sendall(pickle.dumps(GetObjectFromRecv))
    RecvNode = pickle.loads(recv_sock.recv(1024))
    if(RecvNode == 'True'):
        print('Node is busy in a transaction.\n')
        #Send a message to not be a receiver
    else:
        recv_sock.send(pickle.dumps(BecomeReceiver))
        print('Node is not Busy')
        #time.sleep(10)   ##TO BE REMOVED...TO CHECK BUSY TRANSACTION
        ##ASSUME COMMITED
        
        Amount = int(input('\nEnter the amount to be sent:'))
        New_TX = NewTransaction()
        New_TX.Amount = Amount
        New_TX.SenderID = node.id
        New_TX.ReceiverID = receiver

        Share_TX = ShareTransaction()
        Share_TX.New_TX = New_TX
        #Share_TX = node.Input_TX

        #recv_sock.sendall()
    recv_sock.close()
    lock=0
  

def Main(): 
    # local host IP '127.0.0.1' 
    host = '127.0.0.1'
  
    # Define the port on which you want to connect 
    port = 12345


    ######## Initial Socket connect#####
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
  
    # connect to server on local computer 
    s.connect((host,port))
    s.send(pickle.dumps(InitMessage))
    ID = s.recv(1024) 
    print('Received from the server :',pickle.loads(ID))
    nodeInfo = pickle.loads(ID) ##node knows it's ID now.
    node = Node(nodeInfo.split(':')[0])

    #### Initial Bitcoin Gift By God ####
    New_TX = NewTransaction()
    New_TX.Amount = 10
    New_TX.SenderID = node.id
    New_TX.ReceiverID = 0
    tx_list = []
    tx_list.append(New_TX)
    node.Input_TX[node.id] = tx_list
    #### Initial Bitcoin Gift By God ####

    #1. Change 'threaded' in server.py to have a while loop for c.recv()
    #2. After initial connection send "Send Updated List"
    s.send(pickle.dumps(UpdateListMessage))
    ListOfClients = s.recv(1024)
    ListOfClients = pickle.loads(ListOfClients)
    print(ListOfClients)
    node.updateBroadcastList(ListOfClients)


    #3. Broadcast client list
    BroadcastUpdatedClientList(ListOfClients,node.id)
    #4. Broadcast transaction list
    BroadcastLedger(ListOfClients,node,NewNode)

    s.close()
    ####### Initial Socket connect ######

    start_new_thread(threaded_Receiver,(nodeInfo,node,))

    while True:
        global lock
        if lock == 0:
            choice = int(input("1. Become a Sender\n"))
            if choice == 1:
                
                #node = Node(nodeInfo.split(':')[0])
                #node.setBusy(True)
                lock=1
                start_new_thread(threaded_Sender,(node,))
            
  
if __name__ == '__main__': 
    Main() 
