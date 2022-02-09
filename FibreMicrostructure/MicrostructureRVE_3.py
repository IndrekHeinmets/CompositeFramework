from abaqus import *
from abaqusConstants import *
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
m_E = 3800000000.0
m_P = 0.35
m_Ys = 55000000.0
m_Ps = 0.0

# Fiber props:
f_name = 'Carbon Fiber'
f_E1 = 228000000000.0
f_E2 = 17200000000.0
f_E3 = 17200000000.0
f_P12 = 0.2
f_P13 = 0.2
f_P23 = 0.5
f_G12 = 27600000000.0
f_G13 = 27600000000.0
f_G23 = 5730000000.0

# Interface Medium props:
i_name = 'Interface Medium'
i_E = 10000000000.0
i_P = 0.35

# Load displacement:
strain = 0.1
l_disp = RVE_size * strain

# Mesh density:
md = 5.0

# Fiber positions:
point_lst = [(25, -18), (-38, -39), (-2, -58), (44, 37), (-39, 42), (-47, 20), (-16, 24), (59, -25), (-1, -33), (-20, -13), (34, 10), (15, 39),
             (23, -45), (-57, -55), (9, 3), (-42, -5), (-2, 62.0), (-61.0, -25), (63.0, -55), (-57, 65.0), (63.0, 65.0)]
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
mdb.models['Model-1'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P12, f_P13, f_P23, f_G12, f_G13, f_G23), ))
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
                                                      a.instances['Fibre-21'], a.instances['InterfaceMedium-21'], a.instances['EpoxyCube-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
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
s.rectangle(point1=(-(RVE_size / 2), (RVE_size / 2)), point2=((RVE_size / 2), -(RVE_size / 2)))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(-55.68058, 31.096438, 120.0)), sketchUpEdge=e1.findAt(coordinates=(63.157895, 53.397131, 120.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Cell assignment:
fibreCells = p.cells.findAt(((58.708406, -51.097102, 0.0), ), ((-53.229988, 58.746621, 0.0), ), ((-39.642977, -13.516219, 0.0), ), ((17.357022, 30.48378, 0.0), ),
                            ((-17.642977, -21.51622, 0.0), ), ((-44.642977, 11.483781, 0.0), ), ((46.357023, 28.48378, 0.0), ), ((-35.642977, -47.51622, 0.0), ),
                            ((27.357023, -26.51622, 0.0), ), ((-36.642977, 33.48378, 0.0), ), ((-13.642977, 15.483781, 0.0), ), ((1.357023, -41.51622, 0.0), ),
                            ((36.357023, 1.483781, 0.0), ), ((25.357023, -53.51622, 0.0), ), ((11.357023, -5.516219, 0.0), ), ((-59.045747, -21.997962, 0.0), ),
                            ((-52.193105, -59.875866, 0.0), ), ((58.552218, -21.805886, 0.0), ), ((1.288344, -60.173992, 0.0), ), ((-4.703152, 58.421408, 0.0), ),
                            ((59.091236, 57.194096, 0.0), ))
interfaceCells = p.cells.findAt(((58.835899, 54.900359, 0.0), ), ((58.545392, -45.097224, 0.0), ), ((58.552218, -35.342842, 0.0), ), ((-47.735614, -59.875866, 0.0), ),
                                ((-59.157074, 54.835467, 0.0), ), ((-40.533047, -15.708205, 0.0), ), ((16.466953, 28.291795, 0.0), ), ((-18.533047, -23.708205, 0.0), ),
                                ((-45.533047, 9.291795, 0.0), ), ((45.466953, 26.291795, 0.0), ), ((-36.533047, -49.708205, 0.0), ), ((26.466953, -28.708205, 0.0), ),
                                ((-37.533047, 31.291795, 0.0), ), ((-14.533047, 13.291795, 0.0), ), ((0.466953, -43.708205, 0.0), ), ((35.466953, -0.708205, 0.0), ),
                                ((24.466953, -55.708205, 0.0), ), ((10.466953, -7.708205, 0.0), ), ((-58.854153, -35.613365, 0.0), ), ((8.266627, -60.173992, 0.0), ),
                                ((8.138478, 58.20211, 0.0), ))
matrixCells = p.cells.findAt(((59.758252, 8.972106, 40.0), ))

# Fibre orientation assignment:
v = p.vertices
p.DatumCsysByThreePoints(origin=v.findAt(coordinates=(-60.241748, -60.442281, 120.0)), point1=v.findAt(coordinates=(-60.241748, -60.442281, 0.0)), point2=v.findAt(coordinates=(-60.241748, 59.557719, 0.0)), name='Datum csys-1', coordSysType=CARTESIAN)
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
p.setElementType(regions=((fibreCells + interfaceCells + matrixCells), ), elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=md, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Set Assignment:
f = p.faces
faces = f.findAt(((-60.241748, -45.015474, 80.0), ), ((-60.241748, -41.469236, 80.0), ), ((-60.241748, -35.472466, 40.0), ), ((-60.241748, -28.323737, 80.0), ),
                 ((-60.241748, -14.527534, 80.0), ), ((-60.241748, 8.972106, 80.0), ), ((-60.241748, 54.49092, 80.0), ), ((-60.241748, 58.218489, 40.0), ),
                 ((-60.241748, -50.507445, 40.0), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((59.758252, 56.879258, 40.0), ), ((59.758252, 55.015474, 80.0), ), ((59.758252, 8.972106, 40.0), ), ((59.758252, -14.527534, 40.0), ),
                 ((59.758252, -28.323737, 40.0), ), ((59.758252, -35.973721, 40.0), ), ((59.758252, -41.469236, 40.0), ), ((59.758252, -45.015474, 40.0), ),
                 ((59.758252, -55.474862, 40.0), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((58.708406, -51.097102, 0.0), ), ((1.288344, -60.173992, 0.0), ), ((-52.193105, -59.875866, 0.0), ), ((58.835899, 54.900359, 0.0), ),
                 ((-59.045747, -21.997962, 0.0), ), ((-59.157074, 54.835467, 0.0), ), ((58.380931, -38.811782, 0.0), ), ((59.091236, 57.194096, 0.0), ),
                 ((58.545392, -45.097224, 0.0), ), ((8.138478, 58.20211, 0.0), ), ((-4.703152, 58.421408, 0.0), ), ((8.266627, -60.173992, 0.0), ),
                 ((58.552218, -35.342842, 0.0), ), ((58.552218, -21.805886, 0.0), ), ((-47.735614, -59.875866, 0.0), ), ((-58.854153, -35.613365, 0.0), ),
                 ((-53.229988, 58.746621, 0.0), ), ((10.466953, -7.708205, 0.0), ), ((11.357023, -5.516219, 0.0), ), ((24.466953, -55.708205, 0.0), ),
                 ((25.357023, -53.51622, 0.0), ), ((35.466953, -0.708205, 0.0), ), ((36.357023, 1.483781, 0.0), ), ((0.466953, -43.708205, 0.0), ),
                 ((1.357023, -41.51622, 0.0), ), ((-14.533047, 13.291795, 0.0), ), ((-13.642977, 15.483781, 0.0), ), ((-37.533047, 31.291795, 0.0), ),
                 ((-36.642977, 33.48378, 0.0), ), ((26.466953, -28.708205, 0.0), ), ((27.357023, -26.51622, 0.0), ), ((-36.533047, -49.708205, 0.0), ),
                 ((-35.642977, -47.51622, 0.0), ), ((45.466953, 26.291795, 0.0), ), ((46.357023, 28.48378, 0.0), ), ((-45.533047, 9.291795, 0.0), ),
                 ((-44.642977, 11.483781, 0.0), ), ((-18.533047, -23.708205, 0.0), ), ((-17.642977, -21.51622, 0.0), ), ((16.466953, 28.291795, 0.0), ),
                 ((17.357022, 30.48378, 0.0), ), ((-40.533047, -15.708205, 0.0), ), ((-39.642977, -13.516219, 0.0), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((58.708406, -51.097102, 120.0), ), ((1.288344, -60.173992, 120.0), ), ((-52.193105, -59.875866, 120.0), ), ((58.835899, 54.900359, 120.0), ),
                 ((-59.045747, -21.997962, 120.0), ), ((-59.157074, 54.835467, 120.0), ), ((58.380931, -38.811782, 120.0), ), ((59.091236, 57.194096, 120.0), ),
                 ((58.545392, -45.097224, 120.0), ), ((8.138478, 58.20211, 120.0), ), ((-4.703152, 58.421408, 120.0), ), ((8.266627, -60.173992, 120.0), ),
                 ((58.552218, -35.342842, 120.0), ), ((58.552218, -21.805886, 120.0), ), ((-47.735614, -59.875866, 120.0), ), ((-58.854153, -35.613365, 120.0), ),
                 ((-53.229988, 58.746621, 120.0), ), ((10.466953, -7.708205, 120.0), ), ((11.357023, -5.516219, 120.0), ), ((24.466953, -55.708205, 120.0), ),
                 ((25.357023, -53.51622, 120.0), ), ((35.466953, -0.708205, 120.0), ), ((36.357023, 1.483781, 120.0), ), ((0.466953, -43.708205, 120.0), ),
                 ((1.357023, -41.51622, 120.0), ), ((-14.533047, 13.291795, 120.0), ), ((-13.642977, 15.483781, 120.0), ), ((-37.533047, 31.291795, 120.0), ),
                 ((-36.642977, 33.48378, 120.0), ), ((26.466953, -28.708205, 120.0), ), ((27.357023, -26.51622, 120.0), ), ((-36.533047, -49.708205, 120.0), ),
                 ((-35.642977, -47.51622, 120.0), ), ((45.466953, 26.291795, 120.0), ), ((46.357023, 28.48378, 120.0), ), ((-45.533047, 9.291795, 120.0), ),
                 ((-44.642977, 11.483781, 120.0), ), ((-18.533047, -23.708205, 120.0), ), ((-17.642977, -21.51622, 120.0), ), ((16.466953, 28.291795, 120.0), ),
                 ((17.357022, 30.48378, 120.0), ), ((-40.533047, -15.708205, 120.0), ), ((-39.642977, -13.516219, 120.0), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((-52.487667, 59.557719, 40.0), ), ((-47.449725, 59.557719, 40.0), ), ((-24.448206, 59.557719, 40.0), ), ((-12.210676, 59.557719, 40.0), ),
                 ((1.232393, 59.557719, 40.0), ), ((8.724174, 59.557719, 40.0), ), ((38.325407, 59.557719, 40.0), ), ((54.030176, 59.557719, 40.0), ),
                 ((58.042376, 59.557719, 40.0), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((54.030176, -60.442281, 80.0), ), ((38.325407, -60.442281, 80.0), ), ((8.210676, -60.442281, 40.0), ), ((1.232393, -60.442281, 80.0), ),
                 ((-12.210676, -60.442281, 80.0), ), ((-24.448206, -60.442281, 80.0), ), ((-48.030176, -60.442281, 40.0), ), ((-52.487667, -60.442281, 80.0), ),
                 ((56.326501, -60.442281, 40.0), ))
p.Set(faces=faces, name='YBottom')

# Longitudinal Shear setup:
mdb.models.changeKey(fromName='Model-1', toName='LongitudinalShear')
mdb.Model(name='TransverseShearSide', objectToCopy=mdb.models['LongitudinalShear'])
mdb.Model(name='TransverseShearTop', objectToCopy=mdb.models['LongitudinalShear'])
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

# Transverse Side Shear setup:
a = mdb.models['TransverseShearSide'].rootAssembly
a.regenerate()
# History output:
regionDef = mdb.models['TransverseShearSide'].rootAssembly.allInstances['RVECube-1'].sets['XFront']
mdb.models['TransverseShearSide'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XBack']
mdb.models['TransverseShearSide'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseShearSide'].DisplacementBC(name='XRoller', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseShearSide'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=l_disp, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Transverse Side Tension setup:
mdb.Model(name='TransverseTensionSide', objectToCopy=mdb.models['TransverseShearSide'])
a = mdb.models['TransverseTensionSide'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XBack']
mdb.models['TransverseTensionSide'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZBack']
mdb.models['TransverseTensionSide'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YBottom']
mdb.models['TransverseTensionSide'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseTensionSide'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=l_disp, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['TransverseTensionSide'].boundaryConditions['XRoller']
a.regenerate()

# Transverse Side Compression setup:
mdb.Model(name='TransverseCompressionSide', objectToCopy=mdb.models['TransverseTensionSide'])
a = mdb.models['TransverseCompressionSide'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XFront']
mdb.models['TransverseCompressionSide'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=-l_disp, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Transverse Top Shear setup:
a = mdb.models['TransverseShearTop'].rootAssembly
a.regenerate()
# History output:
regionDef = mdb.models['TransverseShearTop'].rootAssembly.allInstances['RVECube-1'].sets['YTop']
mdb.models['TransverseShearTop'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)
# Boundary conditions:
region = a.instances['RVECube-1'].sets['YBottom']
mdb.models['TransverseShearTop'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YTop']
mdb.models['TransverseShearTop'].DisplacementBC(name='YRoller', createStepName='Initial', region=region, u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YTop']
mdb.models['TransverseShearTop'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=SET, u3=l_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Transverse Top Tension setup:
mdb.Model(name='TransverseTensionTop', objectToCopy=mdb.models['TransverseShearTop'])
a = mdb.models['TransverseTensionTop'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['XBack']
mdb.models['TransverseTensionTop'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['ZBack']
mdb.models['TransverseTensionTop'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YBottom']
mdb.models['TransverseTensionTop'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['RVECube-1'].sets['YTop']
mdb.models['TransverseTensionTop'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=l_disp, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['TransverseTensionTop'].boundaryConditions['YRoller']
a.regenerate()

# Transverse Top Compression setup:
mdb.Model(name='TransverseCompressionTop', objectToCopy=mdb.models['TransverseTensionTop'])
a = mdb.models['TransverseCompressionTop'].rootAssembly
a.regenerate()
# Boundary conditions:
region = a.instances['RVECube-1'].sets['YTop']
mdb.models['TransverseCompressionTop'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=-l_disp, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()
print('Constraining and Loading done!')

# Job creation:
mdb.Job(name='LongitudinalTensionAnalysis', model='LongitudinalTension', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='LongitudinalCompressionAnalysis', model='LongitudinalCompression', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='LongitudinalShearAnalysis', model='LongitudinalShear', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseSideTensionAnalysis', model='TransverseTensionSide', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseSideCompressionAnalysis', model='TransverseCompressionSide', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseSideShearAnalysis', model='TransverseShearSide', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseTopTensionAnalysis', model='TransverseTensionTop', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseTopCompressionAnalysis', model='TransverseCompressionTop', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='TransverseTopShearAnalysis', model='TransverseShearTop', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['LongitudinalTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['LongitudinalCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['LongitudinalShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseSideTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseSideCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseSideShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseTopTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseTopCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['TransverseTopShearAnalysis'].submit(consistencyChecking=OFF)
# print('Jobs submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
