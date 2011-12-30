#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib2
import re
import hashlib
import json
import getpass
import sys
import os
import datetime
import pylab

# From joeld and crazy2be on http://stackoverflow.com/questions/287871/print-in-terminal-with-colors-using-python
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = "\033[1m"



version = "0"
number_of_plotted_days = 30

def remove_comments(string):
	return(re.sub("#.*\n","",string))



def isOK_apptoken():
	try:
		remove_comments("".join(open("apptoken.dat","r").readlines())).rstrip("\n")
		return True
	except IOError as e:
		# "apptoken.dat" file doesn't exist
		return False

def isOK_appid():
	try:
		remove_comments("".join(open("appid.dat","r").readlines())).rstrip("\n")
		return True
	except IOError as e:
		# "appid.dat" file doesn't exist, need to create one
		return False

def isOK_hashedpassword():
	try:
		remove_comments("".join(open("hashedpassword.dat","r").readlines())).rstrip("\n")
		return True
	except IOError as e:
		# "hasedpassword.dat" file doesn't exist
		return False

def isOK_userid():
	try:
		remove_comments("".join(open("userid.dat","r").readlines())).rstrip("\n")
		return True
	except IOError as e:
		# "userid.dat" file doesn't exist, need to create one
		return False


def get_hashedpassword():
	return remove_comments("".join(open("hashedpassword.dat","r").readlines())).rstrip("\n")

def get_userid():
	return remove_comments("".join(open("userid.dat","r").readlines())).rstrip("\n")

def get_sessiontoken():
	return remove_comments("".join(open("sessiontoken.dat","r").readlines())).rstrip("\n")

def get_key():
	return remove_comments("".join(open("key.dat","r").readlines())).rstrip("\n")


def lookup_userid(email,password):
	signature = hashlib.md5(email + apptoken).hexdigest()
	out = json.loads(urllib2.urlopen("http://api.toodledo.com/2/account/lookup.php?appid="+appid+";sig="+signature+";email="+email+";pass="+password).read())
	userid = out["userid"]
	return userid

def lookup_sessiontoken(userid, appid, apptoken, version):
	signature = hashlib.md5(userid + apptoken).hexdigest()
	out = json.loads(urllib2.urlopen("http://api.toodledo.com/2/account/token.php?userid="+userid+";appid="+appid+";vers="+version+";sig="+signature).read())
	sessiontoken = out["token"]
	return sessiontoken



