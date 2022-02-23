from part import *
from material import *
from section import *
from assembly import *
from step import *
from interaction import *
from load import *
from mesh import *
from optimization import *
from job import *
from sketch import *
from visualization import *
from connectorBehavior import *
import random
from array import *
from odbAccess import openOdb
import odbAccess
import math
import numpy
import os
import shutil

print('Running OBD reader...')

# Number of jobs:
Max_iterations = 1

isFirstIP = True
for q in range(Max_iterations):
    odbname = 'TestODB'
    path = './Results/'
    myodbpath = path + odbname + '.odb'
    odb = openOdb(myodbpath)

    allIPs = odb.steps['StaticAnalysis'].historyRegions.keys()

    Total_load = 0.0

    for integrationPoint in allIPs:

        if (isFirstIP == True):
            isFirstIP = False
            continue

        tipHistories = odb.steps['StaticAnalysis'].historyRegions[integrationPoint]

        HistoryOutput_RF1 = tipHistories.historyOutputs['RF1'].data
        HistoryOutput_RF2 = tipHistories.historyOutputs['RF2'].data
        HistoryOutput_RF3 = tipHistories.historyOutputs['RF3'].data

        HistoryOutput_U1 = tipHistories.historyOutputs['U1'].data
        HistoryOutput_U2 = tipHistories.historyOutputs['U2'].data
        HistoryOutput_U3 = tipHistories.historyOutputs['U3'].data

        # Open text file to write results:
        sortie = open('ODBResults.txt', 'w')

        # Write results to file:
        sortie.write('Results: ')
        sortie.write('\nRF1: ' + str(HistoryOutput_RF1))
        sortie.write('\nRF2: ' + str(HistoryOutput_RF2))
        sortie.write('\nRF3: ' + str(HistoryOutput_RF3))
        sortie.write('\nU1: ' + str(HistoryOutput_U1))
        sortie.write('\nU2: ' + str(HistoryOutput_U2))
        sortie.write('\nU3: ' + str(HistoryOutput_U3))

    odb.close()
#################################################################
    RVE_size = 120.0
    Strain = 0.1
    Displacement = RVE_size * Strain

    Area = RVE_size**2
    Original_length = RVE_size

    Stress = -Total_load / Area
    Strain = Displacement / Original_length

    Homogenized_E = Stress / Strain

    isFirstIP = True

    sortie.write('\nHomogenized E: ' + str(Homogenized_E))
sortie.close()

# End of script:
print('*************************')
print('End of script, no errors!')
