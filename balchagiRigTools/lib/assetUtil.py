# python imports
import os
import subprocess
import sys
import imp
import re
import shutil
import getpass
import traceback
import time
import glob
import yaml
import cPickle
from datetime import datetime

# Maya imports
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as mui
import maya.OpenMaya as om
import maya.api.OpenMaya as om2
import maya.OpenMayaAnim as omAnim


# global Val
global ASSETPATH
global ASSETTYPELISTPATH
global ASSETTEMPLATEPATH
global ASSETUTILPATH
global ASSETSCRIPTPATH

ASSETPATH = 'D:/NaverCloud/work/zepeto_02/rig/'
ASSETTYPELISTPATH = ASSETPATH + 'PR'
ASSETTEMPLATEPATH = ASSETPATH + 'public'
ASSETUTILPATH     = ASSETPATH + 'util'
ASSETSCRIPTPATH   = ASSETPATH + 'script'

WORKDIRECTORY = os.path.dirname(__file__) 

def assetListDir(path, type, *search):
    # type = d : dir, f : file
    fileDict = {}
    files = os.listdir(path)
    
    if search:
        key = search[0].upper()
    else:
        key = ''
    
    dirFileList = []
    for name in files:
        dirFileList.append(name)       

    dirFileList.sort()
    # print dirFileList
    
    for name in dirFileList:
        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            if type == 'd':
                if key:
                    if name.count(key):
                        # add name.
                        fileDict[name] = full_path
                else:
                    # add name.
                    fileDict[name] = full_path
            
        elif os.path.isfile(full_path):
            if type == 'f':
                if key:
                    if name.count(key):
                        # add name.
                        fileDict[name] = full_path
                else:
                    # add name.
                    fileDict[name] = full_path
    return fileDict

def makeDir(path):
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def zepetoJointSelecter(jntType):
    # joint List. 
    bodyJntList = ['hips', 'spine', 'chest', 'chestUpper', 'neck', 'head', 'iScale_L', 'eye_L', 'eLineIn_L', 'eLineOut_L', 'iScale_R', 'eye_R', 'eLineIn_R', 'eLineOut_R', 'jaw', 'hairAll', 'headUpper', 'foreHead', 'jBone', 'mouth', 'nose', 'shoulder_L', 'upperArm_L', 'upperArmTwist_L', 'lowerArm_L', 'lowerArmTwist_L', 'hand_L', 'thumbPro_L', 'thumbInt_L', 'thumbDis_L', 'indexPro_L', 'indexInt_L', 'indexDis_L', 'middlePro_L', 'middleInt_L', 'middleDis_L', 'ringPro_L', 'ringInt_L', 'ringDis_L', 'littlePro_L', 'littleInt_L', 'littleDis_L', 'shoulder_R', 'upperArm_R', 'upperArmTwist_R', 'lowerArm_R', 'lowerArmTwist_R', 'hand_R', 'thumbPro_R', 'thumbInt_R', 'thumbDis_R', 'indexPro_R', 'indexInt_R', 'indexDis_R', 'middlePro_R', 'middleInt_R', 'middleDis_R', 'ringPro_R', 'ringInt_R', 'ringDis_R', 'littlePro_R', 'littleInt_R', 'littleDis_R', 'pelvis', 'upperLeg_L', 'upperLegTwist_L', 'lowerLeg_L', 'lowerLegTwist_L', 'foot_L', 'toes_L', 'upperReg_R', 'upperRegTwist_R', 'lowerReg_R', 'lowerRegTwist_R', 'foot_R', 'toes_R', 'skirt_L_jnt', 'skirt_R_jnt', 'heel_L', 'heel_R', 'lip_L', 'lip_R']
    scaleJntList = ['chestUpper_scale', 'chest_scale', 'hips_scale', 'lowerArmTwist_L_scale', 'lowerArmTwist_R_scale', 'lowerArm_L_scale', 'lowerArm_R_scale', 'lowerLegTwist_L_scale', 'lowerLeg_L_scale', 'lowerRegTwist_R_scale', 'lowerReg_R_scale', 'neck_scale', 'pelvis_scale', 'shoulder_L_scale', 'shoulder_R_scale', 'spine_scale', 'upperArmTwist_L_scale', 'upperArmTwist_R_scale', 'upperArm_L_scale', 'upperArm_R_scale', 'upperLegTwist_L_scale', 'upperLeg_L_scale', 'upperRegTwist_R_scale', 'upperReg_R_scale']
    earringJointList = ['head', 'hairAll', 'headUpper', 'foreHead', 'jBone']
    hairJointList = ['head', 'hairAll', 'headUpper', 'foreHead', 'jBone']

    # select hair joint.
    if jntType == 'hair':
        selJntList = []
        for jnt in hairJointList:
            if cmds.objExists(jnt):
                selJntList.append(jnt)

        cmds.select(selJntList)
    
    # select earring joint.
    elif jntType == 'earring':
        selJntList = []
        for jnt in earringJointList:
            if cmds.objExists(jnt):
                selJntList.append(jnt)

        cmds.select(selJntList)

    # select body joint.
    elif jntType == 'body':
        selJntList = []
        for jnt in bodyJntList:
            if cmds.objExists(jnt):
                if cmds.objExists(jnt + '_scale'):
                    selJntList.append(jnt + '_scale')
                else :
                    selJntList.append(jnt)

        cmds.select(selJntList)

    return selJntList

# ---------------------------------
# set joint lable
# ---------------------------------

def setJointLabel():
    jntLabelDict = {
    'Hip' : ['hips'],
    'HipScale' : ['hips_scale'],
    'Pelvis' : ['pelvis'],
    'PelvisScale' : ['pelvis_scale'],
    'NeckScale' : ['neck_scale'],
    'Neck' : ['neck'],
    'Shoulder' : ['shoulder_L', 'shoulder_R'],
    'ShoulderScale' : ['shoulder_L_scale', 'shoulder_R_scale'],
    'Arm' : ['upperArm_L', 'upperArm_R'],
    'ArmScale' : ['upperArm_L_scale', 'upperArm_R_scale'],
    'ArmTwist' : ['upperArmTwist_L', 'upperArmTwist_R'],
    'ArmTwistScale' : ['upperArmTwist_L_scale', 'upperArmTwist_R_scale'],
    'Elbow' : ['lowerArm_L', 'lowerArm_R'],
    'ElbowScale' : ['lowerArm_L_scale', 'lowerArm_R_scale'],
    'ElbowTwist' : ['lowerArmTwist_L', 'lowerArmTwist_R'],
    'ElbowTwistScale' : ['lowerArmTwist_L_scale', 'lowerArmTwist_R_scale'],
    'Hand' : ['hand_L', 'hand_R'],
    'Leg' : ['upperLeg_L', 'upperReg_R'],
    'LegScale' : ['upperLeg_L_scale', 'upperReg_R_scale'],
    'LegTwist' : ['upperLegTwist_L', 'upperRegTwist_R'],
    'LegTwistScale' : ['upperLegTwist_L_scale', 'upperRegTwist_R_scale'],
    'Knee' : ['lowerLeg_L', 'lowerReg_R'],
    'KneeScale' : ['lowerLeg_L_scale', 'lowerReg_R_scale'],
    'KneeTwist' : ['lowerLegTwist_L', 'lowerRegTwist_R'],
    'KneeTwistScale' : ['lowerLegTwist_L_scale', 'lowerRegTwist_R_scale'],
    'Foot' : ['foot_L', 'foot_R'],
    'Toe' : ['toes_L', 'toes_R']}
    
    allJntList = cmds.ls(type='joint')
    
    jntLabelList = jntLabelDict.keys()
    for jntLabel in jntLabelList:
        labelJntList = jntLabelDict[jntLabel]
        # print labelJntList
        for labelJnt in labelJntList:
            # find all jointList. 
            jntList = cmds.ls(labelJnt)
            # print jntList
            if jntList:
                for jnt in jntList:
                    jntName = jnt.split('|')[-1]

                    if len(labelJntList) == 1:
                        side = 'C'
                    else:
                        side = jntName.split('_')[1]
                        
                    if side == 'L':
                        cmds.setAttr(jnt + '.side', 1)
                        cmds.setAttr(jnt + '.type', 18)
                        cmds.setAttr(jnt + '.otherType', jntLabel, type='string')
                    elif side == 'R':
                        cmds.setAttr(jnt + '.side', 2)
                        cmds.setAttr(jnt + '.type', 18)
                        cmds.setAttr(jnt + '.otherType', jntLabel,  type='string')     
                    elif side == 'C':
                        cmds.setAttr(jnt + '.side', 0)
                        cmds.setAttr(jnt + '.type', 18)
                        cmds.setAttr(jnt + '.otherType', jntLabel,  type='string')             
                        

