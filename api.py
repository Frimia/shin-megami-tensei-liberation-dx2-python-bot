# -*- coding: utf-8 -*-
from crypter import Crypter
from answers import good
from tools import Tools
import hashlib
import io
import json
import random
import requests
import socket
import struct
import sys
import time
import units
import urllib
from requests_toolbelt import MultipartEncoder
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.s=requests.Session()
		self.s.verify=False
		self.s.headers.update({'User-Agent':'SEGA Web Client for D2SMTL 2018'})
		self.crypter=Crypter()
		self.tools=Tools()
		self.lang=1
		self._tm=1
		self.platform=1
		self.gender=random.randint(0,1)
		self.check_code='1.6.0'
		self.ek=None
		self.used_acts=[]
		self.setRegion()

	def setcanTalk(self):
		self.canTalk=True

	def setRegion(self,region=1):
		if region==1:
			self.api_base='https://ad2r-sim.mobile.sega.jp/socialsv/'
		else:
			self.api_base='https://d2r-sim.mobile.sega.jp/socialsv/'
		self.region=region

	def setCustomName(self,name):
		self.log_name=name
		
	def setCanRefill(self):
		self.refill=True

	def setAccount(self,id):
		self.account=id

	def setUuid(self,id):
		self.uuid=id

	def setSecure_id(self,id):
		self.secure_id=id

	def setPassword2(self,id):
		self.password=id

	def setTransferId(self,id):
		self.transfer_id=id

	def login(self):
		self.GetUrl('check_code={}&platform={}&lang={}&bundle_id={}&_tm_={}'.format('1.6.0','1','1','com.sega.d2megaten.en',self._tm))
		self.LoadInfo('lang={}&_tm_={}'.format('1',self._tm))
		self.Login('account={}&uuid={}&secure_id={}&check_code={}&lang={}&platform={}&country={}&asset_bundle_version={}&_tm_={}'.format(self.account,self.uuid,self.secure_id,'1.6.0','1','1','DE','1.6.0.Kpv8LSfB2ZU6',self._tm))
		self.SNEntry('basic_info={}&_tm_={}'.format('iPadAir2+%3a+iPad5%2c4',self._tm))
		gems=self.Home('is_ar={}&_tm_={}'.format('0',self._tm))['usr']['cp']
		#print gems
		self.Notification('type={}&_tm_={}'.format('1',self._tm))
		self.ChatEntry('_tm_={}'.format(self._tm))
		self.CpProductList('lang={}&platform={}&store={}&_tm_={}'.format('1','1','1',self._tm))

	def urlencode(self,str):
		return urllib.quote_plus(str,safe='=&').lower()

	def setProxy(self,proxy):
		self.log('using proxy %s'%(proxy))
		self.s.proxies.update({'http': 'http://%s'%proxy,'https': 'https://%s'%proxy,})

	def setPlatform(self,id):
		self.platform=id
		
	def log(self,msg):
		print '[%s]%s'%(time.strftime('%H:%M:%S'),str(msg).encode('utf-8'))

	def genRandomIP(self):
		return socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
		
	def callAPI(self,kind,param=None,path=None,encoded=True):
		if not path:
			path=sys._getframe(1).f_code.co_name+'.do'
		if kind==1:
			if encoded:
				r=self.s.get(self.api_base+path+'?param=%s'%(self.crypter.encode(param,self.ek if self.ek else None)))
			else:
				r=self.s.get(self.api_base+path+'?'+param)
			self._tm+=2
		else:
			r=self.s.post(self.api_base+path,data=param,headers={'Content-Type':'application/x-www-form-urlencoded'})
			self._tm+=2
		res= json.loads(r.content)
		if 'Insufficient Stamina.' in r.content and hasattr(self,'refill'):
			self.UserRecoverAp('_tm_=%s'%(self._tm))
			return self.callAPI(kind,param,path,encoded)
		if 'Insufficient Duel Stamina.' in r.content and hasattr(self,'refill'):
			self.UserRecoverBp('_tm_=%s'%(self._tm))
			return self.callAPI(kind,param,path,encoded)
		return res

	def LoadInfo(self,param):
		return self.callAPI(1,param)

	def RegistAccount(self,param):
		res= self.callAPI(1,param)
		self.account=res['account_id']
		self.uuid=res['uuid']
		self.transfer_id=res['transfer_id']
		self.secure_id=self.crypter.GetSecureID(self.account)
		return res

	def DbgRegistAccount(self,param):
		res= self.callAPI(1,param,'dbg/DbgRegistAccount.do')
		self.account=res['account_id']
		self.uuid=res['uuid']
		self.transfer_id=res['transfer_id']
		self.secure_id=self.crypter.GetSecureID(self.account)
		return res

	def Login(self,param):
		res= self.callAPI(1,param)
		self.ek=res['ek']
		self.user_id=res['user_id']
		self.gender=res['gnd']
		return res

	def SNEntry(self,param):
		return self.callAPI(1,param)

	def SNTest(self,param):
		return self.callAPI(2,{'param':self.crypter.encode(param,self.ek if self.ek else None)})

	def GetBaseData(self,param):
		res= self.callAPI(1,param)
		if False:
			self.tools.setBasedata(res['data'],'%s_%s'%(time.strftime('%H_%M_%S'),random.randint(0,1000)))
		return res

	def Drama(self,param):
		return self.callAPI(1,param)

	def CpProductList(self,param):
		return self.callAPI(1,param,'iap/CpProductList.do')

	def ChatEntry(self,param):
		return self.callAPI(1,param,'chat/ChatEntry.do')

	def TutorialUserCreate(self,param):
		return self.callAPI(1,param)

	def Helper(self,param):
		return self.callAPI(1,param)

	def FriendOffer(self,param):
		return self.callAPI(1,param)

	def TutorialBattleEntry(self,param):
		return self.callAPI(1,param)

	def DramaEnd(self,param):
		return self.callAPI(1,param)

	def TutorialBattleNext(self,param):
		return self.callAPI(1,param)

	def TutorialMap(self,param):
		return self.callAPI(1,param)

	def TutorialFacility(self,param):
		return self.callAPI(1,param)

	def TutorialSociety(self,param):
		return self.callAPI(1,param)

	def Mission(self,param):
		return self.callAPI(1,param)

	def Society(self,param):
		return self.callAPI(1,param)

	def TutorialFinish(self,param):
		return self.callAPI(1,param)

	def Home(self,param):
		res= self.callAPI(1,param)
		self.usr=res['usr']
		return res

	def Notification(self,param):
		return self.callAPI(1,param)

	def PresentList(self,param):
		res= self.callAPI(1,param)
		self.gifts=res
		return res

	def IngameTutorialEnd(self,param):
		return self.callAPI(1,param)

	def UserInfo(self,param):
		return self.callAPI(1,param)

	def PresentRecv(self,param):
		return self.callAPI(1,param)

	def Map(self,param):
		res= self.callAPI(1,param)
		limit=3 if self.region==1 else 2
		if len(self.used_acts)<=3:
			for a in res['acts']:
				tgt=a['user_id']
				uniq=a['uniq']
				if tgt in self.used_acts:	continue
				self.ActivitySocialRewardSend('tgt=%s&uniq=%s&_tm_=%s'%(tgt,uniq,self._tm))
				self.used_acts.append(tgt)
		return res

	def DramaQuest(self,param):
		return self.callAPI(1,param)

	def ActivitySocialRewardSend(self,param):
		return self.callAPI(1,param)

	def Pvp(self,param):
		return self.callAPI(1,param)

	def PvpOpponentGet(self,param):
		return self.callAPI(1,param)

	def PvpBattleEntry(self,param):
		return self.callAPI(1,param)

	def PvpBriefing(self,param):
		return self.callAPI(1,param)

	def PvpBattleResult(self,param):
		return self.callAPI(2,{'param':self.crypter.encode(param,self.ek if self.ek else None)})

	def Party(self,param):
		return self.callAPI(1,param)

	def BattleEntry(self,param):
		return self.callAPI(1,param)

	def BattleTalk(self,param):
		return self.callAPI(1,param)

	def BattleNext(self,param):
		return self.callAPI(1,param)

	def Fusion(self,param):
		return self.callAPI(1,param)

	def FusionExec(self,param):
		return self.callAPI(1,param)

	def Gacha(self,param):
		return self.callAPI(1,param)

	def Buildup(self,param):
		return self.callAPI(1,param)

	def DevilSale(self,param):
		return self.callAPI(1,param)

	def UserRecoverAp(self,param):
		self.log('UserRecoverAp() was called')
		return self.callAPI(1,param)

	def UserRecoverBp(self,param):
		self.log('UserRecoverBp() was called')
		return self.callAPI(1,param)

	def TutorialBattleResult(self,param):
		return self.callAPI(2,{'param':self.crypter.encode(param,self.ek if self.ek else None)})

	def BattleResult(self,param):
		return self.callAPI(2,{'param':self.crypter.encode(param,self.ek if self.ek else None)})

	def DevilSaleExec(self,param):
		return self.callAPI(2,{'param':self.crypter.encode(param,self.ek if self.ek else None)})

	def GachaExec(self,param):
		res= self.callAPI(1,param)
		return res

	def Facility(self,param):
		return self.callAPI(1,param)

	def SpecialDungeon(self,param):
		return self.callAPI(1,param)

	def SpecialDungeonList(self,param):
		return self.callAPI(1,param)

	def FacilityHarvest(self,param):
		return self.callAPI(1,param)

	def AccountTransferPasswordRegist(self,param):
		return self.callAPI(2,param,'common/AccountTransferPasswordRegist.do')

	def GateDungeon(self,param):
		return self.callAPI(1,param)

	def GateDungeonFloorEntry(self,param):
		return self.callAPI(1,param)

	def FacilityLevelUp(self,param):
		return self.callAPI(1,param)

	def PartySet(self,param):
		return self.callAPI(1,param)

	def SocietyRankupExec(self,param):
		return self.callAPI(1,param)

	def MissionReceive(self,param):
		return self.callAPI(1,param)

	def GateDungeonFloorUpdate(self,param):
		return self.callAPI(1,param)

	def GateDungeonResult(self,param):
		return self.callAPI(1,param)

	def BattleAssistSelect(self,param):
		return self.callAPI(1,param)

	def BattleAssistSend(self,param):
		return self.callAPI(1,param)

	def ItemUse(self,param):#'id=1100&num=1&part=-1&series_id=-1&_tm_=210'
		return self.callAPI(1,param)

	def GetUrl(self,param):
		return self.callAPI(1,param,'common/GetUrl.do')

	def DevilWatch(self,param):
		return self.callAPI(2,param)

	def Enhance(self,param):
		return self.callAPI(2,param)

	def EnhanceExec(self,param):
		return self.callAPI(2,param)

	def IngameTutorialCheck(self,param):
		return self.callAPI(2,param)

	def getGifts(self):
		self.PresentList('_tm_={}'.format(self._tm))
		pr=[]
		for i in self.gifts['present_list']:
			pr.append('uniq_id='+str(i['present_id']))
		if len(pr)>=1:
			return self.PresentRecv('%s&type=0&part=-1&series_id=-1&_tm_=191'%('&'.join(pr)))

	def getColor(self,id):
		return {'4':'green','3':'purple','2':'yellow','1':'red','0':'clear'}[str(id)]

	def GetName(self,id):
		return units.data[str(id)]['name']

	def getRarity(self,id):
		return units.data[str(id)]['rarity']

	def finishTutorial(self):
		self.IngameTutorialEnd('tgt=0&tutorial_id=1&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=2&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=3&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=4&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=5&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=6&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=101&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=102&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=103&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=104&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=106&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=107&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=108&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=109&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=110&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=111&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=112&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=113&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=115&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=120&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=121&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=122&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=200&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=201&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=202&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=203&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=204&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=220&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=221&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=222&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=300&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=301&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=302&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=303&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=304&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=305&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=306&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=307&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=308&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=309&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=310&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=311&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=312&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=313&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=314&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=315&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=316&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=317&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=318&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=319&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=320&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=321&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=322&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=323&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=325&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=326&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=327&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=328&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=329&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=400&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=401&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=402&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=403&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=404&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=405&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=406&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=407&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=408&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=409&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=411&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=500&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=413&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=414&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=415&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=416&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=418&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=450&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=451&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=452&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=453&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=454&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=455&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=460&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=461&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=462&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=463&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=464&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=465&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=466&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=470&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=471&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=472&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=473&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=480&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=490&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=491&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=900&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=901&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=902&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=903&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=905&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=906&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=907&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=908&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=909&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=910&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1000&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1001&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1002&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1004&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1005&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1006&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1007&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1100&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1101&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1102&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1103&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1105&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1106&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1107&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1108&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1109&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1110&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1111&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1112&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1113&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1114&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1115&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1117&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1211&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1213&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1215&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1217&is_skip=False&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=1116&is_skip=False&_tm_={}'.format(self._tm))

	def doGate(self,pos):
		self.GateDungeonBattleEntry('pos={}&main=1&sub=2&_tm_={}'.format(pos,self._tm))
		self.GateDungeonBattleResult('stage=7&result=1&an_info=%5b%7b%22id%22%3a+12010%2c%22attr%22%3a+2147483647%7d%2c%7b%22id%22%3a+12420%2c%22attr%22%3a+97%7d%5d&item_use=&df_info=%5b%7b%22uniq%22%3a+700%2c%22type%22%3a+1%7d%2c%7b%22uniq%22%3a+701%2c%22type%22%3a+1%7d%5d&dvhp_info=%5b%7b%22uniq%22%3a+9223159%2c%22hp%22%3a+196%7d%2c%7b%22uniq%22%3a+9223153%2c%22hp%22%3a+238%7d%2c%7b%22uniq%22%3a+9222900%2c%22hp%22%3a+215%7d%2c%7b%22uniq%22%3a+9222685%2c%22hp%22%3a+210%7d%2c%7b%22uniq%22%3a+9222104%2c%22hp%22%3a+112%7d%2c%7b%22uniq%22%3a+9222105%2c%22hp%22%3a+102%7d%5d&damage=0&smn_change=1&max_damage=137&turn=1&p_act=3&e_act=0&mem_cnt=0&dtcr_err=0&_tm_={}'.format(self._tm))
		
	def unlockMaze(self):
		self.GateDungeon('id=999&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_01%2f001&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fgd_01%2f001&id=1&id=2&select=2&select=1&lnc_pt=0&lnc_pt=0&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=0&menu_id=0&gd_id=999&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_01%2f002&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=400&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorEntry('id=999&floor=1&main_party=1&sub_party=2&type=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=20&map_dir=0&dp=100&event_type=16&steps=20&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fgd_p1_01%2f001&id=0&select=1&lnc_pt=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=23&map_dir=1&dp=95&event_type=1&steps=21&steps=20&steps=21&steps=22&steps=23&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=19&map_dir=0&dp=94&event_type=16&steps=19&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_02%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=7&map_dir=0&dp=91&event_type=16&steps=15&steps=11&steps=7&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_03%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=7&map_dir=0&dp=91&event_type=2&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_03%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_03%2f003&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=2&map_dir=3&dp=89&event_type=16&steps=7&steps=3&steps=2&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_04%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=1&map_dir=3&dp=88&event_type=1&steps=1&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=1&map_dir=3&dp=88&event_type=16&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_05%2f001&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=1&map_dir=3&dp=88&event_type=8&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=14&map_dir=2&dp=135&event_type=1&steps=6&steps=10&steps=14&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=12&map_dir=3&dp=133&event_type=5&steps=13&steps=12&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=12&map_dir=3&dp=133&event_type=16&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_06%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=4&map_dir=0&dp=131&event_type=16&steps=8&steps=4&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_07%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonResult('result_type=0&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fgd_p1_07%2f001&id=1&id=2&select=1&select=1&lnc_pt=0&lnc_pt=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f008&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.GateDungeon('id=999&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=0&menu_id=0&gd_id=999&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.GateDungeonFloorEntry('id=999&floor=1&main_party=1&sub_party=2&type=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=20&map_dir=0&dp=131&event_type=16&steps=20&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_08%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fgd_p1_08%2f001&id=1&select=1&lnc_pt=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=23&map_dir=1&dp=128&event_type=16&steps=21&steps=22&steps=23&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_09%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=15&map_dir=0&dp=126&event_type=1&steps=19&steps=15&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=6&map_dir=2&dp=122&event_type=1&steps=11&steps=7&steps=3&steps=2&steps=6&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=14&map_dir=2&dp=121&event_type=16&steps=10&steps=14&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_10%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=14&map_dir=2&dp=121&event_type=2&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		#self.GateDungeonBattleEntry('pos=14&main=1&sub=2&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_10%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_10%2f003&_tm_={}'.format(self._tm))
		#self.GateDungeonBattleResult('stage=14&result=1&an_info=%5b%7b%22id%22%3a+10910%2c%22attr%22%3a+25%7d%2c%7b%22id%22%3a+12320%2c%22attr%22%3a+2147483647%7d%5d&item_use=&df_info=%5b%7b%22uniq%22%3a+698%2c%22type%22%3a+1%7d%2c%7b%22uniq%22%3a+699%2c%22type%22%3a+1%7d%5d&dvhp_info=%5b%7b%22uniq%22%3a+9223159%2c%22hp%22%3a+196%7d%2c%7b%22uniq%22%3a+9223153%2c%22hp%22%3a+238%7d%2c%7b%22uniq%22%3a+9222900%2c%22hp%22%3a+215%7d%2c%7b%22uniq%22%3a+9222685%2c%22hp%22%3a+210%7d%2c%7b%22uniq%22%3a+9222104%2c%22hp%22%3a+90%7d%2c%7b%22uniq%22%3a+9222105%2c%22hp%22%3a+62%7d%5d&damage=0&smn_change=2&max_damage=55&turn=3&p_act=4&e_act=4&mem_cnt=0&dtcr_err=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=8&map_dir=0&dp=116&event_type=1&steps=14&steps=18&steps=17&steps=16&steps=12&steps=8&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=4&map_dir=0&dp=115&event_type=16&steps=4&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_11%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fgd_p1_11%2f001&id=1&select=2&lnc_pt=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=0&map_dir=0&dp=114&event_type=3&steps=0&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		#self.GateDungeonBattleEntry('pos=0&main=1&sub=2&_tm_={}'.format(self._tm))
		#self.GateDungeonBattleResult('stage=0&result=1&an_info=%5b%7b%22id%22%3a+12330%2c%22attr%22%3a+67%7d%2c%7b%22id%22%3a+12110%2c%22attr%22%3a+2147483647%7d%2c%7b%22id%22%3a+12310%2c%22attr%22%3a+2147483647%7d%5d&item_use=&df_info=%5b%7b%22uniq%22%3a+40%2c%22type%22%3a+1%7d%2c%7b%22uniq%22%3a+41%2c%22type%22%3a+1%7d%2c%7b%22uniq%22%3a+42%2c%22type%22%3a+1%7d%5d&dvhp_info=%5b%7b%22uniq%22%3a+9223159%2c%22hp%22%3a+196%7d%2c%7b%22uniq%22%3a+9223153%2c%22hp%22%3a+219%7d%2c%7b%22uniq%22%3a+9222900%2c%22hp%22%3a+118%7d%2c%7b%22uniq%22%3a+9222685%2c%22hp%22%3a+210%7d%2c%7b%22uniq%22%3a+9222104%2c%22hp%22%3a+90%7d%2c%7b%22uniq%22%3a+9222105%2c%22hp%22%3a+62%7d%5d&damage=0&smn_change=1&max_damage=94&turn=2&p_act=5&e_act=4&mem_cnt=0&dtcr_err=0&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=0&map_dir=0&dp=114&event_type=16&steps=0&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p1_12%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=0&map_dir=0&dp=114&event_type=4&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorEntry('id=999&floor=2&main_party=1&sub_party=2&type=1&_tm_={}'.format(self._tm))
		self.GateDungeonFloorUpdate('map_pos=31&map_dir=0&dp=114&event_type=16&steps=31&main_party=1&box_key_num=-1&trap_result=-1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgd_p2_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.GateDungeonResult('result_type=0&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f009&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.GateDungeon('id=4&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		
	def doChapter1(self,diff=1,extend=False):
		if extend:
			self.doQuest(10031)
			self.doQuest(10041)
			self.doQuest(10051)
			self.doQuest(10061)
			self.doQuest(10071)
			self.Map('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2forder_02%2f001&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2forder_02%2f002&_tm_={}'.format(self._tm))
			self.Facility('_tm_=15')
			self.Drama('lang=1&path=tutorial%2forder_02%2f003&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=908&is_skip=False&_tm_={}'.format(self._tm))
			self.Buildup('_tm_={}'.format(self._tm))
			self.Notification('type=3&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fbuildup_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=301&is_skip=False&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f001&_tm_={}'.format(self._tm))
			self.Enhance('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f002&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f003&_tm_={}'.format(self._tm))
			self.EnhanceExec('base_devil=100000000000&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&devil_item_id=22100&devil_item_num=1&_tm_=26')
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f004&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=302&is_skip=False&_tm_={}'.format(self._tm))
			self.Facility('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=mission%2forder%2f006&_tm_={}'.format(self._tm))
			self.doQuest(10081)
			self.doQuest(10091)
			self.doQuest(10101)
			self.doQuest(10111)
			self.doQuest(10121)
			self.doQuest(1001)
			self.IngameTutorialCheck('igt_id=418&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2flevelling_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=418&is_skip=False&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=story%2fcapter_01%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=10131&_tm_={}'.format(self._tm))
			self.Map('_tm_={}'.format(self._tm))
			self.Home('is_ar=0&_tm_={}'.format(self._tm))
			self.Notification('type=1&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2finstquest_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=115&is_skip=False&_tm_={}'.format(self._tm))
		else:
			diff=str(diff)
			self.doQuest(str('1001')+diff)
			self.doQuest(str('1002')+diff)
			self.doQuest(str('1003')+diff)
			self.doQuest(str('1004')+diff)
			self.doQuest(str('1005')+diff)
			self.doQuest(str('1006')+diff)
			self.doQuest(str('1007')+diff)
			self.doQuest(str('1008')+diff)
			self.doQuest(str('1009')+diff)
			self.doQuest(str('1010')+diff)
			self.doQuest(str('1011')+diff)
			self.doQuest(str('1012')+diff)
			self.doQuest(str('100')+diff)

	def doChapter2(self,diff=1):
		diff=str(diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_02%2f000_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=11001&_tm_={}'.format(self._tm))
		self.doQuest(str('1101')+diff)
		self.doQuest(str('1102')+diff)
		self.doQuest(str('1103')+diff)
		self.doQuest(str('1104')+diff)
		self.doQuest(str('1105')+diff)
		self.doQuest(str('1106')+diff,2)
		self.doQuest(str('1107')+diff,2)
		self.doQuest(str('1108')+diff,2)
		self.doQuest(str('1109')+diff)
		self.doQuest(str('1110')+diff)
		self.doQuest(str('1111')+diff)
		self.doQuest(str('1112')+diff)
		self.doQuest(str('1113')+diff)
		self.doQuest(str('1114')+diff)
		self.doQuest(str('110')+diff)
		if diff=='1':
			self.Drama('lang=1&path=tutorial%2factivity_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=906&is_skip=False&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fmap_01%2f001&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fmap_01%2f002&_tm_={}'.format(self._tm))
			self.Map('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fmap_01%2f003&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=101&is_skip=False&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=story%2fcapter_02%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=11151&_tm_={}'.format(self._tm))
			self.Map('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=mission%2forder%2f011&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))

	def doChapter3(self,diff=1):
		diff=str(diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_03%2f000_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=12001&_tm_={}'.format(self._tm))
		self.doQuest(str('1201')+diff)
		self.doQuest(str('1202')+diff)
		self.doQuest(str('1203')+diff)
		self.doQuest(str('1204')+diff)
		self.doQuest(str('1205')+diff)
		self.doQuest(str('1206')+diff,2)
		self.doQuest(str('1207')+diff,2)
		self.doQuest(str('1208')+diff,2)
		self.doQuest(str('1209')+diff)
		self.doQuest(str('1210')+diff)
		self.doQuest(str('1211')+diff)
		self.doQuest(str('1212')+diff)
		self.doQuest(str('1213')+diff)
		self.doQuest(str('1214')+diff)
		self.doQuest(str('1215')+diff)
		self.doQuest(str('1216')+diff)
		self.doQuest(str('1217')+diff)
		self.doQuest(str('1217')+diff)
		self.doQuest(str('120')+diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_03%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=12181&_tm_={}'.format(self._tm))
			self.Map('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=mission%2forder%2f013&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fspd_limit_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=491&is_skip=True&_tm_={}'.format(self._tm))
			self.IngameTutorialCheck('igt_id=401&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fspdungeon_01%2f001&_tm_={}'.format(self._tm))
			self.SpecialDungeon('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fspdungeon_01%2f002&_tm_={}'.format(self._tm))
			self.SpecialDungeonList('type=1&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fspdungeon_01%2f003&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fspdungeon_01%2f004&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=401&is_skip=False&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))

	def doChapter4(self,diff=1):
		diff=str(diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_04%2f000_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=13001&_tm_={}'.format(self._tm))
		self.doQuest(str('1301')+diff)
		self.doQuest(str('1302')+diff)
		self.doQuest(str('1303')+diff)
		self.doQuest(str('1304')+diff)
		self.doQuest(str('1305')+diff)
		self.doQuest(str('1306')+diff)
		self.doQuest(str('1307')+diff)
		self.doQuest(str('1308')+diff)
		self.doQuest(str('1309')+diff)
		self.doQuest(str('1310')+diff,2)
		self.doQuest(str('1311')+diff)
		self.doQuest(str('1312')+diff)
		self.doQuest(str('1313')+diff)
		self.doQuest(str('1314')+diff)
		self.doQuest(str('1315')+diff)
		self.doQuest(str('1316')+diff)
		self.doQuest(str('130')+diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_04%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=13171&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))

	def doChapter5(self,diff=1):
		diff=str(diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_05%2f000_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=14001&_tm_={}'.format(self._tm))
		self.doQuest(str('1401')+diff)
		self.doQuest(str('1402')+diff)
		self.doQuest(str('1403')+diff)
		self.doQuest(str('1404')+diff)
		self.doQuest(str('1405')+diff)
		self.doQuest(str('1406')+diff)
		self.doQuest(str('1407')+diff)
		self.doQuest(str('1408')+diff)
		self.doQuest(str('1409')+diff)
		self.doQuest(str('1410')+diff)
		self.doQuest(str('1411')+diff)
		self.doQuest(str('1412')+diff)
		self.doQuest(str('1413')+diff)
		self.doQuest(str('1414')+diff)
		self.doQuest(str('1415')+diff)
		self.doQuest(str('1416')+diff)
		self.doQuest(str('140')+diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_05%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=14171&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))

	def doChapter6(self,diff=1):
		diff=str(diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_06%2f000_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=15001&_tm_={}'.format(self._tm))
		self.doQuest(str('1501')+diff)
		self.doQuest(str('1502')+diff)
		self.doQuest(str('1503')+diff,2)
		self.doQuest(str('1504')+diff,5)
		self.doQuest(str('1505')+diff,4)
		self.doQuest(str('1506')+diff,6)
		self.doQuest(str('1507')+diff)
		self.doQuest(str('1508')+diff)
		self.doQuest(str('1509')+diff)
		self.doQuest(str('1510')+diff)
		self.doQuest(str('1511')+diff)
		self.doQuest(str('1512')+diff)
		self.doQuest(str('1513')+diff)
		self.doQuest(str('1514')+diff)
		self.doQuest(str('1515')+diff)
		self.doQuest(str('150')+diff)
		if diff=='1':
			self.Drama('lang=1&path=story%2fcapter_06%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=15161&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))

	def doDeceit(self):
		self.doQuest(2001011)
		self.doQuest(2001021)
		self.doQuest(2001031)
		self.doQuest(2001041)
		self.doQuest(2001051)
		self.doQuest(2001061)
		self.doQuest(2001071)
		self.doQuest(2001081)
		self.doQuest(2001091)
		self.doQuest(2001101)

	def doSloth(self):
		self.doQuest(2000011)
		self.doQuest(2000021)
		self.doQuest(2000031)
		self.doQuest(2000041)
		self.doQuest(2000051)
		self.doQuest(2000061)
		self.doQuest(2000071)
		self.doQuest(2000081)
		self.doQuest(2000091)
		self.doQuest(2000101)

	def doChaoticSignal(self):
		self.doQuest(2014011)
		self.doQuest(2014021)
		self.doQuest(2014031)
		self.doQuest(2014041)
		self.doQuest(2014051)
		self.doQuest(2014061)
		self.doQuest(2014071)
		self.doQuest(2014081)
		self.doQuest(2014091)
		self.doQuest(2014101)

	def doDarkSignal(self):
		self.doQuest(2011011)
		self.doQuest(2011021)
		self.doQuest(2011031)
		self.doQuest(2011041)
		self.doQuest(2011051)
		self.doQuest(2011061)
		self.doQuest(2011071)
		self.doQuest(2011081)
		self.doQuest(2011091)
		self.doQuest(2011101)

	def doLightSignal(self):
		self.doQuest(2010011)
		self.doQuest(2010021)
		self.doQuest(2010031)
		self.doQuest(2010041)
		self.doQuest(2010051)
		self.doQuest(2010061)
		self.doQuest(2010071)
		self.doQuest(2010081)
		self.doQuest(2010091)
		self.doQuest(2010101)

	def doNeutralSignal(self):
		self.doQuest(2012011)
		self.doQuest(2012021)
		self.doQuest(2012031)
		self.doQuest(2012041)
		self.doQuest(2012051)
		self.doQuest(2012061)
		self.doQuest(2012071)
		self.doQuest(2012081)
		self.doQuest(2012091)
		self.doQuest(2012101)

	def doLawfulSignal(self):
		self.doQuest(2013011)
		self.doQuest(2013021)
		self.doQuest(2013031)
		self.doQuest(2013041)
		self.doQuest(2013051)
		self.doQuest(2013061)
		self.doQuest(2013071)
		self.doQuest(2013081)
		self.doQuest(2013091)
		self.doQuest(2013101)

	def setPassword(self,extend=False):
		passw=self.tools.rndHex(6)
		hasfour=0
		hasfive=0
		units=[]
		self.GachaExec('id=4000110&multi=0&_tm_={}'.format(self._tm))
		self.GachaExec('id=4600100&multi=0&_tm_={}'.format(self._tm))
		if extend:
			self.doQuest(10031)
			self.doQuest(10041)
			self.doQuest(10051)
			self.doQuest(10061)
			self.doQuest(10071)
			self.Map('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2forder_02%2f001&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2forder_02%2f002&_tm_={}'.format(self._tm))
			self.Facility('_tm_=15')
			self.Drama('lang=1&path=tutorial%2forder_02%2f003&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=908&is_skip=False&_tm_={}'.format(self._tm))
			self.Buildup('_tm_={}'.format(self._tm))
			self.Notification('type=3&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fbuildup_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=301&is_skip=False&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f001&_tm_={}'.format(self._tm))
			self.Enhance('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f002&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f003&_tm_={}'.format(self._tm))
			self.EnhanceExec('base_devil=100000000000&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&devil_item_id=22100&devil_item_num=1&_tm_=26')
			self.Drama('lang=1&path=tutorial%2fenhance_01%2f004&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=302&is_skip=False&_tm_={}'.format(self._tm))
			self.Facility('_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=mission%2forder%2f006&_tm_={}'.format(self._tm))
			self.doQuest(10081)
			self.doQuest(10091)
			self.doQuest(10101)
			self.doQuest(10111)
			self.doQuest(10121)
			self.doQuest(1001)
			self.IngameTutorialCheck('igt_id=418&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2flevelling_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=418&is_skip=False&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=story%2fcapter_01%2f100_qb&_tm_={}'.format(self._tm))
			self.DramaQuest('quest_id=10131&_tm_={}'.format(self._tm))
			self.Map('_tm_={}'.format(self._tm))
			self.Home('is_ar=0&_tm_={}'.format(self._tm))
			self.Notification('type=1&_tm_={}'.format(self._tm))
			self.Drama('lang=1&path=tutorial%2finstquest_01%2f001&_tm_={}'.format(self._tm))
			self.IngameTutorialEnd('tgt=0&tutorial_id=115&is_skip=False&_tm_={}'.format(self._tm))
			self.Gacha('_tm_={}'.format(self._tm))
			self.Home('is_ar=0&_tm_={}'.format(self._tm))
			self.Notification('type=1&_tm_={}'.format(self._tm))
			self.Gacha('_tm_={}'.format(self._tm))
			self.GachaExec('id=104990101&multi=0&_tm_={}'.format(self._tm))
		for i in self.Party('edit=1&quest_id=0&menu_id=0&gd_id=0&_tm_=204')['devils']:
			#if i['id'] in [11760,12310]:	continue
			if i['rarity']==4:
				hasfour+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 4* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
			if i['rarity']==5:
				hasfive+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 5* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
		savestr='%s,%s,%s,%s,%s:%s,%s,%s,%s'%(self.account,self.uuid,self.secure_id,'female' if self.gender==1 else 'male',self.transfer_id,passw,hasfour,hasfive,','.join(units))
		if hasfive>=1:
			print passw,str(self.transfer_id)
			self.sappend(savestr,'accounts%s_5_%s.csv'%(self.log_name if hasattr(self,'log_name') else '',hasfive))
		elif hasfour>=1:
			print passw,str(self.transfer_id)
			self.sappend(savestr,'accounts%s_4_%s.csv'%(self.log_name if hasattr(self,'log_name') else '',hasfour))
		else:
			self.sappend(savestr,'accounts%s_other.csv'%(self.log_name if hasattr(self,'log_name') else ''))
		return self.callAPI(2,'account=%s&transfer_id=%s&password=%s&uuid=%s&secure_id=%s&_tm_=220'%(self.account,self.transfer_id,self.crypter.md5(passw).upper(),self.uuid,self.secure_id),'common/AccountTransferPasswordRegist.do')
		
	def exportUnits(self):
		units=[]
		hasfive=0
		hasfour=0
		#passw=self.password
		passw=self.tools.rndHex(6)
		print passw
		self.AccountTransferPasswordRegist('account={}&transfer_id={}&password={}&uuid={}&secure_id={}&_tm_={}'.format(self.account,self.transfer_id,self.crypter.md5(passw).upper(),self.uuid,self.secure_id,self._tm))
		#for i in self.Party('edit=1&quest_id=0&menu_id=0&gd_id=0&_tm_=%s'%(self._tm))['devils']:
		for i in self.Party('quest_id=0&menu_id=70&gd_id=0&_tm_=%s'%(self._tm))['devils']:
			#if i['id'] in [11760,12310]:	continue
			if i['rarity']==4:
				hasfour+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 4* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
			if i['rarity']==5:
				hasfive+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 5* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
		if not hasattr(self,'transfer_id'):
			self.transfer_id=self.account
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		savestr='%s,%s,%s,%s,%s:%s,%s,%s,%s'%(self.account,self.uuid,self.secure_id,'female' if self.gender==1 else 'male',self.transfer_id,passw,hasfour,hasfive,','.join(units))
		savefile='%s_accounts%s_4x_%s_5x_%s_lvl_%s_gems_%s.csv'%('gl' if self.region==1 else 'jp',self.log_name if hasattr(self,'log_name') else '',hasfour,hasfive,self.usr['lv'],self.usr['cp'])
		self.sappend(savestr,savefile)

	def doPVP(self):
		try:
			self.Pvp('_tm_=%s'%(self._tm))
			usr_id=random.choice(self.PvpOpponentGet('is_pay_update=0&_tm_=%s'%(self._tm))['list'])['user']['usr_id']
			self.PvpBriefing('user_id=%s&log_id=0&rival_id=0&_tm_=%s'%(usr_id,self._tm))
			start=self.PvpBattleEntry('user_id=%s&main=1&sub=0&rival_id=0&log_id=0&_tm_=%s'%(usr_id,self._tm))
			enemies=start['enemies']
			return self.PvpBattleResult(self.urlencode('enemy_user_id=%s&result=1&an_info=[{"id": %s,"attr": %s},{"id": %s,"attr": %s},{"id": %s,"attr": %s},{"id": %s,"attr": %s}]&item_use=&df_info=[{"uniq": %s,"type": 1},{"uniq": %s,"type": 1},{"uniq": %s,"type": 1},{"uniq": %s,"type": 1}]&smn_change=1&max_damage=550&turn=5&p_act=19&e_act=9&mem_cnt=0&dtcr_err=0&_tm_=%s'%(usr_id,enemies[0]['id'],enemies[0]['anlz'],enemies[1]['id'],enemies[1]['anlz'],enemies[2]['id'],enemies[2]['anlz'],enemies[3]['id'],enemies[3]['anlz'],enemies[0]['uniq'],enemies[1]['uniq'],enemies[2]['uniq'],enemies[3]['uniq'],self._tm)))
		except:
			pass

	def getTalkStatus(self,status):
		return {0:'TALK_RESULT_NONE',1:'TALK_RESULT_SUCCESS',2:'TALK_RESULT_GREAT_SUCCESS',3:'TALK_RESULT_CONTRACT_SUCCESS',4:'TALK_RESULT_FAIL',5:'TALK_RESULT_DEVIL_MAX',6:'TALK_RESULT_ESCAPE',7:'TALK_RESULT_END',8:'TALK_RESULT_DEAD'}[status]
	
	def doTalk(self,id,talk_type):
		select=0
		working_combo=[]
		while(1):
			start=self.BattleTalk('tgt=%s&select=%s&talk_type=%s&is_contract=0&is_all_dead=0&_tm_=%s'%(id,select,talk_type,self._tm))
			if 'talk_list' not in start:	break
			talk_list=start['talk_list']
			for i in talk_list:
				if len(i['select_list'])>=1:
					select2=None
					for j in i['select_list']:
						#if 'Accept' in j['text'] or 'Make Companion' in j['text']:	select2=j
						if j['text'] in good:	select2=j
					rnd=random.choice(i['select_list'])
					if select2:	rnd=select2
					#working_combo.append('%s %s'%(rnd['text'],rnd['select_id']))
					working_combo.append(rnd['text'])
					select=select2['select_id'] if select2 else rnd['select_id']
			if 'result' in start and start['result']:	break
		if 'result' in start and start['result']==1:
			if len(working_combo)>=1:
				#print working_combo
				self.sappend(';'.join(working_combo),'correct_answer.csv')
		#elif 'result' in start:
		#	print self.getTalkStatus(start['result'])
		
	def sellLow(self):
		devils=self.DevilSale('_tm_=%s'%(self._tm))['stock']
		tosell=[]
		for i in devils:
			if (i['rarity']==1 or i['rarity']==2) and i['lv']<=1:
				tosell.append('devils=%s'%(i['uniq']))
		if len(tosell)>=1:
			self.DevilSaleExec('%s&_tm_=%s'%('&'.join(tosell),self._tm))
		
	def makebig(self):
		self.collectMissions()
		self.SocietyRankupExec('_tm_={}'.format(self._tm))
		self.SocietyRankupExec('_tm_={}'.format(self._tm))
		self.FacilityLevelUp('id=2&_tm_={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.collectMissions()
		self.SocietyRankupExec('_tm_={}'.format(self._tm))
		self.FacilityLevelUp('id={}'.format(self._tm))
		self.collectMissions()
		
	def collectMissions(self):
		mission_list=self.Mission('_tm_=%s'%(self._tm))['mission_list']
		for i in mission_list:
			if i['is_clear'] and not i['is_received']:
				self.MissionReceive('id=%s&_tm_=%s'%(i['id'],self._tm))
		
	def doAssist(self,card,skill):
		self.BattleAssistSelect('card=%s&skill=%s&_tm_=%s'%(card,skill,self._tm))
		self.BattleAssistSend('type=1&card=%s&skill=%s&_tm_=%s'%(card,skill,self._tm))

	def doQuest(self,stage,main=1):
		start=self.BattleEntry('stage=%s&main=%s&sub=0&helper=0&smn_id=0&is_auto=0&_tm_=%s'%(stage,main,self._tm))
		current_wave=start['wave']
		wave_max=start['wave_max']
		anlz=start['enemies'][0]['anlz']
		id=start['enemies'][0]['id']
		uniq=start['enemies'][0]['uniq']
		parties=start['parties'][0]['devils']
		#time.sleep(0.5)
		if wave_max<>1:
			while(True):
				anlz=start['enemies'][0]['anlz']
				id=start['enemies'][0]['id']
				uniq=start['enemies'][0]['uniq']
				if hasattr(self,'canTalk') and 'talk' in start and start['talk']['talk_tgt']:
					self.doTalk(start['talk']['talk_tgt'],start['talk']['talk_start_type'])
				if 'assist_target' in start and start['assist_target']['usr_id']:
					devil=random.choice(parties)
					self.doAssist(devil['uniq'],devil['skl'][0]['id'])
				start=self.BattleNext(self.urlencode('stage=%s&wave=%s&an_info=[{"id": %s,"attr": %s}]&item_use=&df_info=[{"uniq": %s,"type": 1}]&turn=1&p_act=1&e_act=0&_tm_=%s'%(stage,current_wave,id,anlz,uniq,self._tm)))
				current_wave=start['wave']
				if current_wave == start['wave_max']:	break
				#time.sleep(0.5)
		res= self.BattleResult(self.urlencode('stage=%s&result=1&an_info=[{"id": %s,"attr": %s}]&item_use=&df_info=[{"uniq": %s,"type": 1}]&mission_result=0&defeat_count=3&smn_change=1&max_damage=512&turn=1&p_act=1&e_act=0&mem_cnt=0&dtcr_err=0&_tm_=%s'%(stage,id,anlz,uniq,self._tm)))
		self.log('quest %s finished'%(stage))
		return res
		
	def sappend(self,d,f):
		with io.open(f, 'a', encoding='utf8') as the_file:
			the_file.write('%s\n'%(unicode(d)))
		
	def rerollv2(self):
		self.GetUrl('check_code=1.6.0&platform=1&lang=1&bundle_id=com.sega.d2megaten.en&_tm_={}'.format(self._tm))
		self.LoadInfo('lang=1&_tm_={}'.format(self._tm))
		self.RegistAccount('platform=1&country=DE&lang=1&_tm_={}'.format(self._tm))
		names=self.Login('account=%s&uuid=%s&secure_id=%s&check_code=1.6.0&lang=1&platform=%s&country=DE&_tm_=%s'%(self.account,self.uuid,self.secure_id,self.platform,self._tm))['rand_names']
		nonce=self.SNEntry('basic_info=iPadAir2+%3a+iPad5%2c4&_tm_={}'.format(self._tm))['nonce']
		self.GetBaseData('type=data1&_tm_={}'.format(self._tm))
		self.SNTest('jws=&device_info=&status_code=-5000&nonce={}&_tm_={}'.format(nonce,self._tm))
		self.GetBaseData('type=data2&_tm_={}'.format(self._tm))
		self.GetBaseData('type=data3&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f001&_tm_={}'.format(self._tm))
		self.CpProductList('lang=1&platform=1&store=1&_tm_={}'.format(self._tm))
		self.ChatEntry('_tm_={}'.format(self._tm))
		self.TutorialUserCreate('name=%s&gender=%s&_tm_=%s'%(random.choice(names),self.gender,self._tm))
		self.TutorialBattleEntry('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f002&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fnewgame_01%2f002&id=1&select=1&lnc_pt=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f003&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f004&_tm_={}'.format(self._tm))
		self.TutorialBattleNext('wave=1&an_info=%5b%7b%22id%22%3a+11530%2c%22attr%22%3a+3%7d%5d&turn=1&p_act=2&e_act=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f005&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f006&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f007&_tm_={}'.format(self._tm))
		self.TutorialBattleNext('wave=2&an_info=%5b%7b%22id%22%3a+12520%2c%22attr%22%3a+18%7d%5d&turn=1&p_act=2&e_act=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f008&_tm_={}'.format(self._tm))
		self.TutorialBattleResult('result=1&an_info=%5b%7b%22id%22%3a+11320%2c%22attr%22%3a+18%7d%5d&smn_change=1&max_damage=28&turn=1&p_act=3&e_act=0&mem_cnt=0&dtcr_err=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f009&_tm_={}'.format(self._tm))
		self.TutorialMap('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f011&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fnewgame_01%2f011&id=1&select=1&lnc_pt=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f012&_tm_={}'.format(self._tm))
		self.TutorialFacility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f013&_tm_={}'.format(self._tm))
		self.DramaEnd('path=tutorial%2fnewgame_01%2f013&id=1&select=1&lnc_pt=0&_tm_={}'.format(self._tm))
		self.TutorialSociety('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f014&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f015&_tm_={}'.format(self._tm))
		self.Mission('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f016&_tm_={}'.format(self._tm))
		self.Society('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f017&_tm_={}'.format(self._tm))
		self.TutorialFacility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f018&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fnewgame_01%2f019&_tm_={}'.format(self._tm))
		self.TutorialFinish('step=0&_tm_={}'.format(self._tm))
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f000_qb&_tm_={}'.format(self._tm))
		self.DramaQuest('quest_id=10001&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10011&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10011)
		self.Drama('lang=1&path=story%2fcapter_01%2f001_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ftalk_01%2f001&_tm_={}'.format(self._tm))
		self.BattleTalk('tgt=4&select=0&talk_type=1&is_contract=0&is_all_dead=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ftalk_01%2f002&_tm_={}'.format(self._tm))
		self.BattleTalk('tgt=4&select=1&talk_type=1&is_contract=0&is_all_dead=0&_tm_={}'.format(self._tm))
		self.BattleTalk('tgt=4&select=2&talk_type=1&is_contract=0&is_all_dead=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ftalk_01%2f003&_tm_={}'.format(self._tm))
		self.BattleTalk('tgt=4&select=12&talk_type=1&is_contract=0&is_all_dead=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ftalk_01%2f004&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f001_qa&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10021&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbattle_party_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbattle_party_01%2f002&_tm_={}'.format(self._tm))
		self.DevilWatch('')
		self.Drama('lang=1&path=tutorial%2fbattle_party_01%2f003&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbattle_party_01%2f004&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbattle_party_01%2f005&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=204&is_skip=False&_tm_={}'.format(self._tm))
		self.doQuest(10021)
		self.Drama('lang=1&path=story%2fcapter_01%2f002_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2flongpress_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2flongpress_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2flongpress_01%2f003&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2flongpress_01%2f004&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fresult_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fresult_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fresult_01%2f003&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fresult_01%2f004&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=406&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f000&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f002_qa&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2forder_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2forder_01%2f002&_tm_={}'.format(self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2forder_01%2f003&_tm_={}'.format(self._tm))
		self.Fusion('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffusion_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffusion_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffusion_01%2f003&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffusion_01%2f004&_tm_={}'.format(self._tm))
		self.FusionExec('uniq_a=60012953743&uniq_b=100000000000&id=11810&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffusion_01%2f005&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgacha_02%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=103&is_skip=False&_tm_={}'.format(self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgacha_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgacha_01%2f002&_tm_={}'.format(self._tm))
		self.GachaExec('id=1000001&multi=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fgacha_01%2f003&_tm_={}'.format(self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fparty_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fparty_01%2f002&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=104&is_skip=False&_tm_={}'.format(self._tm))
		self.Party('edit=1&quest_id=0&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fedit_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fedit_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fedit_01%2f003&_tm_={}'.format(self._tm))
		self.DevilWatch('uniq=60012966990&uniq=60012965839&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fedit_01%2f004&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=200&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f002&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10031&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.PartySet('devil=60012965839&party=1&idx=3&is_set=1&_tm_={}'.format(self._tm))
		self.doQuest(10031)
		self.Drama('lang=1&path=story%2fcapter_01%2f003_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fauto_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fauto_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fauto_01%2f003&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10041&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10041)
		self.Drama('lang=1&path=story%2fcapter_01%2f004_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ftarget_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10051&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fcoop_select_01%2f001&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10051&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fcoop_select_01%2f002&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=409&is_skip=False&_tm_={}'.format(self._tm))
		self.doQuest(10051)
		self.Drama('lang=1&path=story%2fcapter_01%2f005_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fcoop_battle_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=903&is_skip=False&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10061&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10061&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10061)
		self.Drama('lang=1&path=story%2fcapter_01%2f006_qb&_tm_={}'.format(self._tm))
		self.BattleAssistSelect('card=60012966990&skill=1012&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fassist_01%2f001&_tm_={}'.format(self._tm))
		self.BattleAssistSend('type=1&card=60012966990&skill=1012&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fassist_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fassist_01%2f003&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffriend_prefer_01%2f001&_tm_={}'.format(self._tm))
		self.FriendOffer('user_id=841602&route=6&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2ffriend_prefer_01%2f002&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=500&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f006_qa&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10071&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10071&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10071)
		self.Drama('lang=1&path=story%2fcapter_01%2f007_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbattle_item_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=True&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f003&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2forder_02%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2forder_02%2f002&_tm_={}'.format(self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2forder_02%2f003&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=908&is_skip=False&_tm_={}'.format(self._tm))
		self.Buildup('_tm_={}'.format(self._tm))
		self.Notification('type=3&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbuildup_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=301&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fenhance_01%2f001&_tm_={}'.format(self._tm))
		self.Enhance('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fenhance_01%2f002&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fenhance_01%2f003&_tm_={}'.format(self._tm))
		self.EnhanceExec('base_devil=100000000000&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&ingredient_devils=0&devil_item_id=22100&devil_item_num=1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fenhance_01%2f004&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=302&is_skip=False&_tm_={}'.format(self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=mission%2forder%2f006&_tm_={}'.format(self._tm))
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10081&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10081&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10081)
		self.Drama('lang=1&path=story%2fcapter_01%2f008_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fbattle_mp_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=0&is_skip=False&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fanalyze_06%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=910&is_skip=False&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10091&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10091&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10091)
		self.Drama('lang=1&path=story%2fcapter_01%2f009_qb&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.IngameTutorialCheck('igt_id=418&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2flevelling_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=418&is_skip=False&_tm_={}'.format(self._tm))
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10101&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10101&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10101)
		self.Drama('lang=1&path=story%2fcapter_01%2f010_qb&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10111&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10111&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10111)
		self.Drama('lang=1&path=story%2fcapter_01%2f011_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f011_qa&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Helper('quest_id=10121&_tm_={}'.format(self._tm))
		self.Party('edit=0&quest_id=10121&menu_id=0&gd_id=0&_tm_={}'.format(self._tm))
		self.Notification('type=2&_tm_={}'.format(self._tm))
		self.doQuest(10121)
		self.Drama('lang=1&path=story%2fcapter_01%2f012_qb&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f012_qa&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=story%2fcapter_01%2f100_qb&_tm_={}'.format(self._tm))
		self.DramaQuest('quest_id=10131&_tm_={}'.format(self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2finstquest_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=115&is_skip=False&_tm_={}'.format(self._tm))
		self.PresentList('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fpresent_01%2f001&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=107&is_skip=False&_tm_={}'.format(self._tm))
		self.getGifts()
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.GachaExec('id=4000110&multi=0&_tm_={}'.format(self._tm))
		self.GachaExec('id=4600100&multi=0&_tm_={}'.format(self._tm))
		self.GachaExec('id=104990101&multi=0&_tm_={}'.format(self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		self.UserInfo('_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fprofile_01%2f001&_tm_={}'.format(self._tm))
		self.Drama('lang=1&path=tutorial%2fprofile_01%2f002&_tm_={}'.format(self._tm))
		self.IngameTutorialEnd('tgt=0&tutorial_id=110&is_skip=False&_tm_={}'.format(self._tm))
		self.Home('is_ar=0&_tm_={}'.format(self._tm))
		self.Notification('type=1&_tm_={}'.format(self._tm))
		passw=self.tools.rndHex(6)
		hasfour=0
		hasfive=0
		units=[]
		for i in self.Party('edit=1&quest_id=0&menu_id=0&gd_id=0&_tm_=%s'%(self._tm))['devils']:
			if i['rarity']==4:
				hasfour+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 4* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
			if i['rarity']==5:
				hasfive+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 5* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
		savestr='%s,%s,%s,%s,%s:%s,%s,%s,%s'%(self.account,self.uuid,self.secure_id,'female' if self.gender==1 else 'male',self.transfer_id,passw,hasfour,hasfive,','.join(units))
		if hasfive>=1:
			print passw,str(self.transfer_id)
			self.sappend(savestr,'accounts%s_5_%s.csv'%(self.log_name if hasattr(self,'log_name') else '',hasfive))
		elif hasfour>=1:
			print passw,str(self.transfer_id)
			self.sappend(savestr,'accounts%s_4_%s.csv'%(self.log_name if hasattr(self,'log_name') else '',hasfour))
		else:
			self.sappend(savestr,'accounts%s_other.csv'%(self.log_name if hasattr(self,'log_name') else ''))
		return self.callAPI(2,'account=%s&transfer_id=%s&password=%s&uuid=%s&secure_id=%s&_tm_=%s'%(self.account,self.transfer_id,self.crypter.md5(passw).upper(),self.uuid,self.secure_id,self._tm),'common/AccountTransferPasswordRegist.do')

	def reroll(self,extend=False):
		self.GetUrl('check_code={}&platform={}&lang={}&bundle_id={}&_tm_={}'.format('1.6.0','1','1','com.sega.d2megaten.en',self._tm))
		self.LoadInfo('lang={}&_tm_={}'.format('1',self._tm))
		self.RegistAccount('platform={}&country={}&lang={}&_tm_={}'.format('1','DE','1',self._tm))
		names=self.Login('account={}&uuid={}&secure_id={}&check_code={}&lang={}&platform={}&country={}&_tm_={}'.format(self.account,self.uuid,self.secure_id,'1.6.0','1','1','DE',self._tm))['rand_names']
		nonce=self.SNEntry('basic_info={}&_tm_={}'.format('iPadAir2+%3a+iPad5%2c4',self._tm))['nonce']
		self.GetBaseData('type={}&_tm_={}'.format('data1',self._tm))
		self.SNTest('jws={}&device_info={}&status_code={}&nonce={}&_tm_={}'.format('','','-5000',nonce,self._tm))
		self.GetBaseData('type={}&_tm_={}'.format('data2',self._tm))
		self.GetBaseData('type={}&_tm_={}'.format('data3',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f001',self._tm))
		self.CpProductList('lang={}&platform={}&store={}&_tm_={}'.format('1','1','1',self._tm))
		self.ChatEntry('_tm_={}'.format(self._tm))
		self.TutorialUserCreate('name={}&gender={}&_tm_={}'.format(random.choice(names),self.gender,self._tm))
		self.TutorialBattleEntry('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f002',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f003',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f004',self._tm))
		self.TutorialBattleNext('wave={}&an_info={}&turn={}&p_act={}&e_act={}&_tm_={}'.format('1','%5b%7b%22id%22%3a+11530%2c%22attr%22%3a+1%7d%5d','1','2','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f005',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f006',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f007',self._tm))
		self.TutorialBattleNext('wave={}&an_info={}&turn={}&p_act={}&e_act={}&_tm_={}'.format('2','%5b%7b%22id%22%3a+12520%2c%22attr%22%3a+17%7d%5d','1','3','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f008',self._tm))
		self.TutorialBattleResult('result={}&an_info={}&smn_change={}&max_damage={}&turn={}&p_act={}&e_act={}&mem_cnt={}&dtcr_err={}&_tm_={}'.format('1','%5b%7b%22id%22%3a+11320%2c%22attr%22%3a+17%7d%5d','1','28','1','3','0','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f009',self._tm))
		self.TutorialMap('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f011',self._tm))
		self.DramaEnd('path={}&id={}&select={}&lnc_pt={}&_tm_={}'.format('tutorial%2fnewgame_01%2f011','1','2','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f012',self._tm))
		self.TutorialFacility('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f013',self._tm))
		self.TutorialSociety('_tm_={}'.format(self._tm))
		self.DramaEnd('path={}&id={}&select={}&lnc_pt={}&_tm_={}'.format('tutorial%2fnewgame_01%2f013','1','1','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f014',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f015',self._tm))
		self.Mission('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f016',self._tm))
		self.Society('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f017',self._tm))
		self.TutorialFacility('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f018',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fnewgame_01%2f019',self._tm))
		self.TutorialFinish('step={}&_tm_={}'.format('0',self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','story%2fcapter_01%2f000_qb',self._tm))
		self.DramaQuest('quest_id={}&_tm_={}'.format('10001',self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Party('edit={}&quest_id={}&menu_id={}&gd_id={}&_tm_={}'.format('0','10011','0','0',self._tm))
		self.Notification('type={}&_tm_={}'.format('2',self._tm))
		self.BattleEntry('stage={}&main={}&sub={}&helper={}&smn_id={}&is_auto={}&_tm_={}'.format('10011','1','0','0','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','story%2fcapter_01%2f001_qb',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ftalk_01%2f001',self._tm))
		self.BattleTalk('tgt={}&select={}&talk_type={}&is_contract={}&is_all_dead={}&_tm_={}'.format('4','0','1','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ftalk_01%2f002',self._tm))
		self.BattleTalk('tgt={}&select={}&talk_type={}&is_contract={}&is_all_dead={}&_tm_={}'.format('4','1','1','0','0',self._tm))
		self.BattleTalk('tgt={}&select={}&talk_type={}&is_contract={}&is_all_dead={}&_tm_={}'.format('4','3','1','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ftalk_01%2f003',self._tm))
		self.BattleTalk('tgt={}&select={}&talk_type={}&is_contract={}&is_all_dead={}&_tm_={}'.format('4','12','1','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ftalk_01%2f004',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','0','False',self._tm))
		self.BattleNext('stage={}&wave={}&an_info={}&item_use={}&df_info={}&turn={}&p_act={}&e_act={}&_tm_={}'.format('10011','1','%5b%7b%22id%22%3a+11910%2c%22attr%22%3a+127%7d%5d','','%5b%7b%22uniq%22%3a+4%2c%22type%22%3a+2%7d%5d','1','0','0',self._tm))
		self.BattleNext('stage={}&wave={}&an_info={}&item_use={}&df_info={}&turn={}&p_act={}&e_act={}&_tm_={}'.format('10011','2','%5b%7b%22id%22%3a+12010%2c%22attr%22%3a+18%7d%5d','','%5b%7b%22uniq%22%3a+5%2c%22type%22%3a+1%7d%5d','1','2','0',self._tm))
		self.BattleResult('stage={}&result={}&an_info={}&item_use={}&df_info={}&mission_result={}&defeat_count={}&smn_change={}&max_damage={}&turn={}&p_act={}&e_act={}&mem_cnt={}&dtcr_err={}&_tm_={}'.format('10011','1','%5b%7b%22id%22%3a+11730%2c%22attr%22%3a+3%7d%5d','','%5b%7b%22uniq%22%3a+6%2c%22type%22%3a+1%7d%5d','0','3','1','36','1','2','0','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','story%2fcapter_01%2f001_qa',self._tm))
		self.Map('_tm_={}'.format(self._tm))
		tut_organize_devil=self.Party('edit={}&quest_id={}&menu_id={}&gd_id={}&_tm_={}'.format('0','10021','0','0',self._tm))['tut_organize_devil']
		self.Notification('type={}&_tm_={}'.format('2',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fbattle_party_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fbattle_party_01%2f002',self._tm))
		#self.DevilWatch('uniq={}&uniq={}&uniq={}&uniq={}&_tm_={}'.format('30015373309','30015373332','30015372806','30015372805',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fbattle_party_01%2f003',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fbattle_party_01%2f004',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fbattle_party_01%2f005',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','204','False',self._tm))
		self.BattleEntry('stage={}&main={}&sub={}&helper={}&smn_id={}&is_auto={}&_tm_={}'.format('10021','2','0','0','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','story%2fcapter_01%2f002_qb',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2flongpress_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2flongpress_01%2f002',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2flongpress_01%2f003',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2flongpress_01%2f004',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','0','False',self._tm))
		self.BattleNext('stage={}&wave={}&an_info={}&item_use={}&df_info={}&turn={}&p_act={}&e_act={}&_tm_={}'.format('10021','1','%5b%7b%22id%22%3a+12110%2c%22attr%22%3a+25%7d%5d','','%5b%7b%22uniq%22%3a+7%2c%22type%22%3a+1%7d%2c%7b%22uniq%22%3a+8%2c%22type%22%3a+1%7d%5d','1','3','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fanalyze_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fanalyze_01%2f002',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','0','False',self._tm))
		self.BattleNext('stage={}&wave={}&an_info={}&item_use={}&df_info={}&turn={}&p_act={}&e_act={}&_tm_={}'.format('10021','2','%5b%7b%22id%22%3a+10910%2c%22attr%22%3a+9%7d%5d','','%5b%7b%22uniq%22%3a+9%2c%22type%22%3a+1%7d%5d','1','2','0',self._tm))
		self.BattleResult('stage={}&result={}&an_info={}&item_use={}&df_info={}&mission_result={}&defeat_count={}&smn_change={}&max_damage={}&turn={}&p_act={}&e_act={}&mem_cnt={}&dtcr_err={}&_tm_={}'.format('10021','1','%5b%7b%22id%22%3a+12010%2c%22attr%22%3a+19%7d%5d','','%5b%7b%22uniq%22%3a+10%2c%22type%22%3a+1%7d%5d','0','4','1','52','1','2','0','0','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fresult_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fresult_01%2f002',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fresult_01%2f003',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fresult_01%2f004',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','406','False',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','mission%2forder%2f000',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','story%2fcapter_01%2f002_qa',self._tm))
		self.Map('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2forder_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2forder_01%2f002',self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2forder_01%2f003',self._tm))
		self.Fusion('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ffusion_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ffusion_01%2f002',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ffusion_01%2f003',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ffusion_01%2f004',self._tm))
		self.FusionExec('uniq_a={}&uniq_b={}&id={}&_tm_={}'.format(tut_organize_devil,'100000000000','11810',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2ffusion_01%2f005',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','0','False',self._tm))
		self.Facility('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','mission%2forder%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fgacha_02%2f001',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','103','False',self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fgacha_01%2f001',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fgacha_01%2f002',self._tm))
		self.GachaExec('id={}&multi={}&_tm_={}'.format('1000001','0',self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fgacha_01%2f003',self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.Home('is_ar={}&_tm_={}'.format('0',self._tm))
		self.Notification('type={}&_tm_={}'.format('1',self._tm))
		self.PresentList('_tm_={}'.format(self._tm))
		self.Drama('lang={}&path={}&_tm_={}'.format('1','tutorial%2fpresent_01%2f001',self._tm))
		self.IngameTutorialEnd('tgt={}&tutorial_id={}&is_skip={}&_tm_={}'.format('0','107','False',self._tm))
		self.getGifts()
		self.Home('is_ar={}&_tm_={}'.format('0',self._tm))
		self.Notification('type={}&_tm_={}'.format('1',self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.GachaExec('id={}&multi={}&_tm_={}'.format('4000110','0',self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		self.GachaExec('id={}&multi={}&_tm_={}'.format('4600100','0',self._tm))
		self.Gacha('_tm_={}'.format(self._tm))
		passw=self.tools.rndHex(6)
		hasfour=0
		hasfive=0
		units=[]
		for i in self.Party('edit={}&quest_id={}&menu_id={}&gd_id={}&_tm_={}'.format('1','0','0','0',self._tm))['devils']:
			if i['rarity']==4:
				hasfour+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 4* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
			if i['rarity']==5:
				hasfive+=1
				units.append('%s %s* (%s)'%(self.GetName(i['id']),i['rarity'],self.getColor(i['arc'])))
				print 'has 5* name:%s color:%s'%(self.GetName(i['id']),self.getColor(i['arc']))
		savestr='%s,%s,%s,%s:%s,%s,%s'%(self.account,self.uuid,self.secure_id,self.transfer_id,passw,'female' if self.gender==1 else 'male',','.join(units))
		savefile='%s_accounts%s_4x_%s_5x_%s.csv'%('gl' if self.region==1 else 'jp',self.log_name if hasattr(self,'log_name') else '',hasfour,hasfive)
		print passw,str(self.transfer_id)
		self.sappend(savestr,savefile)
		self.AccountTransferPasswordRegist('account={}&transfer_id={}&password={}&uuid={}&secure_id={}&_tm_={}'.format(self.account,self.transfer_id,self.crypter.md5(passw).upper(),self.uuid,self.secure_id,self._tm))

if __name__ == "__main__":
	a=API()
	a.setProxy('127.0.0.1:8888')
	a.reroll(True)
	a.doChapter2()
	#a.finishTutorial()