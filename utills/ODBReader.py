from job import *
from odbAccess import openOdb
from scipy.stats import linregress
import csv
print('Running ODB reader...')


def findAvg(lst):
    elSum = 0.0
    for el in lst:
        elSum += el
    return (elSum / len(lst))


def matCol(i, matrix):
    return [row[i] for row in matrix]


def findStress(force_vals, specSize):
    return [force / specSize**2 for force in force_vals]


def findStrain(disp_vals, specSize):
    return [disp / specSize for disp in disp_vals]


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


def caseAxis(RF1, RF2, RF3, U1, U2, U3):
    loadCase, loadAxis = '', 0

    # Find load case:
    if U1[-1] == 0 or U2[-1] == 0 or U3[-1] == 0:
        loadCase = 'shear'
    elif RF1[-1] < 0 or RF2[-1] < 0 or RF3[-1] < 0:
        loadCase = 'compression'
    elif RF1[-1] > 0 or RF2[-1] > 0 or RF3[-1] > 0:
        loadCase = 'tension'

    # Find Primary loading axis:
    if RF1[-1] < 0 or RF1[-1] > 0:
        loadAxis = 1
    elif RF2[-1] < 0 or RF2[-1] > 0:
        loadAxis = 2
    elif RF3[-1] < 0 or RF3[-1] > 0:
        loadAxis = 3
    return loadCase, loadAxis


def readODB(path, job_list, specSize, elasticCrit=0.015):
    for c, job in enumerate(job_list):

        odb = openOdb(path + job + '.odb')
        keys = odb.steps['StaticAnalysis'].historyRegions.keys()

        # X-axis & Z-axis flipped! [longitudinal fibre direction to X]
        # Reactions:
        frp = odb.steps['StaticAnalysis'].historyRegions[keys[1]]
        hOut_RF1 = frp.historyOutputs['RF3'].data
        hOut_RF2 = frp.historyOutputs['RF2'].data
        hOut_RF3 = frp.historyOutputs['RF1'].data

        time_vals = matCol(0, hOut_RF1)
        RF1_vals = matCol(1, hOut_RF1)
        RF2_vals = matCol(1, hOut_RF2)
        RF3_vals = matCol(1, hOut_RF3)

        # Displacements:
        crp = odb.steps['StaticAnalysis'].historyRegions[keys[2]]
        hOut_U1 = crp.historyOutputs['U3'].data
        hOut_U2 = crp.historyOutputs['U2'].data
        hOut_U3 = crp.historyOutputs['U1'].data
        odb.close()

        U1_vals = matCol(1, hOut_U1)
        U2_vals = matCol(1, hOut_U2)
        U3_vals = matCol(1, hOut_U3)

        # Stresses & Strains:
        stressX, stressY, stressZ = findStress(RF1_vals, specSize), findStress(RF2_vals, specSize), findStress(RF3_vals, specSize)
        strainX, strainY, strainZ = findStrain(U1_vals, specSize), findStrain(U2_vals, specSize), findStrain(U3_vals, specSize)

        # # TEMPORARY WRITER:
        # with open('Results from ' + job + '.csv', 'wb') as csvfile:
        # writer = csv.writer(csvfile)
        # writer.writerow(['Results from ' + job + ':'])
        # writer.writerow(['Time', 'RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'])
        # for i, time in enumerate(time_vals):
        # writer.writerow([time, RF1_vals[i], RF2_vals[i], RF3_vals[i], U1_vals[i], U2_vals[i], U3_vals[i]])

        loadCase, loadAxis = caseAxis(RF1_vals, RF2_vals, RF3_vals, U1_vals, U2_vals, U3_vals)

        # Tensile Young's Modulus & Poisson's Ratio:
        # Stress/Strain limited to eleastic region only [Criterion:10% strain]
        if loadCase == 'tension':
            if loadAxis == 1:
                strainX, i = limitList(elasticCrit, strainX)
                E1_tens = findSlope(stressX[0:i], strainX) / 1e9
                P12_tens = -findSlope(strainY[0:i], strainX)
                P13_tens = -findSlope(strainZ[0:i], strainX)

            elif loadAxis == 2:
                strainY, i = limitList(elasticCrit, strainY)
                E2_tens = findSlope(stressY[0:i], strainY) / 1e9
                P23_tens = -findSlope(strainZ[0:i], strainY)

            elif loadAxis == 3:
                strainZ, i = limitList(elasticCrit, strainZ)
                E3_tens = findSlope(stressZ[0:i], strainZ) / 1e9

        # Compressive Young's Modulus & Poisson's Ratio:
        elif loadCase == 'compression':
            if loadAxis == 1:
                strainX, i = limitList(elasticCrit, strainX)
                E1_comp = findSlope(stressX[0:i], strainX) / 1e9
                P12_comp = -findSlope(strainY[0:i], strainX)
                P13_comp = -findSlope(strainZ[0:i], strainX)

            elif loadAxis == 2:
                strainY, i = limitList(elasticCrit, strainY)
                E2_comp = findSlope(stressY[0:i], strainY) / 1e9
                P23_comp = -findSlope(strainZ[0:i], strainY)

            elif loadAxis == 3:
                strainZ, i = limitList(elasticCrit, strainZ)
                E3_comp = findSlope(stressZ[0:i], strainZ) / 1e9

        # Shear Modulus:
        elif loadCase == 'shear':
            # ###|TEMP|###
            # G12, G13, G23 = 0, 0, 0
            # ##########
            if loadAxis == 1:
                if job == jobList[5]:
                    strainX, i = limitList(elasticCrit, strainX)
                    G12 = findSlope(stressX[0:i], strainX) / 1e9
                elif job == jobList[8]:
                    strainZ, i = limitList(elasticCrit, strainZ)
                    G13 = findSlope(stressZ[0:i], strainZ) / 1e9
            elif loadAxis == 2:
                strainY, i = limitList(elasticCrit, strainY)
                G23 = findSlope(stressY[0:i], strainY) / 1e9

    # Averaged E & P values from Tension & Compression:
    E1, E2, E3 = (E1_tens + abs(E1_comp)) / 2, (E2_tens + abs(E2_comp)) / 2, (E3_tens + abs(E3_comp)) / 2
    P12, P13, P23 = (P12_tens + abs(P12_comp)) / 2, (P13_tens + abs(P13_comp)) / 2, (P23_tens + abs(P23_comp)) / 2

    return [E1, E2, E3, P12, P13, P23, G12, G13, G23]


