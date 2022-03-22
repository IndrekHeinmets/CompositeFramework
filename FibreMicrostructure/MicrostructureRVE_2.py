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
m_E = 3.8e9
m_P = 0.35
m_G = 2.1e9
m_Ys = 55e6
m_Ps = 0.0

# Fiber props:
f_name = 'Carbon Fiber'
f_E1 = 228e9
f_E2 = 17.2e9
f_E3 = 17.2e9
f_P12 = 0.2
f_P13 = 0.2
f_P23 = 0.5
f_G12 = 27.6e9
f_G13 = 27.6e9
f_G23 = 5.73e9

# Interface Medium props:
i_name = 'Interface Medium'
i_E = 10e9
i_P = 0.35
i_G = 3.5e9
i_Ys = 70e6
i_Ps = 0.0

# Load displacement:
strain = 0.1
l_disp = RVE_size * strain

# Mesh density:
md = 8.0

# History output time interval:
hi = 20

# Fiber positions:
point_lst = [(-58, 16), (-32, 57), (-12, -49), (32, 18), (-25, 15), (59, 44), (-18, -24), (-3, 22), (-7, 45), (21, -53), (49, -25), (14, -18),
             (52, -50), (-48, -11), (25, 41), (-4, -2), (62.0, 16), (-32, -63.0), (-61.0, 44), (21, 67.0), (-68.0, -50)]
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
mdb.models['Model-1'].materials[m_name].Elastic(type=ENGINEERING_CONSTANTS, table=((m_E, m_E, m_E, m_P, m_P, m_P, m_G, m_G, m_G), ))
mdb.models['Model-1'].materials[m_name].Plastic(scaleStress=None, table=((m_Ys, m_Ps), ))
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P12, f_P13, f_P23, f_G12, f_G13, f_G23), ))
mdb.models['Model-1'].Material(name=i_name)
mdb.models['Model-1'].materials[i_name].Elastic(type=ENGINEERING_CONSTANTS, table=((i_E, i_E, i_E, i_P, i_P, i_P, i_G, i_G, i_G), ))
mdb.models['Model-1'].materials[i_name].Plastic(scaleStress=None, table=((i_Ys, i_Ps), ))

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
fibreCells = p.cells.findAt(((-1.642977, -10.516219, 0.0), ), ((-45.642977, -19.51622, 0.0), ), ((16.357022, -26.51622, 0.0), ), ((-0.642977, 13.483781, 0.0), ),
                            ((34.357023, 9.483781, 0.0), ), ((-9.642977, -57.51622, 0.0), ), ((-22.642977, 6.483781, 0.0), ), ((-15.642977, -32.51622, 0.0), ),
                            ((-4.642977, 36.48378, 0.0), ), ((51.357023, -33.51622, 0.0), ), ((27.357023, 32.48378, 0.0), ), ((19.807961, 58.925579, 0.0), ),
                            ((-29.313555, -59.321499, 0.0), ), ((23.824917, -59.73097, 0.0), ), ((58.552218, 47.194113, 0.0), ), ((-35.333333, 58.705147, 0.0), ),
                            ((-57.917926, 18.936925, 0.0), ), ((48.038308, -52.10316, 0.0), ), ((58.595133, 18.731594, 0.0), ), ((-59.045747, 47.002037, 0.0), ),
                            ((-59.833897, -48.534578, 0.0), ))
interfaceCells = p.cells.findAt(((59.039029, 26.55003, 0.0), ), ((58.798674, -42.157677, 0.0), ), ((58.552218, 54.342842, 0.0), ), ((28.97371, -59.73097, 0.0), ),
                                ((28.054065, 58.712163, 0.0), ), ((-2.533047, -12.708205, 0.0), ), ((-46.533047, -21.708205, 0.0), ), ((15.466953, -28.708205, 0.0), ),
                                ((-1.533047, 11.291795, 0.0), ), ((33.466953, 7.291795, 0.0), ), ((-1.279666, -47.562679, 0.0), ), ((-23.533047, 4.291795, 0.0), ),
                                ((-16.533047, -34.708205, 0.0), ), ((-5.533047, 34.291795, 0.0), ), ((38.065669, -25.706502, 0.0), ), ((26.466953, 30.291795, 0.0), ),
                                ((-21.896051, -59.101994, 0.0), ), ((-21.75632, 59.277072, 0.0), ), ((-59.051539, 26.312062, 0.0), ), ((-58.854153, 54.613365, 0.0), ),
                                ((-59.566964, -43.052006, 0.0), ))
