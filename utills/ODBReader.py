from job import *
from odbAccess import openOdb
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

        # Stresses & Strains:
        stressX = [rf / RVE_size**2 for rf in RF1_vals]
        stressY = [rf / RVE_size**2 for rf in RF2_vals]
        stressZ = [rf / RVE_size**2 for rf in RF3_vals]
        strainX = [u / RVE_size for u in U1_vals]
        strainY = [u / RVE_size for u in U2_vals]
        strainZ = [u / RVE_size for u in U3_vals]

        # Open file and write results:
        with open('Results - ' + job + '.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Results from ' + job + ':'])
            writer.writerow(['Time', 'RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3', 'StressX', 'StressY', 'StressZ', 'StrainX', 'StrainY', 'StrainZ'])
            for c, time in enumerate(time_vals):
                writer.writerow([time, RF1_vals[c], RF2_vals[c], RF3_vals[c], U1_vals[c], U2_vals[c], U3_vals[c],
                                 stressX[c], stressY[c], stressZ[c], strainX[c], strainY[c], strainZ[c]])
        odb.close()


############################# VARIABLES ###################################
rve_jobs = ['LongitudinalTensionAnalysis', 'LongitudinalCompressionAnalysis', 'LongitudinalShearAnalysis',
            'TransverseSideTensionAnalysis', 'TransverseSideCompressionAnalysis', 'TransverseSideShearAnalysis',
            'TransverseTopTensionAnalysis', 'TransverseTopCompressionAnalysis', 'TransverseTopShearAnalysis']
comp_jobs = ['TensionAnalysis', 'CompressionAnalysis', 'ShearAnalysis']
path = './ODBData/'
RVE_size = 120

readODB(path, rve_jobs, RVE_size)

# End of script:
print('*************************')
print('Results written, no errors!')
