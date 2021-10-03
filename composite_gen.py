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
    points1 = []
    points2 = []

    for i in range(0, int((pi_len * pi) / step)):
        x = step * i
        y1 = (sin(sin_x * x)) / sc
        y2 = (sin((sin_x * x) + pi)) / sc
        points1.append((x, y1))
        points2.append((x, y2))

    points1 = tuple(points1)
    points2 = tuple(points2)

    return points1, points2


print('Running script... so gimme a sec, aight?')

# Scale (m -> mm):
sc = 1000

# Sin curve:
sin_x = 0.5
step = 0.01
pi_len = 24.0
period = pi / (sin_x * sc)

# Elipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
overhang = 0.5
b_width = (pi_len * pi) - (2 * overhang)
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
md = 1

# Pressure magnitude:
p_mag = 500

# Sin spline nodes:
points1, points2 = find_sin_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)

# Sin wave 1:
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep1__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Spline(points=(points1))
s.unsetPrimaryObject()

# Weave profile 1:
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile1__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.ConstructionLine(point1=(-0.5, 0.0), point2=(0.5, 0.0))
s1.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5))
s1.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / sc), 0.0))
s1.CoincidentConstraint(entity1=v1[0], entity2=g1[3], addUndoState=False)
s1.CoincidentConstraint(entity1=v1[2], entity2=g1[2], addUndoState=False)
s1.unsetPrimaryObject()

# Sin wave 2:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__sweep2__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.Spline(points=(points2))
s2.unsetPrimaryObject()

# Weave profile 2:
s3 = mdb.models['Model-1'].ConstrainedSketch(name='__profile2__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g3, v3, d3, c3 = s3.geometry, s3.vertices, s3.dimensions, s3.constraints
s3.setPrimaryObject(option=SUPERIMPOSE)
s3.ConstructionLine(point1=(-0.5, 0.0), point2=(0.5, 0.0))
s3.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5))
s3.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / sc), 0.0))
s3.CoincidentConstraint(entity1=v1[0], entity2=g1[3], addUndoState=False)
s3.CoincidentConstraint(entity1=v1[2], entity2=g1[2], addUndoState=False)
s3.unsetPrimaryObject()

# Resin block profile:
s4 = mdb.models['Model-1'].ConstrainedSketch(name='__profile3__', sheetSize=1)
g4, v4, d4, c4 = s4.geometry, s4.vertices, s4.dimensions, s4.constraints
s4.setPrimaryObject(option=STANDALONE)
s4.rectangle(point1=(0.0, 0.0), point2=(b_width / sc, b_height / sc))
s4.unsetPrimaryObject()
print('Sketching done!')

# # Part creation:
p = mdb.models['Model-1'].Part(name='CfWeave1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p1 = mdb.models['Model-1'].Part(name='CfWeave2', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p2 = mdb.models['Model-1'].Part(name='ResinBlock', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['CfWeave1']
p1 = mdb.models['Model-1'].parts['CfWeave2']
p2 = mdb.models['Model-1'].parts['ResinBlock']
p.BaseSolidSweep(sketch=s1, path=s)
p1.BaseSolidSweep(sketch=s3, path=s2)
p2.BaseSolidExtrude(sketch=s4, depth=b_width / sc)
print('Part creation done!')

# # Delete sketches:
del mdb.models['Model-1'].sketches['__sweep2__']
del mdb.models['Model-1'].sketches['__sweep1__']
del mdb.models['Model-1'].sketches['__profile3__']
del mdb.models['Model-1'].sketches['__profile2__']
del mdb.models['Model-1'].sketches['__profile1__']

# # Material creation:
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].Material(name=m_name)
mdb.models['Model-1'].materials[f_name].Elastic(table=((f_YsM, f_PsR), ))
mdb.models['Model-1'].materials[m_name].Elastic(table=((m_YsM, m_PsR), ))

# # Section creation:
mdb.models['Model-1'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)
mdb.models['Model-1'].HomogeneousSolidSection(name='Epo_sec', material=m_name, thickness=None)

# # Assembly creation:
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)

# # Instance creation:
a.Instance(name='CfWeave1-1', part=p, dependent=ON)
a.Instance(name='CfWeave1-2', part=p, dependent=ON)
a.Instance(name='CfWeave2-1', part=p1, dependent=ON)
a.Instance(name='CfWeave2-2', part=p1, dependent=ON)
a.Instance(name='ResinBlock-1', part=p2, dependent=ON)

