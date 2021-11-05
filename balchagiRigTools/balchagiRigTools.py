#--------------------------------------------------------------------------------------#
# 20210906.0.0.1 - initial version. 
#--------------------------------------------------------------------------------------

__VERSION__ = "20210906.0.0.1"
AUTHOR = "Hun Back"

import os, re, functools, webbrowser, cPickle, logging, cStringIO, platform, zipfile, sys, types, shutil
import subprocess
from maya  import cmds, mel, OpenMayaUI, OpenMaya
import xml.etree.ElementTree as xml 
import yaml
import imp
from datetime import datetime
import json


#Reload boolean
doReload = True

# import 
from lib.qtUtil import *

from lib import assetUtil as util
if(doReload): reload(util)

from lib import FlowLayout
if(doReload): reload(FlowLayout)

from lib import AssetButton
if(doReload): reload(AssetButton)

sys.path.append(os.path.dirname(WORKDIRECTORY))

Ui_MainWindow, Ui_BaseClass = loadUiType( '%s/blachagiRigToolsUI.ui'%WORKDIRECTORY )
Ui_checkToolWindow, Ui_checkToolBaseClass = loadUiType( '%s/checkTool.ui'%WORKDIRECTORY )

def getMayaWindow():
    """
    Get the main Maya window as a QtGui.QMainWindow instance
    @return: QtGui.QMainWindow instance of the top level Maya windows
    """
    MayaWindowPtr = OpenMayaUI.MQtUtil.mainWindow()
    if MayaWindowPtr is not None:
        return wrapinstance( long(MayaWindowPtr))

