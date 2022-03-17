from job import *
from odbAccess import openOdb
import numpy as np
import csv
print('Running ODB reader...')


def matCol(i, matrix):
    return [row[i] for row in matrix]


def findStress(force_vals, RVE_size):
    return [force / RVE_size**2 for force in force_vals]


def findStrain(disp_vals, RVE_size):
    return [disp / RVE_size for disp in disp_vals]


def caseAxis(RF1, RF2, RF3, U1, U2, U3):
    loadCase, loadAxis = '', 0

    # Find load case:
    # if U1[-1] or U2[-1] or U3[-1] == 0:
    #     loadCase = 'shear'
    # elif RF1[-1] or RF2[-1] or RF3[-1] < 0:
    #     loadCase = 'compression'
    # elif RF1[-1] or RF2[-1] or RF3[-1] > 0:
    #     loadCase = 'tension'

    if U1[-1] == 0 or U2[-1] == 0 or U3[-1] == 0:
        loadCase = 'shear'
    elif RF1[-1] < 0 or RF2[-1] < 0 or RF3[-1] < 0:
        loadCase = 'compression'
    elif RF1[-1] > 0 or RF2[-1] > 0 or RF3[-1] > 0:
        loadCase = 'tension'

    # Find Primary loading axis:
    # if 0 < RF1[-1] < 0:
    #     loadAxis = 1
    # elif 0 < RF2[-1] < 0:
    #     loadAxis = 2
    # elif 0 < RF3[-1] < 0:
    #     loadAxis = 3

    if RF1[-1] < 0 or RF[-1] > 0:
        loadAxis = 1
    elif RF2[-1] < 0 or RF2[-1] > 0:
        loadAxis = 2
    elif RF3[-1] < 0 or RF3[-1] > 0:
        loadAxis = 3

    return loadCase, loadAxis


def readODB(path, job_list, RVE_size):
    for c, job in enumerate(job_list):

        odb = openOdb(path + job + '.odb')
        keys = odb.steps['StaticAnalysis'].historyRegions.keys()

        # Reactions:
        frp = odb.steps['StaticAnalysis'].historyRegions[keys[1]]
        hOut_RF1 = frp.historyOutputs['RF1'].data
        hOut_RF2 = frp.historyOutputs['RF2'].data
        hOut_RF3 = frp.historyOutputs['RF3'].data

        time_vals = matCol(0, hOut_RF1)
        RF1_vals = matCol(1, hOut_RF1)
        RF2_vals = matCol(1, hOut_RF2)
        RF3_vals = matCol(1, hOut_RF3)

        # Displacements:
        crp = odb.steps['StaticAnalysis'].historyRegions[keys[2]]
        hOut_U1 = crp.historyOutputs['U1'].data
        hOut_U2 = crp.historyOutputs['U2'].data
        hOut_U3 = crp.historyOutputs['U3'].data
        odb.close()

        U1_vals = matCol(1, hOut_U1)
        U2_vals = matCol(1, hOut_U2)
        U3_vals = matCol(1, hOut_U3)

        # Stresses & Strains:
        stressX, stressY, stressZ = findStress(RF1_vals, RVE_size), findStress(RF2_vals, RVE_size), findStress(RF3_vals, RVE_size)
        strainX, strainY, strainZ = findStrain(U1_vals, RVE_size), findStrain(U2_vals, RVE_size), findStrain(U3_vals, RVE_size)

        # Material Properties Calculations:
        loadCase, loadAxis = caseAxis(RF1_vals, RF2_vals, RF3_vals, U1_vals, U2_vals, U3_vals)
        if loadCase == 'tension':
            if loadAxis == 1:
                E1_tens = ((stressZ[-1] - stressZ[0]) / (strainZ[-1] - strainZ[0])) / 1e9
                P12_tens = ((strainX[-1] - strainX[0]) / (strainZ[-1] - strainZ[0]))

            elif loadAxis == 2:
                E2_tens = ((stressX[-1] - stressX[0]) / (strainX[-1] - strainX[0])) / 1e9
                P13_tens = ((strainY[-1] - strainY[0]) / (strainZ[-1] - strainZ[0]))

            elif loadAxis == 3:
                E3_tens = ((stressY[-1] - stressY[0]) / (strainY[-1] - strainY[0])) / 1e9
                P23_tens = ((strainX[-1] - strainX[0]) / (strainZ[-1] - strainZ[0]))

        elif loadCase == 'compression':
            if loadAxis == 1:
                E1_comp = -((stressZ[-1] - stressZ[0]) / (strainZ[-1] - strainZ[0])) / 1e9
                P12_comp = -((strainX[-1] - strainX[0]) / (strainZ[-1] - strainZ[0]))

            elif loadAxis == 2:
                E2_comp = -((stressX[-1] - stressX[0]) / (strainX[-1] - strainX[0])) / 1e9
                P13_comp = -((strainY[-1] - strainY[0]) / (strainZ[-1] - strainZ[0]))

            elif loadAxis == 3:
                E3_comp = -((stressY[-1] - stressY[0]) / (strainY[-1] - strainY[0])) / 1e9
                P23_comp = -((strainX[-1] - strainX[0]) / (strainY[-1] - strainY[0]))

        elif loadCase == 'shear':
            elif loadAxis == 1:
                G12 = ((stressX[-1] - stressX[0]) / (strainZ[-1] - strainZ[0])) / 1e9

            elif loadAxis == 2:
                G13 = ((stressY[-1] - stressY[0]) / (strainZ[-1] - strainZ[0])) / 1e9

            elif loadAxis == 3:
                G23 = ((stressX[-1] - stressX[0]) / (strainY[-1] - strainY[0])) / 1e9

    # Averaged E&P vales from Tension&Compression:
    E1, E2, E3 = (E1_tens + E1_comp) / 2, (E2_tens + E2_comp) / 2, (E3_tens + E3_comp) / 2
    P12, P13, P23 = (P12_tens + P12_comp) / 2, (P13_tens + P13_comp) / 2, (P23_tens + P23_comp) / 2

    return E1, E2, E3, P12, P13, P23, G12, G13, G23, E1_tens, E1_comp, E2_tens, E2_comp, E3_tens, E3_comp, P12_tens, P12_comp, P13_tens, P13_comp, P23_tens, P23_comp


