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

# Number of jobs:
Max_iterations = 1

# Open text file to write results
sortie = open('ODBResults.txt', 'w')

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

        HistoryOutput_RF2 = tipHistories.historyOutputs['RF2'].data

        sortie.write('RF2 values' + HistoryOutput_RF2)

        # def column(matrix, i):
        #     return [row[i] for row in matrix]

        # RF2_values = column(HistoryOutput_RF2, 1)
        # Time_values = column(HistoryOutput_RF2, 0)

        # Load = RF2_values[-1]

        # Total_load += Load

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

    sortie.write('\n')
sortie.close()

# End of script:
print('*************************')
print('End of script, no errors!')