# # Weave arrangement:
a.rotate(instanceList=('CfWeave1-1', 'CfWeave2-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.translate(instanceList=('CfWeave1-1', 'CfWeave2-1'), vector=((e_width / (2 * sc)), 0.0, 0.0))
a.translate(instanceList=('CfWeave2-1', ), vector=((period), 0.0, 0.0))
a.translate(instanceList=('CfWeave2-2', ), vector=(0.0, 0.0, (period / 2)))
a.translate(instanceList=('CfWeave1-1', 'CfWeave2-1', 'CfWeave1-1-lin-2-1', 'CfWeave1-1-lin-3-1', 'CfWeave1-1-lin-4-1', 'CfWeave1-1-lin-5-1', 'CfWeave2-1-lin-2-1', 'CfWeave2-1-lin-3-1', 'CfWeave2-1-lin-4-1', 'CfWeave2-1-lin-5-1'), vector=(((period / 2) - (e_width / (2 * sc))), 0.0, 0.0))
a.translate(instanceList=('CfWeave1-2', ), vector=(0.0, 0.0, (1.5 * period)))
a.LinearInstancePattern(instanceList=('CfWeave1-1', 'CfWeave2-1'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=int(pi_len / 4), number2=1, spacing1=(period * 2), spacing2=2.60488)
a.rotate(instanceList=('CfWeave1-1', 'CfWeave2-1', 'CfWeave1-1-lin-2-1', 'CfWeave1-1-lin-3-1', 'CfWeave1-1-lin-4-1', 'CfWeave1-1-lin-5-1', 'CfWeave2-1-lin-2-1', 'CfWeave2-1-lin-3-1', 'CfWeave2-1-lin-4-1', 'CfWeave2-1-lin-5-1', 'CfWeave2-2', 'CfWeave1-2'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.LinearInstancePattern(instanceList=('CfWeave2-2', 'CfWeave1-2'), direction1=(-1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=int(pi_len / 4), number2=1, spacing1=(period * 2), spacing2=2.60488)
a.rotate(instanceList=('CfWeave1-1', 'CfWeave2-1', 'CfWeave1-1-lin-2-1', 'CfWeave1-1-lin-3-1', 'CfWeave1-1-lin-4-1', 'CfWeave1-1-lin-5-1', 'CfWeave2-1-lin-2-1', 'CfWeave2-1-lin-3-1', 'CfWeave2-1-lin-4-1', 'CfWeave2-1-lin-5-1', 'CfWeave2-2', 'CfWeave1-2', 'CfWeave2-2-lin-2-1',
                       'CfWeave2-2-lin-3-1', 'CfWeave2-2-lin-4-1', 'CfWeave2-2-lin-5-1', 'CfWeave2-2-lin-6-1', 'CfWeave1-2-lin-2-1', 'CfWeave1-2-lin-3-1', 'CfWeave1-2-lin-4-1', 'CfWeave1-2-lin-5-1', 'CfWeave1-2-lin-6-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 90.0, 0.0), angle=90.0)
a.InstanceFromBooleanMerge(name='Fibers', instances=(a.instances['CfWeave1-1'], a.instances['CfWeave1-2'], a.instances['CfWeave2-1'], a.instances['CfWeave2-2'], a.instances['CfWeave1-1-lin-2-1'], a.instances['CfWeave1-1-lin-3-1'], a.instances['CfWeave1-1-lin-4-1'],
                                                     a.instances['CfWeave1-1-lin-5-1'], a.instances['CfWeave1-1-lin-6-1'], a.instances['CfWeave2-1-lin-2-1'], a.instances['CfWeave2-1-lin-3-1'], a.instances['CfWeave2-1-lin-4-1'], a.instances['CfWeave2-1-lin-5-1'],
                                                     a.instances['CfWeave2-1-lin-6-1'], a.instances['CfWeave2-2-lin-2-1'], a.instances['CfWeave2-2-lin-3-1'], a.instances['CfWeave2-2-lin-4-1'], a.instances['CfWeave2-2-lin-5-1'], a.instances['CfWeave2-2-lin-6-1'],
                                                     a.instances['CfWeave1-2-lin-2-1'], a.instances['CfWeave1-2-lin-3-1'], a.instances['CfWeave1-2-lin-4-1'], a.instances['CfWeave1-2-lin-5-1'], a.instances['CfWeave1-2-lin-6-1'], ), originalInstances=DELETE, domain=GEOMETRY)

# # Delete original weaves:
del mdb.models['Model-1'].parts['CfWeave1']
del mdb.models['Model-1'].parts['CfWeave2']
p = mdb.models['Model-1'].parts['Fibers']

# # Resin matrix creation:
a.translate(instanceList=('ResinBlock-1', ), vector=((overhang / sc), -(b_height / (2 * sc)), (overhang / sc)))
a.Instance(name='Fibers-2', part=p, dependent=ON)
a.InstanceFromBooleanCut(name='ResinMatrix', instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['ResinBlock-1'], cuttingInstances=(a.instances['Fibers-2'], ), originalInstances=DELETE)

# # Delete original resin block:
del mdb.models['Model-1'].parts['ResinBlock']
p1 = mdb.models['Model-1'].parts['ResinMatrix']
print('Assembly done!')

# # Section assignment:
c = p.cells
cells = c.getSequenceFromMask(mask=('[#ffffff ]', ), )
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
c1 = p1.cells
cells = c1.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(cells=cells)
p1.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# # Seeding and meshing:
p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p1.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
c = p1.cells
pickedRegions = c.getSequenceFromMask(mask=('[#1 ]', ), )
p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
c = p1.cells
cells = c.getSequenceFromMask(mask=('[#1 ]', ), )
pickedRegions = (cells, )
p1.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
p1.generateMesh()
a.regenerate()
print('Meshing done!')

# # Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# # Boundary conditions (x-y supports):
e1 = a.instances['ResinMatrix-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#0:2 #40000 ]', ), )
region = regionToolset.Region(edges=edges1)
mdb.models['Model-1'].DisplacementBC(name='BC-1', createStepName='StaticAnalysis', region=region, u1=0.0, u2=0.0,
                                     u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

e1 = a.instances['ResinMatrix-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#0:2 #20000 ]', ), )
region = regionToolset.Region(edges=edges1)
mdb.models['Model-1'].DisplacementBC(name='BC-2', createStepName='StaticAnalysis', region=region, u1=0.0, u2=0.0,
                                     u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)

# # Load (uniform pressure):
s1 = a.instances['ResinMatrix-1'].faces
side1Faces1 = s1.getSequenceFromMask(mask=('[#10000000 ]', ), )
region = regionToolset.Region(side1Faces=side1Faces1)
mdb.models['Model-1'].Pressure(name='PressureLoad', createStepName='StaticAnalysis', region=region, distributionType=UNIFORM, field='', magnitude=p_mag, amplitude=UNSET)

# # Job creation:
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# # mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
# # print('Job submitted for processing!')

# End:
print('*************************')
print('End of script, no errors!')
