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
pi_len = 24.0
period = pi / (sin_x * sc)

# Overlap:
overlap_len = period * 2

# Ellipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
b_width = (pi_len * pi)
b_height = 4.0

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


def find_spline_nodes(sin_x, step, pi_len, sc):
    points = []

    for i in range(int((pi_len * pi) / step)):
        x = step * i
        y = sin(sin_x * x) / sc
        points.append((x, y))

    return points


def add_straight(x, y, overlap_len, step, points, offset):
    for i in range(int((overlap_len / step) + step)):
        x += step
        offset += step
        points.append((x, y))

    return x, offset, points


def find_spline_nodes_l(sin_x, step, pi_len, overlap_len, sc):
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
points = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)
points_l = find_spline_nodes_l((sin_x * sc), (step / sc), (pi_len / (2 * sc)), overlap_len, sc)

# Sin wave sketch short:
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Spline(points=points)
s.unsetPrimaryObject()

# Sin wave sketch long:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__sweep1__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.Spline(points=points_l)
s2.unsetPrimaryObject()

# Weave cross-section sketch short:
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.ConstructionLine(point1=(-0.5, 0.0), point2=(0.5, 0.0))
s1.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5))
s1.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / sc), 0.0))
s1.CoincidentConstraint(entity1=v1[0], entity2=g1[3], addUndoState=False)
s1.CoincidentConstraint(entity1=v1[2], entity2=g1[2], addUndoState=False)
s1.unsetPrimaryObject()

# Weave cross-section sketch long:
s3 = mdb.models['Model-1'].ConstrainedSketch(name='__profile1__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g3, v3, d3, c3 = s3.geometry, s3.vertices, s3.dimensions, s3.constraints
s3.setPrimaryObject(option=SUPERIMPOSE)
s3.ConstructionLine(point1=(-0.5, 0.0), point2=(0.5, 0.0))
s3.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5))
s3.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / sc), 0.0))
s3.CoincidentConstraint(entity1=v3[0], entity2=g3[3], addUndoState=False)
s3.CoincidentConstraint(entity1=v3[2], entity2=g3[2], addUndoState=False)
s3.unsetPrimaryObject()

# Resin block profile sketch:
s4 = mdb.models['Model-1'].ConstrainedSketch(name='__profile2__', sheetSize=1)
g4, v4, d4, c4 = s4.geometry, s4.vertices, s4.dimensions, s4.constraints
s4.setPrimaryObject(option=STANDALONE)
s4.rectangle(point1=(0.0, 0.0), point2=(b_width / sc, b_height / sc))
s4.unsetPrimaryObject()
print('Sketching done!')