# ---------------------------------
# setHeelPosition
# ---------------------------------
# 20190620 - setHeelPosition.
# 20190822 - more comport and apply multiple joint.
# 20200318 - change heel position methhod.

def setHeelPosition(heelPOS='base'):
    # base heel position.
    baseHeelPosDict = {
    'hips' : [0.0, 53.18578793074292, 0.41017291277671936],
    'foot_L' : [0.0, 0.0, 0.0],
    'foot_R' : [0.0, 0.0, 0.0],
    'toes_L' : [0.0, 0.0, 0.0],
    'toes_R' : [0.0, 0.0, 0.0],
    'heel_L' : [1.0, 1.0, 1.0],
    'heel_R' : [1.0, 1.0, 1.0]
    }

    if heelPOS == 'base':
        adjHeelPosition(baseHeelPosDict)
    elif heelPOS == 'heel':
        # get expressions values
        heelPosDict = getHeelPosition()
        adjHeelPosition(heelPosDict)


def adjHeelPosition(heelPosDict):
    adjHeelJntList = heelPosDict.keys()

    for adjJnt in adjHeelJntList:
        if adjJnt == 'heel_L' or adjJnt == 'heel_R':
            if cmds.objExists('heel_L') or cmds.objExists('heel_R'):
                cmds.xform(adjJnt, scale=heelPosDict[adjJnt])

        elif adjJnt == 'hips':
            cmds.xform(adjJnt, translation=heelPosDict[adjJnt])

        else:
            cmds.xform(adjJnt, rotation=heelPosDict[adjJnt])

def getHeelPosition():
    # base heel position.
    heelExpValDict = {
    'hips' : [0.0, 53.18578793074292, 0.41017291277671936],
    'foot_L' : [0.0, 0.0, 0.0],
    'foot_R' : [0.0, 0.0, 0.0],
    'toes_L' : [0.0, 0.0, 0.0],
    'toes_R' : [0.0, 0.0, 0.0],
    'heel_L' : [1.0, 1.0, 1.0],
    'heel_R' : [1.0, 1.0, 1.0]
    }

    if cmds.objExists('expressions'):
        # get foot value
        for side in ['_L', '_R']:
            footRot = cmds.xform('_foot'+side, query=True, rotation=True)
            
            if side == '_L':
                heelExpValDict['foot_L'] = footRot
            
            if side == '_R':
                heelExpValDict['foot_R'] = footRot

        # get toes value
        for side in ['_L', '_R']:
            toesRot = cmds.xform('_toes'+side, query=True, rotation=True)
            
            if side == '_L':
                heelExpValDict['toes_L'] = toesRot
            
            if side == '_R':
                heelExpValDict['toes_R'] = toesRot

        # get heel value
        for side in ['_L', '_R']:
            heelRot = cmds.xform('_heel'+side, query=True, relative=True, scale=True)
            
            if side == '_L':
                heelExpValDict['heel_L'] = heelRot
            
            if side == '_R':
                heelExpValDict['heel_R'] = heelRot

        # get hips values
        hipsVal = cmds.xform('_hips', query=True, translation=True)
        hipsVal[2] = 0.41017291277671936
        heelExpValDict['hips'] = hipsVal

    return heelExpValDict

            
def setBasePose(poseType):
    # base pose [TPose, APose, Stands]
    
    shoulderRotDict = {'TPose' : [0.0, 0.0, 0.0], 
                       'APose'  : [0.0, 0.0, -7.5],
                       'Stands'   : [0.0, 0.0, -16.5]}
    
    upperArmRotDict = {'TPose' : [0.0, 0.0, 0.0], 
                       'APose'  : [0.0, 0.0, -40.0],
                       'Stands'   : [0.0, 0.0, -65.0]}

    if cmds.objExists('shoulder_L'):
        # check joint multiple joint.
        checkShoulderJnt = cmds.ls('shoulder_L', 'shoulder_R')
        [ cmds.xform(shoulderJnt, rotation=shoulderRotDict[poseType]) for shoulderJnt in checkShoulderJnt ]
        
        checkArmJnt = cmds.ls('upperArm_L', 'upperArm_R')
        [ cmds.xform(armJnt, rotation=upperArmRotDict[poseType]) for armJnt in checkArmJnt ]
            
            

def publicFileImport(fileType):

    # publicPath = ASSETTEMPLATEPATH
    publicFile ={ 'body'      : 'zepeto_02_skin_F',
                  'scaleBody' : 'zepeto_02_skin_F_scale',
                  'hair'      : 'hairRig_v001',
                  'earring'   : 'earringRig_v001' }

    # import file type. 
    if fileType == 'body':
        # make file path.
        importFilePath = ASSETTEMPLATEPATH + '/' + publicFile[fileType] + '.mb'

        # import File.
        cmds.file(importFilePath, i=True, type='mayaBinary', ignoreVersion=True, options='v=0' )

    if fileType == 'scaleBody':
        # make file path.
        importFilePath = ASSETTEMPLATEPATH + '/' + publicFile[fileType] + '.mb'

        # import File.
        cmds.file(importFilePath, i=True, type='mayaBinary', ignoreVersion=True, options='v=0' )

    if fileType == 'hair':
        # make file path.
        importFilePath = ASSETTEMPLATEPATH + '/' + publicFile[fileType] + '.mb'

        # import File.
        cmds.file(importFilePath, i=True, type='mayaBinary', ignoreVersion=True, options='v=0' )

    if fileType == 'earring':
        # make file path.
        importFilePath = ASSETTEMPLATEPATH + '/' + publicFile[fileType] + '.mb'

        # import File.
        cmds.file(importFilePath, i=True, type='mayaBinary', ignoreVersion=True, options='v=0' )


def makePreviewImage(assetType ,assetName):
    # camera rig in [ ASSETUTILPATH + '/cam' ]
    boundingBoxPreSet = {
    'hair'     : {'trans' : [0.0, -30.0, 0.0], 
                  'rot'   : [0.0, 0.0, 0.0],
                  'scale' : [5.0, 5.0, 5.0]},
    
    'body'     : {'trans' : [0.0, 5.0, 0.0], 
                  'rot'   : [0.0, 0.0, 0.0],
                  'scale' : [6.5, 6.5, 6.5]},

    'shoes'    : {'trans' : [0.0, 0.0, 0.0], 
                  'rot'   : [0.0, 30.0, 0.0],
                  'scale' : [3.0, 3.0, 3.0]},

    'earring'  : {'trans' : [0.0, -12.0, 0.0], 
                  'rot'   : [0.0, 0.0, 0.0],
                  'scale' : [2.5, 2.5, 2.5]},

    'bracelet' : {'trans' : [37.0, 80.0, 15.0], 
                  'rot'   : [-90.0, 0.0, 0.0],
                  'scale' : [2.0, 2.0, 2.0]},

    'necklace' : {'trans' : [0.0, 63.0, 0.0], 
                  'rot'   : [0.0, 0.0, 0.0],
                  'scale' : [2.0, 2.0, 2.0]} }
    
    # import screen Camera.
    screenCamFile = ASSETUTILPATH + '/cam/screenShotCamRig_v002.ma'
    cmds.file(screenCamFile, i=True)
    
    # move boundingBox proper position by type.
    if assetType in ['OTR', 'TOP', 'DR', 'BTM']:
        previewType = 'body'

    elif assetType in ['M_HAIR', 'F_HAIR', 'HEADWEAR']:
        previewType = 'hair'

    elif assetType in ['SH']:
        previewType = 'shoes'

    elif assetType in ['NECKLACE']:
        previewType = 'necklace'

    elif assetType in ['EARRING']:
        previewType = 'earring'

    elif assetType in ['BRACELET']:
        previewType = 'bracelet'

    else:
        previewType = 'body'

    # set boundingBox position.
    cmds.xform('boundingBox', translation = boundingBoxPreSet[previewType]['trans'])
    cmds.xform('boundingBox', rotation    = boundingBoxPreSet[previewType]['rot'])
    cmds.xform('boundingBox', scale       = boundingBoxPreSet[previewType]['scale'])


    # set image format (png)
    cmds.setAttr('defaultRenderGlobals.imageFormat',32)
    
    # set renderer.
    mel.eval('setCurrentRenderer("mayaHardware2")')
    
    renderFile = cmds.hwRender(camera='frontCAM', h=1024, w=1024)
    
    # make Path.
    previewFileName = assetName + '_previewImage.png'

    copyPath = ASSETTYPELISTPATH + '/' + assetType + '/' + assetName + '/' + previewFileName
    previewArchivePath = ASSETTYPELISTPATH + '/' + assetType + '/preview/'
    
    shutil.move(renderFile, copyPath)

    if os.path.isdir(previewArchivePath):
        shutil.copy(copyPath, previewArchivePath + previewFileName)

    else:
        # if not Exists folder.
        os.mkdir(previewArchivePath)

        shutil.copy(copyPath, previewArchivePath + previewFileName)

    
    # delete camara util.
    cmds.delete('boundingBox')
    
    messge = [True, copyPath]

    return messge
    

