from abaqus import *
from abaqusConstants import *
from math import sqrt
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
import random

############################# VARIABLES ###################################
# Scale: Microns

fibre_diameter = 20
fibre_count = 16
fibre_spacing_buffer = 2

# RVE cube:
RVE_size = 6 * fibre_diameter

# Matrix props:
m_name = 'Epoxy Resin'
m_E = 38000000000.0
m_P = 0.35
m_Ys = 55000000.0
m_Ps = 0.0

# Fiber props:
f_name = 'Carbon Fiber'
f_E1 = 105500000000.0
f_E2 = 7200000000.0
f_E3 = 7200000000.0
f_G1 = 3400000000.0
f_G2 = 3400000000.0
f_G3 = 2520000000.0
f_P1 = 0.34
f_P2 = 0.34
f_P3 = 0.378

# Load displacement:
l_disp = 15.0

# Mesh density:
md = 0.5
###########################################################################

# New model database creation:
Mdb()
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
print('Running script...')

# Fibre creation:
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(fibre_diameter / 2, 0.0))
p = mdb.models['Model-1'].Part(name='Fibre', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p.BaseSolidExtrude(sketch=s, depth=RVE_size)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Fibre']
del mdb.models['Model-1'].sketches['__profile__']

# RVECube creation:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__profile2__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.rectangle(point1=(-(RVE_size / 2), (RVE_size / 2)), point2=((RVE_size / 2), -(RVE_size / 2)))
p2 = mdb.models['Model-1'].Part(name='RVECube', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p2.BaseSolidExtrude(sketch=s2, depth=RVE_size)
s2.unsetPrimaryObject()
p2 = mdb.models['Model-1'].parts['RVECube']
del mdb.models['Model-1'].sketches['__profile2__']

# Material creation:
mdb.models['Model-1'].Material(name=m_name)
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].materials[m_name].Elastic(table=((m_E, m_P), ))
mdb.models['Model-1'].materials[m_name].Plastic(scaleStress=None, table=((m_Ys, m_Ps), ))
mdb.models['Model-1'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P1, f_P2, f_P3, f_G1, f_G2, f_G3), ))

# Section creation:
mdb.models['Model-1'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Epo_sec', material=m_name, thickness=None)

# Assembly creation:
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)

# Random fibre distribution:
x_lst, y_lst = [0], [0]
for i in range(fibre_count + 1):
    x = random.randrange(-(RVE_size / 2), (RVE_size / 2))
    y = random.randrange(-(RVE_size / 2), (RVE_size / 2))
    x_lst.append(x)
    y_lst.append(y)

    for c, val in enumerate(x_lst):
        x1, y1 = x_lst[c], y_lst[c]
        dx, dy = abs(x1 - x), abs(y1 - 1)
        if ((fibre_diameter / 2) + fibre_spacing_buffer) < (sqrt((dx**2) + (dy**2))):
            a.Instance(name='Fibre-' + str(i + 1), part=p, dependent=ON)
            a.translate(instanceList=('Fibre-' + str(i + 1), ), vector=(x, y, 0.0))
        else:
            break

a.Instance(name='RVECube-1', part=p2, dependent=ON)

# (sqrt((dx**2) + (dy**2)))

# Merge into composite & delete original parts:

# Composite specimen creation:

# # Fibre orientation assignment:
# v1 = p.vertices
# p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(62.699112, -2.0, 59.208453)), point1=v1.findAt(coordinates=(62.699112, -2.0, 21.208453)), point2=v1.findAt(coordinates=(62.699112, 2.0, 21.208453)), name='Datum csys-1', coordSysType=CARTESIAN)
# v2 = p.vertices
# p.DatumCsysByThreePoints(origin=v2.findAt(coordinates=(62.699112, -2.0, 59.208453)), point1=v2.findAt(coordinates=(24.699112, -2.0, 59.208453)), point2=v2.findAt(coordinates=(24.699112, 2.0, 59.208453)), name='Datum csys-2', coordSysType=CARTESIAN)
# c = p.cells
# cells = c.findAt(((38.593716, -0.303228, 21.208453), ), ((44.8769, -0.303228, 21.208453), ), ((61.93725, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ),
#                  ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ))
# region = regionToolset.Region(cells=cells)
# orientation = mdb.models['Model-1'].parts['Composite'].datums[3]
# mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)
# c = p.cells
# cells = c.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ),
#                  ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 58.795686), ))
# region = regionToolset.Region(cells=cells)
# orientation = mdb.models['Model-1'].parts['Composite'].datums[4]
# mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# # Section assignment:
# c = p.cells
# cells = c.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ),
#                  ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 58.795686), ), ((38.593716, -0.303228, 21.208453), ), ((44.8769, -0.303228, 21.208453), ),
#                  ((61.93725, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ), ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ))
# region = regionToolset.Region(cells=cells)
# p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
# c = p.cells
# cells = c.findAt(((49.948112, -0.147777, 59.208453), ))
# region = regionToolset.Region(cells=cells)
# p = mdb.models['Model-1'].parts['Composite']
# p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
# print('Assembly done!')

