SParam= ('pcr','vpts','apts','vdump','adump')
class TsConfig:
	def __init__(self):
		self.configs = dict()
		self.filePath = ''
	def config(self,clist):
		self.configs.clear();
		for param in clist:
			if param.startswith("--") :
				ret =self.parseParam(param)
			else :
				ret =self.filePath = param;
		if len(self.filePath) == 0 :
			print "Please Input Filepath"
		return ret 
	def parseParam(self, param):
		if ('=' in param):
			ce = param.partition('=')
			#print ce
			svalue = ce[2]
			sitem = ce[0]
		else :
			print "[waring] can not recognize param:",param
			return -1;

		value = int(svalue)
		item = sitem.lstrip('-')
		if item.lower() not in SParam :
			print "[waring] unrecognize config: ",item
			return -1;
		if value in self.configs:
			self.configs[value][item] = True
		else :
			self.configs[value] = dict()
			self.configs[value][item.lower()]=True
		print self.configs
		return 0
	def getCurrentFile(self):
		return self.filePath
	def getCurrentConfig(self):
		return self.configs
