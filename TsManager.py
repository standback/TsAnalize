import io
import os
import string
import time
from exceptions import IOError
class TsManager:
	def __init__(self, config):
		self.config=config
		self.packetSize= 188
		self.readBufferSize= 4*1024
		self.dataBuffer=""
		self.RemaindData = ""
		self.context = {"size":0,"offset":0,"remainSize":0}
	
	def __del__(self):
		self.destroyFiles();
	def prepareFiles(self):
		self.files = dict()
		try:
			self.files["TsFile"]=open(self.config.getCurrentFile(),"rb")
			lconfig = self.config.getCurrentConfig()
			for item in lconfig :
				self.files[item] = dict()
				for subitem in lconfig[item] :
					filename = subitem+'_'+str(hex(item))+'_'+ time.strftime('%m%d%H%M%S',time.localtime())
					self.files[item][subitem]= open("output/"+filename,"w")	
		except IOError,ioe:
			print  ioe
		print self.files

	def destroyFiles(self):
		try:
			for key in self.files:
				if key=="TsFile" :
					self.files[key].close()
				else :
					for subkey in self.files[key] :
						self.files[key][subkey].close()
		except IOError,ioe:
			print ioe
		self.files.clear()
		print self.files
	def readData(self):
		if self.context["remainSize"]>0 :
		   self.RemaindData = self.dataBuffer[self.context["offset"] :]
		
		self.dataBuffer = self.files["TsFile"].read(self.readBufferSize)
	
			
		if self.dataBuffer:
			self.dataBuffer = ''.join([self.RemaindData, self.dataBuffer])
			self.context["size"] = len(self.dataBuffer);
			self.context["remainSize"] = self.context["size"]
			self.context["offset"] = 0;
#	print "size:"+ str(self.context["size"])
			return 0
		else :
			return -1
	def syncPacketStartCode(self):
		while True:
			if (self.context["remainSize"] and ord(self.dataBuffer[self.context["offset"]]) == 0x47 ):
				if (self.context["remainSize"] >= 204):
					if(ord(self.dataBuffer[self.context["offset"]+self.packetSize])== 0x47):
						break;

					if(ord(self.dataBuffer[self.context["offset"]+188])== 0x47):
						print "changePacketSize:188"
						self.packetSize= 188
						break
					elif (ord(self.dataBuffer[self.context["offset"]+192])== 0x47):
						print "changePacketSize:192"
						self.packetSize= 192
						break
					elif (ord(self.dataBuffer[self.context["offset"]+204])== 0x47):
						print "changePacketSize:204"
						self.packetSize= 204
						break
					else :
						self.context["offset"]+=1
						self.context["remainSize"] -=1
				else:
				  return -1
			else:
				self.context["offset"]+=1
				self.context["remainSize"] -=1
			
		return 0

	def saveData(self,value):
		if value[1]=='PTS':
			value[0].write(str(hex(value[2]))+'\n')

	def ParseData(self, Ccig):
		packetOffset = self.context["offset"]
		cc= ord(self.dataBuffer[packetOffset +3]) &0x0F
		adaptation_field_control = (ord(self.dataBuffer[packetOffset +3]) & 0x30 )>>4
		# cc check
		packetOffset += 4
		if adaptation_field_control & 0b10 :
			adaptation_length = ord(self.dataBuffer[packetOffset])
			if adaptation_length > 0 :
				adaptation_flags = ord(self.dataBuffer[packetOffset+1])
				if ("pcr" in Ccig) and (adaptation_flags & 0x10) :
					pcr = 0
					for it in self.dataBuffer[packetOffset+2:packetOffset+7] :
						pcr = (pcr<<8) + ord(it)
					pcr = pcr >>7
					result = (Ccig["pcr"],"PTS",pcr)
					self.saveData(result)
			packetOffset += adaptation_length

               
	def handleData(self):
		while True:
			if (self.syncPacketStartCode()<0):
				break;
			pid = 0x1FFF & ((ord(self.dataBuffer[self.context["offset"]+1])<<8)| ord(self.dataBuffer[self.context["offset"]+2]))
			if pid in self.files :
				self.ParseData(self.files[pid])
			self.context["offset"] += self.packetSize
			self.context["remainSize"] -=self.packetSize

			
#		print "parse data finish!"+ str(self.context["offset"])+"--remain:"+str(self.context["remainSize"])

	def Run(self):
		self.prepareFiles()
		while True:	
			if self.readData()<0:
				break;
			self.handleData()
		
		print "finish!"
		for i in self.files:
			if i =='TsFile':
				print "parse :"+ self.files[i].name
			else:
				for subkey in self.files[i]:
					print str(i)+'  '+subkey+' :'+self.files[i][subkey].name
		return 0
		
