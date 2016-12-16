#!/usr/bin/python
#this is open source application ,
#@all copyright reserved
#@author: jason_wang@realsil.com.cn
#
import sys
from TsConfig import TsConfig
from TsManager import TsManager

def Tshelp():
	print ('''
		================================================================
		TsAnalize usage:
		TsRunging.py  [--options] [TsPath]
		options:
			--PCR=[pcrPid] 	dumpPCR value from packet which pid=pcrPid
			--pts=[Pid]	dump PTS from packet which pid=Pid
			--dumpes=[Pid] dump es Data from packet which pid=Pid
		===============================================================
		''')

if len(sys.argv)<2:
	print (" argument is too few..")
	Tshelp()
	quit()
sys.argv.pop(0)
config= TsConfig()
if config.config(sys.argv) <0 :
	print ("argument is wrong!!")
	print (sys.argv)
	Tshelp()
else :
	tsManager =TsManager(config)
	tsManager.Run()