# Part creation:
p = mdb.models['Model-1'].Part(name='CfWeave', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p1 = mdb.models['Model-1'].Part(name='ResinBlock', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p2 = mdb.models['Model-1'].Part(name='CfWeave_l', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['CfWeave']
p1 = mdb.models['Model-1'].parts['ResinBlock']
p2 = mdb.models['Model-1'].parts['CfWeave_l']
p.BaseSolidSweep(sketch=s1, path=s)
p1.BaseSolidExtrude(sketch=s4, depth=b_width / sc)
p2.BaseSolidSweep(sketch=s3, path=s2)
print('Part creation done!')

# Delete sketches:
del mdb.models['Model-1'].sketches['__sweep__']
del mdb.models['Model-1'].sketches['__sweep1__']
del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__profile1__']
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

# Instance creation:
a.Instance(name='CfWeave-1', part=p, dependent=ON)
a.Instance(name='CfWeave-2', part=p, dependent=ON)
a.Instance(name='CfWeave-5', part=p, dependent=ON)
a.Instance(name='CfWeave-6', part=p, dependent=ON)
a.Instance(name='CfWeave_l-1', part=p2, dependent=ON)
a.Instance(name='CfWeave_l-2', part=p2, dependent=ON)
a.Instance(name='CfWeave-3', part=p, dependent=ON)
a.Instance(name='CfWeave-4', part=p, dependent=ON)
a.Instance(name='CfWeave-7', part=p, dependent=ON)
a.Instance(name='CfWeave-8', part=p, dependent=ON)
a.Instance(name='CfWeave_l-3', part=p2, dependent=ON)
a.Instance(name='CfWeave_l-4', part=p2, dependent=ON)
a.Instance(name='ResinBlock-1', part=p1, dependent=ON)

# Weave arrangement:
a.rotate(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-5', 'CfWeave-6', 'CfWeave_l-1', 'CfWeave_l-2'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.rotate(instanceList=('CfWeave-2', 'CfWeave-5', 'CfWeave_l-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 0.0, 180.0), angle=180.0)
a.rotate(instanceList=('CfWeave-4', 'CfWeave-8', 'CfWeave_l-3'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.translate(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-5', 'CfWeave-6', 'CfWeave_l-1', 'CfWeave_l-2'), vector=((period / 2), 0.0, 0.0))
a.translate(instanceList=('CfWeave-3', 'CfWeave-4', 'CfWeave-7', 'CfWeave-8', 'CfWeave_l-3', 'CfWeave_l-4'), vector=(0.0, 0.0, (period / 2)))
a.translate(instanceList=('CfWeave-2', ), vector=(period, 0.0, 0.0))
a.translate(instanceList=('CfWeave_l-2', ), vector=((period * 2), 0.0, 0.0))
a.translate(instanceList=('CfWeave-5', ), vector=((period * 3), 0.0, 0.0))
a.translate(instanceList=('CfWeave-6', ), vector=((period * 4), 0.0, 0.0))
a.translate(instanceList=('CfWeave_l-1', ), vector=((period * 5), 0.0, 0.0))
a.translate(instanceList=('CfWeave-3', ), vector=(0.0, 0.0, period))
a.translate(instanceList=('CfWeave_l-3', ), vector=(0.0, 0.0, (period * 2)))
a.translate(instanceList=('CfWeave-7', ), vector=(0.0, 0.0, (period * 3)))
a.translate(instanceList=('CfWeave-8', ), vector=(0.0, 0.0, (period * 4)))
a.translate(instanceList=('CfWeave_l-4', ), vector=(0.0, 0.0, (period * 5)))
a.translate(instanceList=('CfWeave_l-1', 'CfWeave_l-2'), vector=(0.0, 0.0, -(period * 2)))
a.translate(instanceList=('CfWeave_l-3', 'CfWeave_l-4'), vector=(-(period * 2), 0.0, 0.0))
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-5', 'CfWeave-6', 'CfWeave_l-1', 'CfWeave_l-2'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1=(period * 6), spacing2=1)
a.LinearInstancePattern(instanceList=('CfWeave_l-4', 'CfWeave-8', 'CfWeave-7', 'CfWeave_l-3', 'CfWeave-3', 'CfWeave-4'), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1=(period * 6), spacing2=1)
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), 0.0))

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-5'], a.instances['CfWeave-6'], a.instances['CfWeave_l-1'], a.instances['CfWeave_l-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'],
                                                        a.instances['CfWeave-7'], a.instances['CfWeave-8'], a.instances['CfWeave_l-3'], a.instances['CfWeave_l-4'], a.instances['ResinBlock-1'], a.instances['CfWeave-1-lin-2-1'], a.instances['CfWeave-2-lin-2-1'], a.instances['CfWeave-6-lin-2-1'], a.instances['CfWeave_l-2-lin-2-1'],
                                                        a.instances['CfWeave-5-lin-2-1'], a.instances['CfWeave_l-1-lin-2-1'], a.instances['CfWeave_l-4-lin-2-1'], a.instances['CfWeave-8-lin-2-1'], a.instances['CfWeave-4-lin-2-1'], a.instances['CfWeave-7-lin-2-1'], a.instances['CfWeave_l-3-lin-2-1'], a.instances['CfWeave-3-lin-2-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['CfWeave']
del mdb.models['Model-1'].parts['CfWeave_l']
del mdb.models['Model-1'].parts['ResinBlock']
p = mdb.models['Model-1'].parts['Composite']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(25.132741, 2.0, 50.265483)), sketchUpEdge=e.findAt(coordinates=(75.398224, 2.0, 18.849556)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(37.699112, 2.0, 37.699112))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=0.002, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=((19.0 / sc), (19.0 / sc)), point2=(-(19.0 / sc), -(19.0 / sc)))
s.rectangle(point1=(-(70.0 / sc), -(70.0 / sc)), point2=((70.0 / sc), (70.0 / sc)))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(25.132741, 2.0, 50.265483)), sketchUpEdge=e1.findAt(coordinates=(75.398224, 2.0, 18.849556)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Cell assignment:
fibreCells1 = p.cells.findAt(((38.598564, 0.07419, 18.699112), ), ((49.366029, -0.07419, 18.699112), ), ((51.164355, -0.999926, 18.699112), ), ((36.800237, 0.999926, 18.699112), ),
                             ((24.233288, -0.07419, 18.699112), ), ((26.032194, 0.07419, 18.699112), ))
fibreCells2 = p.cells.findAt(((18.699112, -0.07419, 38.598564), ), ((18.699112, 0.999926, 51.164355), ), ((18.699112, 0.07419, 49.366029), ), ((18.699112, -0.999926, 36.800237), ),
                             ((18.699112, 0.07419, 24.233288), ), ((18.699112, -0.07419, 26.032194), ))
matrixCells = p.cells.findAt(((18.699112, -0.659536, 43.275667), ))

# Fibre orientation assignment:
v1 = p.vertices
p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(56.699112, -2.0, 56.699112)), point1=v1.findAt(coordinates=(56.699112, -2.0, 18.699112)), point2=v1.findAt(coordinates=(56.699112, 2.0, 18.699112)), name='Datum csys-1', coordSysType=CARTESIAN)
v2 = p.vertices
p.DatumCsysByThreePoints(origin=v2.findAt(coordinates=(56.699112, -2.0, 56.699112)), point1=v2.findAt(coordinates=(18.699112, -2.0, 56.699112)), point2=v2.findAt(coordinates=(18.699112, 2.0, 56.699112)), name='Datum csys-2', coordSysType=CARTESIAN)
region = regionToolset.Region(cells=fibreCells1)
orientation = mdb.models['Model-1'].parts['Composite'].datums[3]
mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)
region = regionToolset.Region(cells=fibreCells2)
orientation = mdb.models['Model-1'].parts['Composite'].datums[4]
mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# Section assignment:
region = regionToolset.Region(cells=fibreCells1 + fibreCells2)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
region = regionToolset.Region(cells=matrixCells)
p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
print('Assembly done!')

