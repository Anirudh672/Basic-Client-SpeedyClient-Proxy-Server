# Simple web client program implemented using SSL socket so able to connect to https (port 443)

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
import time


# Asking user whether to connect to server via proxy or directly
print("How would you like to get the file? \n if directly from server : enter choice 0 \n if through proxy : enter choice 1 \n")
choice = int(input())


# If choice chosen is 0 then client directly connects to server
if choice==0:

    # Using sys.argv to take command line arguments
    no_of_args = len(sys.argv)
    print("Total number of arguments passed : ", no_of_args)


    # Way to pass arguments for directly connecting to server: python3 Client.py hostname portno path , press enter and choose choice 0 
    pythonFile = sys.argv[0]
    serverHostname = sys.argv[1]
    serverPortNo = int(sys.argv[2])
    Path = sys.argv[3]

    # Checking if the serverPortNo is 443, if it is then connect using SSL socket otherwise normal socket
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

        # After obtained response close the ssl_socket. Non-Persistent HTTP
        ssl_socket.close()
        

        # Decoded and stored the bytes response in response1, Split the headers using the \r\n\r\n
        response1 = response.decode("utf-8")

        # Headers would be 0th index after splitting
        rmheaders = response1.split("\r\n\r\n")[0]

        # Response code checking, responde code would be in first line of the response and 2nd word so used split()[1]
        resCode = int(rmheaders.split()[1])
        print(f"Response code : {resCode}")

        # Modified response is just the data without headers extracted from response
        modified_response = response1[len(rmheaders)+4:]


        # This function return various error messages based on the passed resCode as obtained earlier
        def resCodeInfo(code):
            if code==200:
                return f"{code} OK: Request was successful "
            elif code==404:
                return f"{code} Not Found: The requested resource does not exist"
            elif code==400:
                return f"{code} Bad Request: The request is invalid or improperly formatted"
            elif code==301:
                return f"{code} Moved Permanently: Resource has permanently moved to a new location"
            elif code==302:
                return f"{code} Found: Resource has temporarily moved to a different location"
            elif code==304:
                return f"{code} Not Modified: Resource has not been modified since the last request"
            else :
                return f"Unexpected Error"


        # error message obtained from the resCodeinfo function
        errormssg = resCodeInfo(resCode)


        # If the response code is not 200 then print the error message and exit as the index/base html file itself can't be obtained
        if resCode!=200:
            print(errormssg)
            exit(0)
        else :
            print(modified_response)
        
        splitPath = Path.split("/")[-1]
        checkForPath = splitPath.split(".")
        if checkForPath[0] != '' and (checkForPath[-1]!="HTML" or checkForPath[-1]!="html"):
             fileName = checkForPath[0].split('/')[-1] + "." + checkForPath[-1]
             newfile = open(fileName, "wb")
             newfile.write(modified_response.encode("utf-8"))
             newfile.close()
             exit(0)


        # This funtion makes the http request attaches the path (arguement to this function) in the http request, and receives the response
        def getobject(targethost, targetport, path):
            newclientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newsslSocket = ssl_context.wrap_socket(newclientSocket, server_hostname = targethost)
            newsslSocket.connect((targethost, targetport))
            newhttpRequest = f"GET {path} HTTP/1.0\r\nAccept: text/html\r\nHost: {targethost}\r\n\r\n"
            newsslSocket.send(newhttpRequest.encode())
            newresponse = b""
            while True:
                content = newsslSocket.recv(1024)
                if not content:
                    break
                newresponse += content
            newsslSocket.close()
            return newresponse


        # Created a soup object (created using BeautifulSoup) which is helpful in parsing the base html file.
        soup = BeautifulSoup(response1, "html.parser")


        # Parsed all the images using soup object, request for images only if len(img_tags)!=0 which means there are images to retrieve
        img_tags = soup.find_all("img")
        if len(img_tags)!=0:

            # We will request all images one by one
            for img in img_tags:

                # Get the img_url which is image path from
                img_url = img["src"]

                # temp here is the file name required so that we can open a new file with that name and save the content retrieved in it.
                temp = img_url.split('/')[-1]

                # Calling function to fetch the image and response stored in newresponse
                newresponse = getobject(serverHostname, 443, img_url)

                # Even to save the images in bytes format first the http response headers must be removed
                rmheaders = newresponse.split(b"\r\n\r\n")[0]

                # Checking the response code in the response just in case.
                resCode = int(rmheaders.split()[1])

                # modified newresponse is response content after removing headers.
                modified_newresponse = newresponse[len(rmheaders)+4:]
                errormssg = resCodeInfo(resCode)
                if resCode!=200:
                    print(errormssg)
                    continue
                else :
                    # Saving the response in a new file of name temp extracted eariler, "wb" is write bytes format
                    newfile = open(temp, "wb")
                    newfile.write(modified_newresponse)
                    newfile.close()

                    # Displaying the image
                    image = Image.open(BytesIO(modified_newresponse))
                    image.show()


        # Parsed all the scipts
        script_tags = soup.find_all("script")
        if len(script_tags)!=0:

            # Same as images requesting all the scripts one by one
            for scripts in script_tags:

                # Additional if beacuse in case of scripts there are inline scripts for which we don't need to request from server
                if scripts.has_attr('src'):

                    # Getting the paths (script_url) to pass them in getobject function
                    script_url = scripts["src"]

                    # temp_script is the name of the script
                    temp_script = script_url.split('/')[-1]

                    # Calling function to fetch the script and storing the response in scriptresponse
                    scriptresponse = getobject(serverHostname, 443, script_url)

                    # Again removing headers before saving it into a file
                    rmheaders = scriptresponse.split(b"\r\n\r\n")[0]

                    # Extracting the response code and checking it just in case
                    resCode = int(rmheaders.split()[1])

                    # Mpdified scriptresponse is script response without headers.
                    modified_scriptresponse = scriptresponse[len(rmheaders)+4:]

                    # Checking for resCodeInfo and getting error message in case
                    errormssg = resCodeInfo(resCode)
                    if resCode!=200:
                        print(errormssg)
                        continue
                    else :

                        # Opening and saving the content in that file
                        newfile = open(temp_script, "wb")
                        newfile.write(modified_scriptresponse)
                        newfile.close()
                        print(modified_scriptresponse.decode("utf-8"))
                else:
                    inlineScript = scripts.get_text()
                    print(f"Inline scipt content : {inlineScript}")


        # Parse icon tags all steps similar to as done when parsing images.
        icon_tags = soup.find_all("link", rel="icon")
        if len(icon_tags)!=0:
            for icon_tag in icon_tags:
                icon_url = icon_tag.get('href')
                temp_icon = icon_url.split('/')[-1]
                iconresponse = getobject(serverHostname, 443, icon_url)
                rmheaders = iconresponse.split(b"\r\n\r\n")[0]
                resCode = int(rmheaders.split()[1])
                modified_iconresponse = iconresponse[len(rmheaders)+4:]
                errormssg = resCodeInfo(resCode)
                if resCode!=200:
                        print(errormssg)
                        continue
                else :
                        newfile = open(temp_icon, "wb")
                        newfile.write(modified_iconresponse)
                        newfile.close()
                        icon = Image.open(BytesIO(modified_iconresponse))
                        icon.show()

        # Finished time of all retrieved objects calculated and thier difference is latency.
        endTime = time.time()
        latency = endTime - startTime
        print(f"latency Non-Persistent HTTP : {latency} seconds")


    # if the serverPortNo is not 443 then connect using a normal socket, all other code remains same just that we connect using normal socket
    else :       
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverHostname, serverPortNo))
        httpRequest = f"GET {Path} HTTP/1.0\r\nAccept: text/html\r\nHost: {serverHostname}\r\n\r\n"
        startTime = time.time()
        clientSocket.send(httpRequest.encode())
        response = b""
        while True:
            data = clientSocket.recv(1024)
            if not data:
                break
            response += data

        clientSocket.close()


        response1 = response.decode("utf-8")
        rmheaders = response1.split("\r\n\r\n")[0]
        resCode = int(rmheaders.split()[1])
        modified_response = response1[len(rmheaders)+4:]
    

        def resCodeInfo(code):
            if code==200:
                return f"{code} OK: Request was successful "
            elif code==404:
                return f"{code} Not Found: The requested resource does not exist"
            elif code==400:
                return f"{code} Bad Request: The request is invalid or improperly formatted"
            elif code==301:
                return f"{code} Moved Permanently: Resource has permanently moved to a new location"
            elif code==302:
                return f"{code} Found: Resource has temporarily moved to a different location"
            elif code==304:
                return f"{code} Not Modified: Resource has not been modified since the last request"
            else :
                return f"Unexpected Error"


        errormssg = resCodeInfo(resCode)
        if resCode!=200:
            print(errormssg)
            exit(0)
        else :
            print(modified_response)


        def getobject(targethost, targetport, path):
            newclientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newclientSocket.connect((targethost, targetport))
            newhttpRequest = f"GET {path} HTTP/1.0\r\nAccept: text/html\r\nHost: {targethost}\r\n\r\n"
            newclientSocket.send(newhttpRequest.encode())
            newresponse = b""
            while True:
                content = newclientSocket.recv(1024)
                if not content:
                    break
                newresponse += content
            return newresponse

        soup = BeautifulSoup(response1, "html.parser")

        img_tags = soup.find_all("img")
        print("Length of the Imge list : " + str(len(img_tags)))
        if len(img_tags)!=0:
            for img in img_tags:
                img_url = img["src"]
                temp = img_url.split('/')[-1]
                newresponse = getobject(serverhostname, serverport, new_path)
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
                    scriptresponse = getobject(serverHostname, 80, script_url)
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
                iconresponse = getobject(serverHostname, 80, icon_url)
                rmheaders = iconresponse.split(b"\r\n\r\n")[0]
                modified_iconresponse = iconresponse[len(rmheaders)+4:]
                newfile = open(temp_icon, "wb")
                newfile.write(modified_iconresponse)
                newfile.close()
                icon = Image.open(BytesIO(modified_iconresponse))
                icon.show()

        endTime = time.time()
        latency = endTime - startTime
        print(f"latency Non-Persistent Not Parallel : {latency} ")