def readWriteResults(basePath, jobList, modelList, specSize):
    matProps, resList, avgProps = ['E1', 'E2', 'E3', 'P12', 'P13', 'P23', 'G12', 'G13', 'G23'], [], []
    for c, model in enumerate(modelList):
        path = basePath + model + '/'
        resList.append(readODB(path, jobList, specSize))

    # Open file and write computational data:
    with open('NumericalMaterialProperties' + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for c, res in enumerate(resList):
            writer.writerow(['Results from ' + modelList[c] + ':'])
            writer.writerow(matProps)
            writer.writerow(res)
            writer.writerow([' '])

        # for c, p in enumerate(matProps):
        #     avgProps.append(findAvg([resList[0][c], resList[1][c], resList[2][c]]))  # For RVE's
        #     avgProps.append(findAvg([resList[0][c], resList[1][c], resList[2][c],  # For Composite Models's
        #                              resList[3][c], resList[4][c], resList[5][c]]))
        # writer.writerow(['Average results:'])
        # writer.writerow(matProps)
        # writer.writerow(avgProps)


if __name__ == '__main__':
    ############################# VARIABLES #################################
    jobs = ['ZTensionAnalysis', 'ZCompressionAnalysis', 'XYShearAnalysis',
            'XTensionAnalysis', 'XCompressionAnalysis', 'YZShearAnalysis',
            'YTensionAnalysis', 'YCompressionAnalysis', 'XZShearAnalysis']
    compModels = ['Plain', 'Basket', 'Mock-Leno',
                  'Satin', 'Twill', 'Extra']
    rveModels = ['RVE1', 'RVE2', 'RVE3']

    path = './ODBData/'
    rveSize = 120
    compSize = 38

    readWriteResults(path, jobs, rveModels, compModels, rveSize, compSize)

    # End of script:
    print('*************************')
    print('Results written, no errors!')