# # Seeding and meshing:
# c = p.cells
# pickedRegions = c.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ),
#                          ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 58.795686), ), ((38.593716, -0.303228, 21.208453), ), ((44.8769, -0.303228, 21.208453), ),
#                          ((61.93725, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ), ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ),
#                          ((49.948112, -0.147777, 59.208453), ))
# p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
# elemType1 = mesh.ElemType(elemCode=C3D20R)
# elemType2 = mesh.ElemType(elemCode=C3D15)
# elemType3 = mesh.ElemType(elemCode=C3D10)
# pickedRegions = (cells, )
# p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
# p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
# p.generateMesh()
# print('Meshing done!')

# # Static analysis step:
# mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# # Set Assignment:s
# f = p.faces
# faces = f.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, -0.133154, 58.795686), ),
#                  ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ), ((24.699112, -1.083472, 50.98902), ))
# p.Set(faces=faces, name='XBack')
# faces = f.findAt(((62.699112, -0.140695, 27.377146), ), ((62.699112, -0.140695, 52.509888), ), ((62.699112, -0.140695, 33.660332), ), ((62.699112, -0.140695, 58.793072), ),
#                  ((62.699112, 0.140695, 41.737892), ), ((62.699112, 0.140695, 35.454708), ), ((62.699112, -1.189111, 25.817607), ))
# p.Set(faces=faces, name='XFront')
# faces = f.findAt(((61.93725, 0.303228, 21.208453), ), ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ),
#                  ((44.8769, -0.303228, 21.208453), ), ((38.593716, -0.303228, 21.208453), ), ((32.773502, -1.066097, 21.208453), ))
# p.Set(faces=faces, name='ZBack')
# faces = f.findAt(((61.932788, -0.032528, 59.208453), ), ((55.649602, -0.032528, 59.208453), ), ((30.516861, -0.032528, 59.208453), ), ((36.800046, -0.032528, 59.208453), ),
#                  ((44.881362, 0.032528, 59.208453), ), ((38.598178, 0.032528, 59.208453), ), ((49.948112, -0.147777, 59.208453), ))
# p.Set(faces=faces, name='ZFront')
# faces = f.findAt(((50.032445, 2.0, 33.87512), ))
# p.Set(faces=faces, name='YTop')
# faces = f.findAt(((50.032445, -2.0, 46.541787), ))
# p.Set(faces=faces, name='YBottom')

# # History output:
# regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Composite-1'].sets['XFront']
# mdb.models['Model-1'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)

# # Boundary conditions:
# region = a.instances['Composite-1'].sets['XBack']
# mdb.models['Model-1'].DisplacementBC(name='XBackSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
# region = a.instances['Composite-1'].sets['ZBack']
# mdb.models['Model-1'].DisplacementBC(name='ZBackSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
# region = a.instances['Composite-1'].sets['YBottom']
# mdb.models['Model-1'].DisplacementBC(name='YBaseSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# # Front face displacement:
# region = a.instances['Composite-1'].sets['XFront']
# mdb.models['Model-1'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

# # Load case creation:
# mdb.models.changeKey(fromName='Model-1', toName='XTensCase')
# mdb.Model(name='XCompCase', objectToCopy=mdb.models['XTensCase'])
# mdb.Model(name='YShearCase', objectToCopy=mdb.models['XTensCase'])

# # Loading model changes:
# mdb.models['XTensCase'].boundaryConditions['Load'].setValues(u1=l_disp)
# a = mdb.models['XTensCase'].rootAssembly
# a.regenerate()
# mdb.models['XCompCase'].boundaryConditions['Load'].setValues(u1=-l_disp)
# a = mdb.models['XCompCase'].rootAssembly
# a.regenerate()
# mdb.models['YShearCase'].boundaryConditions['Load'].setValues(u2=l_disp)
# mdb.models['YShearCase'].boundaryConditions['XBackSupport'].setValues(u2=SET, u3=SET)
# a = mdb.models['YShearCase'].rootAssembly
# region = a.instances['Composite-1'].sets['XFront']
# mdb.models['YShearCase'].DisplacementBC(name='XFrontRoller', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
# del mdb.models['YShearCase'].boundaryConditions['YBaseSupport']
# del mdb.models['YShearCase'].boundaryConditions['ZBackSupport']
# a.regenerate()
# print('Constraining and Loading done!')

# # # Job creation:
# mdb.Job(name='TensionAnalysis', model='XTensCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
#         explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.Job(name='CompressionAnalysis', model='XCompCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
#         explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.Job(name='ShearAnalysis', model='YShearCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
#         explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# # mdb.jobs['TensionAnalysis'].submit(consistencyChecking=OFF)
# # mdb.jobs['ShearAnalysis'].submit(consistencyChecking=OFF)
# # mdb.jobs['CompressionAnalysis'].submit(consistencyChecking=OFF)
# # print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
