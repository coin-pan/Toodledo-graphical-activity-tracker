#!/usr/bin/python
# -*- coding: UTF-8 -*-
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

import unittest
import tracker
import copy



############################################################	
# TESTING importance
############################################################
class test_importance(unittest.TestCase):
	
	# non-completed task with no startdate, no due date, created at time 5
	taskA = {u'startdate': 0, u'added': 5, u'star': u'0', u'completed': 0, u'duedate': 0, u'priority': u'-1'}
	# non-completed task with no startdate, due date at 10, created at time 5
	taskB = {u'startdate': 0, u'added': 5, u'star': u'0', u'completed': 0, u'duedate': 10, u'priority': u'3'}
	# task with startdate at 7, due date at 10, created at time 5, completed at 15
	taskC = {u'startdate': 7, u'added': 5, u'star': u'0', u'completed': 15, u'duedate': 10, u'priority': u'3'}

	# non-completed task with no startdate, no due date will always return 1 if priority == -1, 2 if priority == 0 ...
	def test_importance_1(self):
		task = copy.copy(self.taskA)
		self.assertEqual(tracker.importance(task,10), 1)
		self.assertEqual(tracker.importance(task,15), 1)
		task['priority'] =u'0'
		self.assertEqual(tracker.importance(task,10), 2)
		self.assertEqual(tracker.importance(task,15), 2)
		task['priority'] =u'1'
		self.assertEqual(tracker.importance(task,10), 3)
		self.assertEqual(tracker.importance(task,15), 3)
		task['priority'] =u'2'
		self.assertEqual(tracker.importance(task,10), 4)
		self.assertEqual(tracker.importance(task,15), 4)
		task['priority'] =u'3'
		self.assertEqual(tracker.importance(task,10), 5)
		self.assertEqual(tracker.importance(task,15), 5)

	# star increases by 1 the importance
	# otherwise, identical to test_importance_1
	def test_importance_2(self):
		task = copy.copy(self.taskA)
		task['star'] =u'1'		
		self.assertEqual(tracker.importance(task,10), 2)
		self.assertEqual(tracker.importance(task,15), 2)
		task['priority'] =u'0'
		self.assertEqual(tracker.importance(task,10), 3)
		self.assertEqual(tracker.importance(task,15), 3)
		task['priority'] =u'1'
		self.assertEqual(tracker.importance(task,10), 4)
		self.assertEqual(tracker.importance(task,15), 4)
		task['priority'] =u'2'
		self.assertEqual(tracker.importance(task,10), 5)
		self.assertEqual(tracker.importance(task,15), 5)
		task['priority'] =u'3'
		self.assertEqual(tracker.importance(task,10), 6)
		self.assertEqual(tracker.importance(task,15), 6)


	# before creation, return -1
	# exactly on creation, don't return -1 if no startdate 
	def test_importance_3(self):
		task = copy.copy(self.taskB)
		self.assertEqual(tracker.importance(task,4), -1)
		self.assertEqual(tracker.importance(task,5)==-1,False)

	# before creation, return -1
	# exactly on creation with posterior startdate, return -1
	# between creation and startdate, return -1
	# exactly on startdate, don't return -1
	def test_importance_4(self):
		task = copy.copy(self.taskC)
		self.assertEqual(tracker.importance(task,4), -1)
		self.assertEqual(tracker.importance(task,5), -1)
		self.assertEqual(tracker.importance(task,6), -1)
		self.assertEqual(tracker.importance(task,7)==-1,False)

	# before completiondate, don't return -1
	# exactly on completiondate, don't return -1
	# after completiondate, return -1
	def test_importance_5(self):
		task = copy.copy(self.taskC)
		self.assertEqual(tracker.importance(task,14)==-1,False)
		self.assertEqual(tracker.importance(task,15)==-1,False)
		self.assertEqual(tracker.importance(task,16), -1)




if __name__ == '__main__':

	unittest.main()