def exportFile(myFilePath):
    # print currentVersion
    cmds.file(rename=myFilePath)
    cmds.file(force=True, type='mayaAscii', save=True, options='v=0;')

def versioningFile(versionsPath = None, myFilePath = None, comment = None):

    currentVersion = ''
    commentDict = []

    if versionsPath and myFilePath and comment:
        # let's create the folders if there are not there
        if not os.path.isdir(versionsPath):
            # fs.file_session.begin()
            os.makedirs(versionsPath)
            # fs.file_session.commit()
        
        commentsFilePath = versionsPath + '/comments.yml'

        # comment file check get current version. 
        if os.path.isfile(commentsFilePath):
            commentFile = file(commentsFilePath, 'r') 
            commentFileDict = yaml.load(commentFile, Loader=yaml.FullLoader)
            if commentFileDict:
                commentDict = commentFileDict
                currentVersion = str(len(commentDict) + 1)
            else:
                currentVersion = str(len(commentDict) + 1)

        else:
            with open(commentsFilePath, 'w') as outfile:
                yaml.safe_dump(commentDict, outfile, encoding='utf-8', allow_unicode=True)

                outfile.close()

            currentVersion = str(len(commentDict) + 1)

        # print currentVersion
        filename = os.path.split(myFilePath)[-1]
        shutil.copy(myFilePath, versionsPath + '/' + filename + '.' + currentVersion)

        # current date and time
        timeCode = datetime.now()
        currentTime = timeCode.strftime("%Y-%m-%d, %H:%M:%S")

        # make dict 
        exportDict = {'comment' : comment,
                      'file'    : versionsPath + '/' + filename + '.' + currentVersion,
                      'date'    : currentTime,
                      'version' : currentVersion }

        commentDict.append(exportDict)

        with open(commentsFilePath, 'w') as outfile:
            # yaml.dump(commentDict, outfile, allow_unicode=True)
            yaml.safe_dump(commentDict, outfile, encoding='utf-8', allow_unicode=True)

            outfile.close()

    return exportDict
    
def openFile(filePath):
    cmds.file(filePath, ignoreVersion=True, typ='mayaAscii', open=True)


def readCommentFile(commentFilePath):
    commentFile = file(commentFilePath, 'r') 
    commentDict = yaml.load(commentFile, Loader=yaml.FullLoader)

    return commentDict


def read_project_file():
    project_file_path = WORKDIRECTORY + '/project.yml'

    project_dict = []

    check_project_file = os.path.isfile(project_file_path)

    if check_project_file:
        project_file = file(project_file_path, 'r') 
        project_dict = yaml.load(project_file, Loader=yaml.FullLoader)

    return project_dict

def setup_project_folder(project_path):

    asset_dir = project_path + '/asset'
    chr_dir = project_path + '/asset/chr'
    prp_dir = project_path + '/asset/prp'
    set_dir = project_path + '/asset/set'
    
    makeDir(asset_dir)
    makeDir(chr_dir)
    makeDir(prp_dir)
    makeDir(set_dir)

    # if not Exists version folder.
    project_file_path = WORKDIRECTORY + '/project.yml'
    check_project_file = os.path.isfile(project_file_path)

    # make dict 
    project_name = project_path.split('/')[-1]
    
    exportDict = {'project' : project_name,
                  'path'    : project_path
                  }

    project_dict = read_project_file()
    project_dict.append(exportDict)

    with open(project_file_path, 'w') as outfile:
        yaml.safe_dump(project_dict, outfile, encoding='utf-8', allow_unicode=True)

        outfile.close()

    return project_dict

#--------------------------------------------------------
# SUPPORT FUNCTIONS
#--------------------------------------------------------

def parseSkinData(lines):
    
    dataDict = {}
    startWeights=False
    startInf=False
    vertNum = 0
    lineList = []
    infList = []
    weightDict = {}
    weightList = []
    for i in range(len(lines)):
        line =  lines[i].replace('\n', '')
        lineParts = line.split(':')
        
        if 'envelop' in line :
            dataDict[lineParts[0]] = float(lineParts[1].lstrip())
        
        if 'vertexCount' in line:
            dataDict[lineParts[0]] = int(lineParts[1].lstrip())
            startInf =False
        
        if 'influences' in line:
            
            # break the line up by , so we can turn in into a 'real' list instead of a string that prints like a list
            lineList = lineParts[1].split(',')
            newLineList=[]
            #strip leading space out of each part of line list
            for x in range(len(lineList)):
                if lineList[x]:
                    newLineList.append(lineList[x].lstrip().rstrip())
            # more stripping
            newLineList[0] = newLineList[0].replace('[','').lstrip().rstrip()
            newLineList[-1] = newLineList[-1].replace(']','').lstrip().rstrip()
            # hey we have an actual list
            infList += newLineList
            startInf = True
            continue
            
        # trigger a bool now that we've hit the weights part of the file
        if 'weights' in line:
            startWeights = True
            startInf =False
            continue
            
        if startInf:
            # break the line up by , so we can turn in into a 'real' list instead of a string that prints like a list
            lineList = lineParts[0].split(',')
            
            # more stripping
            lineList[0] = lineList[0].replace('[','').lstrip()
            lineList[-1] = lineList[-1].replace(']','').lstrip()
            
            newLineList = []
            #strip leading space out of each part of line list
            for x in range(len(lineList)):
                lineList[x] = lineList[x].lstrip()
                if lineList[x]:
                    newLineList.append(lineList[x])
                
            # hey we have an actual list
            infList += newLineList
            
        if startWeights:
            
            # if there is a : in line then its the vert num
            if ':' in line:
                # add the weight list to the previous vert num before we advance to the next one
                weightDict[vertNum] = weightList
                weightList = []
                vertNum = int(lineParts[0].lstrip())
                # print vertNum
            
            elif ' - ' in line:
                # break the line up by , so we can turn in into a 'real' list instead of a string that prints like a list
                lineList = line.split(',')
                lineList[0] = lineList[0].replace('- [','').lstrip()
                
                # lineList[1] is the weight val, so lets strip the junk off it and turn it into a float
                lineList[1] = float(lineList[1].replace(']','').lstrip())
                
                weightList.append(lineList)
            
            # make sure we get the last weight info
            if i == len(lines)-1:
                weightDict[vertNum] = weightList
                weightList = []
                
                
    # now that we're at the end of the file add the weights dict to the dataDict
    dataDict['weights'] = weightDict
    dataDict['influences'] = infList
    return dataDict

def exportSkinWeights(myDagPath = None, myFilePath = None):
    '''
    @return:
    - True or False
    '''
    # let's open a file session
    # fs.file_session.begin()

    result = False
    # let's check if we have all we need
    if myDagPath and myFilePath:
        # let's get the shape name
        shapeName = myDagPath.fullPathName().split('|')[-1]
        shapeFullName = myDagPath.fullPathName()

        # the dictionary to hold the data
        data = {}

        # let's get the skinCluster connected to this node
        # let's get the transform fo the shape

        if cmds.nodeType(shapeFullName) != 'transform':
            myTransformFullName = cmds.listRelatives(shapeFullName, parent = True, fullPath = True, type = 'transform')[0]

        else:
            myTransformFullName = shapeFullName

        cmds.select(myTransformFullName, replace = True)
        mySel = cmds.ls(selection = True)[0]

        melCommand = 'findRelatedSkinCluster("' + mySel + '")'
        clusterName = mel.eval(melCommand)
        
        if clusterName:
            # let's get the envelope value and populate our dictionary
            data['envelop'] = cmds.getAttr(clusterName + '.envelope')

            # let's get the list of influence objects (usually the joints that deform the geometry)
            data['influences'] = []
            infMap = {}
            for infPlug in cmds.listAttr(clusterName + '.matrix', multi = True):
                infName = cmds.listConnections(clusterName + '.' + infPlug, source = True)[0]

                if infName:
                    infIndex = infPlug.split('[')[1].split(']')[0]
                    infMap[infIndex] = str(infName)

                    data['influences'].append(str(infName))

            # let's get the weights
            data['weights'] = {}
            components = cmds.ls(clusterName + '.weightList[*]')
            for comp in components:
                compIndex = int(comp.split('[')[1].split(']')[0])
                data['weights'][compIndex] = []

                # let's get the influences that are affecting this component
                influences = cmds.listAttr(comp + '.weights', multi = True)
                if influences:
                    for influence in influences:
                        infIndex = influence.split('[')[2].split(']')[0]
                        if infIndex in infMap:
                            infName = infMap[infIndex]
                            weight = cmds.getAttr(clusterName + '.' + influence)

                            data['weights'][compIndex].append([str(infName), weight])

            # let's get the number of components
            data['vertexCount'] = len(components)
            
            # we now should have our data collected
            # let's create the folder if it's not there
            myPath = os.path.split(myFilePath)[0]
            '''
            if not os.path.isdir(myPath):
                fs.file_session.make_dir(myPath, lock = False)
            '''

            # let's save the file
            
            openFile = open(myFilePath, 'w')
            openFile.write(yaml.dump(data, default_flow_style = None, indent = 4))
            openFile.close()
            # file_utils.simple_chmod(myFilePath)

            result = True

            print 'Export done -- ' + myTransformFullName
        else:
            print 'No skinCluster found for: ' + myTransformFullName

    # fs.file_session.commit()

    return result

