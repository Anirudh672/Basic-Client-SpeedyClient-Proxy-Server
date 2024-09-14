**Basic Client, Proxy, Server and Speedy Web Client**

DIRECTIONS TO RUN CLIENT PROGRAM :
For client program we have two choices connecting directly to server or connecting via proxy both have different ways of giving input arguments.
To connect directly to server open terminal where Client.py is stored and enter "python3 Client.py hostname portno path" and press enter and then
select choice 0 when asked.
For example to connect to cse.iith.ac.in directly : " python3 Client.py cse.iith.ac.in 443 / "  Enter.
					          :  enter 0 (choice) and Enter


Before connecting Client via proxy make sure proxy server is running
To connect to cse.iith.ac.in via Proxy : " python3 Client.py " Enter
				       : Enter choice 1 and press enter
				       : Enter Proxy IP = "127.0.0.1"  Enter
				       : Enter port on which proxy is listening = "15000"   Enter
				       : Enter server hostname or IP = " cse.iith.ac.in "   Enter
				       : Enter port no of server = " 443 "	Enter
				       : Enter the file path = " / "	Enter


To connect to our simple web server using our simple web client:
Step 0 : Please change the IP address (in bind() in the program) to which we bind our socket because as you will be connected on different
	 network and you will be having different private IP (which changes with the network on which we are connected to), save it and then run 
	 the server program. Also please run everything from terminal only instead of using Visual Studio code. Use ifconfig command in linux to
	 get your private IP.
Step 1 : Make sure server is running
Step 2 : on terminal write command "python3 Client.py 127.0.0.1 20000 /index.html"
Step 3 : Enter choice 0.
NOTE if the file path is even slightly incomplete my server is not able to fetch it and it returns a 404 Not Found error message.



DIRECTIONS TO RUN AND CHECK SIMPLE WEB SERVER PROGRAM :
Step 0 : Please change the IP address (in bind() in the program) to which we bind our socket because as you will be connected on different
         network and you will be having different private IP (which changes with the network on which we are connected to), save it and then run
         the server program. Also please run everything from terminal only instead of using Visual Studio code. Use ifconfig command in linux to 
	 find your private IP. 
Step 1 : Run web server "python3 Server.py"
Step 2 : Open a web browser enter the url "127.0.0.1:20000/index.html" as my server is listening on port 20000
Step 3 : Web page will be displayed, 404 Not Found will be displayed in case file path is not correct.



DIRECTIONS TO RUN AND CHECK SIMPLE WEB PROXY :
Step 0 : Like in server program here also please change the proxyIP variable in program with the your private IP. Your private IP can be found 
	 using ifconfig command in linux.
Step 1 : Run simple web proxy "python3 Proxy.py"
Step 2 : All other steps like how to connect to proxy etc are explained in directions for client program.



DIRECTIONS TO RUN AND CHECK SPEEDY WEB CLIENT :
Step 1 : All the steps remain same as in directions for client program just change the python file name from "Client.py" to "SpeedyWebClient.py"


