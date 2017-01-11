#For the code to work - sudo pip install -U future

from __future__ import print_function
from __future__ import division
from builtins import input

# the above lines are meant for Python3 compatibility.
# they force the use of Python3 functionality for print(), 
# the integer division and input()
# mind your parentheses!

import subprocess
debug =0
def send_command(bashCommand):
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE) #, stderr=subprocess.PIPE)
	output = process.communicate()[0]
	return output
	
def check_ir():
	flag=0
	if 'lirc_dev' in open('/etc/modules').read():
		flag=1
		if debug:
			print ("lirc_dev in /etc/modules")
	
	if 'lirc_rpi gpio_in_pin=15' in open('/etc/modules').read():
		flag=1
		if debug:
			print ("lirc_rpi gpio_in_pin=15 in /etc/modules")
			
	if 'lirc_rpi gpio_in_pin=14' in open('/etc/modules').read():
		flag=1
		if debug:
			print ("lirc_rpi gpio_in_pin=14 in /etc/modules")
		
	if 'dtoverlay=lirc-rpi,gpio_in_pin=14' in open('/boot/config.txt').read():
		flag=1
		if debug:
			print ("dtoverlay=lirc-rpi,gpio_in_pin=14 in /boot/config.txt")
			
	if 'dtoverlay=lirc-rpi,gpio_in_pin=15' in open('/boot/config.txt').read():
		flag=1
		if debug:
			print ("dtoverlay=lirc-rpi,gpio_in_pin=15 in /boot/config.txt")
			
	if flag:
		return True
	return False
	
def replace_in_file(filename,replace_from,replace_to):
	f = open(filename,'r')
	filedata = f.read()
	f.close()

	newdata = filedata.replace(replace_from,replace_to)

	f = open(filename,'w')
	f.write(newdata)
	f.close()
		
def disable_ir():
	if check_ir()==True:
		if debug:
			print ("Disabling IR")
		replace_in_file('/etc/modules',"lirc_dev","")
		replace_in_file('/etc/modules',"lirc_rpi gpio_in_pin=15","")
		replace_in_file('/etc/modules',"lirc_rpi gpio_in_pin=14","")
		replace_in_file('/boot/config.txt',"dtoverlay=lirc-rpi,gpio_in_pin=14","")
		replace_in_file('/boot/config.txt',"dtoverlay=lirc-rpi,gpio_in_pin=15","")
	else:
		if debug:
			print ("IR already disabled")

def enable_ir():
	if 'lirc_dev' in open('/etc/modules').read():
		if debug:
			print ("lirc_dev already in /etc/modules")
	else:
		if debug:
			print ("lirc_dev added")
			
		with open('/etc/modules', 'a') as file:
			file.write('lirc_dev\n')
			
	if 'lirc_rpi gpio_in_pin=15' in open('/etc/modules').read():
		if debug:
			print ("lirc_rpi gpio_in_pin=15 already in /etc/modules")
	else:
		if debug:
			print ("lirc_rpi gpio_in_pin=15 added")
			
		with open('/etc/modules', 'a') as file:
			file.write('lirc_rpi gpio_in_pin=15\n')
	
	if 'dtoverlay=lirc-rpi,gpio_in_pin=15' in open('/boot/config.txt').read():
		if debug:
			print ("dtoverlay=lirc-rpi,gpio_in_pin=15 already in /boot/config.txt")
	else:
		if debug:
			print ("dtoverlay=lirc-rpi,gpio_in_pin=15 added")
			
		with open('/boot/config.txt', 'a') as file:
			file.write('dtoverlay=lirc-rpi,gpio_in_pin=15\n')
			
			
if __name__ == "__main__":
	checked = check_ir()
	print (checked)
	#disable_ir()
	#enable_ir()