class blachagiRigTools(Ui_MainWindow, Ui_BaseClass):
    def __init__(self, parent=getMayaWindow()):
        super(blachagiRigTools,self).__init__(parent)
        self.setupUi(self)

        # ===== Style sheet =====
        QT_COLORTHEME = "Lime"
        QT_STYLESHEET = os.path.normpath(os.path.join(__file__, "../q%s.stylesheet"%QT_COLORTHEME))
        
        with open( QT_STYLESHEET, "r" ) as fh:
            self.setStyleSheet( fh.read() )

        # initial project setting.
        self._initial_project_setting()

        #Instance Vars
        # self.flowLayout = FlowLayout.FlowLayout()
        self.selectedAssetItem = ''
        self.currentProject = ''
        self.currentAssetType = ''
        self.assetItemList = {}
        
        self.assetTreeWidgetItemList = []
        self.fileTreeWidgetItemList = []

        # ui-building
        self._SetFunctionUtilTab()
        self._SetAssetBrowserTreeWidget()
        self._SetFileBrowserTreeWidget()

        self._assetIndicator('main')
        self._assetIndicator('other')
        
        #Set flowLayout
        # self.scrlAreaAssetButtonsWidget.setLayout(self.flowLayout)

        self.__iconManagement()
        self._meunbarSetup()
        self._scriptTableUISetup()
        self._buttonManagement() 

        # Connect sldButtonSize
        # self.sldButtonSize.valueChanged.connect(self.resizePoseButtons)

        #------------------------
        # visual
        #------------------------
        self.blueFontColor = QBrush(QColor(143, 255, 242))
        self.whiteFontColor = QBrush(QColor(255, 255, 255))
        self.redFontColor = QBrush(QColor(255, 103, 92))
        self.blackFontColor = QBrush(QColor(0, 0, 0))
        self.greyFontColor = QBrush(QColor(150, 150, 150))
        self.darkGreenColor = QColor(55, 109, 99)
        self.darkRedColor = QColor(148, 71, 85)
        self.darkBlueColor = QColor(74, 71, 149)
        self.blueColor = QColor(133, 222, 255)
        self.yellowColor = QColor(255, 250, 123)
        self.darkGreyColor = QColor(50, 50, 50)
        self.cashewbrownColor = QColor(162, 113, 99)
    
    def _initial_UI_setup(self):

        #------------------------
        # set the rest of the UI
        #------------------------

        self.btnAddAsset.setEnabled(False)
        self.btnSearch.setEnabled(False)
        self.build_btn.setEnabled(False)
        self.unset_btn.setEnabled(False)
        self.set_btn.setEnabled(False)
        self.deleteAssetPart_btn.setEnabled(False)
        self.dataFolders_layout.setHidden(True)

    def _initial_project_setting(self):
        # reset project combo box
        self.cbProject.clear()        
        # initial project setting.
        project_dict = util.read_project_file()

        if project_dict:
            for project_item in project_dict:
                self.cbProject.addItem(project_item['project'])

        self.cbProject.currentTextChanged.connect(self._project_changed)

        # initialize Type combo box. 
        self._loadAssetTypeList()

    def _project_changed(self):
        # get current project. 
        curr_project, curr_project_path = self._get_current_project()

        # initialize Type combo box. 
        self._loadAssetTypeList()

        self.currentProject = curr_project

    def __iconManagement(self):
        ''' attach correct items to buttons, QT designer has problems doing this dynamically '''
        def applyPNGIcon(qtObject, qtConnection, iconName, ToolTip = ''):
            qtObject.clicked.connect(qtConnection)
            buttonIcon = QIcon("%s/Icon/%s.png"%(os.path.dirname(__file__), iconName))
            qtObject.setIcon(buttonIcon)
            qtObject.setWhatsThis(ToolTip)

        def applyMayaIcon(qtObject, qtConnection, iconName, ToolTip = ''):
            qtObject.clicked.connect(qtConnection)
            buttonIcon = QIcon(":/%s"%(iconName))
            qtObject.setIcon(buttonIcon)
            qtObject.setWhatsThis(ToolTip)
        
        # applyPNGIcon( self.AvarageWeightButton,      self.avarageVertex,           "AvarageVerts",    "average" )
        # applyPNGIcon( self.btn_script_box_pin,      '',           "pin",    "pined" )

    def _meunbarSetup(self):
        self.actionAdd_Project.triggered.connect(self._add_project_setup)
        # self.actionAdd_Type.triggered.connect()



    def _scriptTableUISetup(self):
        self.tableWidget_main_script_box.setColumnCount(1)
        self.tableWidget_main_script_box.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableWidget_main_script_box.setAlternatingRowColors(True)
        self.tableWidget_main_script_box.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_main_script_box.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.tableWidget_main_script_box.setEditTriggers(QTableWidget.NoEditTriggers) #user cannot edit the cells in the table
        self.tableWidget_main_script_box.verticalHeader().setVisible(False)
        self.tableWidget_main_script_box.horizontalHeader().setVisible(False)

        self.tableWidget_other_script_box.setColumnCount(1)
        self.tableWidget_other_script_box.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tableWidget_other_script_box.setAlternatingRowColors(True)
        # self.tableWidget_other_script_box.setColumnWidth(1, 40)
        self.tableWidget_other_script_box.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_other_script_box.verticalHeader().setVisible(False)
        self.tableWidget_other_script_box.horizontalHeader().setVisible(False)
        self.tableWidget_other_script_box.setEditTriggers(QTableWidget.NoEditTriggers) #user cannot edit the cells in the table

        # script box connections
        self.tableWidget_main_script_box.itemClicked.connect(self._scriptBoxItem)


    def _buttonManagement(self):
        ''' attach processes to buttons''' 
        def connectClicked(button, attachment, ToolTip = ''):
            button.clicked.connect(attachment)

            if not ToolTip == '':
                button.setWhatsThis(ToolTip)

        # connectClicked( self.maxInfluencesButton,      self.setMaxJointInfluences, "maxInf" )

        # self.cbAssetType.
        connectClicked( self.btnTypeRefresh,      self._populateAssetList, '' )

        # Connect btnAdd
        connectClicked( self.btnAddAsset,         self._addAssetButton, '' )

        # Connect btnSearch
        connectClicked( self.btnSearch,           self._searchInCurrentList, '' )

        # Connect clear asset list.
        # connectClicked( self.btnClearSelection , self._assetSelectionClear, '' )

        # Connect Export file.
        connectClicked( self.btnExportAll,        self._exportAll, '' )

        # Connect Open Asset. 
        connectClicked( self.btnOpenAsset,    self._openFile , '')

        # Connect openBrowser
        connectClicked( self.btnOpenBrowser,      self._openBrowser, '' )

        # Connect Import.
        connectClicked( self.btnImportBody,       functools.partial(util.publicFileImport, 'body'), '' )
        connectClicked( self.btnImportScaleBody,  functools.partial(util.publicFileImport, 'scaleBody'), '' )

        # Connect Select Joint.
        connectClicked( self.btnSelectBodyJnt,    functools.partial(util.zepetoJointSelecter, 'body'), '' )
        connectClicked( self.btnSelectHairEarJnt, functools.partial(util.zepetoJointSelecter, 'hair'), '' )

        # Connect Set Pose. 
        connectClicked( self.btnSetTPose,         functools.partial(util.setBasePose, 'TPose'), '' )
        connectClicked( self.btnSetAPose,         functools.partial(util.setBasePose, 'APose'), '' )
        connectClicked( self.btnSetStandPose,     functools.partial(util.setBasePose, 'Stands'), '' )

        # Connect Open CheckTool. 
        connectClicked( self.btnOpenCheckTool, self.open_checkTool_window, '')

        # Connect make snapshot.
        connectClicked( self.btnMakePreviewImage, self._makePreviewImage, '')

        # Connect Export Output.
        connectClicked( self.btn_exportOutputToMaya, self._exportOutputToMaya, '')
        connectClicked( self.btn_exportOutputToFbx, self._exportOutputToFbx, '')

        # Connect add joint label.
        connectClicked( self.btnAddJointLabel, self._addJointLabel, '')

        # Connect add joint label.
        connectClicked( self.btn_script_box_add, self._addCustomScriptDialog, '')

        # Connect save script box.
        connectClicked( self.btn_script_box_save, self._saveScriptBoxItem, '')
        connectClicked( self.btn_script_box_run, self._runManifestItems, '')
        connectClicked( self.btn_script_box_del, functools.partial(self._removeScriptBoxItem, myTable = self.tableWidget_main_script_box), '')
        connectClicked( self.btn_script_box_order_up, functools.partial(self._moveScriptBoxItem, myTable = self.tableWidget_main_script_box, direction = 'up'), '')
        connectClicked( self.btn_script_box_order_down, functools.partial(self._moveScriptBoxItem, myTable = self.tableWidget_main_script_box, direction = 'down'), '')

        connectClicked( self.btn_other_script_box_maya, functools.partial(self._loadScriptBox, loadScriptType='import', scriptBox = 'other'))
        connectClicked( self.btn_other_script_box_move_up, self._addAllScriptBoxItems, '')
        
        connectClicked( self.btn_other_script_box_clear, self._clearOtherScriptBoxItems, '')

    def _makePreviewImage(self):
        # Connect make snapshot.
        # print self.currentAssetType
        # print self.selectedAssetItem

        if self.selectedAssetItem:
            if not self.currentAssetType:
                self.currentAssetType = self.cbAssetType.currentText()

            checkMsg, copyPath = util.makePreviewImage(self.currentAssetType, self.selectedAssetItem)

            if checkMsg:
                self.setStatus('Captured : [ ' + copyPath + ' ]#' ,'m')

                self._refreshAssetItem()

        else:
            self.setStatus('please, select asset.','w')

    def _SetFunctionUtilTab(self):
        self.tabFunctionUtil.setTabText(0, 'scriptsBox')
        self.tabFunctionUtil.setTabText(1, 'Asset')
        self.tabFunctionUtil.setTabText(2, 'Output')

    # -------------- asset tw ----------
    def _SetAssetBrowserTreeWidget(self):
        # clear all item. 
        self.twAssetBrowser.clear()
        self.twAssetBrowser.setHeaderHidden(1)
        self.twAssetBrowser.itemSelectionChanged.connect(self._assetPartSelected)

        # self.twAssetBrowser.itemSelectionChanged.connect(self._checkAssetTreeWidgetItem)
        # self.twAssetBrowser.itemSelectionChanged.connect(self._checkAssetTreeWidgetItem)


    def _checkAssetTreeWidgetItem(self):
        assetWidgetItem = self.twAssetBrowser.currentItem()
        # print(assetWidgetItem.text())
        # self._assetPartSelected()
        # print self.fileTreeWidgetItemList

    # -------------- asset tw ----------


    def _SetFileBrowserTreeWidget(self):
        # clear all item. 
        self.twFileBrowser.clear()

        # set header labels.
        self.twFileBrowser.setHeaderLabels(['no', 'date', 'comment'])

        # item clicked. 
        # self.twFileBrowser.itemSelectionChanged.connect(self._fileBrowserTWClicked())

        # current date and time
        # timeCode = datetime.now()
        # currentTime = timeCode.strftime("%Y-%m-%d, %H:%M:%S")

        # make tree Widget item.
        # test = QTreeWidgetItem(['1', currentTime, 'asdasdqwdqa'])
        # self.twFileBrowser.addTopLevelItem(test)
        
        # refresh ttreewidget. 
        # self._refreshFileBrowserTreeWidget()

        self.twFileBrowser.itemSelectionChanged.connect(self._checkFileTreeWidgetItem)

        self.twFileBrowser.setColumnWidth(0, 35)
        self.twFileBrowser.setColumnWidth(1, 75)

    def _checkFileTreeWidgetItem(self):
        self.fileTreeWidgetItemList = []

        self.fileTreeWidgetItemList.extend(self.twFileBrowser.selectedItems())

        # print self.fileTreeWidgetItemList

    def _openFile(self):
        # project path seletor.
        ASSETTYPELISTPATH = self._project_path_selector()

        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            paths = self._getPathToAssetPart(item = selItem)

            myFilePath = paths['buildFilePath']
            commentPath = paths['buildCommentsFilePath']

            # make current asset path. 
            if selItem.parent():
                if selItem.parent().text(0) == 'data':
                    myFilePath = paths['assetPartPath'] + '/' + selItem.text(0) + '.ma'
                    commentPath = paths['assetPartPath'] + '/versions/comments.yml'
                    
            commentDict = util.readCommentFile(commentPath)
            # get selected Item in file browers.
            # fileTreeWidgetItemList = self.twFileBrowser.selectedItems()
            checkOpen = ''
            treeWidgetItem = ''

            if len(self.fileTreeWidgetItemList) == 1:
                checkOpen = 'verOpen'
                treeWidgetItem = self.fileTreeWidgetItemList[0]

            elif len(self.fileTreeWidgetItemList) > 1:
                self.setStatus('Select One Item.', 'w')

            elif len(self.fileTreeWidgetItemList) == 0:
                checkOpen = 'lastOpen'

            if checkOpen == 'verOpen':
                filePath = treeWidgetItem.toolTip(0)

                # open selected File Item.
                # check modified.
                isModified = cmds.file(q=True, modified=True)

                if isModified:
                    if self.isOpenFile():
                        cmds.file( new = True, force = True ) 
                        cmds.file( filePath, open = True )

                        print 'File Opend -- ' + filePath

                else:
                    # open selected File Item.
                    cmds.file( new = True, force = True )
                    cmds.file( filePath, open = True )

                    print 'File Opend -- ' + filePath

            elif checkOpen == 'lastOpen':
                # get last file path.            
                # lastFilePath = myFilePath

                # open file.
                # check modified.
                isModified = cmds.file(q=True, modified=True)

                if isModified:
                    if self.isOpenFile():
                        cmds.file( new = True, force = True ) 
                        cmds.file( myFilePath, open = True )

                        print 'File Opend -- ' + myFilePath

                else:
                    # open selected File Item.
                    cmds.file( new = True, force = True )
                    cmds.file( myFilePath, open = True )

                    print 'File Opend -- ' + myFilePath


        else:
            self.setStatus('please, select asset.','w')
        # self.twFileBrowser.

    def _exportAll(self):
        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]

            # if we have no item to work with
            # or the item is 'data' or item is top level asset
            # do nothing
            if not selItem or not selItem.isSelected() or selItem.text(0) == 'data' or not selItem.parent():
                self.setStatus('No valid asset part selected.','w')
                return

            # we have an item
            # let's get the paths
            paths = self._getPathToAssetPart(item = selItem)
            
            myFilePath = paths['buildFilePath']
            versionsPath = paths['buildVersionsPath']
            commentFilePath = paths['buildCommentsFilePath']

            if selItem.parent():
                if selItem.parent().text(0) == 'data':
                    myFilePath = paths['assetPartPath'] + '/' + selItem.text(0) + '.ma'
                    versionsPath = paths['assetPartPath'] + '/versions'
                    commentFilePath = paths['assetPartPath'] + '/versions/comments.yml'

            comment = self.get_comment()
            
            if not comment == '':
                exportDict = util.exportFile(myFilePath)
                util.versioningFile(versionsPath, myFilePath, comment)

            self._refreshFileBrowserTreeWidget(selItem)


    def _loadScriptBox(self, loadScriptType = None, scriptBox = None):
        # self.currentAssetType
        # self.currentProject
        # self.selectedAssetItem

        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            paths = self._getPathToAssetPart(item = selItem)

            currWorkingAsset = self._assetListItemPath(selItem)

        # scriptBoxFilePath = None
        # currWorkingAsset = None

        if loadScriptType == 'import':
            scriptBoxFilePath = 'import'
        elif loadScriptType == 'scriptBox':
            scriptBoxFilePath = paths['scriptBoxFilePath']


        if scriptBox == 'main':
            myTable = self.tableWidget_main_script_box
        elif scriptBox == 'other':
            myTable = self.tableWidget_other_script_box

        myTable.clear()
        myTable.setRowCount(0)

        if os.path.isfile(scriptBoxFilePath):
            openFile = open(scriptBoxFilePath, 'r')
            rawData = openFile.read()
            data = yaml.load(rawData, Loader=yaml.FullLoader)
            openFile.close()

            if data:
                # let's iterate through each element in the list
                for rowNum in range(len(data)):
                    myTable.insertRow(rowNum)
                    myTable.setRowHeight(rowNum, 20)

                    myLabel = data[rowNum]['label']
                    myType = data[rowNum]['type']
                    myAction = data[rowNum]['action']
                    myData = data[rowNum]['data']

                    item = QTableWidgetItem(myLabel)
                    item.setData(1001, myType)
                    item.setData(1002, myAction)
                    item.setData(1003, myData)

                    if scriptBox == 'main':
                        myTable.setItem(rowNum, 0, item)

                        if myAction == 'import':
                            myTable.item(rowNum, 0).setBackground(self.cashewbrownColor)

                    if scriptBox == 'other':
                        myTable.setItem(rowNum, 0, item)
                        
                        if myAction == 'import':
                            myTable.item(rowNum, 0).setBackground(self.cashewbrownColor)

        elif scriptBoxFilePath == 'import':
            # the user clicked the 'load imports' button and we have an asset part selected
            # we are going to populate the 'other manifest' table with 'import' actions for
            # the build.mb and all the different 'data' subfolders .mb files
            
            # now let's assemble the full path to the .mb files
            importList = []
            for path in os.listdir(paths['dataPath']):
                importList.append(paths['dataPath'] + '/' + path + '/' + path.split('/')[-1] + '.ma')

            importListSorted = sorted(importList)

            # print indicator
            self._assetIndicator('other')

            row = 0
            for i in range(len(importListSorted)):
                currWorkingAsset_asString = [str(x).upper() for x in currWorkingAsset]
                myLabel = 'import ' + os.path.split(importListSorted[i])[-1] + ' (' + ' / '.join(currWorkingAsset_asString) + ')'
                myType = 'action'
                myAction = 'import'
                myData = importListSorted[i]
                
                # print(os.path.isfile(myData))
                if os.path.isfile(myData):

                    myTable.insertRow(row)
                    myTable.setRowHeight(row, 20)

                    # print(row)
                    item = QTableWidgetItem(myLabel)
                    item.setData(1001, myType)
                    item.setData(1002, myAction)
                    item.setData(1003, myData)
                    # item.setData(1004, 'importMayaFile')
                    # item.setBackground(self.darkGreenColor)
                    
                    mapValue = ','.join([myLabel, myType, myAction, myData])
                    # addBtn = QtWidgets.QPushButton('add', myTable)
                    # self.mapper.setMapping(addBtn, mapValue)
                    # addBtn.clicked.connect(self.mapper.map)

                    # myTable.setCellWidget(row, 0, addBtn)
                    myTable.setItem(row, 0, item)
                    myTable.item(row, 0).setBackground(self.cashewbrownColor)
                    row += 1


    def _addCustomScriptDialog(self):
        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            paths = self._getPathToAssetPart(item = selItem)

            myParent = getMayaWindow()
            customScriptDialog = QInputDialog(myParent)
            customScriptDialog.setTextValue('Script name')
            customScript, ok = QInputDialog.getText(myParent, 'Script', 'Enter the name of the script:')

            if ok and not customScript == '':
                # remove space
                customScript = customScript.replace(' ', '')

                # paths = self._getPathToAssetPart(item)

                myLabel = customScript + '.py'
                myType = 'script'
                myAction = 'run'
                myData = paths['scriptPath'] + '/' + myLabel

                myInfo = ','.join([myLabel, myType, myAction, myData])

                myCustomScriptPath = myData

                # if the script file doesn't exits, let's create it
                if not os.path.isfile(myCustomScriptPath):
                    openFile = open(myCustomScriptPath, 'a').close()

                if os.path.isfile(myCustomScriptPath):
                    pythonContents = '#-----------------------------\n'
                    pythonContents += '# This file was created automaticaly.\n'
                    pythonContents += '# Some information were added to it. Feel free to add/remove/change this file.\n'
                    pythonContents += '# This file uses a 4 space indentation.\n'
                    pythonContents += '# If you are using Tabs, set it to use 4 spaces.\n'
                    pythonContents += '#-----------------------------\n\n'

                    pythonContents += 'import os # OS, files and folders package\n'
                    pythonContents += 'import imp # used to import python modules using full path\n'
                    pythonContents += 'import yaml # To parse yaml files like the config one\n'
                    pythonContents += 'import maya.cmds as cmds # Maya commands for Python\n'
                    pythonContents += 'import maya.mel as mel # To execute MEL code within Python\n'
                    pythonContents += 'import maya.OpenMaya as om # Maya Python API when performance is need\n\n\n'

                    pythonContents += '# DO NOT modify the name of this funtion. Other scripts are expecting and calling this name\n'
                    pythonContents += 'def _main(**kwargs):\n\n'
                    pythonContents += '    # This function carries a list of arguments (kwargs)\n'
                    pythonContents += '    # If you want to know which variables this list is carrying you can just print it.\n'
                    pythonContents += '    # Bellow is the one variable that is always passed over:\n\n'
                    pythonContents += '    assetPartPath = kwargs["assetPartPath"]\n'
                    pythonContents += '    print assetPartPath\n\n'
                    pythonContents += '    # YOUR CODE HERE .....\n'

                    pythonContents += '    \n\n'
                    pythonContents += '\n\n'
                    pythonContents += '#-----------------------------\n'
                    pythonContents += '# END OF FILE\n'
                    pythonContents += '#-----------------------------\n'

                    openFile = open(myCustomScriptPath, 'w')
                    openFile.write(pythonContents)
                    openFile.close()
                    # file_utils.simple_chmod(myCustomScriptPath)
                
                # let's send the info to the function that adds items into the manifest
                self._addScriptBoxItem(myInfo)
                # print(myInfo)

    def _addScriptBoxItem(self, myInfo):
        # get my info
        # print(myInfo)
        myLabel, myType, myAction, myData = myInfo.split(',')

        # let's find out if there is an item already in the table
        overwrite = False
        existingItemList = self.tableWidget_main_script_box.findItems(myLabel, Qt.MatchFixedString)

        # if script box has duplicates, ask user to check
        if len(existingItemList) == 1:
            msgBox = QMessageBox()
            msgBox.setText(myLabel + ' already exists!')

            answer = None
            msgBox.setInformativeText('Do you want to overwrite it?')
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Cancel)
            answer = msgBox.exec_()

            if answer == QMessageBox.Ok:
                overwrite = True

        # items inserted from 'other manifest' are dressed as italic and blue
        myFont = QFont()
        myFont.setItalic(True)

        # let's create the new item and set all the information
        item = QTableWidgetItem(myLabel)
        item.setData(1001, myType)
        item.setData(1002, myAction)
        item.setData(1003, myData)
        # item.setData(1004, myExtraData)

        # let's apply the font
        item.setFont(myFont)

        # let's insert the new row bellow the selected rows (or above if the selected is the first one)
        # if there are no selected rows, we insert at the end of the table
        if len(existingItemList) == 0:
            lastRow = self.tableWidget_main_script_box.rowCount()
            selRanges = self.tableWidget_main_script_box.selectedRanges()

            lastSelRow = 0
            for l in selRanges:
                if l.bottomRow() > lastSelRow:
                    lastSelRow = l.bottomRow() + 1
            
            insertRow = lastSelRow if selRanges else lastRow

            self.tableWidget_main_script_box.insertRow(insertRow)
            self.tableWidget_main_script_box.setRowHeight(insertRow, 20)
            self.tableWidget_main_script_box.setItem(insertRow, 0, item)

        elif len(existingItemList) == 1 and overwrite:
            insertRow = existingItemList[0].row()
            self.tableWidget_main_script_box.setItem(insertRow, 0, item)

        # now that the item is set into the table we can change the cell background color
        # if the item is a 'loading' action
        if myAction == 'import':
            self.tableWidget_main_script_box.item(insertRow, 0).setBackground(self.cashewbrownColor)

        self.btn_script_box_save.setEnabled(True)

        return True

    def _addAllScriptBoxItems(self):
        '''
        adds all scripts to the loaded manifest
        '''
        if self.tableWidget_other_script_box.rowCount() > 0:
            for item in self.tableWidget_other_script_box.selectedItems():
                
                myLabel = str(item.text())
                myType = str(item.data(1001))
                myAction = str(item.data(1002))
                myData = str(item.data(1003))

                mapValue = ','.join([myLabel, myType, myAction, myData])
                self._addScriptBoxItem(mapValue)

    def _removeScriptBoxItem(self, myTable):
        '''
        removes the selected rows
        '''
        sel = myTable.selectedItems()

        for item in sel:
            myTable.removeRow(item.row())

        self._clearTableSelection(myTable = myTable)


    def _clearOtherScriptBoxItems(self):
        myTable = self.tableWidget_other_script_box

        myTable.clear()
        myTable.setRowCount(0)

    def _clearTableSelection(self, myTable = None):
        '''
        clears the selection on the table
        '''
        myTable.clearSelection()
        myTable.setCurrentCell(-1, 0)
    
    def _runManifestItems(self):
        '''
        collects the selected items from the manifest table and run each line in order
        '''
        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            paths = self._getPathToAssetPart(item = selItem)

            asset = selItem.text(0)

        # let's setup a progress bar
        total = len(self.tableWidget_main_script_box.selectedItems())
        mayaWindow = getMayaWindow()
        myProgressDialog = QProgressDialog('Processing...', 'Abort', 0, total, mayaWindow)
        myProgressDialog.setWindowModality(Qt.WindowModal)
        myProgressDialog.setMinimumDuration(500)

        # let's iterate through the items to run
        itemsProcessed = 0
        for item in self.tableWidget_main_script_box.selectedItems():
            # let's check if user cancelled it
            if myProgressDialog.wasCanceled():
                break

            # we are going to try run each item
            try:
                myLabel = str(item.text())
                myType = str(item.data(1001))
                myAction = str(item.data(1002))
                myData = str(item.data(1003))

                # let's update the progress bar
                myProgressDialog.setLabelText('Processing... ' + myLabel)

                if myType == 'action':
                    # let's check which action to perform
                    if myAction == 'import':
                        # let's check if the path (myData) is valid, otherwise, we do nothing
                        myData = os.path.expandvars(myData)
                        if os.path.isfile(myData):
                            # let's check if it's a model file
                            path, filename = os.path.split(myData)

                            print 'Importing file: ' + filename
                            cmds.file(myData, force = True, i = True, ignoreVersion = True)
                            print '---------------------------------------'

                    cmds.dgdirty(allPlugs = True)

                elif myType == 'script':
                    # USING IMP
                    
                    # let's check if the path (myData) is valid, otherwise, we do nothing
                    myData = os.path.expandvars(myData)
                    if os.path.isfile(myData):
                        # if_runManifestItems it's a python script, we need to load it first before running it
                        # if it's a MEL script, we need to source it in Maya before running it
                        filePath, filename = os.path.split(myData)
                        baseName, extension = os.path.splitext(filename)
                        if extension == '.py':
                            # let's load the script
                            fp, pathname, description = imp.find_module(baseName, [filePath])
                            # fp is the opened file object returned by the 'find_module'
                            # we need to close it after we are done with it
                            try:
                                module = imp.load_module(baseName, fp, pathname, description)
                            except:
                                print 'Could not load ' + filePath
                            finally:
                                fp.close()
                            # filePath2 = os.path.expandvars(filePath)
                            # module = imp.load_source(baseName, filePath2)
                            # if we loaded the module and it has a function named '_main'
                            # print module+'//aa'
                            if module:
                                print str(baseName) + ' module loaded'
                                if hasattr(module, '_main'):
                                    try:

                                        importStr = 'python "import '+baseName+'"'
                                        mel.eval(importStr)

                                        commandStr = 'python "'+baseName+'._main(assetPartPath=\\"'+paths['assetPartPath']+'\\", assetName=\\"'+str(asset)+'\\")"'

                                        cmds.dgdirty(allPlugs=True)
                                        cmds.refresh(force=True)
                                        
                                        mel.eval(commandStr)

                                    except:
                                        raise




                        elif extension == '.mel':
                            # let's source the script
                            print 'it is a MEL script... I will deal with it later'
                    else:
                        print 'could not find the script'
                        print myData

            except:
                pass

            # let's update the progress bar
            itemsProcessed += 1
            myProgressDialog.setValue(itemsProcessed)

        # let's update the progress bar
        myProgressDialog.setValue(total)

        # let's set all plugs to be dirty (for evaluation and debugging)
        # not sure if we really need this one, but I will reconsider it later
        #cmds.dgdirty(allPlugs = True)

        cmds.select(None)

    def _saveScriptBoxItem(self):
        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            paths = self._getPathToAssetPart(item = selItem)
            scriptBoxFilePath = paths['scriptBoxFilePath']
            scriptFolderPath = paths['scriptPath']

        # creates the manifest file if it doesn't exist
        if not os.path.isfile(scriptBoxFilePath):
            openFile = open(scriptBoxFilePath, 'a').close()

        instructionList = []
        # if we have a manifest file to save
        if os.path.isfile(scriptBoxFilePath):
            for row in range(self.tableWidget_main_script_box.rowCount()):
                currItem = self.tableWidget_main_script_box.item(row, 0)
                
                myLabel = str(currItem.text())
                myType = str(currItem.data(1001))
                myAction = str(currItem.data(1002))
                myData = str(currItem.data(1003))

                instructionList.append({'label':myLabel, 'type':myType, 'action':myAction, 'data':myData})

            # if the script folder doesn't exist, create it
            if not os.path.isdir(scriptFolderPath):
                os.makedirs(scriptFolderPath)

            # let's save the manifest file
            openFile = open(scriptBoxFilePath, 'w')
            openFile.write(yaml.safe_dump(instructionList, default_flow_style = False, encoding='utf-8', allow_unicode=True))
            openFile.close()

            # 
            self.setStatus('ScriptBox list saved.','w')
    
    def _moveScriptBoxItem(self, myTable = None, direction = None):
        '''
        Moves the selected items from 'myTable' in the provided 'direction'
        '''
        # let's get the user selection
        mySel = myTable.selectedItems()
        myRanges = myTable.selectedRanges()

        # if we have a selection
        if mySel:
            # let's collect the original row indices
            oldIndices = []
            for item in mySel:
                oldIndices.append(myTable.row(item))
            
            # let's setup the increment based on direction
            # and sort the indeces to that
            increment = 0
            canSwap = False
            if direction == 'up':
                oldIndices = sorted(oldIndices)
                increment = -1

                # let's find out if we have room to swapp
                canSwap = True if oldIndices[0] != 0 else False
            elif direction == 'down':
                oldIndices = sorted(oldIndices, reverse = True)
                increment = 1

                # let's find out if we have room to swapp
                canSwap = True if oldIndices[0] + 1 != myTable.rowCount() else False

            if canSwap:
                # per row, let's collect source and destination rows
                # and swap them
                for index in oldIndices:
                    sourceRow = myTable.takeItem(index, 0)
                    destRow = myTable.takeItem(index + increment, 0)

                    myTable.setItem(index, 0, destRow)
                    myTable.setItem(index + increment, 0, sourceRow)

                # let's clear the selection
                #newRange = QtWidgets.QTableWidgetSelectionRange(, 0, 0, 0)
                myTable.clearSelection()
                myTable.setCurrentCell(-1, 0)

                # let's select the original selection but in the new rows
                for selRange in myRanges:
                    topRow = selRange.topRow() + increment
                    bottomRow = selRange.bottomRow() + increment
                    newRange = QTableWidgetSelectionRange(topRow, 0, bottomRow, 0)
                    myTable.setRangeSelected(newRange, True)

    def _scriptBoxItem(self, item):
        '''
        prints to script editor in case user wants to copy full path or check it
        '''
        print '-----------------------'
        print 'myLabel: ' + str(item.text())
        print 'myType: ' + str(item.data(1001))
        print 'myAction: ' + str(item.data(1002))
        print 'myData: ' + os.path.expandvars(str(item.data(1003)))
        print '-----------------------'

    def _loadAssetTypeList(self):
        # project path seletor.
        ASSETTYPELISTPATH = self._project_path_selector()

        # print(ASSETTYPELISTPATH)
        # clear all type list. 
        self.cbAssetType.clear()

        # call assetType list.
        if ASSETTYPELISTPATH:
            assetTypeDict = util.assetListDir(ASSETTYPELISTPATH, 'd')
            assetTypeNameList = assetTypeDict.keys()

            # add assetType list.
            self.cbAssetType.addItems(assetTypeNameList)

        # return assetTypeNameList

    def _populateAssetList(self):
        # let's read from the ui (project and asset type comboboxes)
        self.currentProject = str(self.cbProject.currentText())
        self.currentAssetType = str(self.cbAssetType.currentText())

        # let's clear the asset table first
        self.twAssetBrowser.clear()

        # let's read from the ui (project and asset type comboboxes)
        ASSETTYPELISTPATH = self._project_path_selector()

        selType = self.cbAssetType.currentText()
        # ASSETTYPEPATH = ASSETTYPELISTPATH + '/' + selType


        # let's get the path to the asset type (chr, prp, set, etc)
        # paths = self._getPathToAssetPart()
        assetTypePath = ASSETTYPELISTPATH + '/' + selType

        # let's try getting the asset list from Coffer
        # if fails, let's read the folders
        assetList = []
        assetList = os.listdir(assetTypePath)

        # to decorate
        myFont = QFont()
        myFont.setItalic(True)

        # progress bar here
        total = len(assetList)
        itemsProcessed = 0
        cmds.progressWindow(title = 'Reading folders',
                            progress = itemsProcessed,
                            status = 'Reading.... ',
                            isInterruptable = False)

        # let's iterate all the assets
        for myAsset in assetList:

            # let's update the progress bar
            cmds.progressWindow(edit = True, progress = itemsProcessed, status = ('Reading.... ' + myAsset))
            # let's update the progress bar
            itemsProcessed += 1


            # since we don't know if the asset is coming from Coffer or the folders...
            asset = myAsset

            # create and setup the top level item
            topLevelItem = QTreeWidgetItem()
            topLevelItem.setText(0, asset)
            topLevelItem.setFont(0, myFont)
            topLevelItem.setForeground(0, self.blueColor)
            topLevelItem.setBackground(1, self.darkGreyColor)

            self.twAssetBrowser.addTopLevelItem(topLevelItem)

            # find out any rigging parts
            assetPath = assetTypePath + '/' + asset
            finalPath = assetPath

            # each key in this dictionary is the path to the asset part
            # each value in this dictionary is the item widget associated with the asset part
            currDict = {asset:topLevelItem}


            # let's navegate through all the folders/subfolders inside the 'autorig' folder for the current asset
            subFolders_list = list(set(self._listSubDirs(finalPath)))
            for info in sorted(subFolders_list):

                # let's see if we need to ignore the current folder/subfolder
                partialPath = info.split(assetPath)[1]
                folderArray = partialPath.split('/')
                folder = folderArray[-1]

                # let's build the path to the item and parent
                # this will be a new key in the dictionary
                itemPath = asset + info.split(finalPath)[-1]
                parentPath = asset + info.split(finalPath)[1].rsplit('/', 1)[0]


                # let's get the parent item
                # when adding a new widget item to a treeWidget, we need to specify
                # which tree item will be it's parent
                parentItem = currDict[parentPath]

                # let's create the new tree item, assign it to it's parent,
                # add the new item to the dictionary and change the text that will be shown
                # in the tree UI
                currDict[itemPath] = QTreeWidgetItem(parentItem)
                currDict[itemPath].setText(0, folder)

                # we don't want to allow the user to 'SET' the 'data' folder as an asset
                mayaFilePath = ''
                if folder == 'data':
                    currDict[itemPath].setFont(0, myFont)
                    currDict[itemPath].setForeground(0, self.yellowColor)

                if parentItem.text(0) == 'data':
                    currDict[itemPath].setForeground(0, self.yellowColor)

        # let's update the progress bar
        cmds.progressWindow(endProgress = 1)

        # resize the columns
        self.twAssetBrowser.resizeColumnToContents(0)
        self.twAssetBrowser.resizeColumnToContents(1)
        self.twAssetBrowser.sortItems(0, Qt.SortOrder(Qt.AscendingOrder))


    def _assetPartSelected(self):
        # reset btn click
        assetList = self.assetItemList.keys()
        selType = self.cbAssetType.currentText()
        self.currentAssetType = selType

        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            paths = self._getPathToAssetPart(item = selItem)

            # if it's the 'data' or top level, we clear the history table and disable the buttons
            # if selItem.text(0) == 'data' or not selItem.parent():
            if selItem.text(0) == 'data' or not selItem.parent():
                # clear the table
                self.twFileBrowser.clear()

                # disable buttons for save/load/import
                self.btnExportAll.setEnabled(False)
                self.btnOpenAsset.setEnabled(False)
                self.btnImportAsset.setEnabled(False)

            elif selItem.parent() and selItem.parent().text(0) == 'data':
                # enable buttons for save/load/import
                self.btnExportAll.setEnabled(True)
                self.btnOpenAsset.setEnabled(True)
                self.btnImportAsset.setEnabled(True)

                self.selectedAssetItem = selItem.text(0)
            else:
                # we enable the buttons
                self.btnExportAll.setEnabled(True)
                self.btnOpenAsset.setEnabled(True)
                self.btnImportAsset.setEnabled(True)

                self.selectedAssetItem = selItem.text(0)

            # if not a 'data' folder or top level asset
            if not selItem.text(0) == 'data' and selItem.parent():
                # let's populate the history table based on the new asset part selection
                # self._populateBuildHistoryList(selItem)
                self.selectedAssetItem = selItem.text(0)
                self._refreshFileBrowserTreeWidget(selItem)
                
                # load script box path
                self._loadScriptBox(loadScriptType = 'scriptBox', scriptBox = 'main')

                # print indicator. 
                self._assetIndicator('main')



            # we should not allow 'add part' to 'data' subfolders
            self.btnAddAsset.setEnabled(True)
            self.leAddAsset.setEnabled(True)

            if selItem.parent():
                if selItem.parent().text(0) == 'data':
                    self.btnAddAsset.setEnabled(False)
                    self.leAddAsset.setEnabled(False)
    
    def _refreshFileBrowserTreeWidget(self, item):
        # clear all item. 
        self.twFileBrowser.clear()

        # if we have no item to work with
        # or the item is 'data' or item is top lavel asset
        # do nothing
        if not item or item.text(0) == 'data' or not item.parent():
            return

        # project path seletor.
        # let's get the paths
        ASSETTYPELISTPATH = self._project_path_selector()
        paths = self._getPathToAssetPart(item = item)

        # let's check if the item is a 'data' subfolder
        if item.parent().text(0) == 'data':
            # this would be the default 'comments' file path
            commentsFilePath = paths['assetPartPath'] + '/versions/comments.yml'

            # but we are going to change it for special cases
            if item.text(0) == 'blendWeights':
                commentsFilePath = paths['assetPartPath'] + '/versions/comments.yml'
        else:
            commentsFilePath = paths['buildCommentsFilePath']
            # print(commentsFilePath)
            # print(os.path.isfile(commentsFilePath))


        # let's parse the comments file and populate the history table
        if os.path.isfile(commentsFilePath):
            commentDict = util.readCommentFile(commentsFilePath)
            # commentDict.sort(reverse=True)
            if commentDict:
                for i in reversed(range(len(commentDict))):

                    # add QTreeWidget
                    commentItem = QTreeWidgetItem( [ commentDict[i]['version'], commentDict[i]['date'], commentDict[i]['comment'] ] )
                    commentItem.setToolTip(0,commentDict[i]['file'])

                    self.twFileBrowser.addTopLevelItem(commentItem)



    def _getPathToAssetPart(self, item = None, array = None, part = None):
        # initial path dict.
        paths = {}
        paths['assetTypePath'] = ''
        paths['assetPath'] = ''
        paths['assetPartPath'] = ''
        paths['dataPath'] = ''
        paths['buildFilePath'] = ''
        paths['buildVersionsPath'] = ''
        paths['buildCommentsFilePath'] = ''
        paths['scriptPath'] = ''
        paths['scriptBoxFilePath'] = ''

        # project path seletor.
        projectPath = self._project_path_selector()

        if not self.currentAssetType:
            self.currentAssetType = self.cbAssetType.currentText()

        assetTypePath = projectPath + '/' + self.currentAssetType
        paths['assetTypePath'] = assetTypePath


        treeArray = []
        if item and not array:
            treeArray = self._assetListItemPath(item)
        elif array and not item:
            treeArray = array

        if treeArray:
            assetName = treeArray[0]
            assetPath = assetTypePath + '/' + treeArray[0]
            assetPartPath = assetPath

            if len(treeArray) > 1:
                for d in treeArray[1:]:
                    assetPartPath += str('/' + d)
    
            if part:
                assetPartPath += str('/' + part)

            paths['assetPath'] = str(assetPath)
            paths['assetPartPath'] = str(assetPartPath)
            paths['dataPath'] = str(assetPartPath + '/data')
            paths['buildFilePath'] = str(assetPartPath + '/data/build/build.ma')
            paths['buildVersionsPath'] = str(assetPartPath + '/data/build/versions')
            paths['buildCommentsFilePath'] = str(assetPartPath + '/data/build/versions/comments.yml')
            paths['scriptPath'] = str(assetPartPath + '/scripts')
            paths['scriptBoxFilePath'] = str(assetPartPath + '/scriptBox.yml')

        return paths            

    def _assetListItemPath(self, item):
        '''
        When the user has some item selected in the Asset List (QTreeWidget),
        this function is used to retrieve the branch for the selected item.

        @param:
        - item: the QTreeWidgetItem current selected by the user

        @return:
        - myList: a python list containing all the elements that build up the branch
        '''
        myFolders = []
        currItem = item
        while currItem is not None:
            myText = currItem.text(0)
            myFolders.append(myText)
            currItem = currItem.parent()

        myList = [x for x in reversed(myFolders)]
        return myList

    def _listSubDirs(self, path):
        '''
        '''
        skip = ['build', 'scripts', 'versions', '.mayaSwatches']
        dirs = []
        
        if os.path.isdir(path):
            subDirs = os.listdir(path)

            for d in subDirs:
                if os.path.isdir(path + '/' + d):
                    if d not in skip:
                        if (path + '/' + d) not in dirs:
                            dirs.append(path + '/' + d)
            for d in dirs:
                dirs += self._listSubDirs(d)

        return dirs

    def _assetIndicator(self, myLabelType = None):

        if myLabelType == 'main':
            myLabel = self.lbCurrentAssetIndicator
        elif myLabelType == 'other':
            myLabel = self.lb_other_asset_indicator

        # get assetType.
        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            selectedBranch = self._assetListItemPath(selItem)

            myLabelText = self.currentProject.upper() + ' ----- '
            myLabelText += ' / '.join(str(info) for info in selectedBranch)

            myLabel.setText(myLabelText)
            myLabel.setAlignment(Qt.AlignCenter)

            if myLabelType == 'main':
                myLabel.setStyleSheet("QLabel {background-color: lightgreen;color:gray}")
            elif myLabelType == 'other':
                myLabel.setStyleSheet("QLabel {background-color: #FF8F8F;color:gray}")

        else:
            myLabel.setText('--- / ---')

            myLabel.setAlignment(Qt.AlignCenter)
            myLabel.setStyleSheet("QLabel {background-color: #FF8F8F;color:gray}")


    def _openBrowser(self):
        mySelection = self.twAssetBrowser.selectedItems()
        if mySelection:
            selItem = mySelection[0]
            selType = self.cbAssetType.currentText()
        
            # project path seletor.
            ASSETTYPELISTPATH = self._project_path_selector()

            paths = self._getPathToAssetPart(selItem)

            # build dir path. 
            assetDirPath = paths['assetPartPath']
            
            assetDirPath = assetDirPath.replace('/', '\\')

            # open browser.
            subprocess.call("explorer {}".format(assetDirPath), shell=True)
            # subprocess.Popen(r'explorer /select,"{}"'.format(assetDirPath))
        else:
            self.setStatus('please, select asset.','w')

    def _refreshAssetItem(self):

        selType = self.cbAssetType.currentText()

        assetList = self.assetItemList.keys()
        assetList.sort(key=self.natural_keys)

        # clear assetItemList. 
        self._clearAssetItem()

        # contain current layout tpye.
        self.currentAssetType = selType

        # add new button.
        '''
        for assetName in assetItemList:
            btn = AssetButton.AssetButton(assetName, selType)
            self.flowLayout.addWidget(btn)

            self.assetItemList[assetName] = btn
            '''

    def _clearAssetItem(self):
        #Iterate objects in flowlyt itemList
        self.twAssetBrowser.clear()

        # initial asset dict.
        self.selectedAssetItem = ''
        self.currentAssetType = ''
        self.assetItemList = {}

        self.assetTreeWidgetItemList = []
              
    # SEARCH FUNCTION 
    #------------------------------------------------------------------  
    def _searchInCurrentList(self):
        searchString = self.leSearch.text()
        selType = self.cbAssetType.currentText()

        # split in search String.
        tempSearchList = searchString.split(',')
        searchItemList = []

        # remove un used space
        for searchItem in tempSearchList:
            searchItemList.append(searchItem.replace(' ', ''))

        # remove empty item.
        for i in  range(len(searchItemList)):
            if searchItemList[i] == '':
                searchItemList.remove(searchItemList[i])

        # project path seletor.
        ASSETTYPELISTPATH = self._project_path_selector()

        # make assetType path.
        ASSETTYPEPATH = ASSETTYPELISTPATH + '/' + selType
        # print ASSETTYPEPATH

        assetDirDict = util.assetListDir(ASSETTYPEPATH, 'd')
        # print assetDirDict

        assetNameList = assetDirDict.keys()


        # assetList = self.assetItemList.keys()
        # print assetList
        # print searchItemList

        matchingList = []

        for searchItem in searchItemList:
            matching = [s for s in assetNameList if searchItem in s]
            matchingList.extend(matching)

        # print matchingList
        # clear assetItemList. 
        self._clearAssetItem()

        # contain current layout tpye.
        self.currentAssetType = selType

        for assetName in matchingList:
            assetItem = QTreeWidgetItem( [assetName] )
            self.twAssetBrowser.addTopLevelItem(assetItem)
            self.assetItemList[assetName] = assetItem


    #addAssetButton
    def _addAssetButton(self):
    
        #ADD Asset
        #------------------------------------------------------------------
        selType = self.cbAssetType.currentText()
        newAssetName = self.leAddAsset.text()

        # let's get the value of the text field. This will be our part name
        # let's remove from it all whitespaces
        newAssetName = newAssetName.replace(' ', '')

        if newAssetName:
            # let's get the current item selected from the asset list
            selItem = self.twAssetBrowser.currentItem()

            if selItem:
                paths = self._getPathToAssetPart(item = selItem, part = newAssetName)

                assetPartPath = paths['assetPartPath']

                # if the part already exists, do nothing
                if os.path.exists(assetPartPath):
                    return

                # let's find out if the new part is a real part or a 'data' part
                partType = ''
                if selItem.text(0) == 'data':
                    partType = 'data'
                else:
                    partType = 'part'
                    if selItem.parent() and selItem.parent().text(0) == 'data':
                        return

                # user is adding a new part (not a data part)
                if partType == 'part':
                    # build the paths
                    buildVersionsPath = paths['buildVersionsPath'] # creates /build/versions
                    buildCommentsFilePath = paths['buildCommentsFilePath'] # creates /build/versions/comments.yml
                    scriptPath = paths['scriptPath'] # creates /scripts
                    scriptBoxFilePath = paths['scriptBoxFilePath'] # creates /manifest.yml

                    # create the paths and the empty file
                    os.makedirs(buildVersionsPath)
                    os.makedirs(scriptPath)

                    open(scriptBoxFilePath, 'a').close()
                    open(buildCommentsFilePath, 'a').close()


                    # update the asset list tree with the new part
                    partItem = QTreeWidgetItem(selItem)
                    partItem.setText(0, newAssetName)
                    partItem.setText(1, '-')

                    myFont = QFont()
                    #myFont.setItalic(True)
                    
                    dataItem = QTreeWidgetItem(partItem)
                    dataItem.setText(0, 'data')
                    dataItem.setText(1, '-')
                    dataItem.setFont(0, myFont)
                    dataItem.setForeground(0, self.yellowColor)
                
                elif selItem.text(0) == 'data':
                    # the user is adding a 'data' subfolder
                    myPath = assetPartPath + '/versions'
                    os.makedirs(myPath)
                    open(myPath + '/comments.yml', 'a').close()

                    # update the asset list tree with the new part
                    dataItem = QTreeWidgetItem(selItem)
                    dataItem.setText(0, newAssetName)
                    dataItem.setText(1, '-')

                    myFont = QFont()
                    myFont.setItalic(True)

                    dataItem.setFont(0, myFont)
                    dataItem.setForeground(0, self.yellowColor)

                self.leAddAsset.clear()
                selItem.setSelected(True)
            else:
                self.setStatus('select at least one item', 'w')
        else:
            self.setStatus(newAssetName + ' is no proper name', 'w')
            self.leAddAsset.clear()

    #setStatus
    def setStatus(self, msg, type):
        if type == 'w':
            self.mainStatusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:red;font-weight:bold;}")
            self.mainStatusbar.showMessage(msg, 5000)
        if type == 'm':
            self.mainStatusbar.setStyleSheet("QStatusBar{padding-left:8px;background:rgba(0,0,0,0);color:yellow;font-weight:bold;}")
            self.mainStatusbar.showMessage(msg, 5000)

    #resizePoseButtons
    def resizePoseButtons(self):
        #Iterate through items in itemList and resize
        newBtnSize = self.getPoseButtonSize()
        for item in self.flowLayout.itemList:
            item.widget().resizeAssetButton(newBtnSize, newBtnSize)

    #getPoseButtonSize
    def getPoseButtonSize(self):
        return self.sldButtonSize.value()

    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [ self.atoi(c) for c in re.split(r'(\d+)', text) ]

    #Flowlayout methods
    #------------------------------------------------------------------
    
    #getItemListObjectNames
    def getItemListObjectNames(self):
        
        objectNamesList = []
        
        for item in self.flowLayout.itemList:
            objectNamesList.append(item.widget().getAssetName())
        
        return objectNamesList
    
        
    #printLayoutItems
    def printLayoutItems(self, lyt):
        for index in range(0, lyt.count()):
            print('item: %s objectName: %s' % (index, lyt.itemAt(index).widget().getAssetName()))

    def get_comment(self):

        myParent = getMayaWindow()
        commentDialog = QInputDialog(myParent)
        commentDialog.setTextValue('input')
        comment, ok = QInputDialog.getText(myParent, 'Comment', 'Your comment please...')

        commentText = ''
        if ok:
            commentText = comment

        return commentText

    def isOpenFile(self):
        myParent = getMayaWindow()
        open_file_dialog = QMessageBox(myParent)
        open_file_dialog.setText('The current file has been changed. \nOpen the file?')
        open_file_dialog.setStandardButtons(QMessageBox.Yes|QMessageBox.No)
        button_open = open_file_dialog.button(QMessageBox.Yes)
        button_open.setText('Open')

        button_cancel = open_file_dialog.button(QMessageBox.No)
        button_cancel.setText('Cancel')
        open_file_dialog.exec_()
        # checkOpen = OpenCheckDlg()
        isStatus = ''
        if open_file_dialog.clickedButton() == button_open:
            isStatus = True
        elif open_file_dialog.clickedButton() == button_cancel:
            isStatus = False

        return isStatus

    def open_checkTool_window(self):

        if not self.currentAssetType:
            self.currentAssetType = self.cbAssetType.currentText()

        currentAssetDict = {}
        currentAssetDict['type']  = self.currentAssetType
        currentAssetDict['Asset'] = self.selectedAssetItem

        try:
            self.checkToolWindow.close()
        except:
            pass

        self.checkToolWindow = CheckToolUI(currentAssetDict, self)

        checkWindow = self.checkToolWindow

        self.checkToolWindow.show()

    # ==============================
    # export output
    # ==============================
    def _exportOutputToMaya(self):

        util.exportOutput(self.currentAssetType, self.selectedAssetItem, 'maya')

    def _exportOutputToFbx(self):

        util.exportOutput(self.currentAssetType, self.selectedAssetItem, 'fbx')


    # ==============================
    # Convert to Scale Joint.
    # ==============================
    def _convertToScaleJnt(self):

        util.scaleSkinConverter(self.currentAssetType, self.selectedAssetItem)

    # ==============================
    # set physics value name.
    # ==============================
    def _setPhysicsVal(self):
        jntList = cmds.ls(sl=1)

        phyDrag = self.sbPhysicsDrag.value()
        phyAngelDrag = self.sbPhysicsAngelDrag.value()
        phyRestoreDrag = self.sbPhysicsRestoreDrag.value()

        phyValues = [phyDrag, phyAngelDrag, phyRestoreDrag]

        if len(jntList):
            util.setPhysicsVal(jntList, phyValues)

        else:
            cmds.warning('There is nothing selected.')

    def _setPhysicsDefaultVal(self):
        self.sbPhysicsDrag.setValue(15)
        self.sbPhysicsAngelDrag.setValue(25)
        self.sbPhysicsRestoreDrag.setValue(40)

    # ==============================
    # set physics value name.
    # ==============================
    def _finalizeShoesAsset(self):

        util.finalizeShoesAsset(self.currentAssetType, self.selectedAssetItem)

    # ==============================
    # set physics value name.
    # ==============================
    def _makeHairGuideMesh(self):
        jointList = cmds.ls(sl=1)
        if jointList:
            util.makeHairGuideMesh(jointList)

    # ==============================
    # add joint label
    # ==============================
    def _addJointLabel(self):
        util.setJointLabel()

    # ==============================
    # project setup
    # ==============================
    def _add_project_setup(self):
        myParent = getMayaWindow()
        projectDialog = QFileDialog(myParent)

        project_path = QFileDialog.getExistingDirectory(myParent,"Choose Project Directory","C:\\")
        # project, ok = QInputDialog.getText(myParent, 'Comment', 'Your comment please...')
        
        # if not ok:
        #     return
        if project_path:
            util.setup_project_folder(project_path)

            self._initial_project_setting()

            myProject = project_path.split('/')[-1]
            print("---------------------------------------")
            print(myProject + " --- Added project.")
            print("---------------------------------------")

    def _get_current_project(self):
        current_project = self.cbProject.currentText()

        # get project list.
        project_dict = util.read_project_file()
        current_project_path = ''

        if project_dict:
            for project_item in project_dict:
                if project_item['project'] == current_project:
                    current_project_path = project_item['path']

        return current_project, current_project_path

    def _project_path_selector(self):
        # get current project.
        current_project, current_project_path = self._get_current_project()

        # initial asset path 
        '''
        if current_project == 'zepeto':
            ASSETTYPELISTPATH = util.ASSETPATH + 'PR'
        else:
            ASSETTYPELISTPATH = current_project_path + '/asset'
        '''
        asset_type_path = None

        if current_project:
            asset_type_path = current_project_path + '/asset'

        return asset_type_path


