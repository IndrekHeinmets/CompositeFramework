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
md = 5.0

# Fiber positions:
point_lst = [(-47, 22), (-11, -29), (-37, -42), (5, 41), (45, 38), (31, -7), (2, 18), (-34, 46), (-31, 1), (-54, -20),
             (-15, -58), (44, -45), (33, 16), (2, -4), (57, 15), (14, -30), (26, 62), (-63, 43), (66, -23)]
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

# Matrix creation:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__profile2__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.rectangle(point1=(-(RVE_size / 2), (RVE_size / 2)), point2=((RVE_size / 2), -(RVE_size / 2)))
p2 = mdb.models['Model-1'].Part(name='EpoxyCube', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p2.BaseSolidExtrude(sketch=s2, depth=RVE_size)
s2.unsetPrimaryObject()
p2 = mdb.models['Model-1'].parts['EpoxyCube']
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

# Fibre placement based on positions:
for c, point in enumerate(point_lst):
    x, y = point
    a.Instance(name='Fibre-' + str(c + 1), part=p, dependent=ON)
    a.translate(instanceList=('Fibre-' + str(c + 1), ), vector=(x, y, 0.0))
a.Instance(name='EpoxyCube-1', part=p2, dependent=ON)

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='RVECube', instances=(a.instances['Fibre-1'], a.instances['Fibre-2'], a.instances['Fibre-3'], a.instances['Fibre-4'],
                                                      a.instances['Fibre-5'], a.instances['Fibre-6'], a.instances['Fibre-7'], a.instances['Fibre-8'],
                                                      a.instances['Fibre-9'], a.instances['Fibre-10'], a.instances['Fibre-11'], a.instances['Fibre-12'],
                                                      a.instances['Fibre-13'], a.instances['Fibre-14'], a.instances['Fibre-15'], a.instances['Fibre-16'],
                                                      a.instances['Fibre-17'], a.instances['Fibre-18'], a.instances['Fibre-19'], a.instances['EpoxyCube-1'], ),
                           keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['Fibre']
del mdb.models['Model-1'].parts['EpoxyCube']
p = mdb.models['Model-1'].parts['RVECube']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(42.60886, 5.727394, 120.0)), sketchUpEdge=e.findAt(coordinates=(60.0, 0.345456, 120.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.034525, -0.507101, 120.0))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=1, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=(-90, 90), point2=(90, -90))
# s.rectangle(point1=(-60.0, 60.0), point2=(60.0, -60.0))
s.rectangle(point1=(-60.034525, 60.507101), point2=(59.965475, -59.492899))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(42.60886, 5.727394, 120.0)), sketchUpEdge=e1.findAt(coordinates=(60.0, 0.345456, 120.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Fibre orientation assignment:
v1, e = p.vertices, p.edges
p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(60.0, 24.539392, 120.0)), point1=v1.findAt(coordinates=(60.0, 24.539392, 0.0)), name='Datum csys-1', coordSysType=CARTESIAN, point2=p.InterestingPoint(edge=e.findAt(coordinates=(60.0, 60.0, 30.0)), rule=MIDDLE))
c = p.cells
cells = c.findAt(((59.16942, -21.239623, 0.0), ), ((56.329138, 24.512853, 0.0), ), ((-11.696655, -59.779453, 0.0), ), ((16.357022, -38.51622, 0.0), ),
                 ((4.357023, -12.516219, 0.0), ), ((46.357023, -53.51622, 0.0), ), ((-31.642978, 37.48378, 0.0), ), ((33.357023, -15.51622, 0.0), ),
                 ((7.357023, 32.48378, 0.0), ), ((-8.642978, -37.51622, 0.0), ), ((-44.642977, 13.483781, 0.0), ), ((-34.642977, -50.51622, 0.0), ),
                 ((47.357023, 29.48378, 0.0), ), ((4.357023, 9.483781, 0.0), ), ((-28.642978, -7.516219, 0.0), ), ((35.357023, 7.483781, 0.0), ),
                 ((-59.059911, 45.710566, 0.0), ), ((-55.412684, -11.143329, 0.0), ), ((23.235078, 58.804863, 0.0), ))
