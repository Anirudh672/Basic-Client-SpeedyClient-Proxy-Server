# Simple web server : If the requested object is in same folder where Server.py is saved it fetches that object 
                    # in all other cases it returns 404 Not Found message.


# Need only Socket and threading library, threading as concurrently any number of clients can connect to server
import socket
import threading
from datetime import datetime


# Each connection in a separeate thread goes here, this function is the target function of the threading
def newclient(clientid, clientSocket ,clientaddr):
    print(f"Connection with {clientaddr} established !")

    # receive the request from the connected client
    msg = clientSocket.recv(1024)
    if len(msg)<=0 :
        clientSocket.close()
        return

    # just printing the request for debugging purpose
    msg = msg.decode("utf-8")
    print("message received from client : " + msg)

    
    # need to extract the url from request so split the msg (request)
    msg = msg.split("\n")

    # Extracting the different parts like url from the request msg 
    request_line1 = msg[0].split()

    url = ""
    if "http://" in request_line1[1]:
        url += request_line1[1].split("20000")[1]
    else :    
        url += request_line1[1] 
    
    print(f"Requested URL : {url}")
    
    # The html file stored in my directory in by name index.html and for making it in path form it becomes /index.html
    if url=='/index.html' or url=='/':
        try :

            # opening a file may raise error in case index.html file not found so used try and except
            with open("index.html", "r") as newfile:

                # read() scans entire file and puth that into variable
                newdata = newfile.read() 
                current_datetime = datetime.now()
                formatted_datetime = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
                # Making the http response message
                http_response = "HTTP/1.1 200 OK\r\n"
                http_response += formatted_datetime
                http_response += "\r\n"
                http_response += "Content-Type : text/html\r\n"
                http_response += "\r\n"

                # Appending the data to the above http response which consists of headers.
                http_response += newdata
                
                # Send the response to the client.
                clientSocket.send(bytes(http_response, "utf-8"))
        except :

            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
            # Maling the http response message in case of exception
            http_response = "HTTP/1.1 404 Not Found\r\n"
            http_response += formatted_datetime
            http_response += "\r\n"
            http_response += "Content-Type : text/html\r\n"
            http_response += "\r\n"

            # 404 Not Found error message, in html format so that any browser can render it
            http_response += "<html><body><h2>404 Not Found</h2> </body> </html> "      
            clientSocket.send(bytes(http_response,"utf-8"))
    else :

        # in case file path in request is not correct the same 404 http response is made and sent to client.
        print("Incorrect URL")
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
        http_response = "HTTP/1.1 404 Not Found\r\n"
        http_response += "Content-Type : text/html\r\n"
        http_response += formatted_datetime
        http_response += "\r\n"
        http_response += "\r\n"
        http_response += "<html><body><h2>404 Not Found</h2> </body> </html> "      
        clientSocket.send(bytes(http_response,"utf-8"))
    clientSocket.close()


# Main Thread Goes Here (program control starts here...)

# Opened a socket and made it in listen state.
ServerMainSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ServerMainSocket.bind(('10.42.0.105', 20000))
ServerMainSocket.listen()
no_of_clients = 0
while True:
    
   # Accepting incoming requests from clients
   clientSocket, addr = ServerMainSocket.accept()

   # no of clients increased by one
   no_of_clients=no_of_clients+1

   # start a separate new thread for each incoming client
   threading._start_new_thread(newclient, (no_of_clients, clientSocket ,addr))
