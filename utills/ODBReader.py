from job import *
from odbAccess import openOdb
import odbAccess
print('Running ODB reader...')


def readODB(path, job_list):
    isFirstIP = True
    for c, job in enumerate(job_list):

        odbpath = path + job + '.odb'
        odb = openOdb(odbpath)

        allIPs = odb.steps['StaticAnalysis'].historyRegions.keys()

        total_load = 0.0

        for integrationPoint in allIPs:

            if isFirstIP:
                isFirstIP = False
                continue

            t = odb.steps['StaticAnalysis'].historyRegions[integrationPoint]

            hOut_U1 = t.historyOutputs['U1'].data
            hOut_U2 = t.historyOutputs['U2'].data
            hOut_U3 = t.historyOutputs['U3'].data
            hOut_RF1 = t.historyOutputs['RF1'].data
            hOut_RF2 = t.historyOutputs['RF2'].data
            hOut_RF3 = t.historyOutputs['RF3'].data

            def matCol(i, matrix):
                return [row[i] for row in matrix]

            U1_vals = matCol(1, hOut_U1)
            U2_vals = matCol(1, hOut_U2)
            U3_vals = matCol(1, hOut_U3)
            RF1_vals = matCol(1, hOut_RF1)
            RF2_vals = matCol(1, hOut_RF2)
            RF3_vals = matCol(1, hOut_RF3)
            time_vals = matCol(0, hOut_RF1)

            # Open text file and write results:
            sortie = open('Results - ' + job + '.csv', 'w')

            sortie.write('Results from ' + job + ': \n')
            sortie.write('\nU1: ' + str(U1_vals))
            sortie.write('\n\nU2: ' + str(U2_vals))
            sortie.write('\n\nU3: ' + str(U3_vals))
            sortie.write('\n\nRF1: ' + str(RF1_vals))
            sortie.write('\n\nRF2: ' + str(RF2_vals))
            sortie.write('\n\nRF3: ' + str(RF3_vals))
            sortie.write('\n\nTime: ' + str(time_vals))

        isFirstIP = True
        odb.close()
        sortie.close()
    return U1_vals, U2_vals, U3_vals, RF1_vals, RF2_vals, RF3_vals


# Job lists:
test_jobs = ['TestODB1', 'TestODB2', 'TestODB3']

rve_jobs = ['LongitudinalTensionAnalysis', 'LongitudinalCompressionAnalysis', 'LongitudinalShearAnalysis',
            'TransverseSideTensionAnalysis', 'TransverseSideCompressionAnalysis', 'TransverseSideShearAnalysis',
            'TransverseTopTensionAnalysis', 'TransverseTopCompressionAnalysis', 'TransverseTopShearAnalysis']

comp_jobs = ['TensionAnalysis', 'CompressionAnalysis', 'ShearAnalysis']

path = './ODBData/'

U1_vals, U2_vals, U3_vals, RF1_vals, RF2_vals, RF3_vals = readODB(path, test_jobs)

RVE_size = 120
e1, e2, e3 = [], [], []

for u1 in U1_vals:
    e1.append(u1 / RVE_size)

for u2 in U2_vals:
    e2.append(u2 / RVE_size)

for u3 in U3_vals:
    e3.append(u3 / RVE_size)

print(e1, e2, e3)

# End of script:
print('*************************')
print('Results written, no errors!')
