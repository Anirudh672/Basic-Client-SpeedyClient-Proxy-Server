# Simple proxy server : receives requests from client and fetches objects from the server. No caching function

# Used libraries, installed BeautiffulSoup used it for parsing
# BytesIO and image libraries imported to display the images and icon
import socket
import threading
import sys
import re
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import ssl


# The resCodeInfo function here based on the response code it received in http response from the server makes the http response message.
# based on the response code obtained from server this will make appropriate http response headers, and then append appropriate content to them.
def resCodeInfo(code, contentType):
        if code==200:
            httpResponseHeaders = "HTTP/1.0 200 OK\r\n"
            httpResponseHeaders += "Content-Type : " + contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            return httpResponseHeaders
        elif code==404:
            httpResponseHeaders = "HTTP/1.0 404 Not Found\r\n"
            httpResponseHeaders += "Content-Type : "+ contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            httpResponseHeaders += "The requested resource or plain teext could not br found"
            return httpResponseHeaders
        elif code==400:
            httpResponseHeaders = "HTTP/1.0 400 Bad Request\r\n"
            httpResponseHeaders += "Content-Type : "+ contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            httpResponseHeaders += "The requested image could not be found of the server"
            return httpResponseHeaders
        elif code==301:
            httpResponseHeaders = "HTTP/1.0 301 Moved Permanently\r\n"
            httpResponseHeaders += "Content-Type : "+ contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            httpResponseHeaders += "Resource has permanently moved to a new location"
            return httpResponseHeaders
        elif code==302:
            httpResponseHeaders = "HTTP/1.0 302 Found\r\n"
            httpResponseHeaders += "Content-Type : "+ contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            httpResponseHeaders += "Resource has temporarily moved to a differenr location"
            return httpResponseHeaders
        elif code==304:
            httpResponseHeaders = "HTTP/1.0 304 Not Modified\r\n"
            httpResponseHeaders += "Content-Type : "+ contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            httpResponseHeaders += "Resource has not been modified since the last request"
        else :
            httpResponseHeaders = "HTTP/1.0 503 Service Unavailable\r\n"
            httpResponseHeaders += "Content-Type : "+ contentType + "\r\n"
            httpResponseHeaders += "\r\n"
            httpResponseHeaders += "The server is temporarily unavialable or overloaded"