def importSkinWeights(myDagPath = None, myFilePath = None):
    '''
    import the skinCluster information into the provided dagPath
    '''
    # let's assume we will have errors
    result = [False, 'Nothing was done yet.']

    shapeName = myDagPath.fullPathName().split('|')[-1]
    shapeFullName = myDagPath.fullPathName()
    transformFullName = cmds.listRelatives(shapeFullName, parent = True, fullPath = True)[0]
    apiType = myDagPath.apiType()


    openFile = open(myFilePath, 'r')
    # to be faster!!!!
    allData = openFile.readlines()
    data = parseSkinData(allData)
    openFile.close()
    

    if data:

        # let's get the skinCluster connected to this node
        # let's get the transform fo the shape

        if cmds.nodeType(shapeFullName) != 'transform':
            myTransformFullName = cmds.listRelatives(shapeFullName, parent = True, fullPath = True, type = 'transform')[0]

        else:
            myTransformFullName = shapeFullName

        cmds.select(myTransformFullName, replace = True)
        mySel = cmds.ls(selection = True)[0]

        melCommand = 'findRelatedSkinCluster("' + mySel + '")'
        clusterName = mel.eval(melCommand)

        # let's get the list of influence objects from data
        incomingInfluenceList = data['influences']


        # ribbons are presenting a bug. Attempting to update an existing skinCluster, let's try to create a new
        if apiType == 294:
            cmds.delete(clusterName)
            clusterName = ''

        if not clusterName:
            result = [False, 'inside the not clustername if']
            for inf in incomingInfluenceList:
                if not cmds.objExists(inf):
                    cmds.warning(inf + ' missing')
                    result = [False, inf + ' missing']
                    return result

            clusterName = cmds.skinCluster(incomingInfluenceList, transformFullName, bindMethod = 0, skinMethod = 0, toSelectedBones = True)
            clusterName = str(clusterName[0])
        
        if clusterName:
            # let's get the weights for all vertices per influence object
            sel_li = om.MSelectionList()
            sel_li.add(clusterName)
            cluster_ob = om.MObject()
            sel_li.getDependNode(0, cluster_ob)
            cluster_fn = omAnim.MFnSkinCluster(cluster_ob)

            # the skinCluster could have the influence objects in a different order
            # let's collect the list of influence objects from the skinCluster and from the incoming data file
            currentInfluenceList = [str(inf) for inf in cmds.skinCluster(clusterName, influence = True, query = True)]

            # let's check to see if we are dealing with the same influence objects
            if set(currentInfluenceList) != set(incomingInfluenceList):
                cmds.warning('Current list of influence objects does not match the incoming list')
                result = [False, 'Current list of influence objects does not match the incoming list']
                return result

            # let's get the vertices indices into an int array
            shape_it = om.MItGeometry(myDagPath)
            numOfVertices = shape_it.count()
            # let's check to see if we are dealing with the same number of vertices
            if numOfVertices !=  data['vertexCount']:
                cmds.warning('Vertex count does not match')
                result = [False, 'Vertex count does not match']
                return result

            # let's clear the weights in this skinCluster
            weights = cmds.ls(clusterName + '.weightList[*]')
            for weight in (weights or []):
                weightAttrs = cmds.listAttr(weight + '.weights', multi = True)
                for weightAttr in (weightAttrs or []):
                    cmds.setAttr(clusterName + '.' + weightAttr, 0)
            cmds.refresh()

            # let's find out what's the influence object indices in the current skinCluster
            # it may be different from the incoming data
            infMap = {}
            infList = cmds.listAttr(clusterName + '.matrix', multi = True)
            for inf in infList:
                infIndex = inf.split('[')[-1].split(']')[0]
                infName = cmds.listConnections(clusterName + '.' + inf, source = True)[0]
                infMap[infName] = infIndex

            cmds.setAttr(clusterName + '.normalizeWeights', 0)


            inc = 0 # for refresh
            if apiType == 294: # 294 for nurbs surfaces
                for compIndex in data['weights']:
                    # let's get the list of influences for this component
                    infList = data['weights'][compIndex]
                    for inf in infList:
                        infName = inf[0] 
                        newWeight = '%.2f' % round(inf[1], 2)
                        weight = float(newWeight)
                        infIndex = int(infMap[infName])
                        if weight != 0.0:
                            cmds.setAttr(clusterName + '.weightList[' + str(compIndex) + '].weights[' + str(infIndex) + ']', weight)
                        else:
                            print shapeName + ' - vtx: ' + str(compIndex) + ' - ' + str(infName) + ' - weight is zero'

                cmds.setAttr(clusterName + '.normalizeWeights', 1)
                cmds.skinCluster(clusterName, edit = True, forceNormalizeWeights = True)

            else:
                for compIndex in data['weights']:
                    # let's get the list of influences for this component
                    infList = data['weights'][compIndex]
                    for inf in infList:
                        infName = inf[0]
                        weight = float(inf[1])
                        infIndex = int(infMap[infName])
                        cmds.setAttr(clusterName + '.weightList[' + str(compIndex) + '].weights[' + str(infIndex) + ']', weight)
                        
                    inc += 1
                    if inc == 10000:
                        cmds.refresh()

                cmds.setAttr(clusterName + '.normalizeWeights', 1)
                cmds.skinCluster(clusterName, edit = True, forceNormalizeWeights = True)


            cmds.refresh()
            
            result = [True, 'Skin weights import done ---- ' + shapeName]
            return result
        else:
            result = [False, 'Could not create/find skincluster for ' + shapeName]
            return result
    else:
        result = [False, 'No skin data for ' + shapeName]
        return result

    return result

