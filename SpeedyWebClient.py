# Part 4 : Extension 5
# Speedy web client : After getting base html file it makes multiple parallel TCP connections to retrieve the referenced objects.


# Used libraries, concurrent.futures was imported to use ThreadPoolExecutor functionilty it provides.
# urlunsplit was used to make a proper complete url
import socket
import threading
import sys
import re
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import ssl
import concurrent.futures
from urllib.parse import urlunsplit
import time


# Asking for choice whether to connect directly to server or through proxy.
print("How would you like to get the file? \n if directly from server : enter choice 0 \n if through proxy : enter choice 1 \n")
choice = int(input())


# if choice is 0, then client directly connects to server
if choice==0:
    
    # Using sys.argv to take command line arguments
    no_of_args = len(sys.argv)
    print("Total number of arguments passed : ", no_of_args)

    
    # Way to pass arguments for directly connecting to server: python3 Client.py hostname portno path , press enter and choose choice 0 
    pythonFile = sys.argv[0]
    serverHostname = sys.argv[1]
    serverPortNo = int(sys.argv[2])
    Path = sys.argv[3]

    # Checking if the serverPortNo is 443 or not if it is 443 then we connect using ssl socket.
    if serverPortNo==443:
        # Make an ssl_context so that we can wrap the socket with secure socket layer so that we can coonect on port 443
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_socket = ssl_context.wrap_socket(clientSocket, server_hostname=serverHostname)


        # Connecting to the server using ssl_socket, secure socket. And made http request to get the first index file.
        ssl_socket.connect((serverHostname, serverPortNo))
        httpRequest = f"GET {Path} HTTP/1.0\r\nAccept: text/html\r\nHost: {serverHostname}\r\n\r\n"
    

        # Started timer so as to give latency comparison between normal client and Speedy client
        startTime = time.time()

    
        # Sending the httprequest to retrieve the base index file, stored in response in bytes format
        ssl_socket.send(httpRequest.encode())
        response = b""
        while True:
            data = ssl_socket.recv(1024)
            if not data:
                break
            response += data

        print(response.decode("utf-8"))
        ssl_socket.close()


        response1 = response.decode("utf-8")

        # Modified response is just the data without headers extracted from response
        rmheaders = response1.split("\r\n\r\n")[0]
        modified_response = response1[len(rmheaders)+4:]
    
    
        # Created a soup object (created using BeautifulSoup) which is helpful in parsing the base html file.
        soup = BeautifulSoup(response1, "html.parser")

    
        # empty lists created so as to store the path of the objects and their names respectively. paths will be used later in fetching objects. 
        object_urls = []
        object_names = []

    
        # Parsed all the images using soup object, append the paths for all images in object_urls.
        img_tags = soup.find_all("img")
        print("Length of the Imge list : " + str(len(img_tags)))
        if len(img_tags)!=0:
            for img in img_tags:
                img_url = img["src"]
                object_urls.append(img_url)            
                temp = img_url.split('/')[-1]
                object_names.append(temp)

    
        # Parsed all the scripts using soup object, append the paths in object_urls
        script_tags = soup.find_all("script")
        if len(script_tags)!=0:
            for scripts in script_tags:
                if scripts.has_attr('src'):
                    script_url = scripts["src"]
                    object_urls.append(script_url)
                    temp_script = script_url.split('/')[-1]
                    object_names.append(script_url)
                else:
                    inlineScript = scripts.get_text()


        # Parsed all the icons using soup object, append the paths in object_urls
        icon_tags = soup.find_all("link", rel="icon")
        if len(icon_tags)!=0:
            for icon_tag in icon_tags:
                icon_url = icon_tag.get('href')
                object_urls.append(icon_url)
                temp_icon = icon_url.split('/')[-1]
                object_names.append(temp_icon)

    
        # When given complete path to this function as argument it retrieves the object from the server. 
        def getNewObject(path):
            print("Inside getNewObject function")
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            newClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newSslSocket = ssl_context.wrap_socket(newClientSocket, server_hostname=serverHostname)
            newSslSocket.connect((serverHostname, serverPortNo))
            httpRequest = f"GET {path} HTTP/1.1\r\nAccept: text/html\r\nHost: {serverHostname}\r\n\r\n"        
            newSslSocket.send(httpRequest.encode())
            newResponse = b""
            while True:
                newData = newSslSocket.recv(1024)
                if not newData:
                    break
                newResponse += newData
            rmheaders = newResponse.split(b"\r\n\r\n")[0]
            modified_newResponse = newResponse[len(rmheaders)+4:]
            fileName = path.split("/")[-1]
            newFile = open(fileName, "wb")
            newFile.write(modified_newResponse)
            newFile.close()


        # just printing all the paths for debugging purpose.
        print(" object urls : ")
        print(object_urls)

    
        # now we create complete urls from the use of server hostname, server port no, elements of object urls and urlunsplit and append them in complete_urls
        complete_urls = []
        for url in object_urls:

            # scheme is http for our scenario
            scheme = "http"

            # netloc has the address:portno , portno is optional
            netloc = serverHostname + ":" + str(serverPortNo)
        
            # query and fragment can be added if there are any
            query = ''
            fragment = ''

            # final complete url is made using the above three and the path which I am referring to as url of object_urls.
            complete_urls.append(urlunsplit((scheme, netloc, url, query, fragment)))

    
        # just printing complete urls for debugging purpose
        print(" complete urls : ")
        print(complete_urls)

        # Working of ThreadPoolExecutor()
        # This is the part where we made parallel TCP connections using ThreadPoolExecutor(). The target funtion of executor is run concurrently
        # (continue) n number of times. This can be set in a parameter max_workers. So for example if max_workers=5 then there will be 5 parallel
        # instances of the function getNewObject in each of which I make a TCP connection so it becomes 5 parallel TCP connections.

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(getNewObject, complete_urls)
    

        # Finished time and its difference with start time is the latency.
        endTime = time.time()
        print()
        latency = endTime - startTime
        print(f" latency : {latency} seconds ")
    
    # if the serverPortNo is not 443 then we connect using normal socket, everything else remains same.
    else:
        # Make a normal port
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connecting to the server using ssl_socket, secure socket. And made http request to get the first index file.
        clientSocket.connect((serverHostname, serverPortNo))
        httpRequest = f"GET {Path} HTTP/1.0\r\nAccept: text/html\r\nHost: {serverHostname}\r\n\r\n"
    

        # Started timer so as to give latency comparison between normal client and Speedy client
        startTime = time.time()

    
        # Sending the httprequest to retrieve the base index file, stored in response in bytes format
        clientSocket.send(httpRequest.encode())
        response = b""
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            response += data

        print(response.decode("utf-8"))
        clientSocket.close()


        response1 = response.decode("utf-8")

        # Modified response is just the data without headers extracted from response
        rmheaders = response1.split("\r\n\r\n")[0]
        modified_response = response1[len(rmheaders)+4:]
    
    
        # Created a soup object (created using BeautifulSoup) which is helpful in parsing the base html file.
        soup = BeautifulSoup(response1, "html.parser")

    
        # empty lists created so as to store the path of the objects and their names respectively. paths will be used later in fetching objects. 
        object_urls = []
        object_names = []

    
        # Parsed all the images using soup object, append the paths for all images in object_urls.
        img_tags = soup.find_all("img")
        print("Length of the Imge list : " + str(len(img_tags)))
        if len(img_tags)!=0:
            for img in img_tags:
                img_url = img["src"]
                object_urls.append(img_url)            
                temp = img_url.split('/')[-1]
                object_names.append(temp)

    
        # Parsed all the scripts using soup object, append the paths in object_urls
        script_tags = soup.find_all("script")
        if len(script_tags)!=0:
            for scripts in script_tags:
                if scripts.has_attr('src'):
                    script_url = scripts["src"]
                    object_urls.append(script_url)
                    temp_script = script_url.split('/')[-1]
                    object_names.append(script_url)
                else:
                    inlineScript = scripts.get_text()


        # Parsed all the icons using soup object, append the paths in object_urls
        icon_tags = soup.find_all("link", rel="icon")
        if len(icon_tags)!=0:
            for icon_tag in icon_tags:
                icon_url = icon_tag.get('href')
                object_urls.append(icon_url)
                temp_icon = icon_url.split('/')[-1]
                object_names.append(temp_icon)

    
        # When given complete path to this function as argument it retrieves the object from the server. 
        def getNewObject(path):
            print("Inside getNewObject function")
            newClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newClientSocket.connect((serverHostname, serverPortNo))
            httpRequest = f"GET {path} HTTP/1.1\r\nAccept: text/html\r\nHost: {serverHostname}\r\n\r\n"        
            newClientSocket.send(httpRequest.encode())
            newResponse = b""
            while True:
                newData = newClientSocket.recv(1024)
                if not newData:
                    break
                newResponse += newData
            rmheaders = newResponse.split(b"\r\n\r\n")[0]
            modified_newResponse = newResponse[len(rmheaders)+4:]
            fileName = path.split("/")[-1]
            newFile = open(fileName, "wb")
            newFile.write(modified_newResponse)
            newFile.close()


        # just printing all the paths for debugging purpose.
        print(" object urls : ")
        print(object_urls)

    
        # now we create complete urls from the use of server hostname, server port no, elements of object urls and urlunsplit and append them in complete_urls
        complete_urls = []
        for url in object_urls:

            # scheme is http for our scenario
            scheme = "http"

            # netloc has the address:portno , portno is optional
            netloc = serverHostname + ":" + str(serverPortNo)
        
            # query and fragment can be added if there are any
            query = ''
            fragment = ''

            # final complete url is made using the above three and the path which I am referring to as url of object_urls.
            complete_urls.append(urlunsplit((scheme, netloc, url, query, fragment)))

    
        # just printing complete urls for debugging purpose
        print(" complete urls : ")
        print(complete_urls)

        # Working of ThreadPoolExecutor()
        # This is the part where we made parallel TCP connections using ThreadPoolExecutor(). The target funtion of executor is run concurrently
        # (continue) n number of times. This can be set in a parameter max_workers. So for example if max_workers=5 then there will be 5 parallel
        # instances of the function getNewObject in each of which I make a TCP connection so it becomes 5 parallel TCP connections.

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(getNewObject, complete_urls)
    

        # Finished time and its difference with start time is the latency.
        endTime = time.time()
        print()
        latency = endTime - startTime
        print(f" latency : {latency} seconds ")

