#!/usr/bin/env python
## ~ LIBRARY IMPORTATION ~ ##
from os import * #Bash commands
from subprocess import * #Bash commands
import curses #Terminal display
import math #Math Operations
import RPi.GPIO as GPIO #Buttons
import time #Time
#############################
## ~ START SUDO - DO NOT TOUCH ~ ##
sudo_password = '1234'
command = 'sudo -i'.split()
p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE,
          universal_newlines=True)
sudo_prompt = p.communicate(sudo_password + '\n')[1]
####################################
## ~ START CURSES ~ ##
stdscr = curses.initscr() #Standard Screen
curses.noecho() #Avoids printing input
curses.cbreak() #Character broken input
curses.curs_set(2) #Set cursor to block
stdscr.keypad(1) #Return characters value 
height = 19 #Terminal window height
width = 52 #Terminal window width
pad = curses.newpad(10000, 129) #Main Screen ~ Allows scrolling
######################
## ~ GLOBAL VARIABLES ~ ##
prints = 0
up = 17
enter = 22
down = 23
back = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(enter, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(back, GPIO.IN, pull_up_down=GPIO.PUD_UP)
##########################
## ~ FUNCTIONS ~ ##
def start(welcome):
	presentUSB = findUSB()
	if welcome:
		ctrprnt(' USB² - Trademark & Copyright 2016 ', curses.A_STANDOUT)
		stdprnt(' ')
	if len(presentUSB[0]) >= 2:
		mountUSB(presentUSB)
		choice = chooseUSB(presentUSB)
		transferFile(chooseFile(choice, listFile(choice, False)), presentUSB[1], choice)
		
	else:
		stdprnt('Connect the missing USB device(s). Press Enter')
		stdprnt(' ')
		while True:
			time.sleep(0.2)
			if GPIO.input(enter) == False:
				start(False)
			elif GPIO.input(back) == False:
				exit()
	finalize(findUSB())	
	
def finalize(presentUSB):
	prints = 0
	pad.clear()
	pad.refresh(0,0,0,0,height,width)
	unmountUSB(presentUSB)
	stdscr.keypad(0)
	curses.nocbreak()
	curses.echo()
	curses.endwin()
	GPIO.cleanup()
	system('kill python > n 2>&1; python app.py')

def escapeProg(*args):
	try:
		if len(args) == 1:
			unmountUSB(args[0])
			stdscr.keypad(0)
			curses.nocbreak()
			curses.echo()
			curses.endwin()
			system('reset')
			a = popen('pidof python').read()
			system('kill ' + a)
		else:
			file = args[0]
			choice = args[1]
			return transferFile(chooseFile(file[:len(file)-file[::-1].index('/')-1],listFile(file[:len(file)-file[::-1].index('/')-1], True)), findUSB()[1], choice)
	except ValueError:
		finalize(findUSB())

def findUSB():
	USB = []
	USBlist = []
	USBname = []
	USBwhole = []
	list = popen('sudo blkid').read().split('\n')
	list.pop(len(list)-1)
	for a in list:
		if 'TYPE="vfat"' in a and 'boot' not in a:
			USBwhole.append(a)
			USBlist.append(a[:a.index(': ')])
	for i in USBwhole:
		name = i[(i.index("L=") + 3):i.index("UUID")-2]
		USBname.append(name)
	USB.append(USBlist)
	USB.append(USBname)
	return USB

def mountUSB(USBdev):
	usb1name = USBdev[1][0]
	usb1path = USBdev[0][0]
	usb2name = USBdev[1][1]
	usb2path = USBdev[0][1]
	system('sudo mkdir '+"'"+usb1name+"'")
	system('sudo mount '+ usb1path + " '" + usb1name + "'")
	system('sudo mkdir '+"'"+usb2name+"'")
	system('sudo mount '+ usb2path + " '" + usb2name + "'")
	
def unmountUSB(presentUSB):
	system('sudo umount ' +"'"+presentUSB[1][0]+"'")
	system('sudo umount ' +"'"+presentUSB[1][1]+"'")
	system('rm -rf ' +"'"+presentUSB[1][0]+"'")
	system('rm -rf ' +"'"+presentUSB[1][1]+"'")
	
def chooseUSB(presentUSB):
	astdprnt('Choose a source: ', curses.A_BOLD)
	stdprnt(' ')
	tbprnt('>  ' + presentUSB[1][0])
	tbprnt('>  ' + presentUSB[1][1])
	top = curses.getsyx()[0]-2
	bottom = curses.getsyx()[0]-1
	stdprnt(' ')
	stdscr.move(top, 4)
	stdscr.refresh()
	while True:
		time.sleep(0.2)
		if GPIO.input(enter) != False:
			if GPIO.input(up) == False:
				if curses.getsyx()[0] > top:
					stdscr.move(curses.getsyx()[0] - 1, 4)
					stdscr.refresh()
			elif GPIO.input(down) == False: 
				if curses.getsyx()[0] < bottom:
					stdscr.move(curses.getsyx()[0] + 1, 4)
					stdscr.refresh()
			elif GPIO.input(back) == False:
				escapeProg(findUSB())
		elif curses.getsyx()[0] == top:
			listFile(presentUSB[1][0], True)
			return presentUSB[1][0]
		elif curses.getsyx()[0] == bottom:
			listFile(presentUSB[1][1], True)
			return presentUSB[1][1]

def listFile(folder, printFiles):
	global prints
	fileList = popen('ls ' + "'" + folder + "'").read().split('\n')
	fileList.remove('')
	if printFiles:
		refresh()
		ctrprnt(' ' + folder + ' ', curses.A_STANDOUT)
		if len(fileList) == 0:
			stdprnt('There are no existing files in ' + folder + '.')
			finalize(findUSB())
		else:
			p = 1
			for i in fileList:
				if path.isdir(folder+'/'+i):
					astdprnt('> ' + str(p) + '. ' + i, curses.A_BOLD)
				else:
					stdprnt('> ' + str(p) + '. ' + i)
				p+=1
			stdprnt(' ')
		return fileList
	else:
		return fileList
	
def chooseFile(folder, fileList):
	global prints
	bottom = curses.getsyx()[0]-2
	try:
		stdscr.move(bottom, 0)
		stdscr.refresh()
	except:
		pass
	pages = int(math.ceil(prints/height))
	topcornerY = (height*pages)
	filePos = len(fileList)
	while True:
		pos = pad.getyx()[0]
		time.sleep(0.2)
		if GPIO.input(enter) != False:
			if GPIO.input(up) == False:
				if filePos > 1:
					if curses.getsyx()[0] == 0:
						topcornerY -= height
						stdscr.move(height, 0)
						pad.refresh(topcornerY,0,0,0,height,width)
					else:
						stdscr.move(curses.getsyx()[0] - 1, 0)
						stdscr.refresh()
						filePos -= 1
			elif GPIO.input(down) == False:
				if filePos < len(fileList):
					if curses.getsyx()[0] == height:
						topcornerY += height
						stdscr.move(0, 0)
						pad.refresh(topcornerY,0,0,0,height,width)
						
					else:
						stdscr.move(curses.getsyx()[0] + 1, 0)
						stdscr.refresh()
						filePos += 1
			elif GPIO.input(back) == False:
				escapeProg(folder, fileList)
		else:
			break
	if path.isdir(folder+'/'+fileList[filePos-1]):
		refresh()
		astdprnt('Open folder '+fileList[filePos-1]+'?', curses.A_BOLD)
		stdprnt(' ')
		tbprnt('1) YES')
		tbprnt('0) NO')
		top = curses.getsyx()[0]-2
		bottom = curses.getsyx()[0]-1
		stdprnt(' ')
		stdscr.move(top, 4)
		stdscr.refresh()
		while True:
			time.sleep(0.2)
			if GPIO.input(enter) != False:
				if GPIO.input(up) == False:
					if curses.getsyx()[0] > top:
						stdscr.move(curses.getsyx()[0] - 1, 4)
						stdscr.refresh()
				elif GPIO.input(down) == False: 
					if curses.getsyx()[0] < bottom:
						stdscr.move(curses.getsyx()[0] + 1, 4)
						stdscr.refresh()
				elif GPIO.input(back) == False:
					escapeProg(folder, fileList)
			elif curses.getsyx()[0] == top:
				return chooseFile(folder + "/" + fileList[filePos-1], listFile(folder + "/" + fileList[filePos-1], True))
			elif curses.getsyx()[0] == bottom:
				return folder + "/" + fileList[filePos-1]
	else:
		return folder + "/" + fileList[filePos-1]
				
def transferFile(file, presentUSB, choice):
	refresh()
	if choice == presentUSB[0]:
		destination = presentUSB[1]
	else:
		destination = presentUSB[0]
	astdprnt('Do you want to send ' + file + '?', curses.A_BOLD)
	stdprnt(' ')
	tbprnt('1) YES')
	tbprnt('0) NO')
	top = curses.getsyx()[0]-2
	bottom = curses.getsyx()[0]-1
	stdscr.move(top, 4)
	stdscr.refresh()
	confirm = 0
	while True:
		time.sleep(0.2)
		if GPIO.input(enter) != False:
			if GPIO.input(up) == False: 
				if curses.getsyx()[0] > top:
					stdscr.move(curses.getsyx()[0] - 1, 4)
					stdscr.refresh()
			elif GPIO.input(down) == False: 
				if curses.getsyx()[0] < bottom:
					stdscr.move(curses.getsyx()[0] + 1, 4)
					stdscr.refresh()
			elif GPIO.input(back) == False:
				escapeProg(choice, listFile(choice,False))
		elif curses.getsyx()[0] == bottom:
			return transferFile(chooseFile(file[:len(file)-file[::-1].index('/')-1],listFile(file[:len(file)-file[::-1].index('/')-1], True)), findUSB()[1], choice)
		elif curses.getsyx()[0] == top:
			confirm = 1
			break
	if confirm == 1:
		stdprnt(' ')
		astdprnt('Do you want to Move or Copy?', curses.A_BOLD)
		stdprnt(' ')
		tbprnt('0) MOVE')
		tbprnt('1) COPY')
		copyMove = 0
		top = curses.getsyx()[0]-2
		bottom = curses.getsyx()[0]-1
		stdscr.move(top, 4)
		stdscr.refresh()
		while True:
			time.sleep(0.2)
			if GPIO.input(enter) != False:
				if GPIO.input(up) == False: 
					if curses.getsyx()[0] > top:
						stdscr.move(curses.getsyx()[0] - 1, 4)
						stdscr.refresh()
				elif GPIO.input(down) == False: 
					if curses.getsyx()[0] < bottom:
						stdscr.move(curses.getsyx()[0] + 1, 4)
						stdscr.refresh()
				elif GPIO.input(back) == False:
					finalize(findUSB())
			elif curses.getsyx()[0] == top:
				refresh()
				ctrprnt('Loading...', curses.A_BOLD)
				system("sudo mv '"+ file + "' '" + destination + "'")
				finalize(findUSB())
			elif curses.getsyx()[0] == bottom:
				refresh()
				ctrprnt('Loading...', curses.A_BOLD)
				if path.isdir(file):
					system("sudo cp -r '"+ file + "' '" + destination + "'")
				else:
					system("sudo cp '"+ file + "' '" + destination + "'")
				finalize(findUSB())
# ~ PRINTING ~ #
# Standard Print
def stdprnt(usrStr):
	global prints
	pad.addstr(prints,0,usrStr)
	pad.addstr(prints,width,'l')
	pad.refresh(0 + height*(prints/height),0,0,0,height,width)
	prints += 1
	stdscr.move(prints%height,0)
	stdscr.refresh()	
# Standard Print w/ Attribute
def astdprnt(usrStr, attr):
	global prints
	pad.addstr(prints,0,usrStr,attr)
	pad.addstr(prints,width,'l')
	pad.refresh(0 + height*(prints/height),0,0,0,height,width)
	prints += 1
	stdscr.move(prints%height,0)
	stdscr.refresh()
	
def ctrprnt(usrStr, attr):
	global prints
	if len(usrStr) < width:
		pad.addstr(prints,width/2 - len(usrStr)/2,usrStr,attr)
	else:
		pad.addstr(prints,0,usrStr,attr)
	pad.addstr(prints,width,'l')
	pad.refresh(0,0,0,0,height,width)
	prints += 1
	stdscr.move(prints%height,0)
	stdscr.refresh()
# Tab Print
def tbprnt(usrStr):
	global prints
	pad.addstr(prints,4,usrStr)
	pad.addstr(prints,width, 'l')
	pad.refresh(0 + height*(prints/height),0,0,0,height,width)
	prints += 1
	stdscr.move(prints%height,0)
	stdscr.refresh()	
# Tab Print w/ Attribute
def atbprnt(usrStr, attr):
	global prints
	pad.addstr(prints,4,usrStr,attr)
	pad.addstr(prints,width,'l')
	pad.refresh(0 + height*(prints/height),0,0,0,height,width)
	prints += 1
	stdscr.move(prints%height,0)
	stdscr.refresh()
# Refresh
def refresh():
	global prints
	prints = 0
	pad.clear()
	pad.refresh(0,0,0,0,height,width)
################
###################
start(True)
