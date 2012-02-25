##Patrick O'Shea
##CS450
##10/1/2010
##HW2 Pt3
##This is a kernel scheduling simulator developed for my Operating Systems coursework

import os.path
import sys
from collections import deque

BLOCK = 500
blocktimer = 0
waittimer = 0
q1time = 0
q2time = 0
q3time = 0

###############Create class for containing process info
class Process:
	def __init__(self, procNum, numBursts, bursts):
		self.procNum=procNum
		self.numBursts=numBursts
		self.bursts = bursts
		self.turnaround = 0
		self.wait = 0
		self.numWaits = 0
		self.avgWait = 0
		self.qSwitches = 0
		self.preempted = 0		#preemption flag
		self.originalBurst = bursts	#bursts original size (for preemption tracking)
		self.burstsCompleted = 0	#running ms count

###############get file arguments
configFileName = sys.argv[1]
execFileName = sys.argv[2]


###############check for config file
if os.path.exists(configFileName):
	configFile = open(configFileName, "r")
else:
	print "Error opening config file"
	exit(1)

###############check for execute file
if os.path.exists(execFileName):
	#print "opening exec file"
	execFile = open(execFileName, "r")
else:
	print "Error openening execute file"
	exit(1)


###############read the config file
#1st read context switching var
cstline = configFile.readline()
cstline = cstline.split(' ')
cst = float(cstline[1])
#print "CST ", cst

#2nd read Queue setups
q1Line = configFile.readline()
q1Line = q1Line.split(' ')
q1 = q1Line[1]
q1 = q1.split('.')
q1 = int(q1[0])
q1Percent = float(q1Line[2])
#print  "q1 = ", q1, " q1percent = ", q1Percent

q2Line = configFile.readline()
q2Line = q2Line.split(' ')
q2 = q2Line[1]
q2 = q2.split('.')
q2 = int(q2[0])
q2Percent = float(q2Line[2])
#print  "q2 = ", q2, " q2percent = ", q2Percent

q3Line = configFile.readline()
q3Line = q3Line.split(' ')
q3 = q3Line[1]
q3 = q3.split('.')
q3 = int(q3[0])
q3Percent = float(q3Line[2])
#print  "q3 = ", q3, " q3percent = ", q3Percent

#Make sure aggregate percentage is 100
if (q1Percent+q2Percent+q3Percent) != 1.0:
	print "\nQueue percentages must equal 100"
	exit(1)


###############Read the execute file into Process class objects
processes = []  #list of Process objects
procNum = 0
for line in execFile:
	tmp = line.split(':')
	tmp = tmp[1]
	tmp = tmp.strip()
	tmp = tmp.split(' \n')
	tmp = tmp[0]	
	tmp = tmp.split(',')

	#get the cpu bursts
	bursts = deque()
	for x in tmp:
		bursts.append(x)
	
	#create Process object
	process = Process(procNum, len(bursts), bursts)
  	processes.append(process)
	procNum=procNum+1	
	#print "procNum ", process.procNum, " numBursts ", process.numBursts, " bursts ", process.bursts


###############Simulation operations


###enqueue initial processes and init queues 2 & 3
queue1 = deque()
for process in processes:
	queue1.append(process)
queue2 = deque()
queue3 = deque()
completedProcesses = deque()  #list of processes that have completed execution 