matrixCells = p.cells.findAt(((59.454422, -59.390252, 0.0), ), ((1.225905, 59.557719, 40.0), ))

# Fibre orientation assignment:
v = p.vertices
p.DatumCsysByThreePoints(origin=v.findAt(coordinates=(-60.241748, -60.442281, 120.0)), point1=v.findAt(coordinates=(-60.241748, -60.442281, 0.0)), point2=v.findAt(coordinates=(-60.241748, 59.557719, 0.0)), name='Datum csys-1', coordSysType=CARTESIAN)
region = regionToolset.Region(cells=fibreCells)
orientation = mdb.models['Model-1'].parts['RVECube'].datums[3]
mdb.models['Model-1'].parts['RVECube'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)
region = regionToolset.Region(cells=matrixCells + interfaceCells)
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
faces = f.findAt(((-60.241748, -59.139952, 40.0), ), ((-60.241748, -57.035915, 40.0), ), ((-60.241748, -47.89684, 40.0), ), ((-60.241748, -42.964085, 80.0), ),
                 ((-60.241748, -10.689995, 40.0), ), ((-60.241748, 5.743211, 40.0), ), ((-60.241748, 19.248496, 40.0), ), ((-60.241748, 26.256788, 80.0), ),
                 ((-60.241748, 30.776478, 40.0), ), ((-60.241748, 33.527534, 40.0), ), ((-60.241748, 47.323737, 40.0), ), ((-60.241748, 54.472466, 80.0), ),
                 ((-60.241748, 58.196805, 40.0), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((59.758252, 54.472466, 40.0), ), ((59.758252, 47.323737, 80.0), ), ((59.758252, 33.527534, 80.0), ), ((59.758252, 30.776478, 80.0), ),
                 ((59.758252, 26.768087, 80.0), ), ((59.758252, 19.248496, 80.0), ), ((59.758252, 5.743211, 80.0), ), ((59.758252, -12.384295, 40.0), ),
                 ((59.758252, -23.645583, 80.0), ), ((59.758252, -33.212571, 80.0), ), ((59.758252, -42.964085, 40.0), ), ((59.758252, -47.89684, 80.0), ),
                 ((59.758252, -57.035915, 80.0), ), ((59.758252, -59.791116, 40.0), ), ((59.758252, 56.83589, 40.0), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((58.552218, 47.194113, 0.0), ), ((58.595133, 18.731594, 0.0), ), ((48.038308, -52.10316, 0.0), ), ((59.039029, 26.55003, 0.0), ),
                 ((-58.854153, 54.613365, 0.0), ), ((23.824917, -59.73097, 0.0), ), ((28.97371, -59.73097, 0.0), ), ((-1.279666, -47.562679, 0.0), ),
                 ((-59.051539, 26.312062, 0.0), ), ((-29.313555, -59.321499, 0.0), ), ((5.663073, 54.030103, 0.0), ), ((-59.566964, -43.052006, 0.0), ),
                 ((-59.833897, -48.534578, 0.0), ), ((-59.045747, 47.002037, 0.0), ), ((58.798674, -42.157677, 0.0), ), ((-57.917926, 18.936925, 0.0), ),
                 ((-21.75632, 59.277072, 0.0), ), ((-35.333333, 58.705147, 0.0), ), ((58.552218, 54.342842, 0.0), ), ((-21.896051, -59.101994, 0.0), ),
                 ((28.054065, 58.712163, 0.0), ), ((19.807961, 58.925579, 0.0), ), ((26.466953, 30.291795, 0.0), ), ((27.357023, 32.48378, 0.0), ),
                 ((38.065669, -25.706502, 0.0), ), ((51.357023, -33.51622, 0.0), ), ((-5.533047, 34.291795, 0.0), ), ((-4.642977, 36.48378, 0.0), ),
                 ((-16.533047, -34.708205, 0.0), ), ((-15.642977, -32.51622, 0.0), ), ((-23.533047, 4.291795, 0.0), ), ((-22.642977, 6.483781, 0.0), ),
                 ((-9.642977, -57.51622, 0.0), ), ((33.466953, 7.291795, 0.0), ), ((34.357023, 9.483781, 0.0), ), ((-1.533047, 11.291795, 0.0), ),
                 ((-0.642977, 13.483781, 0.0), ), ((15.466953, -28.708205, 0.0), ), ((16.357022, -26.51622, 0.0), ), ((-46.533047, -21.708205, 0.0), ),
                 ((-45.642977, -19.51622, 0.0), ), ((-2.533047, -12.708205, 0.0), ), ((-1.642977, -10.516219, 0.0), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((58.552218, 47.194113, 120.0), ), ((58.595133, 18.731594, 120.0), ), ((48.038308, -52.10316, 120.0), ), ((59.039029, 26.55003, 120.0), ),
                 ((-58.854153, 54.613365, 120.0), ), ((23.824917, -59.73097, 120.0), ), ((28.97371, -59.73097, 120.0), ), ((-1.279666, -47.562679, 120.0), ),
                 ((-59.051539, 26.312062, 120.0), ), ((-29.313555, -59.321499, 120.0), ), ((5.663073, 54.030103, 120.0), ), ((-59.566964, -43.052006, 120.0), ),
                 ((-59.833897, -48.534578, 120.0), ), ((-59.045747, 47.002037, 120.0), ), ((58.798674, -42.157677, 120.0), ), ((-57.917926, 18.936925, 120.0), ),
                 ((-21.75632, 59.277072, 120.0), ), ((-35.333333, 58.705147, 120.0), ), ((58.552218, 54.342842, 120.0), ), ((-21.896051, -59.101994, 120.0), ),
                 ((28.054065, 58.712163, 120.0), ), ((19.807961, 58.925579, 120.0), ), ((26.466953, 30.291795, 120.0), ), ((27.357023, 32.48378, 120.0), ),
                 ((38.065669, -25.706502, 120.0), ), ((51.357023, -33.51622, 120.0), ), ((-5.533047, 34.291795, 120.0), ), ((-4.642977, 36.48378, 120.0), ),
                 ((-16.533047, -34.708205, 120.0), ), ((-15.642977, -32.51622, 120.0), ), ((-23.533047, 4.291795, 120.0), ), ((-22.642977, 6.483781, 120.0), ),
                 ((-9.642977, -57.51622, 120.0), ), ((33.466953, 7.291795, 120.0), ), ((34.357023, 9.483781, 120.0), ), ((-1.533047, 11.291795, 120.0), ),
                 ((-0.642977, 13.483781, 120.0), ), ((15.466953, -28.708205, 120.0), ), ((16.357022, -26.51622, 120.0), ), ((-46.533047, -21.708205, 120.0), ),
                 ((-45.642977, -19.51622, 120.0), ), ((-2.533047, -12.708205, 120.0), ), ((-1.642977, -10.516219, 120.0), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((-48.888556, 59.557719, 40.0), ), ((-42.182233, 59.557719, 40.0), ), ((-28.777542, 59.557719, 40.0), ), ((-21.302902, 59.557719, 40.0), ),
                 ((1.225905, 59.557719, 40.0), ), ((13.624789, 59.557719, 40.0), ), ((23.226418, 59.557719, 40.0), ), ((29.071168, 59.557719, 40.0), ),
                 ((49.761209, 59.557719, 40.0), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((53.605849, -60.442281, 80.0), ), ((41.377343, -60.442281, 80.0), ), ((28.375211, -60.442281, 40.0), ), ((23.226418, -60.442281, 80.0), ),
                 ((13.624789, -60.442281, 80.0), ), ((-3.155213, -60.442281, 40.0), ), ((-11.616419, -60.442281, 80.0), ), ((-15.696507, -60.442281, 80.0), ),
                 ((-21.817765, -60.442281, 40.0), ), ((-28.777542, -60.442281, 80.0), ), ((-42.182233, -60.442281, 80.0), ), ((-54.565152, -60.442281, 40.0), ),
                 ((57.797782, -60.442281, 40.0), ))
p.Set(faces=faces, name='YBottom')

# Refrence point and history output:
a.ReferencePoint(point=(-60.0, -60.0, 140.0))
refPoints1 = (a.referencePoints[90], )
a.Set(referencePoints=refPoints1, name='RPSet')
v = a.instances['RVECube-1'].vertices
verts = v.findAt(((59.758252, 59.557719, 120.0), ))
a.Set(vertices=verts, name='CornerNodeSet')

regionDef = mdb.models['Model-1'].rootAssembly.sets['RPSet']
mdb.models['Model-1'].HistoryOutputRequest(name='RPHO', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, numIntervals=hi)
regionDef = mdb.models['Model-1'].rootAssembly.sets['CornerNodeSet']
mdb.models['Model-1'].HistoryOutputRequest(name='CornerNodeHO', createStepName='StaticAnalysis', variables=('U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, numIntervals=hi)


# End of script:
print('*************************')
print('End of script, no errors!')
