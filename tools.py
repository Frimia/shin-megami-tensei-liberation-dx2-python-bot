import StringIO
import gzip
import base64
import random

class Tools(object):
	def __init__(self):
		pass
		
	def rndHex(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])
		
	def setBasedata(self,data,name):
		compressedFile = StringIO.StringIO()
		compressedFile.write(base64.b64decode(data))
		compressedFile.seek(0)
		decompressedFile = gzip.GzipFile(fileobj=compressedFile, mode='rb')
		with open(name+'.json', 'w') as outfile:
			outfile.write(decompressedFile.read())