def readWriteResults(base_path, model_list, job_list, RVE_size):  # AFTER TESTING REMOVE TENS/COMP SPECIFIC VALUES
    for c, model in enumerate(model_list):
        path = base_path + model + '/'

        # Read and return results from ODB:
        E1, E2, E3, P12, P13, P23, G12, G13, G23, E1_tens, E1_comp, E2_tens, E2_comp, E3_tens, E3_comp, P12_tens, P12_comp, P13_tens, P13_comp, P23_tens, P23_comp = readODB(path, job_list, RVE_size)

        # Open file and write simulation data:
        with open('Results-' + model + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Results from ' + model + ':'])
            writer.writerow(['E1', 'E2', 'E3', 'P12', 'P13', 'P23', 'G12', 'G13', 'G23', 'e1_tens', 'e1_comp', 'e2_tens', 'e2_comp', 'e3_tens', 'e3_comp', 'p12_tens', 'p12_comp', 'p13_tens', 'p13_comp', 'p23_tens', 'p23_comp'])
            writer.writerow([E1, E2, E3, P12, P13, P23, G12, G13, G23, E1_tens, E1_comp, E2_tens, E2_comp, E3_tens, E3_comp, P12_tens, P12_comp, P13_tens, P13_comp, P23_tens, P23_comp])


if __name__ == '__main__':
    ############################### VARIABLES ###################################
    rve_jobs = ['LongitudinalTensionAnalysis', 'LongitudinalCompressionAnalysis', 'LongitudinalShearAnalysis',
                'TransverseSideTensionAnalysis', 'TransverseSideCompressionAnalysis', 'TransverseSideShearAnalysis',
                'TransverseTopTensionAnalysis', 'TransverseTopCompressionAnalysis', 'TransverseTopShearAnalysis']
    rveModel_list = ['RVE1', 'RVE2', 'RVE3']

    comp_jobs = ['TensionAnalysis', 'CompressionAnalysis', 'ShearAnalysis']
    compModel_list = ['iNSERT ALL MODEL NAMES!']

    path = './ODBData/'
    RVE_size = 120

    readWriteResults(path, rveModel_list, rve_jobs, RVE_size)

    # End of script:
    print('*************************')
    print('Results written, no errors!')
