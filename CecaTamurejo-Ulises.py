#!/usr/bin/python3

import socket
import urllib.request
import time


def stage0():
	socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#TCP Socket declaration
	socketTCP.connect(("atclab.esi.uclm.es", 2000))	#We connect to the address given
	msg = socketTCP.recv(1024)	#We store the received data
	if msg == "":	#If no data is received
		sys.exit(1)	#We exit the program
	else:
		print(msg.decode())	#We print the received data
		stage1(msg.decode().partition('¡')[0].strip() + " 2050")	#We get the identifier for the next stage
		socketTCP.close()	#We close the connection

def stage1(identifier):
	socketUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	#UDP Socket declaration
	socketUDP.bind(('', 2050))	#We bind the socket with the given address
	socketUDP.sendto(identifier.encode(), ("atclab.esi.uclm.es", 2000))	#We create the connection with the server through UDP
	msg, client = socketUDP.recvfrom(1024)	#We receive the msg
	print(msg.decode())	#We print the message
	stage2(("atclab.esi.uclm.es", int (msg.decode().partition('¡')[0].strip())))	#We call the next stage with the necessary identifier
	
def stage2(address):
	socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#TCP Socket declaration
	socketTCP.connect(address)	#We connect to the address given
	while True:	#While there are data
		time.sleep(.1)	#If we don't sleep we get EOF error
		operation = str(socketTCP.recv(8192).decode())	#We convert the received message to string
		if operation[0] == '(':	#We check if it's an operation
			result = operate(operation)	#We operate it
			print(operation + " = " + result)	#We print it
			socketTCP.send(result.encode())	#We send the result to the server
		else:
			socketTCP.close()	#We close the connection
			print(operation)	#We print next stage info
			stage3(operation[:5])	#We get the identifier for the next stage
			break
			
def stage3(identifier):
	urllib.request.urlretrieve("http://atclab.esi.uclm.es:5000/" + identifier, "file.txt")	#We retrieve the data with the identifier and we build the file.txt
	f = open('./file.txt', 'r')	#We open the file in the read mode
	print(f.read(2048))	#We print the content of the file
	f.close()	#We close the file
			
def operate(operation):
	while operation[0] == '(':	#While we don't have the result
		splitted = []	#To store the operation elements
		parenthesis = 1	#To know the most inner parenthesis position
		checker = True	#To deal with negative numbers

		for character in operation:	#This for is to put the whole operation elements into different indices from the array
			if character.isdigit():	#If we find a digit
				if splitted[-1].isdigit() or splitted[-1][0] == '-':	#And the previous digit is a number or negative number
					splitted[-1] += character	#We concatenate it to the current element
				else:	#If the previous value is not a digit
					splitted.append(character)	#We start storing the number in a new index
			elif character in '-+/*()':	#If the value is an operator or parenthesis
				splitted.append(character)	#We store it in a new index

		for i in reversed(splitted):	#This for is to find the most inner parenthesis position
			if i == '(':	#If we find the parenthesis
				parenthesis = len(splitted) - parenthesis	#We calculate its position
				break	#And exit the for
			else:	#Otherwise
				parenthesis = parenthesis + 1	#We increment its counter
				
		if (parenthesis+4 <= len(splitted)):	#This is to make sure we don't go out of the bounds of the array
			
			if splitted[parenthesis+3] == ')':	#This is for expressions with negative values which are stored as: '(','5','-4',')'
				checker = True	#We set the negative controller ON
			else:	#Otherwise
				checker = False	#We turn it OFF

			if splitted[parenthesis+2] == '-' and splitted[parenthesis+3][0] == '-':	#If we find an expression like '(','5','-','-5',')' due to negative values - * - is +
				splitted[parenthesis+3] = splitted[parenthesis+3][1:]	#We make the second value positive
				splitted[parenthesis+2] = '+'	#We change the main operator from - to +
			else:	#Otherwise
				if checker == True:	#If we have a normal expression with negative values like '(','5','-4',')'
					result = int(splitted[parenthesis+1]) + int(splitted[parenthesis+2])	#We sum their values
				else:	#Otherwise if there are no negative values we just calculate normally
					if splitted[parenthesis+2] == '*':
						result = int(splitted[parenthesis+1]) * int(splitted[parenthesis+3])
					elif splitted[parenthesis+2] == '/':
						result = int(splitted[parenthesis+1]) // int(splitted[parenthesis+3])
					elif splitted[parenthesis+2] == '+':
						result = int(splitted[parenthesis+1]) + int(splitted[parenthesis+3])
					splitted[parenthesis + 4] = ''	#We delete the ')' element. We have it here since we have an extra operator in this posibility

				splitted[parenthesis] = str(int(round(result)))	#We store the result were the most inner parenthesis were
				splitted[parenthesis + 1] = ''	#We delete the first operand
				splitted[parenthesis + 2] = ''	#We delete the next element which can be an operand or an operator
				splitted[parenthesis + 3] = ''	#We delete the next element which can be an operand or a parenthesis

		operation = ''.join(splitted)	#We store the final array into a string to repeat the process
			
	result = '(' + str(int(float(result))) + ')'	#We convert the result to the necessary format
	
	return result	#We return the result

def main():
	stage0()	#We call the stage 0

main()
