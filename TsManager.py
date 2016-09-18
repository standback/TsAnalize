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
	
	def __del__(self):
		self.destroyFiles();
	def prepareFiles(self):
		self.files = dict()
		try:
			self.files["TsFile"] = dict()
			self.files["TsFile"]["context"]={"size":0,"offset":0,"remainSize":0}
			tsFile = self.config.getCurrentFile()
			self.files["TsFile"]["file"]=open(tsFile,"rb")

			lconfig = self.config.getCurrentConfig()
			for item in lconfig :
				self.files[item] = dict()
				self.files[item]["context"] = {'cc':-1, 'bufferData':'', 'ccErrorCount':0}
				for subitem in lconfig[item] :
					filename = time.strftime('%m%d%H%M%S',time.localtime())+'_'+os.path.splitext(os.path.basename(tsFile))[0]+'_'+subitem+'_'+str(hex(item))
					self.files[item][subitem]= open("output/"+filename,"w")	
		except IOError,ioe:
			print  ioe
#	print self.files

	def destroyFiles(self):
		try:
			for key in self.files:
				if key=="TsFile" :
					self.files[key]['file'].close()
				else :
					for subkey in self.files[key] :
						if subkey != 'context':
							self.files[key][subkey].close()
		except IOError,ioe:
			print ioe
		self.files.clear()
#		print self.files

	def readData(self):
		if self.files["TsFile"]["context"]["remainSize"]>0 :
		   self.RemaindData = self.dataBuffer[self.files["TsFile"]["context"]["offset"] :]
		
		self.dataBuffer = self.files["TsFile"]["file"].read(self.readBufferSize)
	
			
		if self.dataBuffer:
			self.dataBuffer = ''.join([self.RemaindData, self.dataBuffer])
			self.files["TsFile"]["context"]["size"] = len(self.dataBuffer);
			self.files["TsFile"]["context"]["remainSize"] = self.files["TsFile"]["context"]["size"]
			self.files["TsFile"]["context"]["offset"] = 0;
#	print "size:"+ str(self.files["TsFile"]["context"]["size"])
			return 0
		else :
			return -1
	def syncPacketStartCode(self):
		while True:
			if (self.files["TsFile"]["context"]["remainSize"] and ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]]) == 0x47 ):
				if (self.files["TsFile"]["context"]["remainSize"] >= 204):
					if(ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]+self.packetSize])== 0x47):
						break;

					if(ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]+188])== 0x47):
						print "changePacketSize:188"
						self.packetSize= 188
						break
					elif (ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]+192])== 0x47):
						print "changePacketSize:192"
						self.packetSize= 192
						break
					elif (ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]+204])== 0x47):
						print "changePacketSize:204"
						self.packetSize= 204
						break
					else :
						self.files["TsFile"]["context"]["offset"]+=1
						self.files["TsFile"]["context"]["remainSize"] -=1
				else:
				  return -1
			else:
				self.files["TsFile"]["context"]["offset"]+=1
				self.files["TsFile"]["context"]["remainSize"] -=1
			
		return 0

	def saveData(self,value):
		if value[1]=='PTS':
			value[0].write(str(hex(value[2]))+'\n')
		elif value[1] =='DATA':
			value[0].write(value[2])

	def ParseData(self, Ccig):
		packetOffset = self.files["TsFile"]["context"]["offset"]
		isStartUnit = ord(self.dataBuffer[packetOffset +1]) &0x40

		cc= ord(self.dataBuffer[packetOffset +3]) &0x0F
		adaptation_field_control = (ord(self.dataBuffer[packetOffset +3]) & 0x30 )>>4
		# cc check
		Ccig['context']['cc'] = cc

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
			packetOffset += adaptation_length+1
		
		#pes
		if (isStartUnit):
			if ord(self.dataBuffer[packetOffset])==0x00 and ord(self.dataBuffer[packetOffset+1])==0x00 and ord(self.dataBuffer[packetOffset+2])==0x01 :
				Ccig['context']['bufferData'] = self.dataBuffer[packetOffset: self.files["TsFile"]["context"]["offset"]+188]
		elif Ccig['context']['bufferData'] != '':
			print "xxx"
			Ccig['context']['bufferData'] = Ccig['context']['bufferData']+self.dataBuffer[packetOffset: self.files["TsFile"]["context"]["offset"]+188]
		else:
			if 'dumpes' in Ccig :
				result = (Ccig['dumpes'],"DATA", self.dataBuffer[packetOffset: self.files["TsFile"]["context"]["offset"]+188])
				self.saveData(result)

		if len(Ccig['context']['bufferData'] ) > 14:
			if 'pts' in Ccig:
				if ord(self.dataBuffer[packetOffset+7]) & 0x80 :
					pts = (ord(self.dataBuffer[packetOffset+9])& 0x0e) <<29
					pts = pts +(ord(self.dataBuffer[packetOffset+10])<< 22)
					pts = pts +((ord(self.dataBuffer[packetOffset+11]) &0xfe) <<14)
					pts = pts + (ord(self.dataBuffer[packetOffset+12])<<7)
					pts = pts + (ord(self.dataBuffer[packetOffset+13]) & 0xfe >>1)
					result = (Ccig['pts'], 'PTS', pts)
					self.saveData(result)
			if 'dumpes' in Ccig:
				print str(hex(ord(Ccig['context']['bufferData'][8])))+'-'+str(len(Ccig['context']['bufferData']))
				#for i in Ccig['context']['bufferData']:
				#	print str(hex(ord(i)))

				result = (Ccig["dumpes"],"DATA",Ccig['context']['bufferData'][9+ord(Ccig['context']['bufferData'][8]):len(Ccig['context']['bufferData'])] )
				self.saveData(result)
				#os._exit(0)

			Ccig['context']['bufferData']  = ''

		 

               
	def handleData(self):
		while True:
			if (self.syncPacketStartCode()<0):
				break;
			pid = 0x1FFF & ((ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]+1])<<8)| ord(self.dataBuffer[self.files["TsFile"]["context"]["offset"]+2]))
			if pid in self.files :
				self.ParseData(self.files[pid])
			self.files["TsFile"]["context"]["offset"] += self.packetSize
			self.files["TsFile"]["context"]["remainSize"] -=self.packetSize

			
#		print "parse data finish!"+ str(self.files["TsFile"]["context"]["offset"])+"--remain:"+str(self.files["TsFile"]["context"]["remainSize"])

	def Run(self):
		self.prepareFiles()
		while True:	
			if self.readData()<0:
				break;
			self.handleData()
		
		print "------------"+ self.files['TsFile']['file'].name+'-----------------'
		for i in self.files:
			if i !='TsFile':
				for subkey in self.files[i]:
					if subkey != 'context':
						print str(i)+'  '+subkey+' :'+self.files[i][subkey].name
		return 0
		