# This function is target of threading and it also does all the core functionality of proxy server
def newClientToServer(clientSocket, clientAddr):
    print(f"Connection with {clientAddr} established !")

    # receiving request from the client
    request = clientSocket.recv(4096)
    if len(request)<=0:
        clientSocket.close()
        return
    requestString = request.decode("utf-8")
    print("message received from client : " + requestString)


    # Split the requestString 
    requestlines = requestString.split('\r\n')


    # The first line of the requestLines contains request method and target URL
    line1 = requestlines[0]
    print("LINE 1: ", line1)
    
    serverHostname = ''
    serverPort = 0
    if "http://" in line1:
        temp= line1.split("http://")[1]
        temp1 = temp.split("/")[0]
        if ":" in temp1:
            serverHostname += temp1.split(':')[0]
            serverPort = int(temp1.split(':')[1])
        else :
            serverHostname += temp1
            serverPort = 80
    else :
        # Extracting the server address and server port no from line1, port needs to be in integer
        serverAddr = requestString.split('\r\n\r\n')[1]
        serverAddr1 = serverAddr.split(":")
        serverHostname += serverAddr1[0]
        serverPort = int(serverAddr1[1])
    
    
    print("SERVER HOST NAME : ",  serverHostname)
    print("SERVER PORT NO :  ",serverPort)

    # checking if server port is 443 or not, if it is 443 then we connect using ssl socket.
    if serverPort==443:
        # We obtained the URL, Now proxy will work as client. Create a ssl_socket and connect to server using it.
        proxySentSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sslproxySentSocket = ssl_context.wrap_socket(proxySentSocket, server_hostname=serverHostname)
        sslproxySentSocket.connect((serverHostname, serverPort))
    

        # http request sent to server
        modhttprequest = requestlines[0] + "\r\n" + requestlines[1] + "\r\n" + f"Host: {serverHostname}\r\n\r\n"
        sslproxySentSocket.send(modhttprequest.encode())
    
    
        # receiving the response from server.
        response = b""
        while True:
            data = sslproxySentSocket.recv(1024)
            if not data:
                break
            response += data

    
        # socket for communication between proxy and server is closed as after received complete response of one get request.
        sslproxySentSocket.close()


        # removing headers and response1 contains http response retrieved without headers.
        rmheaders = response.split(b"\r\n\r\n")[0]
        response1 = response[len(rmheaders)+4:]
    

        # extracting the response code and content type from the response and headers respectively.
        resCode = int(rmheaders.split()[1])
        contentType = rmheaders.split(b"\r\n")[2].split(b":")[1].decode("utf-8")


        # just printing content type for debugging purpose
        print("Debugging : ")
        print(f"Content Type : {contentType}")


        # passed response code and content type to resCodeInfo funtion to obtain the appropriate http response headers.
        httpResponseHeaders = resCodeInfo(resCode, contentType)
    
    
        # making the final response
        final_response = ""
        if resCode!=200:

            # if the response code is not 200 then the http response message contains only appropriate http headers showing error codes
            final_response = httpResponseHeaders.encode("utf-8")
        else:

            # otherwise append response1 (content from server) to http response headers.
            final_response = httpResponseHeaders.encode('utf-8') + response1
    

        # Send the final response to the client and close the clientSocket also. 
        clientSocket.send(final_response)
        clientSocket.close()
    
    #  if the server port no is not 443 we connect using normal socket, everything else remains same.
    else :
        # We obtained the URL, Now proxy will work as client. Create a ssl_socket and connect to server using it.
        proxySentSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxySentSocket.connect((serverHostname, serverPort))

        # http request sent to server
        modhttprequest = requestlines[0] + "\r\n" + requestlines[1] + "\r\n" + f"Host: {serverHostname}\r\n\r\n"
        proxySentSocket.send(modhttprequest.encode())


        # receiving the response from server.
        response = b""
        while True:
            data = proxySentSocket.recv(1024)
            if not data:
                break
            response += data
        
        # socket for communication between proxy and server is closed as after received complete response of one get request.
        proxySentSocket.close()


        # removing headers and response1 contains http response retrieved without headers.
        rmheaders = response.split(b"\r\n\r\n")[0]
        response1 = response[len(rmheaders)+4:]


        # extracting the response code and content type from the response and headers respectively.
        resCode = int(rmheaders.split()[1])
        contentType = rmheaders.split(b"\r\n")[2].split(b":")[1].decode("utf-8")


        # just printing content type for debugging purpose
        print("Debugging : ")
        print(f"Content Type : {contentType}")


        # passed response code and content type to resCodeInfo funtion to obtain the appropriate http response headers.
        httpResponseHeaders = resCodeInfo(resCode, contentType)
        # making the final response
        final_response = ""
        if resCode!=200:

            # if the response code is not 200 then the http response message contains only appropriate http headers showing error codes
            final_response = httpResponseHeaders.encode("utf-8")
        else:

            # otherwise append response1 (content from server) to http response headers.
            final_response = httpResponseHeaders.encode('utf-8') + response1

        # Send the final response to the client and close the clientSocket also. 
        clientSocket.send(final_response)
        clientSocket.close()



# Program control starts here, we assigned port 15000 for the proxy.
proxyaddress ='10.42.0.105'
proxyport = 15000


# Just creating ssl_context, ssl socket will be made for proxy to server connections as a deployed web server may be running on 443.
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)


# the proxyRecvSocket is for the proxy to accept incoming client requests 
proxyRecvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxyRecvSocket.bind((proxyaddress, proxyport))
proxyRecvSocket.listen()

# This socket is always open in listening state.
while True:

    # Accepting the incoming client request.
    clientSocket, clientAddr = proxyRecvSocket.accept()

    # A separate new thread is started for every client, target function is newClientToServer function
    threading._start_new_thread(newClientToServer, ( clientSocket , clientAddr))
