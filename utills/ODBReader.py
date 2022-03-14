from job import *
from odbAccess import openOdb
import numpy as np
import csv
print('Running ODB reader...')


def matCol(i, matrix):
    return [row[i] for row in matrix]


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

        U1_vals = matCol(1, hOut_U1)
        U2_vals = matCol(1, hOut_U2)
        U3_vals = matCol(1, hOut_U3)

        # Find primary loading axis:
        reactions = [RF1_vals, RF2_vals, RF3_vals]
        for c, reaction in enumerate(reactions):
            if reaction[-1] != 0.0:
                loading_direction = c + 1

        # Stresses & Strains:
        stressX = [rf / RVE_size**2 for rf in RF1_vals]
        stressY = [rf / RVE_size**2 for rf in RF2_vals]
        stressZ = [rf / RVE_size**2 for rf in RF3_vals]
        strainX = [u / RVE_size for u in U1_vals]
        strainY = [u / RVE_size for u in U2_vals]
        strainZ = [u / RVE_size for u in U3_vals]

        # Youngs/Shear Modulus and Poissons Ratio:
        if loading_direction == 1:
            E1 = (stressX[-1] - stressX[0]) / (strainX[-1] - strainX[0])
            P12 = (strainY[-1] - strainY[0]) / (strainX[-1] - strainX[0])
            P13 = (strainZ[-1] - strainZ[0]) / (strainX[-1] - strainX[0])

        elif loadin_direction == 2:
            E2 = (stressY[-1] - stressY[0]) / (strainY[-1] - strainY[0])
            P12 = (strainY[-1] - strainY[0]) / (strainX[-1] - strainX[0])
            P23 = (strainZ[-1] - strainZ[0]) / (strainY[-1] - strainY[0])

        elif loadin_direction == 3:
            E2 = (stressZ[-1] - stressZ[0]) / (strainZ[-1] - strainZ[0])
            P13 = (strainZ[-1] - strainZ[0]) / (strainX[-1] - strainX[0])
            P23 = (strainZ[-1] - strainZ[0]) / (strainY[-1] - strainY[0])

        # Open file and write simulation data:
        with open('Results - ' + job + '.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Results from ' + job + ':'])
            writer.writerow(['Time', 'RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3', 'StressX', 'StressY', 'StressZ', 'StrainX', 'StrainY', 'StrainZ'])
            for c, time in enumerate(time_vals):
                writer.writerow([time, RF1_vals[c], RF2_vals[c], RF3_vals[c], U1_vals[c], U2_vals[c], U3_vals[c],
                                 stressX[c], stressY[c], stressZ[c], strainX[c], strainY[c], strainZ[c]])

        odb.close()
    return E1, E2, E3, P12, P13, P23


############################# VARIABLES ###################################
rve_jobs = ['LongitudinalTensionAnalysis', 'LongitudinalCompressionAnalysis', 'LongitudinalShearAnalysis',
            'TransverseSideTensionAnalysis', 'TransverseSideCompressionAnalysis', 'TransverseSideShearAnalysis',
            'TransverseTopTensionAnalysis', 'TransverseTopCompressionAnalysis', 'TransverseTopShearAnalysis']
comp_jobs = ['TensionAnalysis', 'CompressionAnalysis', 'ShearAnalysis']
path = './ODBData/'
RVE_size = 120

E1, E2, E3, P12, P13, P23 = readODB(path, rve_jobs, RVE_size)

# Open file and write material properties:
with open('MaterialProperties.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['MaterialProperties:'])
    writer.writerow(['E1', 'E2', 'E3', 'P12', 'P13', 'P23'])
    for c, time in enumerate(time_vals):
        writer.writerow([E1, E2, E3, P12, P13, P23])

# End of script:
print('*************************')
print('Results written, no errors!')
