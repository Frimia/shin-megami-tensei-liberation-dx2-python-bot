import hashlib
import struct
import urllib

class Crypter(object):
	def __init__(self):
		pass
		
	def md5(self,s):
		m = hashlib.md5()
		m.update(s)
		return m.hexdigest()

	def decode(self,input):
		md5_fragment=input[:8]
		encoded=input[8:-32].decode('hex')
		lastmd5=input[-32:]
		res= self.eor(encoded,md5_fragment,True)
		return res

	def encode(self,input,custom=None):
		input=input.encode('utf-8')
		md5_fragment=self.md5(input)
		if custom:
			hash=custom[2:-3]+' '
		else:
			hash='L_TMS_2 '
		lastmd5=self.md5(input+hash)
		return md5_fragment[:8]+self.eor(input,md5_fragment[:8])+lastmd5

	def GetSecureID(self,userid):
		return self.md5('%s%sSeK11eTakAAk1'%(userid,userid)).upper()
		
	def eor(self,input,key,decode=False):
		index=0
		if len(key)<30:	key=self.md5(key.decode('hex'))
		key_array=map(ord,key.decode("hex"))
		res=[]
		for i in map(ord,input):
			res.append(struct.pack("B", i^key_array[index]).encode('hex'))
			index+=1
			if index==16:	index=0
		res= ''.join(res)
		if decode:	return res.decode('hex')
		return res