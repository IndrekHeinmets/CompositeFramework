from abaqus import *
from abaqusConstants import *
from math import pi
from math import sin
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

############################# VARIABLES ###################################
# Scale (m -> mm):
sc = 1

# Sin curve:
sin_x = 0.5
step = 0.1
pi_len = 12.0
period = pi / (sin_x * sc)

# Overlap:
overlap_len = period

# Ellipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
b_width = (pi_len * pi) * 2
b_height = 4.0

# Fiber prop:
f_name = 'Carbon Fiber'
f_YsM = 228000000000.0
f_PsR = 0.28

# Matrix prop:
m_name = 'Epoxy Resin'
m_YsM = 38000000000.0
m_PsR = 0.35

# Mesh density:
md = 0.5
###########################################################################


def add_straight(x, y, overlap_len, step, points, offset):
    for i in range(int((overlap_len / step) + step)):
        x += step
        offset += step
        points.append((x, y))

    return x, offset, points


def find_spline_nodes(sin_x, step, pi_len, overlap_len, sc):
    points = []
    offset = 0

    for i in range(int((pi_len * pi) / step)):
        x = step * i
        y_b = sin(sin_x * (x - step)) / sc
        y = sin(sin_x * x) / sc
        y_a = sin(sin_x * (x + step)) / sc
        x += offset

        if y_b < y < y_a or y_b > y > y_a:
            points.append((x, y))

        else:
            x, offset, points = add_straight(x, y, overlap_len, step, points, offset)

    return points


# New model database creation:
Mdb()
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
print('Running script...')

# Sin spline nodes:
points = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), overlap_len, sc)

# Sin wave sketch:
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Spline(points=points)
s.unsetPrimaryObject()

# Weave cross-section sketch:
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.ConstructionLine(point1=(-0.5, 0.0), point2=(0.5, 0.0))
s1.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5))
s1.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / sc), 0.0))
s1.CoincidentConstraint(entity1=v1[0], entity2=g1[3], addUndoState=False)
s1.CoincidentConstraint(entity1=v1[2], entity2=g1[2], addUndoState=False)
s1.unsetPrimaryObject()

# Resin block profile sketch:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__profile1__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.rectangle(point1=(0.0, 0.0), point2=(b_width / sc, b_height / sc))
s2.unsetPrimaryObject()
print('Sketching done!')

