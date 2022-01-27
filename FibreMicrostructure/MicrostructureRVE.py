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
interface_diameter = 1.15 * fibre_diameter

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

# Interface Medium props:
i_name = 'Interface Medium'
i_E = 70000000000.0
i_P = 0.35

# Load displacement:
l_disp = 15.0

# Mesh density:
md = 5.0

# Fiber positions:
point_lst = [(20, -48), (-53, 24), (-20, -12), (-29, 57), (25, 4), (9, 45), (-53, -24), (58, -55), (-23, 28), (-9, -43),
             (-3, 8), (14, -17), (39, -30), (49, 2), (-39, 2), (38, 49), (67.0, 24), (-29, -63.0), (67.0, -24), (-62.0, -55),
             (58, 65.0), (-62.0, 65.0)]
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

# Interface Medium creation:
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile1__', sheetSize=1)
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(interface_diameter / 2, 0.0))
p1 = mdb.models['Model-1'].Part(name='InterfaceMedium', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p1.BaseSolidExtrude(sketch=s1, depth=RVE_size)
s1.unsetPrimaryObject()
p1 = mdb.models['Model-1'].parts['InterfaceMedium']
del mdb.models['Model-1'].sketches['__profile1__']

# Matrix creation:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__profile2__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.rectangle(point1=(-(RVE_size / 1.9), (RVE_size / 1.9)), point2=((RVE_size / 1.9), -(RVE_size / 1.9)))
p2 = mdb.models['Model-1'].Part(name='EpoxyCube', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p2.BaseSolidExtrude(sketch=s2, depth=RVE_size)
s2.unsetPrimaryObject()
p2 = mdb.models['Model-1'].parts['EpoxyCube']
del mdb.models['Model-1'].sketches['__profile2__']

# Material creation:
mdb.models['Model-1'].Material(name=m_name)
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].Material(name=i_name)
mdb.models['Model-1'].materials[m_name].Elastic(table=((m_E, m_P), ))
mdb.models['Model-1'].materials[m_name].Plastic(scaleStress=None, table=((m_Ys, m_Ps), ))
mdb.models['Model-1'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P1, f_P2, f_P3, f_G1, f_G2, f_G3), ))
mdb.models['Model-1'].materials[i_name].Elastic(table=((i_E, i_P), ))

# Section creation:
mdb.models['Model-1'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Int_sec', material=i_name, thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Epo_sec', material=m_name, thickness=None)

# Assembly creation:
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)

# Fibre placement based on positions:
for c, point in enumerate(point_lst):
    x, y = point
    a.Instance(name='Fibre-' + str(c + 1), part=p, dependent=ON)
    a.Instance(name='InterfaceMedium-' + str(c + 1), part=p1, dependent=ON)
    a.translate(instanceList=('Fibre-' + str(c + 1), ), vector=(x, y, 0.0))
    a.translate(instanceList=('InterfaceMedium-' + str(c + 1), ), vector=(x, y, 0.0))
