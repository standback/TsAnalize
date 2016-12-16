#!/usr/bin/python
#this is open source application ,
#
#@Copyright(c) 2014 jason_wang, 
#@author: jason_wang@realsil.com.cn
#
import sys
print(sys.argv)
ux=0
uy=0
def getdataFromFile(file):
	data=list()
	with open(file,'rb') as sf:
		for line in sf:
			data.append(line.split())
	print(file+':'+str(len(data)))
	return data
	
def writeJsDataToFile(datas,base,upper):
	with open("html5-svg-multi-line-chart/data/data.js",'w') as wf:
		wf.write('var data = 	[')
		for item in datas:
			wf.write("\n[")
			for data in item:
				wf.write("{'x':"+data[0]+",'y':"+str(data[1])+"},")
			wf.write('],')
			
		wf.write('\n];\n')
		wf.write("var coord=["+str(upper[0])+','+str(upper[1])+"];\n")
		wf.write("var ptsBase="+str(base)+";\n")
		wf.close()

def shiftPtsData(datas):
	base =0xfffffffff
	for item in datas:
		for data in item:
			if base>int(data[1]):
				base= int(data[1])
				
	
	for item in datas:
		for data in item:
			data[1]=int(data[1]) - base
	print ("ptsBase:"+str(base))
	return base
			
def findUppercordinator(datas):
	ux =0
	uy=0
	for item in datas:
		print(item[0])
		for data in item:
			if ux<int(data[0]):
				ux= int(data[0])
			if uy<int(data[1]):
				uy= int(data[1])
	print("upper:"+str(ux)+','+str(uy))
	return (ux,uy)			
def processPtsDataForJsShow(files):
	print(files)
	datas=list()
	for item in files:
		data = getdataFromFile(item)
		datas.append(data)
	print("--------")
	writeJsDataToFile(datas,shiftPtsData(datas),findUppercordinator(datas))

def main():
	if len(sys.argv)<2:
		print("input data file")
	else :
		processPtsDataForJsShow([sys.argv[1]])
		
if __name__ == '__main__':
	main()

