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


def findStress(force_vals, RVE_size):
    return [force / RVE_size**2 for force in force_vals]


def findStrain(disp_vals, RVE_size):
    return [disp / RVE_size for disp in disp_vals]


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


def readODB(path, job_list, RVE_size):
    for c, job in enumerate(job_list):
        print(job)

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
        stressX, stressY, stressZ = findStress(RF1_vals, RVE_size), findStress(RF2_vals, RVE_size), findStress(RF3_vals, RVE_size)
        strainX, strainY, strainZ = findStrain(U1_vals, RVE_size), findStrain(U2_vals, RVE_size), findStrain(U3_vals, RVE_size)

        # TEMPORARY WRITER:
        with open('Results from ' + job + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Results from ' + job + ':'])
            writer.writerow(['Time', 'RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'])
            for i, time in enumerate(time_vals):
                writer.writerow([time, RF1_vals[i], RF2_vals[i], RF3_vals[i], U1_vals[i], U2_vals[i], U3_vals[i]])

        loadCase, loadAxis = caseAxis(RF1_vals, RF2_vals, RF3_vals, U1_vals, U2_vals, U3_vals)

        # Tensile Young's Modulus & Poisson's Ratio:
        if loadCase == 'tension':
            if loadAxis == 1:
                E1_tens = findSlope(stressX, strainX) / 1e9
                P12_tens = -findSlope(strainY, strainX)

            elif loadAxis == 2:
                E2_tens = findSlope(stressY, strainY) / 1e9
                P23_tens = -findSlope(strainZ, strainY)

            elif loadAxis == 3:
                E3_tens = findSlope(stressZ, strainZ) / 1e9
                P13_tens = -findSlope(strainX, strainZ)

        # Compressive Young's Modulus & Poisson's Ratio:
        elif loadCase == 'compression':
            if loadAxis == 1:
                E1_comp = findSlope(stressX, strainX) / 1e9
                P12_comp = -findSlope(strainY, strainX)

            elif loadAxis == 2:
                E2_comp = findSlope(stressY, strainY) / 1e9
                P23_comp = -findSlope(strainZ, strainY)

            elif loadAxis == 3:
                E3_comp = findSlope(stressZ, strainZ) / 1e9
                P13_comp = -findSlope(strainX, strainZ)

        # Shear Modulus:
        elif loadCase == 'shear':
            ###TEMP###
            # G12, G13, G23 = 0, 0, 0
            ##########
            if loadAxis == 1:
                G12 = findSlope(stressX, strainX) / 1e9
                G13 = findSlope(stressZ, strainZ) / 1e9

            elif loadAxis == 2:
                G23 = findSlope(stressY, strainY) / 1e9

    # Averaged E & P values from Tension & Compression:
    E1, E2, E3 = (E1_tens + abs(E1_comp)) / 2, (E2_tens + abs(E2_comp)) / 2, (E3_tens + abs(E3_comp)) / 2
    P12, P13, P23 = (P12_tens + abs(P12_comp)) / 2, (P13_tens + abs(P13_comp)) / 2, (P23_tens + abs(P23_comp)) / 2

    # AFTER TESTING REMOVE TENS/COMP SPECIFIC VALUES
    return E1, E2, E3, P12, P13, P23, G12, G13, G23, E1_tens, E1_comp, E2_tens, E2_comp, E3_tens, E3_comp, P12_tens, P12_comp, P13_tens, P13_comp, P23_tens, P23_comp


def readWriteResults(basePath, modelList, jobList, RVE_size):
    matProps = ['E1', 'E2', 'E3',
                'P12', 'P13', 'P23',
                'G12', 'G13', 'G23',
                'e1_tens', 'e1_comp', 'e2_tens', 'e2_comp', 'e3_tens', 'e3_comp', 'p12_tens', 'p12_comp', 'p13_tens', 'p13_comp', 'p23_tens', 'p23_comp']
    resList = []
    for c, model in enumerate(modelList):
        path = basePath + model + '/'

        # Read and return results from ODB:
        resList.append(globals()[model]=readODB(path, jobList, RVE_size))

    # Open file and write simulation data:
    with open('NumericalMaterialProperties' + '.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile)
        for c, res in enumerate(resList):
            writer.writerow(['Results from ' + modelList[c] + ':'])
            writer.writerow(matProps)
            writer.writerow(res)
            writer.writerow([' '])
        avgProps = []
        for c, p in enumerate(matProps):
            avgProps.append(findAvg([resList[0][c], resList[1][c], resList[2][c]]))
        writer.writerow(['Average results:'])
        writer.writerow(matProps)
        writer.writerow(avgProps)


# READER BACKUP, DELETE AFTER TESTING
# def readWriteResults(base_path, model_list, job_list, RVE_size):
#     for c, model in enumerate(model_list):
#         path = base_path + model + '/'

#         # Read and return results from ODB:
#         E1, E2, E3, P12, P13, P23, G12, G13, G23, E1_tens, E1_comp, E2_tens, E2_comp, E3_tens, E3_comp, P12_tens, P12_comp, P13_tens, P13_comp, P23_tens, P23_comp = readODB(path, job_list, RVE_size)

#         # Open file and write simulation data:
#         with open('Results-' + model + '.csv', 'wb') as csvfile:
#             writer = csv.writer(csvfile)
#             writer.writerow(['Results from ' + model + ':'])
#             writer.writerow(['E1', 'E2', 'E3', 'P12', 'P13', 'P23', 'G12', 'G13', 'G23', 'Temps-->', 'e1_tens', 'e1_comp', 'e2_tens', 'e2_comp', 'e3_tens', 'e3_comp', 'p12_tens', 'p12_comp', 'p13_tens', 'p13_comp', 'p23_tens', 'p23_comp'])
#             writer.writerow([E1, E2, E3, P12, P13, P23, G12, G13, G23, ' ', E1_tens, E1_comp, E2_tens, E2_comp, E3_tens, E3_comp, P12_tens, P12_comp, P13_tens, P13_comp, P23_tens, P23_comp])


if __name__ == '__main__':
    #################################### VARIABLES ###########################################
    rveJobs = ['ZTensionAnalysis', 'ZCompressionAnalysis', 'XYShearAnalysis',
               'XTensionAnalysis', 'XCompressionAnalysis', 'YZShearAnalysis',
               'YTensionAnalysis', 'YCompressionAnalysis', 'XZShearAnalysis']
    compModels = ['Plain', 'Basket', 'Mock-Leno', 'Satin', 'Twill', 'Extra']
    rveModels = ['RVE1', 'RVE2', 'RVE3']

    # TEMPS: ########
    rveModels.pop(1)
    rveModels.pop(1)
    compModels.pop(1)
    compModels.pop(1)
    compModels.pop(1)
    compModels.pop(1)
    compModels.pop(1)
    #################

    path = './ODBData/'
    RVE_size = 120

    readWriteResults(path, rveModels, rveJobs, RVE_size)

    # End of script:
    print('*************************')
    print('Results written, no errors!')
