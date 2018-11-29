class Node:
	BroadcastList = {}
	isBusy = False
	Input_TX = {}  #Ledger

	def __init__(self,id):
		self.id = id;
	def updateBroadcastList(self,blist):
		self.BroadcastList = blist
	def setBusy(self,flag):
		self.isBusy = flag
	def setPublicKey(self,pub):
		self.publicKey = pub	
	def setPrivateKey(self,priv):
		self.__privateKey = priv
	def verifyTransaction(self,txList):
		#Check all the transactions in tx which not already spent 
		#and add them up to see if it is equal or greater to the amount
		balance=0
		for tx in txList:
			if tx.spent == True:
				balance+=tx.Amount
		return balance
	def updateLedger(self,txList):
		self.Input_TX = txList
		pass				

class NewTransaction:
	SenderID = 0
	ReceiverID = 0
	Amount=0
	#Input_TX = []
	Spent = False

class ShareTransaction:
	#Input_TX = []
	New_TX = None