def importSkinWeightsScaleJointConvert(myDagPath = None, myFilePath = None):
    '''
    import the skinCluster information into the provided dagPath
    '''
    # let's assume we will have errors
    result = [False, 'Nothing was done yet.']


    scaleJntList = ['chestUpper_scale',
     'chest_scale',
     'hips_scale',
     'lowerArmTwist_L_scale',
     'lowerArmTwist_R_scale',
     'lowerArm_L_scale',
     'lowerArm_R_scale',
     'lowerLegTwist_L_scale',
     'lowerLeg_L_scale',
     'lowerRegTwist_R_scale',
     'lowerReg_R_scale',
     'neck_scale',
     'pelvis_scale',
     'shoulder_L_scale',
     'shoulder_R_scale',
     'spine_scale',
     'upperArmTwist_L_scale',
     'upperArmTwist_R_scale',
     'upperArm_L_scale',
     'upperArm_R_scale',
     'upperLegTwist_L_scale',
     'upperLeg_L_scale',
     'upperRegTwist_R_scale',
     'upperReg_R_scale']


    shapeName = myDagPath.fullPathName().split('|')[-1]
    shapeFullName = myDagPath.fullPathName()
    transformFullName = cmds.listRelatives(shapeFullName, parent = True, fullPath = True)[0]
    apiType = myDagPath.apiType()


    openFile = open(myFilePath, 'r')
    # to be faster!!!!
    allData = openFile.readlines()
    data = parseSkinData(allData)
    openFile.close()

    if data:

        # let's get the skinCluster connected to this node
        # let's get the transform fo the shape

        if cmds.nodeType(shapeFullName) != 'transform':
            myTransformFullName = cmds.listRelatives(shapeFullName, parent = True, fullPath = True, type = 'transform')[0]

        else:
            myTransformFullName = shapeFullName

        cmds.select(myTransformFullName, replace = True)
        mySel = cmds.ls(selection = True)[0]

        melCommand = 'findRelatedSkinCluster("' + mySel + '")'
        clusterName = mel.eval(melCommand)

        # let's get the list of influence objects from data
        incomingInfluenceList = data['influences']
        incomingScaleInfluenceList = []

        for inf in incomingInfluenceList:
            checkInf = inf + '_scale'
            if checkInf in scaleJntList:
                incomingScaleInfluenceList.append(checkInf)
            else:
                incomingScaleInfluenceList.append(inf)

        # ribbons are presenting a bug. Attempting to update an existing skinCluster, let's try to create a new
        if apiType == 294:
            cmds.delete(clusterName)
            clusterName = ''

        if not clusterName:
            result = [False, 'inside the not clustername if']
            for inf in incomingInfluenceList:
                if not cmds.objExists(inf):
                    cmds.warning(inf + ' missing')
                    result = [False, inf + ' missing']
                    return result

            clusterName = cmds.skinCluster(incomingScaleInfluenceList, transformFullName, bindMethod = 0, skinMethod = 0, toSelectedBones = True)
            clusterName = str(clusterName[0])
        
        if clusterName:
            # let's get the weights for all vertices per influence object
            sel_li = om.MSelectionList()
            sel_li.add(clusterName)
            cluster_ob = om.MObject()
            sel_li.getDependNode(0, cluster_ob)
            cluster_fn = omAnim.MFnSkinCluster(cluster_ob)

            # the skinCluster could have the influence objects in a different order
            # let's collect the list of influence objects from the skinCluster and from the incoming data file
            currentInfluenceList = [str(inf) for inf in cmds.skinCluster(clusterName, influence = True, query = True)]

            # let's check to see if we are dealing with the same influence objects
            if set(currentInfluenceList) != set(incomingScaleInfluenceList):
                cmds.warning('Current list of influence objects does not match the incoming list')
                result = [False, 'Current list of influence objects does not match the incoming list']
                return result

            # let's get the vertices indices into an int array
            shape_it = om.MItGeometry(myDagPath)
            numOfVertices = shape_it.count()
            # let's check to see if we are dealing with the same number of vertices
            if numOfVertices !=  data['vertexCount']:
                cmds.warning('Vertex count does not match')
                result = [False, 'Vertex count does not match']
                return result

            # let's clear the weights in this skinCluster
            weights = cmds.ls(clusterName + '.weightList[*]')
            for weight in (weights or []):
                weightAttrs = cmds.listAttr(weight + '.weights', multi = True)
                for weightAttr in (weightAttrs or []):
                    cmds.setAttr(clusterName + '.' + weightAttr, 0)
            cmds.refresh()

            # let's find out what's the influence object indices in the current skinCluster
            # it may be different from the incoming data
            infMap = {}
            infList = cmds.listAttr(clusterName + '.matrix', multi = True)
            for inf in infList:
                infIndex = inf.split('[')[-1].split(']')[0]
                infName = cmds.listConnections(clusterName + '.' + inf, source = True)[0]
                infMap[infName] = infIndex

            cmds.setAttr(clusterName + '.normalizeWeights', 0)


            inc = 0 # for refresh
            if apiType == 294: # 294 for nurbs surfaces
                for compIndex in data['weights']:
                    # let's get the list of influences for this component
                    infList = data['weights'][compIndex]
                    for inf in infList:
                        infName = inf[0] 
                        checkInf = infName + '_scale'
                        if checkInf in scaleJntList:
                            infName = checkInf

                        newWeight = '%.2f' % round(inf[1], 2)
                        weight = float(newWeight)
                        infIndex = int(infMap[infName])
                        if weight != 0.0:
                            cmds.setAttr(clusterName + '.weightList[' + str(compIndex) + '].weights[' + str(infIndex) + ']', weight)
                        else:
                            print shapeName + ' - vtx: ' + str(compIndex) + ' - ' + str(infName) + ' - weight is zero'

                cmds.setAttr(clusterName + '.normalizeWeights', 1)
                cmds.skinCluster(clusterName, edit = True, forceNormalizeWeights = True)

            else:
                for compIndex in data['weights']:
                    # let's get the list of influences for this component
                    infList = data['weights'][compIndex]
                    for inf in infList:
                        infName = inf[0]
                        checkInf = infName + '_scale'
                        if checkInf in scaleJntList:
                            infName = checkInf
                        weight = float(inf[1])
                        infIndex = int(infMap[infName])
                        cmds.setAttr(clusterName + '.weightList[' + str(compIndex) + '].weights[' + str(infIndex) + ']', weight)
                        
                    inc += 1
                    if inc == 10000:
                        cmds.refresh()

                cmds.setAttr(clusterName + '.normalizeWeights', 1)
                cmds.skinCluster(clusterName, edit = True, forceNormalizeWeights = True)


            cmds.refresh()
            
            result = [True, 'Skin weights import done ---- ' + shapeName]
            return result
        else:
            result = [False, 'Could not create/find skincluster for ' + shapeName]
            return result
    else:
        result = [False, 'No skin data for ' + shapeName]
        return result

    return result

def getMObject(object):
    '''
    Return an MObject for the input scene object
    @param object: Object to get MObject for
    @type object: str
    '''
    # Check input object
    if not cmds.objExists(object):
        raise UserInputError('Object "'+object+'" does not exist!!')
    # Get selection list
    selectionList = om.MSelectionList()
    om.MGlobal.getSelectionListByName(object,selectionList)
    mObject = om.MObject()
    selectionList.getDependNode(0,mObject)
    # Return result
    return mObject
  
def getMDagPath(object):
    '''
    Return an MDagPath for the input scene object
    @param object: Object to get MDagPath for
    @type object: str
    '''
    # Check input object
    if not cmds.objExists(object):
        raise UserInputError('Object "'+object+'" does not exist!!')
  
    # Get selection list
    selectionList = om.MSelectionList()
    om.MGlobal.getSelectionListByName(object,selectionList)
    mDagPath = om.MDagPath()
    selectionList.getDagPath(0,mDagPath)
  
    # Return result
    return mDagPath


def getShape(trans):
    if "transform" == cmds.nodeType(trans):
        shapes = cmds.listRelatives(trans, s=1)
    return shapes[0]
   
def getTransform(shape):
    transform = ""
    if "transform" != cmds.nodeType(shape):
        parents = cmds.listRelatives(shape, p=1)
        transform = parents[0]
        #print parents[0]
    return transform
            
def setBasePose(pose):
    # base pose [TPose, APose, Stands]
    
    shoulderRotDict = {'TPose' : [0.0, 0.0, 0.0], 
                       'APose'  : [0.0, 0.0, -7.5],
                       'Stands'   : [0.0, 0.0, -16.5]}
    
    upperArmRotDict = {'TPose' : [0.0, 0.0, 0.0], 
                       'APose'  : [0.0, 0.0, -40.0],
                       'Stands'   : [0.0, 0.0, -65.0]}

    if pose == 'TPose':
        if cmds.objExists('shoulder_L'):
            cmds.xform('shoulder_L', rotation=shoulderRotDict['TPose'])
            cmds.xform('shoulder_R', rotation=shoulderRotDict['TPose'])
            cmds.xform('upperArm_L', rotation=upperArmRotDict['TPose'])
            cmds.xform('upperArm_R', rotation=upperArmRotDict['TPose'])
            
    elif pose == 'APose':
        if cmds.objExists('shoulder_L'):
            cmds.xform('shoulder_L', rotation=shoulderRotDict['APose'])
            cmds.xform('shoulder_R', rotation=shoulderRotDict['APose'])
            cmds.xform('upperArm_L', rotation=upperArmRotDict['APose'])
            cmds.xform('upperArm_R', rotation=upperArmRotDict['APose'])
            
    elif pose == 'Stands':
        if cmds.objExists('shoulder_L'):
            cmds.xform('shoulder_L', rotation=shoulderRotDict['Stands'])
            cmds.xform('shoulder_R', rotation=shoulderRotDict['Stands'])
            cmds.xform('upperArm_L', rotation=upperArmRotDict['Stands'])
            cmds.xform('upperArm_R', rotation=upperArmRotDict['Stands'])
            
def getShape(trans):
    if "transform" == cmds.nodeType(trans):
        shapes = cmds.listRelatives(trans, s=1)
    return shapes[0]
   
def getTransform(shape):
    transform = ""
    if "transform" != cmds.nodeType(shape):
        parents = cmds.listRelatives(shape, p=1)
        transform = parents[0]
        #print parents[0]
    return transform
    
