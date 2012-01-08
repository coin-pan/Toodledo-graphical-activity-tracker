#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#
#    Toodledo Activity Tracker & Plotter
#    Copyright (C) 2011  Marc Chauvet (marc DOT chauvet AT gmail DOT com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#



import urllib2
import re
import hashlib
import json
import getpass
import sys
import os
import datetime
import pylab
import time

# From joeld and crazy2be on http://stackoverflow.com/a/287944
class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = "\033[1m"


# From William Park on https://www.physics.rutgers.edu/~masud/computing/WPark_recipes_in_python.html
def conv(x, y):
	P, Q, N = len(x), len(y), len(x)+len(y)-1
	z = []
	for k in range(N):
		t, lower, upper = 0, max(0, k-(Q-1)), min(P-1, k)
		for i in range(lower, upper+1):
			t = t + x[i] * y[k-i]
		z.append(t)
	return z



version = "0.1"
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

# Calculates the importance a task had at a given time
def importance(task,timestamp):
	if timestamp < task['added']:
		return(-1)
	if timestamp < task['startdate']:
		return(-1)
	if (task['completed'] > 0) and (timestamp > task['completed']):
		return(-1)
	imp = 0
	
	if task['duedate'] > 0:
		days_before_deadline = (datetime.date.fromtimestamp(task['duedate'])- datetime.date.fromtimestamp(timestamp)).days
		if days_before_deadline < 0:
			imp = 6
		elif days_before_deadline == 0:
			imp = 5
		elif days_before_deadline == 1:
			imp = 3
		elif days_before_deadline <=6:
			imp = 2
		elif days_before_deadline <= 13:
			imp = 1
	
	imp += int(task['priority']) +2 + int(task['star'])
	return(imp)

# Calculates the meta-importance a task had at a given time
def meta_importance(task,timestamp):
	output={-1:-1,1:0,2:0,3:1,4:1,5:1,6:2,7:2,8:2,9:3,10:3,11:3,12:3}
	return(output[importance(task,timestamp)])






if __name__ == '__main__':

	print """
    Toodledo Activity Tracker & Plotter  Copyright (C) 2011  Marc Chauvet (marc DOT chauvet AT gmail DOT com)
    This program comes with ABSOLUTELY NO WARRANTY;
    This is free software, and you are welcome to redistribute it
    under certain conditions;
    
    For further information, please refer to the "LICENSE" file"""

	print bcolors.BOLD+"\n\n\nToodledo Activity Tracker & Plotter"+bcolors.ENDC+"\n\nProceeding with initial checks...\n"

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


	print "\n\nRetrieving all tasks..."
#	out = json.loads(urllib2.urlopen("http://api.toodledo.com/2/tasks/get.php?key="+get_key()+";comp=1").read())
	all_tasks = json.loads(urllib2.urlopen("http://api.toodledo.com/2/tasks/get.php?key="+get_key()+";fields=priority,duedate,star,startdate,added").read())[1:]
	print "Retrieved "+str(len(all_tasks))+" tasks"
	

	print "\n\nPreparing plotting..."

	last_completed_timestamp = max([t['completed'] for t in all_tasks])
	last_plotted_timestamp = last_completed_timestamp + (int((last_completed_timestamp-time.time())/(60*60*24))+1)*(60*60*24)
	first_plotted_timestamp = last_plotted_timestamp - number_of_plotted_days * (60*60*24)
	Plotted_timestamps = range(first_plotted_timestamp, last_plotted_timestamp +1, 60*60*24)

	d={}
	for timestamp in Plotted_timestamps:
		a = [meta_importance(task,timestamp) for task in all_tasks]
		d[timestamp]={}
		for x in [-1,0,1,2,3]:
			d[timestamp][x]=a.count(x)
	

	Meta_Imp3 = [d[timestamp][3] for timestamp in Plotted_timestamps]
	Meta_Imp2 = [d[timestamp][2]+d[timestamp][3] for timestamp in Plotted_timestamps]
	Meta_Imp1 = [d[timestamp][1]+d[timestamp][2]+d[timestamp][3] for timestamp in Plotted_timestamps]
	
	pylab.fill_between(Plotted_timestamps, 0, Meta_Imp3, facecolor='red')
	pylab.fill_between(Plotted_timestamps, Meta_Imp3, Meta_Imp2, facecolor='orange')
	pylab.fill_between(Plotted_timestamps, Meta_Imp2, Meta_Imp1, facecolor='green')
	pylab.xlim( min(Plotted_timestamps), max(Plotted_timestamps) )
	pylab.show()

	# Count per date the number of closed tasks on that date
#	per_day_activity={}
#	for d in [datetime.date.fromtimestamp(x[u'completed']) for x in all_tasks if x[u'completed']>0]:
#		try:
#			per_day_activity[d]+=1
#		except KeyError:
#			per_day_activity[d]=1
#
#	last_plotted_day=datetime.date.today()
#
	# Count per hour the number of closed tasks on that hour
	per_hour_activity={}
	for d in [x[u'completed'] / 3600 for x in all_tasks if x[u'completed']>0]:
		try:
			per_hour_activity[d]+=1
		except KeyError:
			per_hour_activity[d]=1

	last_plotted_hour=int(round(time.time()/3600))



	# List all the days to be plotted, from the oldest to today
#	X = [last_plotted_day-datetime.timedelta(x) for x in range(number_of_plotted_days,-1,-1)]

	# List all the hours to be plotted, from the oldest to today
	XX = range(min(per_hour_activity),last_plotted_hour)


	# Plot the number of tasks done each day
#	Tasks = []
#	for x in X:
#		try:
#			Tasks.append(per_day_activity[x])
#               except KeyError:
#			Tasks.append(0)


	# Plot the number of tasks done each hour
	Tasks = []
	for x in XX:
		try:
			Tasks.append(per_hour_activity[x])
                except KeyError:
			Tasks.append(None)

	
	# Minimum acceptable per day activity
	minimum_acceptable_per_day_activity = 1
	Minimum_Acceptable_Activity = [minimum_acceptable_per_day_activity for x in XX]


	print "Plotting prepared"

	print "\n\nPlotting..."

	pylab.bar([x for x in range(len(XX)) if Tasks[x]!=None], [t for t in Tasks if t!=None], width=3, bottom=0, color="g", align="center")

	pylab.plot(XX, Minimum_Acceptable_Activity, "r--")


	#pylab.bar([(x-last_plotted_day).days for x in X], Tasks, width=1, bottom=0, color="g", align="center")
#pylab.fill_between(X,Tasks,Minimum_Acceptable_Activity,where=[Tasks[i]>=Minimum_Acceptable_Activity[i] for i in range(len(Tasks))],facecolor='green', interpolate=True)
#pylab.fill_between(X,Tasks,Minimum_Acceptable_Activity,where=[Tasks[i]<Minimum_Acceptable_Activity[i] for i in range(len(Tasks))],facecolor='red', interpolate=True)
#	pylab.xlim( -number_of_plotted_days, 1 )  

	#pylab.savefig("plot_toodledo_activity.png")

	# Look at http://matplotlib.sourceforge.net/examples/api/path_patch_demo.html
	#http://matplotlib.sourceforge.net/users/path_tutorial.html



	pylab.show()


	print "\n\nBye bye\n\n"