a.Instance(name='EpoxyCube-1', part=p2, dependent=ON)

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='RVECube', instances=(a.instances['Fibre-1'], a.instances['InterfaceMedium-1'], a.instances['Fibre-2'], a.instances['InterfaceMedium-2'],
                                                      a.instances['Fibre-3'], a.instances['InterfaceMedium-3'], a.instances['Fibre-4'], a.instances['InterfaceMedium-4'],
                                                      a.instances['Fibre-5'], a.instances['InterfaceMedium-5'], a.instances['Fibre-6'], a.instances['InterfaceMedium-6'],
                                                      a.instances['Fibre-7'], a.instances['InterfaceMedium-7'], a.instances['Fibre-8'], a.instances['InterfaceMedium-8'],
                                                      a.instances['Fibre-9'], a.instances['InterfaceMedium-9'], a.instances['Fibre-10'], a.instances['InterfaceMedium-10'],
                                                      a.instances['Fibre-11'], a.instances['InterfaceMedium-11'], a.instances['Fibre-12'], a.instances['InterfaceMedium-12'],
                                                      a.instances['Fibre-13'], a.instances['InterfaceMedium-13'], a.instances['Fibre-14'], a.instances['InterfaceMedium-14'],
                                                      a.instances['Fibre-15'], a.instances['InterfaceMedium-15'], a.instances['Fibre-16'], a.instances['InterfaceMedium-16'],
                                                      a.instances['Fibre-17'], a.instances['InterfaceMedium-17'], a.instances['Fibre-18'], a.instances['InterfaceMedium-18'],
                                                      a.instances['Fibre-19'], a.instances['InterfaceMedium-19'], a.instances['Fibre-20'], a.instances['InterfaceMedium-20'],
                                                      a.instances['Fibre-21'], a.instances['InterfaceMedium-21'], a.instances['Fibre-22'], a.instances['InterfaceMedium-22'],
                                                      a.instances['EpoxyCube-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['Fibre']
del mdb.models['Model-1'].parts['InterfaceMedium']
del mdb.models['Model-1'].parts['EpoxyCube']
p = mdb.models['Model-1'].parts['RVECube']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(-55.68058, 31.096438, 120.0)), sketchUpEdge=e.findAt(coordinates=(63.157895, 53.397131, 120.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(-0.241748, -0.442281, 120.0))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=1, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=(-90, 90), point2=(90, -90))
s.rectangle(point1=(-60.0, 60.0), point2=(60.0, -60.0))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(-55.68058, 31.096438, 120.0)), sketchUpEdge=e1.findAt(coordinates=(63.157895, 53.397131, 120.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Cell assignment:
fibreCells = p.cells.findAt(((-56.413335, 58.871223, 0.0), ), ((-55.526438, -59.875866, 0.0), ), ((58.475918, -50.272881, 0.0), ), ((-36.642977, -6.516219, 0.0), ),
                            ((41.357023, -38.51622, 0.0), ), ((-0.642977, -0.516219, 0.0), ), ((-20.642977, 19.48378, 0.0), ), ((27.357023, -4.516219, 0.0), ),
                            ((-17.642977, -20.51622, 0.0), ), ((22.357023, -56.51622, 0.0), ), ((11.357023, 36.48378, 0.0), ), ((-6.642978, -51.51622, 0.0), ),
                            ((16.357022, -25.51622, 0.0), ), ((51.357023, -6.516219, 0.0), ), ((40.357023, 40.48378, 0.0), ), ((58.464441, 56.647166, 0.0), ),
                            ((59.077212, -22.762114, 0.0), ), ((59.077212, 25.237886, 0.0), ), ((-54.243562, -14.462568, 0.0), ), ((-54.243562, 33.537434, 0.0), ),
                            ((-32.333333, 58.705147, 0.0), ), ((-26.313555, -59.321499, 0.0), ))
interfaceCells = p.cells.findAt(((-53.158894, 58.619068, 0.0), ), ((-52.735614, -59.875866, 0.0), ), ((58.475918, -44.670522, 0.0), ), ((-59.3367, 15.751175, 0.0), ),
                                ((-59.3367, -32.248825, 0.0), ), ((58.872059, 16.773137, 0.0), ), ((58.872059, -16.773137, 0.0), ), ((58.582887, 54.14256, 0.0), ),
                                ((-37.533047, -8.708205, 0.0), ), ((40.466953, -40.708205, 0.0), ), ((-1.533047, -2.708205, 0.0), ), ((-21.533047, 17.291795, 0.0), ),
                                ((26.466953, -6.708205, 0.0), ), ((-18.533047, -22.708205, 0.0), ), ((21.466953, -58.708205, 0.0), ), ((10.466953, 34.291795, 0.0), ),
                                ((-7.533047, -53.708205, 0.0), ), ((15.466953, -27.708205, 0.0), ), ((38.065669, 1.293498, 0.0), ), ((43.152304, 57.955861, 0.0), ),
                                ((-18.75632, 59.277072, 0.0), ), ((-18.896051, -59.101994, 0.0), ))
matrixCells = p.cells.findAt(((59.758252, -36.500721, 80.0), ))

# Fibre orientation assignment:
e = p.edges
p.DatumCsysByThreePoints(name='Datum csys-1', coordSysType=CARTESIAN, origin=p.InterestingPoint(edge=e.findAt(coordinates=(59.758252, -27.448082, 120.0)), rule=MIDDLE), point1=p.InterestingPoint(edge=e.findAt(coordinates=(59.758252, -20.551918, 0.0)), rule=MIDDLE), point2=p.InterestingPoint(edge=e.findAt(coordinates=(59.758252, -17.103835, 90.0)), rule=MIDDLE))
region = regionToolset.Region(cells=fibreCells)
orientation = mdb.models['Model-1'].parts['RVECube'].datums[3]
mdb.models['Model-1'].parts['RVECube'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# Section assignment:
region = regionToolset.Region(cells=fibreCells)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
region = regionToolset.Region(cells=interfaceCells)
p.SectionAssignment(region=region, sectionName='Int_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
region = regionToolset.Region(cells=matrixCells)
p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
print('Assembly done!')

# Seeding and meshing:
p.setMeshControls(regions=fibreCells + interfaceCells + matrixCells, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
p.setElementType(regions=(cells, ), elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=md, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Set Assignment:
f = p.faces
faces = f.findAt(((-60.241748, -44.648925, 80.0), ), ((-60.241748, -40.067963, 80.0), ), ((-60.241748, -31.575269, 40.0), ), ((-60.241748, -21.701279, 40.0), ),
                 ((-60.241748, -16.42473, 80.0), ), ((-60.241748, -5.022173, 80.0), ), ((-60.241748, 16.42473, 40.0), ), ((-60.241748, 21.701279, 80.0), ),
                 ((-60.241748, 31.575269, 80.0), ), ((-60.241748, 39.834054, 80.0), ), ((-60.241748, 54.142064, 80.0), ), ((-60.241748, 58.090408, 40.0), ),
                 ((-60.241748, -50.251283, 40.0), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((59.758252, 56.623096, 40.0), ), ((59.758252, 54.648925, 80.0), ), ((59.758252, 39.834054, 40.0), ), ((59.758252, 31.575269, 40.0), ),
                 ((59.758252, 21.701279, 40.0), ), ((59.758252, 15.745625, 40.0), ), ((59.758252, 9.064341, 40.0), ), ((59.758252, -36.500721, 80.0), ),
                 ((59.758252, -44.648925, 40.0), ), ((59.758252, -55.346781, 40.0), ), ((59.758252, 0.645583, 40.0), ), ((59.758252, -31.575269, 80.0), ),
                 ((59.758252, -10.732096, 40.0), ), ((59.758252, -21.701279, 80.0), ), ((59.758252, -16.42473, 40.0), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((59.077212, -22.762114, 0.0), ), ((58.475918, -50.272881, 0.0), ), ((-26.313555, -59.321499, 0.0), ), ((-18.896051, -59.101994, 0.0), ),
                 ((-55.526438, -59.875866, 0.0), ), ((58.582887, 54.14256, 0.0), ), ((-54.243562, -14.462568, 0.0), ), ((-18.75632, 59.277072, 0.0), ),
                 ((-54.243562, 33.537434, 0.0), ), ((59.023927, -7.60488, 0.0), ), ((-56.413335, 58.871223, 0.0), ), ((-53.158894, 58.619068, 0.0), ),
                 ((-52.735614, -59.875866, 0.0), ), ((58.475918, -44.670522, 0.0), ), ((-32.333333, 58.705147, 0.0), ), ((-59.3367, 15.751175, 0.0), ),
                 ((-59.3367, -32.248825, 0.0), ), ((58.872059, 16.773137, 0.0), ), ((59.077212, 25.237886, 0.0), ), ((58.872059, -16.773137, 0.0), ),
                 ((58.464441, 56.647166, 0.0), ), ((43.152304, 57.955861, 0.0), ), ((40.357023, 40.48378, 0.0), ), ((38.065669, 1.293498, 0.0), ),
                 ((51.357023, -6.516219, 0.0), ), ((15.466953, -27.708205, 0.0), ), ((16.357022, -25.51622, 0.0), ), ((-7.533047, -53.708205, 0.0), ),
                 ((-6.642978, -51.51622, 0.0), ), ((10.466953, 34.291795, 0.0), ), ((11.357023, 36.48378, 0.0), ), ((21.466953, -58.708205, 0.0), ),
                 ((22.357023, -56.51622, 0.0), ), ((-18.533047, -22.708205, 0.0), ), ((-17.642977, -20.51622, 0.0), ), ((26.466953, -6.708205, 0.0), ),
                 ((27.357023, -4.516219, 0.0), ), ((-21.533047, 17.291795, 0.0), ), ((-20.642977, 19.48378, 0.0), ), ((-1.533047, -2.708205, 0.0), ),
                 ((-0.642977, -0.516219, 0.0), ), ((40.466953, -40.708205, 0.0), ), ((41.357023, -38.51622, 0.0), ), ((-37.533047, -8.708205, 0.0), ),
                 ((-36.642977, -6.516219, 0.0), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((58.872059, -16.773137, 120.0), ), ((58.999016, -0.630029, 120.0), ), ((58.475918, -44.670522, 120.0), ), ((59.077212, 25.237886, 120.0), ),
                 ((58.872059, 16.773137, 120.0), ), ((58.464441, 56.647166, 120.0), ), ((27.274138, 50.423578, 120.0), ), ((-52.735614, -59.875866, 120.0), ),
                 ((-48.938168, -25.186813, 120.0), ), ((-25.716098, 59.277072, 120.0), ), ((-59.3367, 15.751175, 120.0), ), ((33.467287, -58.399541, 120.0), ),
                 ((-56.413335, 58.871223, 120.0), ), ((-53.158894, 58.619068, 120.0), ), ((-55.526438, -59.875866, 120.0), ), ((-31.686444, -59.321499, 120.0), ),
                 ((-18.896051, -59.101994, 120.0), ), ((58.475918, -50.272881, 120.0), ), ((-18.75632, 59.277072, 120.0), ), ((-48.938168, 22.813187, 120.0), ),
                 ((-59.3367, -15.751175, 120.0), ), ((59.077212, -22.762114, 120.0), ), ((58.582887, 54.14256, 120.0), ), ((40.357023, 57.51622, 120.0), ),
                 ((51.357023, 10.516219, 120.0), ), ((15.466953, -6.291795, 120.0), ), ((16.357022, -8.483781, 120.0), ), ((-7.533047, -32.291795, 120.0), ),
                 ((-6.642978, -34.48378, 120.0), ), ((10.466953, 55.708205, 120.0), ), ((11.357023, 53.51622, 120.0), ), ((21.466953, -37.291795, 120.0), ),
                 ((22.357023, -39.48378, 120.0), ), ((-18.533047, -1.291795, 120.0), ), ((-17.642977, -3.483781, 120.0), ), ((26.466953, 14.708205, 120.0), ),
                 ((27.357023, 12.516219, 120.0), ), ((-21.533047, 38.708205, 120.0), ), ((-20.642977, 36.51622, 120.0), ), ((-1.533047, 18.708205, 120.0), ),
                 ((-0.642977, 16.51622, 120.0), ), ((40.466953, -19.291795, 120.0), ), ((41.357023, -21.48378, 120.0), ), ((-37.533047, 12.708205, 120.0), ),
                 ((-36.642977, 10.516219, 120.0), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((-55.821, 59.557719, 40.0), ), ((-52.449725, 59.557719, 40.0), ), ((-44.097731, 59.557719, 40.0), ), ((-39.182233, 59.557719, 40.0), ),
                 ((-25.777542, 59.557719, 40.0), ), ((-18.817765, 59.557719, 80.0), ), ((16.364648, 59.557719, 40.0), ), ((39.51967, 59.557719, 40.0), ),
                 ((44.329098, 59.557719, 80.0), ), ((49.030176, 59.557719, 40.0), ), ((56.37571, 59.557719, 40.0), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((49.030176, -60.442281, 80.0), ), ((25.983503, -60.442281, 80.0), ), ((-18.302902, -60.442281, 80.0), ), ((-25.777542, -60.442281, 80.0), ),
                 ((-39.182233, -60.442281, 80.0), ), ((-44.097731, -60.442281, 80.0), ), ((-53.030176, -60.442281, 40.0), ), ((-55.821, -60.442281, 80.0), ),
                 ((52.993168, -60.442281, 40.0), ))
p.Set(faces=faces, name='YBottom')

# Longitudinal Shear setup:
mdb.models.changeKey(fromName='Model-1', toName='LongitudinalShear')
mdb.Model(name='TransverseShear', objectToCopy=mdb.models['LongitudinalShear'])
a = mdb.models['LongitudinalShear'].rootAssembly
a.regenerate()
# History output:
regionDef = mdb.models['LongitudinalShear'].rootAssembly.allInstances['RVECube-1'].sets['ZFront']
mdb.models['LongitudinalShear'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)
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
# History output:
regionDef = mdb.models['TransverseShear'].rootAssembly.allInstances['RVECube-1'].sets['XFront']
mdb.models['TransverseShear'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)
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
