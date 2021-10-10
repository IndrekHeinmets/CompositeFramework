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


def find_sin_nodes(sin_x, step, pi_len, sc):
    points = []

    for i in range(0, int((pi_len * pi) / step)):
        x = step * i
        y = (sin(sin_x * x)) / sc
        points.append((x, y))

    points = tuple(points)

    return points


# New model database creation:
Mdb()
print('Running script...')

# Scale (m -> mm):
sc = 1000

# Sin curve:
sin_x = 0.5
step = 0.01
pi_len = 12.0
period = pi / (sin_x * sc)

# Elipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
b_width = (pi_len * pi)
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

# Sin spline nodes:
points = find_sin_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)

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
a.Instance(name='ResinBlock-1', part=p1, dependent=ON)

# Weave arrangement:
a.rotate(instanceList=('CfWeave-1', 'CfWeave-2'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.rotate(instanceList=('CfWeave-2', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 0.0, 180.0), angle=180.0)
a.rotate(instanceList=('CfWeave-4', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.translate(instanceList=('CfWeave-2', ), vector=(period, 0.0, 0.0))
a.translate(instanceList=('CfWeave-3', ), vector=(0.0, 0.0, period))
a.translate(instanceList=('CfWeave-1', 'CfWeave-2'), vector=((period / 2), 0.0, 0.0))
a.translate(instanceList=('CfWeave-3', 'CfWeave-4'), vector=(0.0, 0.0, (period / 2)))
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=int(pi_len / 4), number2=1, spacing1=(period * 2), spacing2=1)
a.rotate(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-3', 'CfWeave-4', 'CfWeave-1-lin-2-1', 'CfWeave-1-lin-3-1', 'CfWeave-2-lin-2-1', 'CfWeave-2-lin-3-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 90.0, 0.0), angle=90.0)
a.LinearInstancePattern(instanceList=('CfWeave-4', 'CfWeave-3'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=int(pi_len / 4), number2=1, spacing1=(period * 2), spacing2=1)
a.rotate(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-3', 'CfWeave-4', 'CfWeave-1-lin-2-1', 'CfWeave-1-lin-3-1', 'CfWeave-2-lin-2-1', 'CfWeave-2-lin-3-1',
                       'CfWeave-4-lin-2-1', 'CfWeave-4-lin-3-1', 'CfWeave-3-lin-2-1', 'CfWeave-3-lin-3-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.InstanceFromBooleanMerge(name='Fibers', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'], a.instances['CfWeave-1-lin-2-1'], a.instances['CfWeave-1-lin-3-1'],
                                                     a.instances['CfWeave-2-lin-2-1'], a.instances['CfWeave-2-lin-3-1'], a.instances['CfWeave-4-lin-2-1'], a.instances['CfWeave-4-lin-3-1'], a.instances['CfWeave-3-lin-2-1'], a.instances['CfWeave-3-lin-3-1'], ), originalInstances=DELETE, domain=GEOMETRY)

# Delete original weaves:
del mdb.models['Model-1'].parts['CfWeave']
p = mdb.models['Model-1'].parts['Fibers']

# Resin matrix creation:
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), 0.0))
a.Instance(name='Fibers-2', part=p, dependent=ON)
a.InstanceFromBooleanCut(name='ResinMatrix', instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['ResinBlock-1'], cuttingInstances=(a.instances['Fibers-2'], ), originalInstances=DELETE)

# Delete original resin block:
del mdb.models['Model-1'].parts['ResinBlock']
p1 = mdb.models['Model-1'].parts['ResinMatrix']

# Section assignment:
c = p.cells
cells = c.getSequenceFromMask(mask=('[#fff ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
c1 = p1.cells
cells = c1.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p1.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['Fibers-1'], a.instances['ResinMatrix-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['Fibers']
del mdb.models['Model-1'].parts['ResinMatrix']
p = mdb.models['Model-1'].parts['Composite']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f[4], sketchUpEdge=e[18], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=((b_width / (2 * sc)), (b_height / (2 * sc)), (b_width / (2 * sc))))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=0.106, gridSpacing=0.002, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p = mdb.models['Model-1'].parts['Composite']
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=(-0.022, 0.022), point2=(0.022, -0.022))
s.rectangle(point1=(-0.016, 0.016), point2=(0.016, -0.016))
p = mdb.models['Model-1'].parts['Composite']
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1[4], sketchUpEdge=e1[18], sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']
print('Assembly done!')

# Seeding and meshing:
# p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
# c = p.cells
# pickedRegions = c.getSequenceFromMask(mask=('[#1fff ]', ), )
# p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
# elemType1 = mesh.ElemType(elemCode=C3D20R)
# elemType2 = mesh.ElemType(elemCode=C3D15)
# elemType3 = mesh.ElemType(elemCode=C3D10)
# cells = c.getSequenceFromMask(mask=('[#1fff ]', ), )
# pickedRegions = (cells, )
# p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
# p = mdb.models['Model-1'].parts['Composite']
# p.generateMesh()
# a.regenerate()
# print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Boundary conditions:
# Loads:

# Job creation:
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
# print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