if __name__ == '__main__':

	print bcolors.BOLD+"\nToodledo Activity Representer"+bcolors.ENDC+"\n\nProceeding with initial checks...\n"

	padding = 20
	print "Application ID: ".ljust(padding) + ((bcolors.OKGREEN+"[OK]") if isOK_appid() else (bcolors.FAIL+bcolors.BOLD+"[NOK]")) + bcolors.ENDC
	print "Application token: ".ljust(padding) + ((bcolors.OKGREEN+"[OK]") if isOK_apptoken() else (bcolors.FAIL+bcolors.BOLD+"[NOK]")) + bcolors.ENDC

	if not (isOK_appid() and isOK_apptoken()):
		exit_message = """The application ID and the application token provided by Toodledo need to be provided to this script.
They should appear in files entitled respectively "appid.dat" and "apptoken.dat", located in the same folder as the script."""
		sys.exit(exit_message)

	appid = remove_comments("".join(open("appid.dat","r").readlines())).rstrip("\n")
	apptoken = remove_comments("".join(open("apptoken.dat","r").readlines())).rstrip("\n")


	print "Hashed password: ".ljust(padding) + ((bcolors.OKGREEN+"[OK]") if isOK_hashedpassword() else (bcolors.FAIL+bcolors.BOLD+"[NOK]")) + bcolors.ENDC
	print "User ID: ".ljust(padding) + ((bcolors.OKGREEN+"[OK]") if isOK_userid() else (bcolors.FAIL+bcolors.BOLD+"[NOK]")) + bcolors.ENDC
	
	if not (isOK_hashedpassword() and isOK_userid()):
		print """
Your hashed Toodledo password and/or your Toodledo user ID are currently unknown.
But they are required to download all your completed tasks. These pieces of information
should appear in files entitled respectively "hashedpassword.dat" and "userid.dat",
located in the same folder as the script. The script will now offer to input these pieces
of information in the relevant files for you. But before doing so, you should be aware that:
* your password will be stored as a MD5 hash in your script folder
  (but it will not be stored in plain text);
* your password will be sent unencrypted over HTTP to the Toodledo server to get your userID;
* you are encouraged to look into the source code of this script to ensure that
  nothing bad is done with the information you will enter;
* you can do all this manually by:
	- killing the script now
	- putting in a file entitled "hashedpassword.dat" the MD5 hash of your Toodledo password
	- putting in a file entitled "userid.dat" your Toodledo user ID
	  (found on http://www.toodledo.com/account_edit.php)
	- launching this script again."""
		email = raw_input("\nIf you wish the script to do the job for you, please insert your Toodledo email address >\n")
		password = getpass.getpass("\nNow, please insert your Toodledo password (only stored as a MD5 hash) >\n")
		open("userid.dat","w").write(lookup_userid(email,password))
		open("hashedpassword.dat","w").write(hashlib.md5(password).hexdigest())
		print "\nHashed password: ".ljust(padding) + ((bcolors.OKGREEN+"[OK]") if isOK_hashedpassword() else (bcolors.FAIL+bcolors.BOLD+"[NOK]")) + bcolors.ENDC
		print "User ID: ".ljust(padding) + ((bcolors.OKGREEN+"[OK]") if isOK_userid() else (bcolors.FAIL+bcolors.BOLD+"[NOK]")) + bcolors.ENDC
	
		if not (isOK_hashedpassword() and isOK_userid()):
			exit_message = """Ending script as there is still an issue with your hashed Toodledo password and/or your Toodledo user ID"""
		sys.exit(exit_message)


	try:
		os.remove('sessiontoken.dat')
		print "Session token: ".ljust(padding) + bcolors.OKGREEN + "[Purged]" + bcolors.ENDC
	except OSError as e:
		print "Session token: ".ljust(padding) + bcolors.OKGREEN + "[Inexistent]" + bcolors.ENDC
	open("sessiontoken.dat","w").write(lookup_sessiontoken(get_userid(), appid, apptoken, version))
	print "Session token: ".ljust(padding) + bcolors.OKGREEN + "[OK]" + bcolors.ENDC

	try:
		os.remove('key.dat')
		print "Key: ".ljust(padding) + bcolors.OKGREEN + "[Purged]" + bcolors.ENDC
	except OSError as e:
		print "Key: ".ljust(padding) + bcolors.OKGREEN + "[Inexistent]" + bcolors.ENDC
	open("key.dat","w").write(hashlib.md5(get_hashedpassword() + apptoken + get_sessiontoken()).hexdigest())
	print "Key: ".ljust(padding) + bcolors.OKGREEN + "[OK]" + bcolors.ENDC


	print "\n\nRetrieving completed tasks... "
	out = json.loads(urllib2.urlopen("http://api.toodledo.com/2/tasks/get.php?key="+get_key()+";comp=1").read())
	print "Retrieved "+str(len(out)-1)+" completed tasks"
	

	# Count per date the number of closed tasks on that date
	per_day_activity={}
	for d in [datetime.date.fromtimestamp(x[u'completed']) for x in out[1:]]:
		try:
			per_day_activity[d]+=1
		except KeyError:
			per_day_activity[d]=1



	last_plotted_day=datetime.date.today()


	# List all the days to be plotted, from the oldest to today
	X = [last_plotted_day-datetime.timedelta(x) for x in range(number_of_plotted_days,-1,-1)]

	# Plot the number of tasks done each day
	Tasks = []
	for x in X:
		try:
			Tasks.append(per_day_activity[x])
                except KeyError:
			Tasks.append(0)
	
	# Minimum acceptable per day activity
	minimum_acceptable_per_day_activity = 1
	Minimum_Acceptable_Activity = [minimum_acceptable_per_day_activity for x in X]



	pylab.plot(X, Minimum_Acceptable_Activity, "r--")
	#pylab.bar([(x-last_plotted_day).days for x in X], Tasks, width=1, bottom=0, color="g", align="center")
	pylab.fill_between(X,Tasks,Minimum_Acceptable_Activity,where=[Tasks[i]>=Minimum_Acceptable_Activity[i] for i in range(len(Tasks))],facecolor='green', interpolate=True)
	pylab.fill_between(X,Tasks,Minimum_Acceptable_Activity,where=[Tasks[i]<Minimum_Acceptable_Activity[i] for i in range(len(Tasks))],facecolor='red', interpolate=True)
#	pylab.xlim( -number_of_plotted_days, 1 )  
	pylab.show()
	#pylab.savefig("plot_toodledo_activity.png")

	# Look at http://matplotlib.sourceforge.net/examples/api/path_patch_demo.html
	#http://matplotlib.sourceforge.net/users/path_tutorial.html