# Seeding and meshing:
p.setMeshControls(regions=fibreCells1 + fibreCells2 + matrixCells, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
p.setElementType(regions=(cells, ), elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Set Assignment:
f = p.faces
faces = f.findAt(((18.699112, 0.07419, 24.233288), ), ((18.699112, -0.07419, 26.032194), ), ((18.699112, -0.999926, 36.800237), ), ((18.699112, -0.07419, 38.598564), ),
                 ((18.699112, 0.999926, 51.164355), ), ((18.699112, 0.07419, 49.366029), ), ((18.699112, -0.659536, 43.275667), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((56.699112, -0.075227, 24.238169), ), ((56.699112, 0.075227, 26.027313), ), ((56.699112, -0.99999, 36.800237), ), ((56.699112, 0.075227, 38.593684), ),
                 ((56.699112, 0.99999, 51.164355), ), ((56.699112, -0.075227, 49.370911), ), ((56.699112, -0.774314, 31.613679), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((36.800237, 0.999926, 18.699112), ), ((24.233288, -0.07419, 18.699112), ), ((26.032194, 0.07419, 18.699112), ), ((38.598564, 0.07419, 18.699112), ),
                 ((49.366029, -0.07419, 18.699112), ), ((51.164355, -0.999926, 18.699112), ), ((44.688925, -0.659536, 18.699112), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((36.800237, 0.99999, 56.699112), ), ((24.238169, 0.075227, 56.699112), ), ((26.027313, -0.075227, 56.699112), ), ((38.593684, -0.075227, 56.699112), ),
                 ((49.370911, 0.075227, 56.699112), ), ((51.164355, -0.99999, 56.699112), ), ((55.72765, -1.551284, 56.699112), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((44.032445, 2.0, 31.365779), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((44.032445, -2.0, 44.032445), ))
p.Set(faces=faces, name='YBottom')

# History output:
regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Composite-1'].sets['XFront']
mdb.models['Model-1'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, timeInterval=0.05)

# Boundary conditions:
region = a.instances['Composite-1'].sets['XBack']
mdb.models['Model-1'].DisplacementBC(name='XBackSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['ZBack']
mdb.models['Model-1'].DisplacementBC(name='ZBackSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['YBottom']
mdb.models['Model-1'].DisplacementBC(name='YBaseSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# Front face displacement:
region = a.instances['Composite-1'].sets['XFront']
mdb.models['Model-1'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

# Load case creation:
mdb.models.changeKey(fromName='Model-1', toName='XTensCase')
mdb.Model(name='XCompCase', objectToCopy=mdb.models['XTensCase'])
mdb.Model(name='YShearCase', objectToCopy=mdb.models['XTensCase'])

# Loading model changes:
mdb.models['XTensCase'].boundaryConditions['Load'].setValues(u1=l_disp)
a = mdb.models['XTensCase'].rootAssembly
a.regenerate()
mdb.models['XCompCase'].boundaryConditions['Load'].setValues(u1=-l_disp)
a = mdb.models['XCompCase'].rootAssembly
a.regenerate()
mdb.models['YShearCase'].boundaryConditions['Load'].setValues(u2=l_disp)
mdb.models['YShearCase'].boundaryConditions['XBackSupport'].setValues(u2=SET, u3=SET)
a = mdb.models['YShearCase'].rootAssembly
region = a.instances['Composite-1'].sets['XFront']
mdb.models['YShearCase'].DisplacementBC(name='XFrontRoller', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['YShearCase'].boundaryConditions['YBaseSupport']
del mdb.models['YShearCase'].boundaryConditions['ZBackSupport']
a.regenerate()
print('Constraining and Loading done!')

# # Job creation:
mdb.Job(name='TensionAnalysis', model='XTensCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='CompressionAnalysis', model='XCompCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='ShearAnalysis', model='YShearCase', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['TensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['ShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['CompressionAnalysis'].submit(consistencyChecking=OFF)
# print('Jobs submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