def findRelatedSkin(selObj):
    objType = ''
    
    objType = cmds.objectType(selObj)
    if objType == 'joint':
        objType = 'joint'
        
    elif objType == 'transform':
        checkShape = getShape(selObj)
        checkType = cmds.objectType(checkShape)

        if checkType == 'mesh':
            objType = 'mesh'

        else:
            cmds.warning('check select object type. used joint or mesh.')
            
    # get skinCluster. 
    skinClusterName = ''
    for checkSkin in cmds.ls(type='skinCluster'):
        if objType == 'mesh':
            checkObjList = cmds.skinCluster(checkSkin, query=True, g=True)

        elif objType == 'joint':
            checkObjList = cmds.skinCluster(checkSkin, query=True, inf=True)
        
        for checkObj in checkObjList:
            if objType == 'mesh':
                checkObj = getTransform(checkObj)

            if checkObj == selObj:
                skinClusterName = checkSkin
                
    return skinClusterName

# ========================
# unused joint.
# ========================

def checkUnusedJnt():
    delJntList = []
    checkJntList = []
    leaveJntList = []
    
    jntList = cmds.ls(type='joint', long=True)
    jntList.sort(key=len, reverse=True)
    status = 0
    
    if jntList:
        for jnt in jntList:
            checkJnt = cmds.ls(jnt, shortNames=True)[0]
            checkSkin = findRelatedSkin(checkJnt)
    
            if checkSkin:
                tempLeaveList = jnt.split('|')
    
                for tempLeave in tempLeaveList:
                    if not tempLeave in leaveJntList:
                        leaveJntList.append(tempLeave)
            
            if not checkSkin:
                fullPath = cmds.ls(jnt, long=True)[0]
                childrenList = cmds.listRelatives(jnt, children=True)
                if not childrenList:
                    shortName = cmds.ls(jnt, shortNames=True)[0]
                    if not shortName in leaveJntList:
                        delJntList.append(jnt)
                    
                else:
                    checkChildrenLsit = []
                    for children in childrenList:
                        if findRelatedSkin(children):
                            checkChildrenLsit = children
                            
                    if not checkChildrenLsit:
                        shortName = cmds.ls(jnt, shortNames=True)[0]
                        if not shortName in leaveJntList:
                            delJntList.append(jnt)
                            
            
        if delJntList:
            # have joint list.
            status = 0
        
            for delJnt in delJntList:
                delJntName = cmds.ls(delJnt, shortNames=True)[0]
                checkJntList.append(delJntName)
    
        else:
            # no delete joint.
            status = 1
    
    else:
        # there is no joint.
        status = 2
    
    return status, checkJntList


def delUnusedJnt():
    delJntList = []

    status, delJntList = checkUnusedJnt()

    cmds.delete(delJntList)

    result = True

    return result
        
# ========================
# anim Key in joint.
# ========================
def checkAnimKey():
    jntList = cmds.ls(type='joint')
    checkedJntList = []

    for jnt in jntList:
        checkKey = cmds.keyframe(jnt, query=True, name=True)
        if checkKey:
            checkedJntList.append(jnt)

    return checkedJntList

def delAnimKey():
    jntList = checkAnimKey()

    for jnt in jntList:
        cmds.cutKey(jnt, cl=True)

    result = True
    
    return result

# =======================================================================
# check max infulence.
# =======================================================================
import pymel.core as pm

Default_Maximum_Infulence = 4

def dp_checkMaximumInfluence (skinMesh, maxInflence=Default_Maximum_Infulence):
    res = []
    # getSkinMesh = pm.ls(sl=1)    

    getSkinClusters = []

    if pm.listRelatives (skinMesh, shapes=1)[0].type() == 'mesh':
        getSkinClusters += pm.ls (pm.listHistory (skinMesh, pdo=1), typ= 'skinCluster')      
    
    if  getSkinClusters == []: 
        print 'Please select the mesh object which is bindSkin.'
    
    else:
        for cluster in getSkinClusters:
            for mesh in pm.skinCluster (cluster, q=1, geometry=1):
                res += check_mesh (maxInflence, cluster, mesh)
        
        # print("The joint influence of the [ {0} ] vertex exceeds the upper limit [ {1} ]".format(len(res), maxInflence))

        # pm.select(res)    
    return res, maxInflence


def check_mesh(maxInflence, cluster, mesh):
    vertices = pm.polyListComponentConversion (mesh, toVertex=1)
    vertices = pm.filterExpand (vertices, selectionMask=31)  # polygon vertex
    res = []
    for vert in vertices:
        joints = pm.skinPercent (cluster, vert, query=1, ignoreBelow=0.000001, transform=None)
        if len(joints) > maxInflence:
            res.append(vert)
    return res
    
# =======================================================================
# check Mask vtx Color.
# =======================================================================

def checkMaskVtxColor():
    checkColorDict = {}
    
    if cmds.objExists('mask'):
        maskVtx = cmds.ls('mask.vtx[*]', fl=True)
        
        
        for i in range(len(maskVtx)):
            # get vertex Color.
            vtxColor = cmds.polyColorPerVertex(maskVtx[i], query=True, r=True, g=True, b=True )
            
            for j in range(len(vtxColor)):
                if 0.0 < vtxColor[j] < 1.0:
                    checkColorDict[maskVtx[i]] = vtxColor
                    
        checkVtxList = checkColorDict.keys()
        
        if checkVtxList:
            status = 0
        else:
            status = 1
    else:
        status = 2
    

    return status, checkVtxList

def fixMaskVtxColor():
    status, checkVtxList = checkMaskVtxColor()

    for i in range(len(checkVtxList)):
        vtxColor = cmds.polyColorPerVertex(checkVtxList[i], query=True, r=True, g=True, b=True )

        cmds.polyColorPerVertex(checkVtxList[i], r=round(vtxColor[0]), g=round(vtxColor[1]), b=round(vtxColor[2]))

    result = True

    return result

# =======================================================================
# check hips Joint Assign.
# =======================================================================

def checkHipsJnt(skinMesh):
    # get skinCluster.
    skinCls = findRelatedSkin(skinMesh)
    e = 0

    if cmds.objExists('hips'):
        if skinCls:
        
            infList = cmds.skinCluster(skinCls, query=True, influence=True)
            
            if 'hips' in infList:
                status = 1
            else:
                status = 0
        else:
            status = 2
            e = 1
    else:
        status = 2
        e = 0

    return status, e

def fixHipsJnt(skinMesh):
    # get skinCluster.
    skinCls = findRelatedSkin(skinMesh)

    infList = cmds.skinCluster(skinCls, query=True, influence=True)

    if not 'hips' in infList:
        cmds.skinCluster(skinCls, edit=True, lockWeights=True, weight=0, addInfluence='hips')
    
    result = True

    return result

# =======================================================================
# check essential Object. ['mask', 'hips', asset] 
# =======================================================================
def checkEssentialObj(currentType, currentAsset):
    e = []
    mainJnt = 'hips'
    if currentType == 'F_HAIR':
        mainJnt = 'head'
    elif currentType == 'M_HAIR':
        mainJnt = 'head'

    for obj in ['mask', mainJnt, currentAsset]:
        if not cmds.objExists(obj):
            e.append(obj)
    
    if e:
        status = 0
    else:
        status = 1

    return status, e

# =======================================================================
# export output.
# =======================================================================

def exportOutput(currentType, currentAsset, exportType):
    cmds.select(None)
    if currentAsset:
        scaleJnt = cmds.ls('*_scale', type='joint')
        
        if currentType == 'SH':
            if cmds.objExists('expressions'):
                hipHeights = cmds.getAttr('_hips.ty')
                orgHeights = 53.18578793074292
                cmds.setAttr('_hips.ty', (hipHeights-orgHeights) )

                cmds.parent('expressions', 'hips')
                cmds.xform('expressions', translation=[0.0, 0.0, 0.0])

        if scaleJnt:
            for jnt in scaleJnt:
                cmds.xform(jnt, translation=[0,0,0])

            cmds.select(None)
        
            
        # export Output File. 
        outputPath = 'D:/NaverCloud/work/zepeto_02/rig/PR/{0}/{1}/output/'.format(currentType, currentAsset)

        # if not Exists output folder.
        checkOutputPath = os.path.isdir(outputPath)

        if not checkOutputPath:
            os.mkdir(outputPath)

        # check export type. 
        outType = 'mayaBinary'

        if exportType == 'maya':
            outputFileName = currentAsset + '_rig.mb'
            outType = 'mayaBinary'
        elif exportType == 'fbx':
            outputFileName = currentAsset + '_rig.fbx'
            outType = 'FBX export'

        # clear selected. 
        cmds.select(None)

        # scale reset. 
        scaleJnt = cmds.ls('*_scale', type='joint')

        for jnt in scaleJnt:
            cmds.xform(jnt, translation = [0, 0, 0])

        cmds.select(None)

        # select output object.
        outJnt = 'hips'

        if currentType == 'F_HAIR':
            outJnt = 'head'
        elif currentType == 'M_HAIR':
            outJnt = 'head'
        elif currentType == 'HEADWEAR':
            outJnt = 'head'
        elif currentType == 'EARRING':
            outJnt = 'head'

        outputList = [currentAsset, 'mask', outJnt]
        cmds.select(outputList)

        cmds.file(outputPath + outputFileName, force=True, type=outType, exportSelected=True)
        print 'exported -- ' + outputPath + outputFileName

        # open brower. 
        outputPath = outputPath.replace('/', '\\')

        subprocess.call("explorer {}".format(outputPath), shell=True)

        return outputPath + outputFileName
    else:
        print('There is no asset.')