prevProc=1	# initially set to 1 to catch first context switch into p0
while len(queue1) > 0 or len(queue2) > 0 or len(queue3) > 0 and blocktimer < 500:
		
	
	###Queue1
	while len(queue1) > 0 and q1time<BLOCK*q1Percent:
		#get first process in queue, do work
		tmp = queue1.popleft()
		
		
		#get burst in process' burst queue
		tmpBurst = int(tmp.bursts.popleft())
		
		
		if tmpBurst == q1:
			#completes this quantum
			blocktimer=blocktimer+q1
			waittimer = waittimer+q1
			tmp.burstsCompleted=tmp.burstsCompleted+q1;


			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				if blocktimer-q1!=0:
					tmp.numWaits=tmp.numWaits+1
			if tmp.numWaits!=0:
				tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
						
			tmp.turnaround = blocktimer	
			
			#CST tallying
			if tmp.procNum != prevProc:  ##no more work?  processes or bursts
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum


			#are there more bursts?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50	#IO burst
				blocktimer=blocktimer+50
				queue1.append(tmp)		#put back at end of queue RR		
				
			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			
			q1time=q1time+q1
			
		elif tmpBurst < q1:  	#completes in less than the quantum
			blocktimer=blocktimer+tmpBurst
			waittimer=waittimer+tmpBurst
			tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst;

			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				#if len(tmp.bursts)>0 or tmpBurst>0:
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
				
						
			tmp.turnaround = blocktimer	
			
			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst			
			prevProc=tmp.procNum
			
			#are there more bursts?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50	#IO burst
				blocktimer=blocktimer+50
				queue1.append(tmp)		#put back at end of queue RR			  		
				
			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			
			q1time=q1time+q1
			

		else:
			#moves to queue2
			blocktimer=blocktimer+q1
			waittimer=waittimer+q1
			if tmpBurst < q1:
				tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst
			else:
				tmp.burstsCompleted=tmp.burstsCompleted+q1


			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
			
			tmp.turnaround = blocktimer

			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum
			
			tmpBurst = tmpBurst-q1	#updates the burst length
			tmp.bursts.appendleft(tmpBurst) #places it back in front of burst queue
			tmp.qSwitches=tmp.qSwitches+1  #update number of switches
			tmp.preempted=1
			queue2.append(tmp) 		#append to end of queue2
			q1time=q1time+q1		
			

	###Queue2
	while len(queue2) > 0 and q2time<BLOCK*q2Percent:
		#get first process in queue, do work
		tmp = queue2.popleft()

		#get burst in process' burst queue
		tmpBurst = int(tmp.bursts.popleft())
		
		
		
		if tmpBurst == q2:
			#completes this quanta
			blocktimer=blocktimer+q2
			waittimer=waittimer+q2
			tmp.burstsCompleted=tmp.burstsCompleted+q2;

			if tmpBurst < q2:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q2

			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				#if len(tmp.bursts)>0 or tmpBurst>0:
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
						
			tmp.turnaround = blocktimer	
			
			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum

			#reset preemption
			if tmpBurst==0 and tmp.preempted!=0:
				tmp.preempted = 0
			

			#are there more bursts?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50	#IO burst
				blocktimer=blocktimer+50
				queue2.append(tmp)		#put back at end of queue RR		
				
			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			q2time=q2time+q2
			
	

		elif tmp.preempted == 1 and (q2-tmpBurst) > (q2*.25):  #when it's been preempted
			blocktimer=blocktimer+tmpBurst
			waittimer=waittimer+tmpBurst
			tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst;
	
			if tmpBurst < q2:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q2	
			
			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
			
			
			
			tmp.turnaround = blocktimer
			
			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum

			
			
		
			#reset preemption
			if tmpBurst==0 and tmp.preempted!=0:
				tmp.preempted = 0
			
			#are there more bursts?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50
				blocktimer=blocktimer+50
				queue2.append(tmp)		#put back at end of queue RR		
				
			else:					#the process has completed
				completedProcesses.appendleft(tmp)

			q2time=q2time+q2
			
			

	
		elif tmp.preempted == 0 and (q2-tmpBurst) > (q2*.25):  #hasn't been preempted, move up
			blocktimer=blocktimer+tmpBurst
			waittimer=waittimer+tmpBurst
			tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst;

			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
			
			if tmpBurst < q2:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q2
			

			tmp.turnaround = blocktimer

			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum
			
			

			#are there more bursts?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50	#IO burst
				blocktimer=blocktimer+50
				if tmpBurst !=0:
					tmp.bursts.appendleft(tmpBurst) #places it back in front of burst queue
				tmp.qSwitches=tmp.qSwitches+1  #update number of switches
				queue1.append(tmp)		#put back at end of queue RR		
			
			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			q2time=q2time+q2
	
		else: 						   #else moved to queue3
			#moves to queue3
			blocktimer=blocktimer+q2
			waittimer=waittimer+q2
			if tmpBurst < q2:
				tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst
			else:
				tmp.burstsCompleted=tmp.burstsCompleted+q2


			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
 				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)

			
			if tmpBurst < q2:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q2

			tmp.turnaround = blocktimer

			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst			
			prevProc=tmp.procNum
			
			
			tmp.bursts.appendleft(tmpBurst) #places it back in front of burst queue
			tmp.qSwitches=tmp.qSwitches+1  #update number of switches
			tmp.preempted=1
			queue3.append(tmp) 		#append to end of queue2
			q2time=q2time+q2		
			


	###Queue3
	while (len(queue3) > 0 and q3time<BLOCK*q3Percent) or (len(queue3) > 0 and (len(queue1)==0 and len(queue2)==0)):

		#get first process in queue, do work
		tmp = queue3.popleft()

		#get first burst in process' burst queue
		tmpBurst = int(tmp.bursts.popleft())

		if tmp.preempted == 0 and (q3-tmpBurst) > (q3*.25):	#move up a queue
			blocktimer=blocktimer+tmpBurst
			waittimer=waittimer+tmpBurst
			tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst;

			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
			
			if tmpBurst < q3:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q3
			
			tmp.turnaround = blocktimer

			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum
			
			

			#are there more bursts?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50	#IO burst
				blocktimer=blocktimer+50
				if tmpBurst !=0:
					tmp.bursts.appendleft(tmpBurst) #places it back in front of burst queue
				tmp.qSwitches=tmp.qSwitches+1  #update number of switches
				queue2.append(tmp)		#put back at end of queue RR		
			
			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			q3time=q3time+q3

		elif tmp.preempted == 1 and (q3-tmpBurst) > (q3*.25):  #preempted don't move up
			blocktimer=blocktimer+tmpBurst
			waittimer=waittimer+tmpBurst
			if tmpBurst < q3:
				tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst
			else:
				tmp.burstsCompleted=tmp.burstsCompleted+q3

			
	
			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
			
			if tmpBurst < q3:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q3

			tmp.turnaround = blocktimer
			
			#CST tallying
			if tmp.procNum != prevProc:
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst
			prevProc=tmp.procNum


			
			

			#reset preemption
			if tmpBurst==0 and tmp.preempted!=0:
				tmp.preempted = 0
				

			#are there more bursts?
			if len(tmp.bursts)!= 0:
				queue3.append(tmp)		#put back at end of queue RR		
				tmp.turnaround = tmp.turnaround+50	#IO burst
				blocktimer=blocktimer+50
				
				
			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			q3time=q3time+q3
		else:
			#may not complete this quantum
			blocktimer=blocktimer+q3
			waittimer=waittimer+q3
			if tmpBurst < q3:
				tmp.burstsCompleted=tmp.burstsCompleted+tmpBurst
			else:
				tmp.burstsCompleted=tmp.burstsCompleted+q3

			if tmpBurst < q3:
				tmpBurst=tmpBurst-tmpBurst
			else:
				tmpBurst=tmpBurst-q3

			if blocktimer != 0:
				tmp.wait = waittimer-tmp.burstsCompleted
				tmp.numWaits=tmp.numWaits+1
			tmp.avgWait=float(tmp.wait)/float(tmp.numWaits)
					
			tmp.turnaround = blocktimer	
			
			#CST tallying
			if tmp.procNum != prevProc:			
				tmp.turnaround=tmp.turnaround+cst
				blocktimer=blocktimer+cst			
			prevProc=tmp.procNum


			#need more tests to see if burst completed or finished
			#are there more bursts or cycles?
			if len(tmp.bursts)!= 0:
				tmp.turnaround=tmp.turnaround+50	#IO burst
				blocktimer = blocktimer+50
				queue3.append(tmp)		#put back at end of queue RR		
				
			elif tmpBurst>0:
				tmp.bursts.appendleft(tmpBurst) #places it back in front of burst queue
				queue3.append(tmp)
				

			else:					#the process has completed
				completedProcesses.appendleft(tmp)
			
			q3time=q3time+q3
			


	#####reset block timer
	if blocktimer == 500 and len(queue1)>0 and len(queue2)>0 and len(queue3)>0:
		blocktimer = 0
		q1timer = 0
		q2timer = 0
		q3timer = 0


###############once out of the queue loops, output info

#sort the queue
n = 0
sorted = []
for x in range(len(completedProcesses)):
	for process in completedProcesses:
		if process.procNum == x:
			sorted.append(process)
	


for process in sorted:
	print "Process\t\tTurnaround\tAvg Wait time\tNumber of queue Switches"
	print "-------\t\t----------\t---------\t------------------------"
	print process.procNum, "\t\t", process.turnaround, "\t\t", "%.2f" % process.avgWait, "\t\t", process.qSwitches
	
print "Total Run Time: ", blocktimer 
print "(All times in ms)"
print "\n\n"
	
configFile.close();
execFile.close();
