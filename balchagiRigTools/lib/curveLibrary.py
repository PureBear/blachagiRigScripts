import os
import yaml
import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel


def getCurveLibraryData():
    # get curve library data file path.
    global_util_path = os.path.dirname(os.path.abspath(__file__))
    curveLibraryFilePath = global_util_path + '/curveLibrary.yml'

    openFile = open(curveLibraryFilePath, 'r')
    allData = openFile.read()
    controlCurveDataTemp = yaml.load(allData, Loader=yaml.FullLoader)
    openFile.close()
    controlCurveData = {}
    for key in controlCurveDataTemp:
        controlCurveData[key] = eval(controlCurveDataTemp[key])
    
    return controlCurveData


def shapeDataFromControlCurve(myNode = None):
    '''
    collects data from selected shape
    '''
    sel_li = om.MSelectionList()

    if not myNode:
        om.MGlobal.getActiveSelectionList(sel_li)
    else:
        sel_li.add(myNode)

    ob = om.MObject()
    sel_li.getDependNode(0, ob)
    dag_fn = om.MFnDagNode(ob)
    dagPath_dp = om.MDagPath()
    dag_fn.getPath(dagPath_dp)

    unsignedInt_su = om.MScriptUtil()
    unsignedInt_su.createFromList([0], 1)
    shapes = unsignedInt_su.asUintPtr()

    dagPath_dp.numberOfShapesDirectlyBelow(shapes)

    curveDict = {}
    for i in range(unsignedInt_su.getUint(shapes)):

        pathCopy = om.MDagPath(dagPath_dp)
        pathCopy.extendToShapeDirectlyBelow(i)
        nurbsCurve_fn = om.MFnNurbsCurve(pathCopy)

        # collects the control vertices
        CVs_pa = om.MPointArray()
        nurbsCurve_fn.getCVs(CVs_pa, om.MSpace.kObject)

        # collects the knots
        knots_da = om.MDoubleArray()
        nurbsCurve_fn.getKnots(knots_da)

        curveData = {}
        curveData['degree'] = nurbsCurve_fn.degree()
        curveData['numOfSpans'] = nurbsCurve_fn.numSpans()
        curveData['numOfKnots'] = nurbsCurve_fn.numKnots()
        curveData['numOfCVs'] = nurbsCurve_fn.numCVs()
        curveData['form'] = nurbsCurve_fn.form()

        curveData['CVs'] = []
        for p in range(CVs_pa.length()):
            curveData['CVs'].append((CVs_pa[p][0], CVs_pa[p][1], CVs_pa[p][2]))

        curveData['knots'] = []
        for d in range(knots_da.length()):
            curveData['knots'].append(knots_da[d])

        curveDict[pathCopy.partialPathName()] = curveData

    return curveDict


def combineCurves(curvesToCombine):

    curveShapes = []
    for curve in curvesToCombine[1:]:
        shapeBuffer = cmds.listRelatives (curve, f= True,shapes=True,fullPath=True)
        for shape in shapeBuffer:
            curveShapes.append(shape)

    for shape in curveShapes:
        cmds.parent(shape, curvesToCombine[0], shape=True)
        # parentShapeInPlace(curvesToCombine[0],shape)

    for curve in curvesToCombine[1:]:
        cmds.delete(curve)

    return curvesToCombine[0]

def createCNT(myCrvData, curveName, myPos = (0.0, 0.0, 0.0), myRot = (0.0, 0.0, 0.0), myScale = (1.0, 1.0, 1.0), myColorIndex=0):

    if type(myCrvData) == str:
        myCrvData = eval(myCrvData)

    myCNTCurve = cmds.curve(name = curveName, degree=myCrvData['degree'], knot=myCrvData['knots'], point=myCrvData['CVs'])
    
    # setup scale
    cmds.scale(myScale[0], myScale[1], myScale[2], myCNTCurve)

    # setup rotation
    cmds.setAttr(myCNTCurve + '.rotate', myRot[0], myRot[1], myRot[2])

    # setup translation
    cmds.xform(myCNTCurve, t=[myPos[0], myPos[1], myPos[2]], ws=True)
    cmds.makeIdentity(myCNTCurve, apply = True, translate = True, rotate = True, scale = True, normal = 0)

    # change color
    cmds.setAttr(myCNTCurve + '.overrideEnabled', 1)
    cmds.setAttr(myCNTCurve + '.overrideColor', myColorIndex)

    return myCNTCurve

def generateCNT(CNTShapeName, CNTName, alignTo, myColor, rot = (0.0, 0.0, 0.0), scale = (1.0, 1.0, 1.0)):
    '''
    '''
    allCNTData = getCurveLibraryData()
    myCNTData = allCNTData[CNTShapeName]
    myCNTNode = createCNT(myCNTData, CNTName, myColorIndex = myColor, myRot = rot, myScale = scale)

    adjCNTGr = cmds.group(myCNTNode, name = 'adj_' + CNTName)
    sdkCNTGr = cmds.group(adjCNTGr, name = 'sdk_' + CNTName)
    posCNTGr = cmds.group(sdkCNTGr, name = 'pos_' + CNTName)
    
    alignToPivots(alignTo, posCNTGr)

    return [posCNTGr, sdkCNTGr, adjCNTGr, myCNTNode]

def alignToPivots(source, target):
    '''
    align pivot of target
    it will align the translation pivot only
    '''
    sourcePivot = cmds.xform(source, pivots = True, worldSpace = True, query = True)
    cmds.xform(target, translation = (sourcePivot[0], sourcePivot[1], sourcePivot[2]), worldSpace = True)