# =======================================================================
# scale Joint Convert.
# =======================================================================


def scaleSkinConverter(assetType, currentAsset):
    skinFilePath = ASSETTYPELISTPATH + '/{0}/{1}/skinWeights/'.format(assetType, currentAsset)
    skinFileName = currentAsset + '.skinWeights.cpickle'

    # if not Exists output folder.
    checkSkinFilePath = os.path.isdir(skinFilePath)

    if not checkSkinFilePath:
        os.mkdir(skinFilePath)
    
    # get physics joint.
    phyJntList = cmds.ls('*_physics_*', type='joint')
    phyJntDict = {}

    if phyJntList:
        for phyJnt in phyJntList:
            parJnt = cmds.listRelatives(phyJnt, parent=True)[0]
        
            phyJntDict[phyJnt] = parJnt
            
            cmds.parent(phyJnt, w=True)
    else:
        print('There is no physics joint.')
    
    degPath = getMDagPath(currentAsset)
    exportSkinWeights(degPath, skinFilePath + skinFileName)
    
    cmds.skinCluster(currentAsset, edit=True, ub=True)

    checkVal = 0
    if cmds.objExists('shoulder_L'):
        checkVal = round(cmds.getAttr('shoulder_L.rz'), 3)
    
    cmds.delete('hips')
    
    # import scale body.
    importFilePath = ASSETTEMPLATEPATH + '/zepeto_02_skin_F_scale.mb'
    cmds.file(importFilePath, i=True, type='mayaBinary', ignoreVersion=True, options='v=0' )
    
    # check Pose.
    if checkVal < 0:
        setBasePose('APose')
    else:
        setBasePose('TPose')
        
    # import skin file.
    cmds.parent('hips', w=True)
    cmds.delete('zepeto_skin')
    
    degPath = getMDagPath(getShape(currentAsset))
    importSkinWeightsScaleJointConvert(degPath, skinFilePath + skinFileName)
    
    # clean up.
    setBasePose('TPose')
        
    # get skinCluster. 
    skinClusterName = findRelatedSkin(currentAsset)            
    cmds.skinCluster(skinClusterName, edit=True, lw=True, wt=0, ai='hips')
    
    # delete unused joint.
    delUnusedJnt()
    
    # re parent physics joint.
    if phyJntList:
        for phyJnt in phyJntList:
            cmds.parent(phyJnt, phyJntDict[phyJnt])
        
    # export Output File. 
    # exportOutputToMaya(assetType, currentAsset)

    

# finalize shoes asset.
def rGenerateDelta(good, bad, default):   
    # mesh = cmds.ls(sl=1)
    # good = mesh[0]
    # bad = mesh[1]
    # default = mesh[2] 
    blendShapeCorrective = cmds.blendShape(good, bad, default)
    cmds.blendShape( blendShapeCorrective[0], edit=True, w=[(0, 1),(1, -1)])
    outMesh = cmds.duplicate(default, n = 'delta_of %s and %s' %(good, bad))[0]
    cmds.delete(blendShapeCorrective)

    return outMesh


def finalizeShoesAsset(assetType, currentAsset):
    # currentAsset = 'SH_379'
    # assetType = 'SH'
    if assetType == 'SH' and currentAsset:
        # base heel pose
        checkPos = round(cmds.getAttr('hips.translateY'), 3)
        
        setHeelPosition('base')
        
        # duplicate mesh
        basePoseMesh = cmds.duplicate(currentAsset, name='basePoseMesh')[0]
        # skined -> duplicate mesh.
        infJnt = cmds.skinCluster(currentAsset, query=True, influence=True)
        
        cmds.skinCluster(infJnt, basePoseMesh, maximumInfluences=4, toSelectedBones=True)
        # export org skin.
        skinFilePath = ASSETTYPELISTPATH + '/{0}/{1}/skinWeights/'.format(assetType, currentAsset)
        skinFileName = currentAsset + '.skinWeights.cpickle'

        # if not Exists output folder.
        checkSkinFilePath = os.path.isdir(skinFilePath)

        if not checkSkinFilePath:
            os.mkdir(skinFilePath)

        degPath = getMDagPath(currentAsset)
        exportSkinWeights(degPath, skinFilePath + skinFileName)

        # import skin -> duplicate mesh.
        baseDegPath = getMDagPath(getShape(basePoseMesh))
        importSkinWeights(baseDegPath, skinFilePath + skinFileName)

        # copy default mesh. 
        defaultMesh = cmds.duplicate(basePoseMesh, name='defaultMesh')[0]
        
        # goto heel pose.
        if cmds.objExists('experssions'):
            setHeelPosition('heel')
            
        # get delta mesh. 
        deltaMesh = rGenerateDelta(currentAsset, basePoseMesh, defaultMesh)

        # import skin -> delta mesh.
        setHeelPosition('base')
        
        cmds.skinCluster(infJnt, deltaMesh, maximumInfluences=4, toSelectedBones=True)
        
        deltaDegPath = getMDagPath(getShape(deltaMesh))
        importSkinWeights(deltaDegPath, skinFilePath + skinFileName)

        # delete trash. 
        cmds.delete(basePoseMesh, defaultMesh)
        
        # remane object. 
        cmds.rename(currentAsset, 'org_' + currentAsset)
        cmds.rename(deltaMesh, currentAsset)

# =======================================================================
# setPhysicsVal.
# =======================================================================

def getShortName(long):
    short = cmds.ls(long, shortNames=True)[0]
    
    return short

def setPhysicsVal(jntList, phyValues):
    # select joint.
    # selJntList = cmds.ls(sl=1, long=True)
    
    # get physics value.
    phyDrag = phyValues[0]
    phyAngelDrag = phyValues[1]
    phyRestoreDrag = phyValues[2]
    
    # get shortName
    phyJntList = []

    for jnt in jntList:
        shortName = getShortName(jnt)

        # rename shortName.
        if shortName.count('_physics_'):
            newShortName = shortName.split('_physics')[0]
        else:
            newShortName = shortName
            
        phyName = newShortName + '_physics_' + str(phyDrag) + '_' + str(phyAngelDrag) + '_' + str(phyRestoreDrag)
        jntPath = jnt.replace(shortName, '')
        
        phyJntName = jntPath + phyName
        phyJntList.append(phyJntName)

        cmds.rename(jnt, phyJntName)

    return phyJntList


# =======================================================================
# Make Hair Guide Mesh.
# =======================================================================

