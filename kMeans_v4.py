from numpy import *
import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt

plt.style.use('ggplot')

def file2matrix(filename):
    '''
    - open text file to generate matrix with rows
    [column 0] x-coordinate
    [column 1] y-coordinate
    [column 2] distance of point from (0,0)
    [column 3] angle of point from (0,0)
    '''
    fr = open(filename)
    numOfLines = len(fr.readlines())
    returnMat = zeros((numOfLines,4))
    fr = open(filename)
    index = 0
    for eachLine in fr.readlines():
        eachLine = eachLine.strip()
        listFromLine = eachLine.split('\t')
        x = float(listFromLine[0])
        y = float(listFromLine[1])
        angDeg = round(math.degrees(math.atan2(y,x)),3) #angle in degrees
        dist = round(((x**2)+(y**2))**0.5,3)
        listFromLine.extend([dist,angDeg])
        returnMat[index,:] = listFromLine[0:4]
        index += 1
    sortedMat = mat(sorted(returnMat, key=lambda row: row[3:])) #convert array to matrix and sort by angle column
    minAngle = sortedMat[0,3]
    maxAngle = sortedMat[numOfLines-1,3]
    interval = round(int(sortedMat[numOfLines-1,3]-sortedMat[0,3])/20,1)
    return sortedMat,interval,minAngle,maxAngle

def getSubMatrix():
    '''
    - break angles between max and min angles to have intervalAngle
    - arrOfInstances: include number of points that reside in each intervalAngle
    - distanceMat is array that contains list of distances for each intervalAngle in arrOfInstances
    '''
    sMat,intervalAngle,minAngle,maxAngle = file2matrix('testSet.txt')
    arrOfInstances = []
    distanceMat = []
    index = minAngle - 2.5 * intervalAngle
    loopUntil = maxAngle + 2.5 * intervalAngle
    sMat = np.array(sMat)
    
    while index < loopUntil:
        num = len([x for x in sMat[:,3] if x > index and x < (index+intervalAngle)])
        arrOfInstances.append(num)
        sub = sMat[(sMat[:,3]>index) & (sMat[:,3]<(index + intervalAngle)),2]
        distanceMat.append(sub)
        index = index + intervalAngle
    return arrOfInstances,distanceMat

def avgDist():
    '''
    - calculate mean of all points in 'distanceMat'
    '''
    arrOfInstances,distanceMat = getSubMatrix()
    avgDistArray = []
    for element in distanceMat:
        if len(element) == 0:
            avgDistArray.append(0.) #if no points in element then put 0.0 in avgDistArray
        else:
            avgDistArray.append(around(element.mean(axis=0),decimals=2))
    return avgDistArray

def getLocalMaxima():
    '''
    - find indices in 'arrOfInstances' that correspond to most number of
      points per intervalAngle
    - this is the way local maxima is calculated:
      -- diffStr is a string that will log points such that
      -- is current point has greater value of previous one append 'p' to diffStr else 'm'
      -- if we detect 'pm' in diffStr that points to a local maxima
    '''
    arrOfInstances,distanceMat = getSubMatrix()
    sMat,intervalAngle,minAngle,maxAngle = file2matrix('testSet.txt')
    index = 0
    diffStr = ''
    while index < len(arrOfInstances)-1:
        if arrOfInstances[index+1]-arrOfInstances[index] >= 0: diffStr=diffStr+'p'
        else: diffStr = diffStr + 'm'
        index += 1
    maxLoc = []
    preCondition = 0
    condition = 0
    while condition != -1:
        condition = diffStr.find('pm',preCondition+1)
        if condition > preCondition:
            maxLoc.append(condition+1)
        preCondition = condition
    maxLocAngles = []
    for i in maxLoc:
        angle = round(((i-2.5)*intervalAngle)+minAngle,1)
        maxLocAngles.append(angle)
    return maxLoc,maxLocAngles

def calcDistAtMaxLoc():
    '''
    - calculate average distance at max locations
    '''
    maxLoc,maxLocAngles = getLocalMaxima()
    avgDistArray = avgDist()
    distAtMaxLoc = []
    for element in maxLoc:
        distAtMaxLoc.append(avgDistArray[element])
    return distAtMaxLoc

def clusterCenters():
    '''
    - backcalculate from angles and average distance to cluster centers
    '''
    distAtMaxLoc = calcDistAtMaxLoc()
    maxLoc,maxLocAngles = getLocalMaxima()
    xCoord = []
    yCoord = []
    count = 0
    while count < len(distAtMaxLoc):
        xCalc = distAtMaxLoc[count]*math.cos(math.radians(maxLocAngles[count]))
        yCalc = distAtMaxLoc[count]*math.sin(math.radians(maxLocAngles[count]))
        xCoord.append(xCalc)
        yCoord.append(yCalc)
        count = count + 1
    return xCoord,yCoord
        
def gridLayout():
    '''
    - plot all the relevant points
    '''
    outputMat,interval,minAngle,maxAngle = file2matrix('testSet.txt')
    maxLoc,maxLocAngles=getLocalMaxima()
    arrOfInstances,distanceMat = getSubMatrix()
    xCoord,yCoord = clusterCenters()

    fig = plt.figure()

    ax1 = plt.subplot2grid((2,2),(0,0))
    ax1.scatter(outputMat[:,3],outputMat[:,2])
    for angles in maxLocAngles:
        plt.plot((angles,angles),(2,7),'k-')
    plt.title('Plot of Distance of points by angle from center')
    plt.xlabel('Angles(deg)')
    plt.ylabel('Distance from origin')

    x = [x for x in range(len(arrOfInstances))]
    ax2 = plt.subplot2grid((2,2),(1,0))
    ax2.plot(x,arrOfInstances)
    ax2.scatter(x,arrOfInstances)
    plt.title('Plot of number of points by angle segment')
    plt.xlabel('Array number')
    plt.ylabel('# of points')

    ax3 = plt.subplot2grid((2,2),(0,1), colspan=3)
    ax3.scatter(outputMat[:,0],outputMat[:,1])
    ax3.plot(xCoord,yCoord)
    plt.title('Main points with cluster centers')
    plt.xlabel('x coord')
    plt.ylabel('y coord')

    plt.tight_layout()
    plt.show()

gridLayout()