# Part creation:
p = mdb.models['Model-1'].Part(name='CfWeave', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p1 = mdb.models['Model-1'].Part(name='ResinBlock', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['CfWeave']
p1 = mdb.models['Model-1'].parts['ResinBlock']
p.BaseSolidSweep(sketch=s1, path=s)
p1.BaseSolidExtrude(sketch=s2, depth=b_width / sc)
print('Part creation done!')

# Delete sketches:
del mdb.models['Model-1'].sketches['__sweep__']
del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__profile1__']

# Material creation:
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].Material(name=m_name)
mdb.models['Model-1'].materials[f_name].Elastic(table=((f_YsM, f_PsR), ))
mdb.models['Model-1'].materials[m_name].Elastic(table=((m_YsM, m_PsR), ))

# Section creation:
mdb.models['Model-1'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Epo_sec', material=m_name, thickness=None)

# Assembly creation:
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)

# Instance creation:
a.Instance(name='CfWeave-1', part=p, dependent=ON)
a.Instance(name='CfWeave-2', part=p, dependent=ON)
a.Instance(name='CfWeave-3', part=p, dependent=ON)
a.Instance(name='CfWeave-4', part=p, dependent=ON)
a.Instance(name='CfWeave-5', part=p, dependent=ON)
a.Instance(name='CfWeave-6', part=p, dependent=ON)
a.Instance(name='CfWeave-7', part=p, dependent=ON)
a.Instance(name='CfWeave-8', part=p, dependent=ON)
a.Instance(name='ResinBlock-1', part=p1, dependent=ON)

# Weave arrangement:
a.rotate(instanceList=('CfWeave-3', 'CfWeave-4'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.rotate(instanceList=('CfWeave-5', 'CfWeave-6'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.translate(instanceList=('CfWeave-2', ), vector=(0.0, 0.0, period))
a.translate(instanceList=('CfWeave-3', 'CfWeave-4'), vector=(0.0, 0.0, (period * 2)))
a.translate(instanceList=('CfWeave-4', ), vector=(0.0, 0.0, period))
a.rotate(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-3', 'CfWeave-4'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 90.0, 0.0), angle=90.0)
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-3', 'CfWeave-4'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=3, number2=1, spacing1=(period * 4), spacing2=1)
a.translate(instanceList=('CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8'), vector=((-period / 2), 0.0, (-period / 2)))
a.translate(instanceList=('CfWeave-6', ), vector=(0.0, 0.0, -(period)))
a.translate(instanceList=('CfWeave-7', 'CfWeave-8'), vector=(0.0, 0.0, -(period * 2)))
a.translate(instanceList=('CfWeave-8', ), vector=(0.0, 0.0, -(period)))
a.rotate(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-3', 'CfWeave-4', 'CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8', 'CfWeave-1-lin-2-1', 'CfWeave-1-lin-3-1', 'CfWeave-2-lin-2-1',
                       'CfWeave-2-lin-3-1', 'CfWeave-4-lin-2-1', 'CfWeave-4-lin-3-1', 'CfWeave-3-lin-2-1', 'CfWeave-3-lin-3-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.LinearInstancePattern(instanceList=('CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=3, number2=1, spacing1=(period * 4), spacing2=1)
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), -(period / 1.8)))

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'], a.instances['CfWeave-5'], a.instances['CfWeave-6'], a.instances['CfWeave-7'], a.instances['CfWeave-8'],
                                                        a.instances['ResinBlock-1'], a.instances['CfWeave-1-lin-2-1'], a.instances['CfWeave-1-lin-3-1'], a.instances['CfWeave-2-lin-2-1'], a.instances['CfWeave-2-lin-3-1'], a.instances['CfWeave-4-lin-2-1'], a.instances['CfWeave-4-lin-3-1'], a.instances['CfWeave-3-lin-2-1'],
                                                        a.instances['CfWeave-3-lin-3-1'], a.instances['CfWeave-5-lin-2-1'], a.instances['CfWeave-5-lin-3-1'], a.instances['CfWeave-6-lin-2-1'], a.instances['CfWeave-6-lin-3-1'], a.instances['CfWeave-8-lin-2-1'], a.instances['CfWeave-8-lin-3-1'], a.instances['CfWeave-7-lin-2-1'],
                                                        a.instances['CfWeave-7-lin-3-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['CfWeave']
del mdb.models['Model-1'].parts['ResinBlock']
p = mdb.models['Model-1'].parts['Composite']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(25.132741, 2.0, 46.774822)), sketchUpEdge=e.findAt(coordinates=(75.398224, 2.0, 15.358897)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(37.699112, 2.0, 34.208453))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=0.002, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=((25.0 / sc), (13.0 / sc)), point2=(-(13.0 / sc), -(25.0 / sc)))
s.rectangle(point1=(-(60.0 / sc), -(60.0 / sc)), point2=((60.0 / sc), (60.0 / sc)))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(25.132741, 2.0, 46.774822)), sketchUpEdge=e1.findAt(coordinates=(75.398224, 2.0, 15.358897)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Fibre orientation assignment:
v1 = p.vertices
p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(62.699112, -2.0, 59.208453)), point1=v1.findAt(coordinates=(62.699112, -2.0, 21.208453)), point2=v1.findAt(coordinates=(62.699112, 2.0, 21.208453)), name='Datum csys-1', coordSysType=CARTESIAN)
v2 = p.vertices
p.DatumCsysByThreePoints(origin=v2.findAt(coordinates=(62.699112, -2.0, 59.208453)), point1=v2.findAt(coordinates=(24.699112, -2.0, 59.208453)), point2=v2.findAt(coordinates=(24.699112, 2.0, 59.208453)), name='Datum csys-2', coordSysType=CARTESIAN)
c = p.cells
cells = c.findAt(((38.593716, -0.303228, 21.208453), ), ((44.8769, -0.303228, 21.208453), ), ((61.93725, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ),
                 ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ))
region = regionToolset.Region(cells=cells)
orientation = mdb.models['Model-1'].parts['Composite'].datums[3]
mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)
c = p.cells
cells = c.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ),
                 ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 58.795686), ))
region = regionToolset.Region(cells=cells)
orientation = mdb.models['Model-1'].parts['Composite'].datums[4]
mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# Section assignment:
c = p.cells
cells = c.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ),
                 ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 58.795686), ), ((38.593716, -0.303228, 21.208453), ), ((44.8769, -0.303228, 21.208453), ),
                 ((61.93725, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ), ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ))
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
c = p.cells
cells = c.findAt(((49.948112, -0.147777, 59.208453), ))
region = regionToolset.Region(cells=cells)
p = mdb.models['Model-1'].parts['Composite']
p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
print('Assembly done!')

