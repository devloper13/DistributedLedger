
import socket 
import json  
from _thread import *
import threading 
import pickle
  
print_lock = threading.Lock() 
ListOfClient = {}  
IDCount=0
IDStr='0'
# thread fuction 

def threaded(c,addr):
    global IDCount
    global IDStr
    recv_loop = True
    while recv_loop:
        message = c.recv(1024)
        if pickle.loads(message) == "InitialConnection":
            IDCount+=1
            IDStr = str(IDCount)
            ListOfClient[IDStr] = str(addr[0]) + ':' + str(addr[1])
            IDStr = str(IDCount) + ':' + str(addr[0]) + ':' + str(addr[1])
            c.sendall(pickle.dumps(IDStr))
        elif pickle.loads(message) == "SendUpdatedList":
            c.sendall(pickle.dumps(ListOfClient))
            recv_loop=False
        else:
            print("Something went wrong! :(")
    print_lock.release()
   
    c.close()    

def Main(): 
    host = "" 
  
    # reverse a port on your computer 
    # in our case it is 12345 but it 
    # can be anything 
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.bind((host, port)) 
    print("socket binded to post", port) 
  
    # put the socket into listening mode 
    s.listen(5) 
    print("socket is listening") 
  
    # a forever loop until client wants to exit 
    try:
        while True: 
      
            # establish connection with client 
            c, addr = s.accept() 
      
            # lock acquired by client 
            print_lock.acquire() 
            print('Connected to :', addr[0], ':', addr[1]) 
      
            # Start a new thread and return its identifier 
            start_new_thread(threaded, (c,addr,)) 
        s.close()
    except:
        s.close()    
  
  
if __name__ == '__main__': 
    Main() 