# =========================================================================
# end of blachagiRigTools


class CommentDlg(QDialog):

    def __init__(self):
        super(CommentDlg, self).__init__()

        self.comment = QLineEdit()
        # self.password.setEchoMode(QLineEdit.Password)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QFormLayout()
        layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow(self.comment)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.setWindowTitle("Comment")
        self.setMinimumWidth(250)


class CheckToolUI(Ui_checkToolWindow, Ui_checkToolBaseClass):
    def __init__(self, currentAssetDict, parent = None):
        super(CheckToolUI, self).__init__(parent)
        self.setupUi(self)

        # ===== Style sheet =====
        QT_COLORTHEME = "Lime"
        QT_STYLESHEET = os.path.normpath(os.path.join(__file__, "../q%s.stylesheet"%QT_COLORTHEME))
        
        with open( QT_STYLESHEET, "r" ) as fh:
            self.setStyleSheet( fh.read() )

        self.currentType = currentAssetDict['type']
        self.currentAsset = currentAssetDict['Asset']

        # initial values
        self.checkContentsList = []

        # setup window title.
        self.setWindowTitle( 'CheckTool' )
        
        # set indicator.
        self._assetIndicator()

        self._setupCheckItem()

        # connect check all button.
        self.btnCheckAll.clicked.connect(self._checkAll)

        # connect output
        self.btnExportMayaFile.clicked.connect(self._exportOutputToMaya)
        self.btnExportFBX.clicked.connect(self._exportOutputToFbx)

    def _assetIndicator(self):
        # get Asset Item.
        if self.currentAsset:
            self.lbCurrentAssetIndicator.setText(self.currentType + ' / ' + self.currentAsset)

            self.lbCurrentAssetIndicator.setAlignment(Qt.AlignCenter)
            self.lbCurrentAssetIndicator.setStyleSheet("QLabel {background-color: lightgreen;color:gray}")
        else:
            self.lbCurrentAssetIndicator.setText(self.currentType + ' / ---')

            self.lbCurrentAssetIndicator.setAlignment(Qt.AlignCenter)
            self.lbCurrentAssetIndicator.setStyleSheet("QLabel {background-color: #FBF082;color:gray}")

    def _setupCheckItem(self):

        self._addCheckContent(0, 'essential object ( mask, mainJoint, asset )', functools.partial(self._checkEssentialObj, 0))
        self._addCheckContent(1, 'mask paint ( only 0 or 1 )',             functools.partial(self._checkMaskVtxColor, 1))
        self._addCheckContent(2, 'max infulence( max : 4)',                functools.partial(self._checkMaxInfluence, 2))
        self._addCheckContent(3, 'hips joint assign',                      functools.partial(self._checkHipsJnt, 3))
        self._addCheckContent(4, 'deleted unused joint',                   functools.partial(self._checkUnusedJnt, 4 ))
        self._addCheckContent(5, 'joint in animation key',                 functools.partial(self._checkAnimKey, 5 ))


    def _addCheckContent(self, checkNum, content, setCmd):

        checkBtnSize = 23

        checker = QPushButton( '' )
        checker.clicked.connect(setCmd)

        checker.setMaximumSize(checkBtnSize, checkBtnSize)
        checker.setMinimumSize(checkBtnSize, checkBtnSize)

        checkContents = QLabel( content )

        horizontalLayout = QHBoxLayout()
        horizontalLayout.addWidget( checker )
        horizontalLayout.addWidget( checkContents )

        self.vLayoutCheckItem.addLayout( horizontalLayout )

        checkContentsDict = {}
        checkContentsDict['no'] = checkNum
        checkContentsDict['button']  = checker
        checkContentsDict['content'] = content
        checkContentsDict['commend'] = setCmd

        self.checkContentsList.append(checkContentsDict)

    def _checkBtnClick(self, msg):
        print msg

    def _checkButtonStatus(self, checkNum, status):
        # check False.
        if status == 0:
            self.checkContentsList[checkNum]['button'].setStyleSheet("QPushButton {background-color: tomato;color:gray}")
        # check True.
        elif status == 1:
            self.checkContentsList[checkNum]['button'].setStyleSheet("QPushButton {background-color: lightgreen;color:gray}")
        # check one more.
        elif status == 2:
            self.checkContentsList[checkNum]['button'].setStyleSheet("QPushButton {background-color: gold;color:gray}")

    def _fixButton(self, checkNum):
        # set button style.
        self.checkContentsList[checkNum]['button'].setText('fix')
        self.checkContentsList[checkNum]['button'].setStyleSheet("QPushButton {background-color: tomato;color:white}")

        # connect commend.
        self.checkContentsList[checkNum]['button'].clicked.disconnect()
        self.checkContentsList[checkNum]['button'].clicked.connect(functools.partial(self._fixButtonClicked, checkNum))

    def _fixButtonClicked(self, checkNum):
        
        if checkNum == 0:
            print '0'
        elif checkNum == 1:
            if util.fixMaskVtxColor():
                print 'fixed mask VertexColor.'
        elif checkNum == 2:
            # max inflace
            print '2'
        elif checkNum == 3:
            if util.fixHipsJnt(self.currentAsset):
                print 'Assignd Hips Joint.'
        elif checkNum == 4:
            if util.delUnusedJnt():
                print 'deleted unused joint.'
        elif checkNum == 5:
            if util.delAnimKey():
                print 'deleted animKey in joint.'

        # set button style.
        self.checkContentsList[checkNum]['button'].setText('')
        # self.checkContentsList[checkNum]['button'].clicked.disconnect()
        self._checkButtonStatus(checkNum, 1)

    # ========================
    # check Essential Object.
    # ========================
    def _checkEssentialObj(self, checkNum):
        status, e = util.checkEssentialObj(self.currentType, self.currentAsset)
        self._checkButtonStatus(checkNum, status)

        if status == 0:
            print 'Object is not Exists : ' + str([ str(item) for item in e ])
            # self._fixButton(checkNum)

        elif status == 1:
            print 'done | check Essential Object.'

    # ========================
    # check Mask vtx Color.
    # ========================
    def _checkMaskVtxColor(self, checkNum):
        status, checkVtx = util.checkMaskVtxColor()
        self._checkButtonStatus(checkNum, status)

        if status == 0:
            print 'Please Check Vertex : ' + str([ str(item) for item in checkVtx ])
            self._fixButton(checkNum)

        elif status == 2:
            print 'There is no Mask object.'

        elif status == 1:
            print 'done | check Mask VertexColor.'

    # ========================
    # check unused joint.
    # ========================

    def _checkUnusedJnt(self, checkNum):
        status, checkJnt = util.checkUnusedJnt()

        self._checkButtonStatus(checkNum, status)

        if status == 0:
            print 'Please Check Joint : ' + str([ str(item) for item in checkJnt ])
            self._fixButton(checkNum)

        elif status == 2:
            print 'There is no Joint.'

        elif status == 1:
            print 'done | check unused Joint.'

        # if checkJnt:
    
    # ========================
    # check unused joint.
    # ========================
    
    def _checkAnimKey(self, checkNum):
        # status, checkJnt = util.checkUnusedJnt()
        checkKeyList = util.checkAnimKey()

        if checkKeyList:
            print 'Please Check Joint : ' + str([ str(item) for item in checkKeyList ])

            self._checkButtonStatus(checkNum, 0)
            self._fixButton(checkNum)

        else:
            print 'done | check AnimKey in Joint.'

            self._checkButtonStatus(checkNum, 1)


    # ========================
    # check max inflence.
    # ========================

    def _checkMaxInfluence(self, checkNum):
        if self.currentAsset:
            res, maxInflence = util.dp_checkMaximumInfluence(self.currentAsset)

            if len(res):
                self._checkButtonStatus(checkNum, 0)

                print 'The joint influence of the [ {0} ] vertex exceeds the upper limit [ {1} ]'.format(len(res), maxInflence)

            else:
                self._checkButtonStatus(checkNum, 1)

                print 'done | check MaxInflence.'

    # ========================
    # check hips joint assignd.
    # ========================
    def _checkHipsJnt(self, checkNum):
        if self.currentAsset:
            status, e = util.checkHipsJnt(self.currentAsset)
            
            self._checkButtonStatus(checkNum, status)

            if status == 0:
                print 'hips Joint is not assignd.'
                self._fixButton(checkNum)

            elif status == 2:
                if e == 0:
                    print 'There is no Hips Joint.'
                elif e == 1:
                    print 'There is no SkinCluster.'

            elif status == 1:
                print 'done | check Hips Joint Assignd.'

    def _checkAll(self):
        self._checkEssentialObj(0)
        self._checkMaskVtxColor(1)
        self._checkMaxInfluence(2)
        self._checkHipsJnt(3)
        self._checkUnusedJnt(4) 
        self._checkAnimKey(5)


    # ==============================
    # export output
    # ==============================
    def _exportOutputToMaya(self):

        util.exportOutput(self.currentAssetType, self.selectedAssetItem)

    def _exportOutputToFbx(self):

        util.exportOutput(self.currentAssetType, self.selectedAssetItem, 'fbx')


def main():
    global window
    global checkWindow

    try:
        window.close()
        checkWindow.close()
    except:
        pass

    window_name         = 'blachagi Rig Tools : %s'%__VERSION__
    
    window = blachagiRigTools()
    window.setWindowTitle( window_name )
    window.show()