# If the user choice is 1 then we retrieve all base html and objects through proxy.
else :

    # Taking input for proxy, note for passing arguments in proxy they are not command line they are more gui based 
    # So for connecting through proxy use : python3 Client.py , press enter and enter choice 1 and then enter the arguments as asked.
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


    # Client to Proxy connectioin cannot be made on SSL because our proxy is not running on port 443. 
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((proxyIP, proxyPort))


    # Starting the start time before sending the first http request, for latency comparisons.  
    startTime = time.time()


    # httpRequest to connect for the first time to that web page and retrieve the base html file
    httpRequest = f"GET {Path} HTTP/1.0\r\nAccept: text/html\r\nHost: {proxyIP}\r\n\r\n"


    # Appending the serverIP and serverPort in the request for reference purpose at proxy side so that proxy gets to know the server address
    httpRequest = httpRequest + serverIP + ":" + str(serverPort)
    clientSocket.send(httpRequest.encode())
    

    # All the other procedure to retieve the response remains same as when trying to get objects directly from the server.
    response = b""
    while True:
        data = clientSocket.recv(1024)
        if not data:
            break
        response += data

    clientSocket.close()

    response1 = response.decode("utf-8")


    rmheaders = response1.split("\r\n\r\n")[0]
    modified_response = response1[len(rmheaders)+4:]

    resCode = int(rmheaders.split()[1])

    def resCodeInfo(code):
        if code==200:
            return f"{code} OK: Request was successful "
        elif code==404:
            return f"{code} Not Found: The requested resource does not exist"
        elif code==400:
            return f"{code} Bad Request: The request is invalid or improperly formatted"
        elif code==301:
            return f"{code} Moved Permanently: Resource has permanently moved to a new location"
        elif code==302:
            return f"{code} Found: Resource has temporarily moved to a different location"
        elif code==304:
            return f"{code} Not Modified: Resource has not been modified since the last request"
        else :
            return f"Unexpected Error"

    print()

    errormssg = resCodeInfo(resCode)
    if resCode!=200:
        print(errormssg)
        exit(0)
    else :
        print(modified_response)

    splitPath = Path.split("/")[-1]
    checkForPath = splitPath.split(".")
    if checkForPath[0] != '' and (checkForPath[-1]!="HTML" or checkForPath[-1]!="html"):
        fileName = checkForPath[0].split('/')[-1] + "." + checkForPath[-1]
        newfile = open(fileName, "wb")
        newfile.write(modified_response.encode("utf-8"))
        newfile.close()
        exit(0)

    
    # getobject funtion in proxy is different only in way that we append serverAddress for the reference of proxy 
    # Also there is no ssl in proxy rest all remains same.
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
           rmheaders = newresponse.split(b"\r\n\r\n")[0]
           resCode = int(rmheaders.split()[1])
           modified_newresponse = newresponse[len(rmheaders)+4:]
           errormssg = resCodeInfo(resCode)
           if resCode!=200:
               print(errormssg)
               continue
           else:
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
                resCode = int(rmheaders.split()[1])
                modified_scriptresponse = scriptresponse[len(rmheaders)+4:]
                errormssg = resCodeInfo(resCode)
                if resCode!=200:
                    print(errormssg)
                    continue
                else:
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
            resCode = int(rmheaders.split()[1])
            modified_iconresponse = iconresponse[len(rmheaders)+4:]
            errormssg = resCodeInfo(resCode)
            if resCode!=200:
                print(errormssg)
                continue
            else:
                newfile = open(temp_icon, "wb")
                newfile.write(modified_iconresponse)
                newfile.close()
                icon = Image.open(BytesIO(modified_iconresponse))
                icon.show()

    # Finished time and its difference with start time is the latency.
    endTime = time.time()
    latency = endTime-startTime
    print(f"latency Non-Persistent HTTP with proxy in between : {latency} seconds")

    # End of Client part....