# For connecting via proxy we are not making any parallel TCP connections as from proxy to server still there wouls be only one connection
# So in speedy client also the part to connect via proxy remains same as normal client.
else :
    print("Enter proxy IP : ")
    proxyIP = input()
    print("Enter port on which proxy is listening : ")
    proxyPort = int(input())
    print("Enter Server hostname or IP : ")
    serverIP = input()
    print("Enter port on which server is listening : ")
    serverPort = int(input())
    print("Enter the path of the file to be found on server : ")
    Path = input()


    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    clientSocket.connect((proxyIP, proxyPort))
    httpRequest = f"GET {Path} HTTP/1.0\r\nAccept: text/html\r\nHost: {proxyIP}\r\n\r\n"
    #Appending the server address for reference purpose to proxy
    httpRequest = httpRequest + serverIP + ":" + str(serverPort)
    clientSocket.send(httpRequest.encode())
    response = b""
    while True:
        data = clientSocket.recv(1024)
        if not data:
            break
        response += data
    
    

    print(response.decode("utf-8"))
    clientSocket.close()


    response1 = response.decode("utf-8")


    rmheaders = response1.split("\r\n\r\n")[0]
    modified_response = response1[len(rmheaders)+4:]

    

    print()


    def getobject(targethost, targetport, path):
         newclientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         newclientSocket.connect((targethost, targetport))
         newhttpRequest = f"GET {path} HTTP/1.0\r\nAccept: text/html\r\nHost: {targethost}\r\n\r\n"
         newhttpRequest = newhttpRequest + serverIP + ":" + str(serverPort)
         newclientSocket.send(newhttpRequest.encode())
         newresponse = b""
         while True:
            content = newclientSocket.recv(1024)
            if not content:
                break
            newresponse += content
         newclientSocket.close()
         return newresponse


    soup = BeautifulSoup(response1, "html.parser")

    img_tags = soup.find_all("img")
    print("Length of the Imge list : " + str(len(img_tags)))
    if len(img_tags)!=0:
       for img in img_tags:
           img_url = img["src"]
           temp = img_url.split('/')[-1]
           newresponse = getobject(proxyIP, proxyPort, img_url)
           #Code to display images
           rmheaders = newresponse.split(b"\r\n\r\n")[0]
           modified_newresponse = newresponse[len(rmheaders)+4:]
           newfile = open(temp, "wb")
           newfile.write(modified_newresponse)
           newfile.close()
           image = Image.open(BytesIO(modified_newresponse))
           image.show()



    script_tags = soup.find_all("script")
    if len(script_tags)!=0:
      for scripts in script_tags:
            if scripts.has_attr('src'):
                script_url = scripts["src"]
                temp_script = script_url.split('/')[-1]
                scriptresponse = getobject(proxyIP, proxyPort, script_url)
                rmheaders = scriptresponse.split(b"\r\n\r\n")[0]
                modified_scriptresponse = scriptresponse[len(rmheaders)+4:]
                newfile = open(temp_script, "wb")
                newfile.write(modified_scriptresponse)
                newfile.close()
                print(modified_scriptresponse.decode("utf-8"))
            else:
                inlineScript = scripts.get_text()
                print(f"Inline scipt content : {inlineScript}")



    icon_tags = soup.find_all("link", rel="icon")
    if len(icon_tags)!=0:
      for icon_tag in icon_tags:
            icon_url = icon_tag.get('href')
            temp_icon = icon_url.split('/')[-1]
            iconresponse = getobject(proxyIP, proxyPort, icon_url)
            rmheaders = iconresponse.split(b"\r\n\r\n")[0]
            modified_iconresponse = iconresponse[len(rmheaders)+4:]
            newfile = open(temp_icon, "wb")
            newfile.write(modified_iconresponse)
            newfile.close()
            icon = Image.open(BytesIO(modified_iconresponse))
            icon.show()