region = regionToolset.Region(cells=cells)
orientation = mdb.models['Model-1'].parts['RVECube'].datums[3]
mdb.models['Model-1'].parts['RVECube'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# Section assignment:
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
c = p.cells
cells = c.findAt(((-60.0, 55.02626, 80.0), ))
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
print('Assembly done!')

# Seeding and meshing:
c = p.cells
pickedRegions = c.findAt(((59.16942, -21.239623, 0.0), ), ((56.329138, 24.512853, 0.0), ), ((-11.696655, -59.779453, 0.0), ), ((16.357022, -38.51622, 0.0), ),
                         ((4.357023, -12.516219, 0.0), ), ((46.357023, -53.51622, 0.0), ), ((-31.642978, 37.48378, 0.0), ), ((33.357023, -15.51622, 0.0), ),
                         ((7.357023, 32.48378, 0.0), ), ((-8.642978, -37.51622, 0.0), ), ((-44.642977, 13.483781, 0.0), ), ((-34.642977, -50.51622, 0.0), ),
                         ((47.357023, 29.48378, 0.0), ), ((4.357023, 9.483781, 0.0), ), ((-28.642978, -7.516219, 0.0), ), ((35.357023, 7.483781, 0.0), ),
                         ((-59.059911, 45.710566, 0.0), ), ((-55.412684, -11.143329, 0.0), ), ((23.235078, 58.804863, 0.0), ), ((-60.0, 55.02626, 80.0), ))
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
pickedRegions = (cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=md, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Set Assignment:
f = p.faces
faces = f.findAt(((60.0, -40.666667, 80.0), ), ((60.0, -20.333333, 80.0), ), ((60.0, -1.359595, 80.0), ), ((60.0, 18.179798, 80.0), ),
                 ((60.0, 36.359595, 40.0), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((-60.0, -38.666667, 40.0), ), ((-60.0, -17.333333, 40.0), ), ((-60.0, 18.307073, 40.0), ), ((-60.0, 46.179797, 40.0), ),
                 ((-60.0, 55.02626, 80.0), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((42.60886, 5.727394, 120.0), ), ((59.16942, -21.239623, 120.0), ), ((28.764923, 58.804863, 120.0), ), ((57.563628, 18.007981, 120.0), ),
                 ((-11.696655, -59.779453, 120.0), ), ((-49.557765, -21.464236, 120.0), ), ((-59.059911, 45.710566, 120.0), ), ((35.357023, 24.51622, 120.0), ),
                 ((-28.642978, 9.516219, 120.0), ), ((4.357023, 26.51622, 120.0), ), ((47.357023, 46.51622, 120.0), ), ((-34.642977, -33.48378, 120.0), ),
                 ((-44.642977, 30.51622, 120.0), ), ((-8.642978, -20.48378, 120.0), ), ((7.357023, 49.51622, 120.0), ), ((33.357023, 1.516219, 120.0), ),
                 ((-31.642978, 54.51622, 120.0), ), ((46.357023, -36.48378, 120.0), ), ((4.357023, 4.516219, 120.0), ), ((16.357022, -21.48378, 120.0), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((-59.059911, 54.55703, 0.0), ), ((59.16942, -21.239623, 0.0), ), ((23.235078, 58.804863, 0.0), ), ((56.329138, 24.512853, 0.0), ),
                 ((-11.696655, -59.779453, 0.0), ), ((-55.412684, -11.143329, 0.0), ), ((-59.059911, 45.710566, 0.0), ), ((35.357023, 7.483781, 0.0), ),
                 ((-28.642978, -7.516219, 0.0), ), ((4.357023, 9.483781, 0.0), ), ((47.357023, 29.48378, 0.0), ), ((-34.642977, -50.51622, 0.0), ),
                 ((-44.642977, 13.483781, 0.0), ), ((-8.642978, -37.51622, 0.0), ), ((7.357023, 32.48378, 0.0), ), ((33.357023, -15.51622, 0.0), ),
                 ((-31.642978, 37.48378, 0.0), ), ((46.357023, -53.51622, 0.0), ), ((4.357023, -12.516219, 0.0), ), ((16.357022, -38.51622, 0.0), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((-36.531972, -60.0, 80.0), ), ((-11.734014, -60.0, 80.0), ), ((16.531973, -60.0, 40.0), ))
p.Set(faces=faces, name='YBottom')
faces = f.findAt(((-9.198639, 60.0, 40.0), ), ((29.265986, 60.0, 40.0), ), ((43.865306, 60.0, 80.0), ))
p.Set(faces=faces, name='YTop')

# History output:
regionDef = mdb.models['Model-1'].rootAssembly.allInstances['RVECube-1'].sets['ZFront']
mdb.models['Model-1'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)

# Longitudinal Shear setup:
mdb.models.changeKey(fromName='Model-1', toName='LongitudinalShear')
mdb.Model(name='TransverseShear', objectToCopy=mdb.models['LongitudinalShear'])
a = mdb.models['LongitudinalShear'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['ZBack']
mdb.models['LongitudinalShear'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZFront']
mdb.models['LongitudinalShear'].DisplacementBC(name='ZRoller', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZFront']
mdb.models['LongitudinalShear'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=l_disp, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Longitudinal Tension setup:
mdb.Model(name='LongitudinalTension', objectToCopy=mdb.models['LongitudinalShear'])
a = mdb.models['LongitudinalTension'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XBack']
mdb.models['LongitudinalTension'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZBack']
mdb.models['LongitudinalTension'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YBottom']
mdb.models['LongitudinalTension'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZFront']
mdb.models['LongitudinalTension'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=l_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['LongitudinalTension'].boundaryConditions['ZRoller']
a.regenerate()

# Longitudinal Compression setup:
mdb.Model(name='LongitudinalCompression', objectToCopy=mdb.models['LongitudinalTension'])
a = mdb.models['LongitudinalCompression'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['ZFront']
mdb.models['LongitudinalCompression'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=-l_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Transverse Shear setup:
a = mdb.models['TransverseShear'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XBack']
mdb.models['TransverseShear'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseShear'].DisplacementBC(name='XRoller', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseShear'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=l_disp, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Transverse Tension setup:
mdb.Model(name='TransverseTension', objectToCopy=mdb.models['TransverseShear'])
a = mdb.models['TransverseTension'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XBack']
mdb.models['TransverseTension'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZBack']
mdb.models['TransverseTension'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YBottom']
mdb.models['TransverseTension'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseTension'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=l_disp, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['TransverseTension'].boundaryConditions['XRoller']
a.regenerate()

# Transverse Compression setup:
mdb.Model(name='TransverseCompression', objectToCopy=mdb.models['TransverseTension'])
a = mdb.models['TransverseCompression'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseCompression'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=-l_disp, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()
print('Constraining and Loading done!')

# Job creation:
mdb.Job(name='LongitudinalTensionAnalysis', model='LongitudinalTension', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='LongitudinalCompressionAnalysis', model='LongitudinalCompression', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='LongitudinalShearAnalysis', model='LongitudinalShear', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseTensionAnalysis', model='TransverseTension', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseCompressionAnalysis', model='TransverseCompression', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseShearAnalysis', model='TransverseShear', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['LongitudinalTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['LongitudinalCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['LongitudinalShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseShearAnalysis'].submit(consistencyChecking=OFF)
# print('Jobs submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
