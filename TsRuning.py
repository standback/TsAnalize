#!/usr/bin/python
import sys
from TsConfig import TsConfig
from TsManager import TsManager

def Tshelp():
	print '''
		================================================================
		TsAnalize usage:
		TsRunging.py  [--options] [TsPath]
		options:
			--PCR=[pcrPid] 	dumpPCR value from packet which pid=pcrPid
			--VPTS=[vPid]	dump Video PTS from packet which pid=vPid
			--APTS=[aPid]	dump Audio PTS from packet which pid=aPid
			--vDump=[vPid] dump Video Data from packet which pid=vPid
			--aDump=[aPid] dump Audio Data from packet which pid=aPid
		===============================================================
		'''

if len(sys.argv)<2:
	print " argument is too few.."
	Tshelp()
sys.argv.pop(0)
config= TsConfig()
if config.config(sys.argv) <0 :
	print "argument is wrong!!"
	print sys.argv
	Tshelp()
else :
	tsManager =TsManager(config)
	tsManager.Run()