# def attachObjToCrvSurface(attachItemList, connCrv, axis, *skipObj):
def attachObjToCrvSurface(connCrv, axis, *skipObj):
    # connCrvCVList = cmds.ls(connCrv + '.cv[*]', flatten=True)
    connCrvCVList = connCrv
    
    # make loft curve. 
    loftCrvList = []
    loftPointAPOSList = []
    loftPointBPOSList = []
    
    for i in range(len(connCrvCVList)):
        loftPointA = cmds.group(name=connCrvCVList[i] + 'loftPointA', empty=True)
        loftPointB = cmds.group(name=connCrvCVList[i] + 'loftPointB', empty=True)
        loftPointCenter = cmds.group(name=connCrvCVList[i] + 'loftPointCenter', empty=True)
        cmds.parent(loftPointA, loftPointB, loftPointCenter)
        
        connCrvCVPOS = cmds.xform(connCrvCVList[i], query=True, worldSpace=True, matrix=True)
        # connCrvCVMatrix = cmds.xform(attachItemList[i], query=True, worldSpace=True, matrix=True)
        
        cmds.xform(loftPointCenter, matrix=connCrvCVPOS)
        if axis == 'x':
            cmds.xform(loftPointA, translation=(1,0,0))
            cmds.xform(loftPointB, translation=(-1,0,0))
        elif axis == 'y':
            cmds.xform(loftPointA, translation=(0,1,0))
            cmds.xform(loftPointB, translation=(0,-1,0))
        elif axis == 'z':
            cmds.xform(loftPointA, translation=(0,0,1))
            cmds.xform(loftPointB, translation=(0,0,-1))
        
        # get loft curve point.         
        loftPointAPOS = cmds.xform(loftPointA, query=True, worldSpace=True, translation=True)
        loftPointBPOS = cmds.xform(loftPointB, query=True, worldSpace=True, translation=True)
        loftPointCenterPOS = cmds.xform(connCrvCVList[i], query=True, worldSpace=True, translation=True)
        
        # delete support group.
        cmds.delete(loftPointCenter)
        
        loftPointAPOSList.append(loftPointAPOS)
        loftPointBPOSList.append(loftPointBPOS)

    # make loft curve.
    loftACrv = cmds.curve(point=loftPointAPOSList, degree=3)
    loftACrv = cmds.rename(loftACrv, connCrvCVList[i]+'_loftACrv')

    loftBCrv = cmds.curve(point=loftPointBPOSList, degree=3)
    loftBCrv = cmds.rename(loftBCrv, connCrvCVList[i]+'_loftBCrv')
    
    # go loft.  -ss 3 -rn 0 -po 1 -rsn true
    loftMesh = cmds.loft(loftACrv, loftBCrv,
                         constructionHistory=False, 
                         c=0, ar=1,
                         uniform=True,
                         sectionSpans=3,
                         range=False,
                         polygon=1,
                         reverseSurfaceNormals=True)[0]
                         
    loftMesh = cmds.rename(loftMesh, connCrvCVList[i] + '_loftMesh')
    
    # delete support curve. 
    cmds.delete(loftACrv, loftBCrv)

    return loftMesh
    
    #------------------------------------------------

        
def getMeshParm(meshShape, loc):
    
    # load "nearestPointOnMesh" plugin.
    pomLoaded = cmds.pluginInfo('nearestPointOnMesh', query=True, loaded=True)
    if not pomLoaded:
        cmds.loadPlugin('nearestPointOnMesh')
        pomLoaded = cmds.pluginInfo('nearestPointOnMesh', query=True)
        if not pomLoaded:
            cmds.warning( 'ParentToSurface: Can\'t load nearestPointOnMesh plugin.')
    
    # The following is to overcome a units bug in the nearestPointOnMesh plugin
    # If at some point it correctly handles units, then we need to take out the
    # following conversion factor. 
    convertFac = convertToCmFactor()
    
    clPos = cmds.createNode('nearestPointOnMesh')
    cmds.connectAttr(meshShape+'.worldMesh', clPos+'.inMesh')
    
    bbox = cmds.xform(loc, query=True, worldSpace=True, boundingBox=True)
    pos = [(bbox[0] + bbox[3])*0.5,
           (bbox[1] + bbox[4])*0.5,
           (bbox[2] + bbox[5])*0.5]
           
    cmds.setAttr(clPos + '.inPosition',
                 pos[0]*convertFac,
                 pos[1]*convertFac,
                 pos[2]*convertFac)
                 
    closestU = cmds.getAttr(clPos+'.parameterU')
    closestV = cmds.getAttr(clPos+'.parameterV')
    
    cmds.delete(clPos)
    
    return closestU, closestV
    
def convertToCmFactor():
    cunit = cmds.currentUnit(query=True, linear=True)
    if cunit == 'mm':
        facotrVal = 0.1
    elif cunit == 'cm':
        facotrVal = 1.0
    elif cunit == 'm':
        facotrVal = 100.0
    elif cunit == 'in':
        facotrVal = 2.54
    elif cunit == 'ft':
        facotrVal = 30.48
    elif cunit == 'yd':
        facotrVal = 91.44
    else:
        facotrVal = 1.0
    
    return facotrVal
        
def createFollicle(pbSurfaceShpae=None, follName=None, uPos=0.0, vPos=0.0):
    pbName = follName + '_follicleShape'
    pbFoll = cmds.createNode('follicle', n=pbName)
    pbFollTransform = getTransform(pbFoll)
    
    nType = cmds.nodeType(pbSurfaceShpae)
    if nType == 'nurbsSurface':
        cmds.connectAttr(pbSurfaceShpae+'.local', pbFoll + '.inputSurface')
    else:
        cmds.connectAttr(pbSurfaceShpae+'.outMesh', pbFoll + '.inputMesh')
        
    cmds.connectAttr(pbSurfaceShpae+'.worldMatrix[0]', pbFoll+'.inputWorldMatrix')
    cmds.connectAttr(pbFoll+'.outTranslate', pbFollTransform+'.translate')
    cmds.connectAttr(pbFoll+'.outRotate', pbFollTransform+'.rotate')
    cmds.setAttr(pbFollTransform+'.t',l=1)
    cmds.setAttr(pbFollTransform+'.r',l=1)
    
    cmds.setAttr(pbFoll+'.parameterU', uPos)
    cmds.setAttr(pbFoll+'.parameterV', vPos)

    return pbFollTransform

def makeHairGuideMesh(jointList):

    for mainJoint in jointList:
        cmds.select(None)
        cmds.select(mainJoint, hi=True)

        loftJointList = cmds.ls(sl=True)

        loftMesh = attachObjToCrvSurface(loftJointList, 'z')

        print '[' + loftMesh + ']' + 'is created.'


# =======================================================================
# add joint label.
# =======================================================================
def setJointLabel():
    jntLabelDict = {
    'Hip' : ['hips'],
    'HipScale' : ['hips_scale'],
    'Pelvis' : ['pelvis'],
    'PelvisScale' : ['pelvis_scale'],
    'NeckScale' : ['neck_scale'],
    'Neck' : ['neck'],
    'Shoulder' : ['shoulder_L', 'shoulder_R'],
    'ShoulderScale' : ['shoulder_L_scale', 'shoulder_R_scale'],
    'Arm' : ['upperArm_L', 'upperArm_R'],
    'ArmScale' : ['upperArm_L_scale', 'upperArm_R_scale'],
    'ArmTwist' : ['upperArmTwist_L', 'upperArmTwist_R'],
    'ArmTwistScale' : ['upperArmTwist_L_scale', 'upperArmTwist_R_scale'],
    'Elbow' : ['lowerArm_L', 'lowerArm_R'],
    'ElbowScale' : ['lowerArm_L_scale', 'lowerArm_R_scale'],
    'ElbowTwist' : ['lowerArmTwist_L', 'lowerArmTwist_R'],
    'ElbowTwistScale' : ['lowerArmTwist_L_scale', 'lowerArmTwist_R_scale'],
    'Hand' : ['hand_L', 'hand_R'],
    'Leg' : ['upperLeg_L', 'upperReg_R'],
    'LegScale' : ['upperLeg_L_scale', 'upperReg_R_scale'],
    'LegTwist' : ['upperLegTwist_L', 'upperRegTwist_R'],
    'LegTwistScale' : ['upperLegTwist_L_scale', 'upperRegTwist_R_scale'],
    'Knee' : ['lowerLeg_L', 'lowerReg_R'],
    'KneeScale' : ['lowerLeg_L_scale', 'lowerReg_R_scale'],
    'KneeTwist' : ['lowerLegTwist_L', 'lowerRegTwist_R'],
    'KneeTwistScale' : ['lowerLegTwist_L_scale', 'lowerRegTwist_R_scale'],
    'Foot' : ['foot_L', 'foot_R'],
    'Toe' : ['toes_L', 'toes_R']}
    
    allJntList = cmds.ls(type='joint')
    
    jntLabelList = jntLabelDict.keys()
    for jntLabel in jntLabelList:
        labelJntList = jntLabelDict[jntLabel]
        # print labelJntList
        for labelJnt in labelJntList:
            # find all jointList. 
            jntList = cmds.ls(labelJnt)
            # print jntList
            if jntList:
                for jnt in jntList:
                    jntName = jnt.split('|')[-1]

                    if len(labelJntList) == 1:
                        side = 'C'
                    else:
                        side = jntName.split('_')[1]
                        
                    if side == 'L':
                        cmds.setAttr(jnt + '.side', 1)
                        cmds.setAttr(jnt + '.type', 18)
                        cmds.setAttr(jnt + '.otherType', jntLabel, type='string')
                    elif side == 'R':
                        cmds.setAttr(jnt + '.side', 2)
                        cmds.setAttr(jnt + '.type', 18)
                        cmds.setAttr(jnt + '.otherType', jntLabel,  type='string')     
                    elif side == 'C':
                        cmds.setAttr(jnt + '.side', 0)
                        cmds.setAttr(jnt + '.type', 18)
                        cmds.setAttr(jnt + '.otherType', jntLabel,  type='string')             
                        