# Seeding and meshing:
c = p.cells
pickedRegions = c.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ),
                         ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 58.795686), ), ((38.593716, -0.303228, 21.208453), ), ((44.8769, -0.303228, 21.208453), ),
                         ((61.93725, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ), ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ),
                         ((49.948112, -0.147777, 59.208453), ))
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
pickedRegions = (cells, )
p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Set Assignment:s
f = p.faces
faces = f.findAt(((24.699112, -0.133154, 27.37976), ), ((24.699112, -0.133154, 52.512502), ), ((24.699112, -0.133154, 33.662946), ), ((24.699112, -0.133154, 58.795686), ),
                 ((24.699112, 0.133154, 41.735278), ), ((24.699112, 0.133154, 35.452094), ), ((24.699112, -1.083472, 50.98902), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((62.699112, -0.140695, 27.377146), ), ((62.699112, -0.140695, 52.509888), ), ((62.699112, -0.140695, 33.660332), ), ((62.699112, -0.140695, 58.793072), ),
                 ((62.699112, 0.140695, 41.737892), ), ((62.699112, 0.140695, 35.454708), ), ((62.699112, -1.189111, 25.817607), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((61.93725, 0.303228, 21.208453), ), ((55.654064, 0.303228, 21.208453), ), ((30.521324, 0.303228, 21.208453), ), ((36.804508, 0.303228, 21.208453), ),
                 ((44.8769, -0.303228, 21.208453), ), ((38.593716, -0.303228, 21.208453), ), ((32.773502, -1.066097, 21.208453), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((61.932788, -0.032528, 59.208453), ), ((55.649602, -0.032528, 59.208453), ), ((30.516861, -0.032528, 59.208453), ), ((36.800046, -0.032528, 59.208453), ),
                 ((44.881362, 0.032528, 59.208453), ), ((38.598178, 0.032528, 59.208453), ), ((49.948112, -0.147777, 59.208453), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((50.032445, 2.0, 33.87512), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((50.032445, -2.0, 46.541787), ))
p.Set(faces=faces, name='YBottom')

# Refrence point:
v1, e1, d1, n = p.vertices, p.edges, p.datums, p.nodes
a.ReferencePoint(point=(70.0, -2.0, 68.0))
r1 = a.referencePoints
refPoints1 = (r1[54], )
a.Set(referencePoints=refPoints1, name='RP')

# History output:
regionDef = mdb.models['Model-1'].rootAssembly.sets['RP']
mdb.models['Model-1'].HistoryOutputRequest(name='RPHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
mdb.models['Model-1'].Equation(name='ConstraintEqn', terms=((1.0, 'Composite-1.XFront', 1), (-1.0, 'RP', 1)))

# Boundary conditions:
region = a.instances['Composite-1'].sets['XBack']
mdb.models['Model-1'].DisplacementBC(name='XBackSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['ZBack']
mdb.models['Model-1'].DisplacementBC(name='ZBackSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['YBottom']
mdb.models['Model-1'].DisplacementBC(name='YBaseSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# Refrence point displacement:
region = a.sets['RP']
mdb.models['Model-1'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

# Load case creation:
mdb.models.changeKey(fromName='Model-1', toName='XTensCase')
mdb.Model(name='XCompCase', objectToCopy=mdb.models['XTensCase'])
mdb.Model(name='YShearCase', objectToCopy=mdb.models['XTensCase'])

# Loading magnitudes:
mdb.models['XTensCase'].boundaryConditions['Load'].setValues(u1=15.0)
a = mdb.models['XTensCase'].rootAssembly
a.regenerate()
mdb.models['XCompCase'].boundaryConditions['Load'].setValues(u1=-15.0)
a = mdb.models['XCompCase'].rootAssembly
a.regenerate()
mdb.models['YShearCase'].boundaryConditions['Load'].setValues(u1=UNSET, u2=15.0)
a = mdb.models['YShearCase'].rootAssembly
a.regenerate()
print('Constraining and Loading done!')

# Job creation:
mdb.Job(name='TensionAnalysis', model='XTensCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='CompressionAnalysis', model='XCompCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='ShearAnalysis', model='YShearCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['TensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['ShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['CompressionAnalysis'].submit(consistencyChecking=OFF)
# print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
