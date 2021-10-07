
#AssetButton
#------------------------------------------------------------------
'''
Description
'''

#Imports
#------------------------------------------------------------------
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
import sys, os
import random

from assetUtil import *

#AssetButton class
#------------------------------------------------------------------
class AssetButton(QtWidgets.QWidget):
	
	#Constructor
	def __init__(self, assetName = '',assetType = '', widthHeight = 100, parent = None):
	# def __init__(self, assetName = '', dbName = '', widthHeight = 30, parent = None):	
		super(AssetButton,self).__init__(parent)
		
		#Instance Vars
		self.lytVertButtons = QtWidgets.QVBoxLayout()
		self.assetFrame = QtWidgets.QFrame()
		# self.assetBtn = QtWidgets.QPushButton()
		self.assetBtn = QtWidgets.QToolButton()
		self.assetLabel = QtWidgets.QLabel()
		
		
		self.width = widthHeight
		self.height = widthHeight
		self.delBtnHeight = int(widthHeight/4)
		self.assetName = assetName
		self.assetType = assetType
		# self.dbName = dbName
		
		self.assetBtnStyleSheet = ''
		self.assetLabelStyleSheet = ''
		self.assetBtnImagePath = ''
		self.imageFileFormat = 'png'
		
		#setupAssetButton
		self.setAssetBtnImagePath()
		self.setAssetBtnStyleSheet()
		self.setAssetLabelStyleSheet(self.assetName, 0)
		self.setupAssetButton()
		
		
		
		
	
	#setupAssetButton
	def setupAssetButton(self):
		
		#Buttons setup
		self.assetBtn.setObjectName(self.assetName)
		self.assetLabel.setObjectName(self.assetName)
		
		self.assetBtn.setText(self.assetName)
		self.assetLabel.setText(self.assetName)
		
		self.assetBtn.setMaximumSize(self.width, self.height)
		self.assetBtn.setMinimumSize(self.width, self.height)
		self.assetLabel.setMaximumSize(self.width, self.delBtnHeight)
		self.assetLabel.setMinimumSize(self.width, self.delBtnHeight)
		
		#ButtonStyleSheets
		self.assetBtn.setStyleSheet(self.assetBtnStyleSheet)
		self.assetLabel.setStyleSheet(self.assetLabelStyleSheet)
		self.assetLabel.setAlignment(QtCore.Qt.AlignCenter)

	
		#AssetButton Widget setup
		self.setFixedSize(self.width, self.height + self.delBtnHeight)
		self.setLayout(self.lytVertButtons)
		
		#QToolButton
		self.assetBtn.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
		self.assetBtn.setIconSize(QtCore.QSize(self.width,self.height))
		
		#Lyt setup
		self.lytVertButtons.setMargin(0)
		self.lytVertButtons.setSpacing(0)
		
		self.lytVertButtons.addWidget(self.assetBtn)
		self.lytVertButtons.addWidget(self.assetLabel)

	#setupAssetButton
	def connectAssetButton(self):
		
		#Buttons setup
		self.assetBtn.setObjectName(self.assetName)
		
		
		
	#getAssetName
	def getAssetName(self):
		return self.assetName
		
	#getDbName
	# def getDbName(self):
	# 	return self.dbName
		
	#setWidth
	def setWidth(self, newWidth):
		self.width = newWidth
		
	#setHeight
	def setHeight(self, newHeight):
		self.height = newHeight
		self.delBtnHeight = int(newHeight/4)
		
	#resizeAssetButton
	def resizeAssetButton(self, newWidth, newHeight):
		
		#Set width and height variables
		self.setWidth(newWidth)
		self.setHeight(newHeight)
		
		#Resize assetBtn and assetLabel
		self.assetBtn.setMaximumSize(self.width, self.height)
		self.assetBtn.setMinimumSize(self.width, self.height)
		self.assetBtn.setIconSize(QtCore.QSize(self.width,self.height))

		self.assetLabel.setMaximumSize(self.width, self.delBtnHeight)
		self.assetLabel.setMinimumSize(self.width, self.delBtnHeight)
		
		#AssetButton Widget setup
		self.setFixedSize(self.width, self.height + self.delBtnHeight)
		
	
		
	#setAssetBtnStyleSheet
	def setAssetLabelStyleSheet(self, assetName, selected):
		if selected == 0:
			self.assetLabelStyleSheet = 'QWidget#'+str(assetName)+' {\
			font-weight: bold;\
			color: rgb(255,255,255);\
			}'
			# font-size: 15px;\
		elif selected == 1:
			self.assetLabelStyleSheet = 'QWidget#'+str(assetName)+' {\
			font-weight: bold;\
			color: #2AFFA2;\
			}'
			# font-size: 15px;\

	#setAssetBtnStyleSheet
	def setAssetBtnStyleSheet(self):
		
		
		#check if image exists / if so then set background to red else random
		if(os.path.exists(self.assetBtnImagePath)):
		
			self.assetBtnStyleSheet = 'QWidget#'+str(self.getAssetName())+' {\
			qproperty-icon: url('+self.assetBtnImagePath.replace('\\', '\/')+');\
			border-radius: 5px;\
			font-weight: bold;\
			color: rgb(255,255,255);\
			font-size: 15px;\
			}\
			QWidget#'+str(self.getAssetName())+':hover {\
			border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2AFFA2, stop: 1 #24D387);\
			}'
		
		else:
			self.assetBtnStyleSheet = 'QWidget#'+str(self.getAssetName())+' {\
			background-color: rgb(255, 0,0);\
			font-weight: bold;\
			color: rgb(255,255,255);\
			font-size: 15px;\
			}'
		
		
	#setAssetBtnImagePath
	def setAssetBtnImagePath(self):
		
		#Build final string
		self.assetBtnImagePath = ASSETTYPELISTPATH + '/' + self.assetType + '/' + self.getAssetName() + '/' + self.getAssetName() +'_previewImage.' +self.imageFileFormat
		# print self.assetBtnImagePath
		
		# +self.getDbName() 
		
#Execute if not imported
#------------------------------------------------------------------
if(__name__ == '__main__'):
	app = QtGui.QApplication(sys.argv)
	assetButtonInstance = AssetButton('Heiner', 80)
	#assetButtonInstance.show()
	sys.exit(app.exec_())
		
		

		
		
		
		
		
