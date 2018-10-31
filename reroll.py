from api import API
import random

while(1):
	try:
		a=API()
		a.setRegion(1)
		a.setCustomName('_starter')
		#a.setProxy(random.choice(prox))
		a.setProxy('127.0.0.1:8888')
		a.setPlatform(1)
		a.reroll()
	except:
		pass