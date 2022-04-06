from job import *
from odbAccess import openOdb
from scipy.stats import linregress
import csv
print('Running ODB reader...')


def matCol(i, matrix):
    return [row[i] for row in matrix]


def findStress(forceVals, area):
    return [force / area for force in forceVals]


def findStrain(dispVals, length):
    return [disp / length for disp in dispVals]


def limitList(crit, valList):
    newList = []
    for c, val in enumerate(valList):
        if abs(val) <= crit:
            newList.append(val)
        else:
            break
    return newList, c


def findSlope(listY, listX):
    m, i, r, p, s = linregress(listX, listY)
    return m


def readODB(path, jobList, specSize, elasticCrit=0.01):
    E1List = []
    for c, job in enumerate(jobList):
        odb = openOdb(path + job + '.odb')
        keys = odb.steps['StaticAnalysis'].historyRegions.keys()

        # Reactions & Displacements:
        frp = odb.steps['StaticAnalysis'].historyRegions[keys[1]]
        hOut_RF1 = frp.historyOutputs['RF1'].data
        hOut_U1 = drp.historyOutputs['U1'].data
        time_vals = matCol(0, hOut_RF1)
        RF1_vals = matCol(1, hOut_RF1)
        U1_vals = matCol(1, hOut_U1)

        # Job results writer:
        with open('Results from ' + job + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Results from ' + job + ':'])
            writer.writerow(['Time', 'RF1', 'U1'])
            for i, time in enumerate(time_vals):
                writer.writerow([time, RF1_vals[i], U1_vals[i]])

        # Tensile Young's Modulus:
        # Stress/Strain limited to eleastic region only [Criterion: 10% strain]
        strainX = findStrain(U1_vals, specSize[0])
        stressX = findStress(RF1_vals, (pi * (specSize[1] / 2) * (specSize[2] / 2)))

        strainX, i = limitList(elasticCrit, strainX)
        E1List.append([job, findSlope(stressX[0:i], strainX) / 1e9])

    return E1List


def readWriteResults(jobList, path, specSize):
    resList = readODB(path, jobList, specSize)

    # Open file and write computational data:
    with open('NumericalYarnMaterialProperties' + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for res in (resList):
            writer.writerow(['Results from' + res[0] + ':'])
            writer.writerow(['E1:', res[1]])
            writer.writerow([' '])


if __name__ == '__main__':
    ################# VARIABLES #####################
    jobList = ['WovenFibreTens', 'StraightFibreTens']
    yarnPath = './YarnMesostructure/ODBData/'
    yarnSize = (37.5, 1.2, 4.5)

    readWriteResults(jobList, yarnPath, yarnSize)

    # End of script:
    print('*************************')
    print('Results written, no errors!')
