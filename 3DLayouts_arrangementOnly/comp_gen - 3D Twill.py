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
step = 0.01
pi_len = 12.0
period = pi / (sin_x * sc)
height_mult = 3

# Elipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
b_width = (pi_len * pi) * 2
b_height = 3.0 * height_mult

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


def find_spline_nodes(sin_x, step, pi_len, sc, height_mult):
    points = []
    length = 41
    offset = 0
    i = 0

    while i <= int((pi_len * pi) / step):

        x = step * i
        i += 1

        y_b = (sin(sin_x * (x - step))) / sc
        y = (sin(sin_x * x)) / sc
        y_a = (sin(sin_x * (x + step))) / sc
        x += offset

        if y_b < y < y_a or y_b > y > y_a:
            points.append((x, y * height_mult))

        else:
            for j in range(0, length):
                x += (step * j)
                offset += (step * j)
                points.append((x, y * height_mult))

    return points


# New model database creation:
Mdb()
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
print('Running script...')

# Sin spline nodes:
points = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc, height_mult)

# Sin wave sketch:
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Spline(points=points)
s.unsetPrimaryObject()

# Line sketch:
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__sweep1__', sheetSize=1)
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=STANDALONE)
s1.Line(point1=(-(b_width / sc), 0.0), point2=(0.0, 0.0))
s1.unsetPrimaryObject()

# Weave cross-section sketch:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=SUPERIMPOSE)
s2.ConstructionLine(point1=(-0.5, 0.0), point2=(0.5, 0.0))
s2.ConstructionLine(point1=(0.0, -0.5), point2=(0.0, 0.5))
s2.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / sc), 0.0))
s2.CoincidentConstraint(entity1=v2[0], entity2=g2[3], addUndoState=False)
s2.CoincidentConstraint(entity1=v2[2], entity2=g2[2], addUndoState=False)
s2.unsetPrimaryObject()

# Straight cross-section sketch:
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
p2 = mdb.models['Model-1'].Part(name='CfWeave_s', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['CfWeave']
p1 = mdb.models['Model-1'].parts['ResinBlock']
p2 = mdb.models['Model-1'].parts['CfWeave_s']
p.BaseSolidSweep(sketch=s2, path=s)
p1.BaseSolidExtrude(sketch=s4, depth=b_width / sc)
p2.BaseSolidSweep(sketch=s3, path=s1)
print('Part creation done!')

# Delete sketches:
del mdb.models['Model-1'].sketches['__sweep__']
del mdb.models['Model-1'].sketches['__sweep1__']
del mdb.models['Model-1'].sketches['__profile__']
del mdb.models['Model-1'].sketches['__profile1__']
del mdb.models['Model-1'].sketches['__profile2__']

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
a.Instance(name='CfWeave_s-1', part=p2, dependent=ON)
a.Instance(name='ResinBlock-1', part=p1, dependent=ON)

# Weave arrangement:
a.rotate(instanceList=('CfWeave_s-1', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 90.0, 0.0), angle=90.0)
a.translate(instanceList=('CfWeave_s-1', ), vector=(4.55, 0.0, 0.0))
a.LinearInstancePattern(instanceList=('CfWeave_s-1', ), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1=period - 1, spacing2=1)
a.LinearInstancePattern(instanceList=('CfWeave_s-1', 'CfWeave_s-1-lin-2-1'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=1, number2=2, spacing1=10.7832, spacing2=1.4)
a.LinearInstancePattern(instanceList=('CfWeave_s-1', 'CfWeave_s-1-lin-2-1'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, -1.0, 0.0), number1=1, number2=2, spacing1=10.7832, spacing2=1.4)
a.LinearInstancePattern(instanceList=('CfWeave_s-1', 'CfWeave_s-1-lin-2-1', 'CfWeave_s-1-lin-1-2', 'CfWeave_s-1-lin-2-1-lin-1-2',
                                      'CfWeave_s-1-lin-1-2-1', 'CfWeave_s-1-lin-2-1-lin-1-2-1'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=5, number2=1, spacing1=14.52, spacing2=4.0)
a.InstanceFromBooleanMerge(name='Straigth_fibers', instances=(a.instances['CfWeave_s-1'], a.instances['CfWeave_s-1-lin-2-1'], a.instances['CfWeave_s-1-lin-1-2'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2'], a.instances['CfWeave_s-1-lin-1-2-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-1'], a.instances['CfWeave_s-1-lin-2-1-1'],
                                                              a.instances['CfWeave_s-1-lin-3-1'], a.instances['CfWeave_s-1-lin-4-1'], a.instances['CfWeave_s-1-lin-5-1'], a.instances['CfWeave_s-1-lin-2-1-lin-2-1'], a.instances['CfWeave_s-1-lin-2-1-lin-3-1'],
                                                              a.instances['CfWeave_s-1-lin-2-1-lin-4-1'], a.instances['CfWeave_s-1-lin-2-1-lin-5-1'], a.instances['CfWeave_s-1-lin-1-2-lin-2-1'], a.instances['CfWeave_s-1-lin-1-2-lin-3-1'], a.instances['CfWeave_s-1-lin-1-2-lin-4-1'],
                                                              a.instances['CfWeave_s-1-lin-1-2-lin-5-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-lin-2-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-lin-3-1'],
                                                              a.instances['CfWeave_s-1-lin-2-1-lin-1-2-lin-4-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-lin-5-1'], a.instances['CfWeave_s-1-lin-1-2-1-lin-2-1'],
                                                              a.instances['CfWeave_s-1-lin-1-2-1-lin-3-1'], a.instances['CfWeave_s-1-lin-1-2-1-lin-4-1'], a.instances['CfWeave_s-1-lin-1-2-1-lin-5-1'],
                                                              a.instances['CfWeave_s-1-lin-2-1-lin-1-2-1-lin-2-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-1-lin-3-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-1-lin-4-1'], a.instances['CfWeave_s-1-lin-2-1-lin-1-2-1-lin-5-1'], ), originalInstances=DELETE, domain=GEOMETRY)
a.rotate(instanceList=('CfWeave-2', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.translate(instanceList=('CfWeave-1', ), vector=(0.0, 0.0, 6.28))
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2'), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=6, number2=1, spacing1=12.56, spacing2=1)

a.InstanceFromBooleanMerge(name='Fibers', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['Straigth_fibers-1'], a.instances['CfWeave-1-lin-2-1'], a.instances['CfWeave-1-lin-3-1'], a.instances['CfWeave-1-lin-4-1'], a.instances['CfWeave-1-lin-5-1'],
                                                     a.instances['CfWeave-1-lin-6-1'], a.instances['CfWeave-2-lin-2-1'], a.instances['CfWeave-2-lin-3-1'], a.instances['CfWeave-2-lin-4-1'], a.instances['CfWeave-2-lin-5-1'], a.instances['CfWeave-2-lin-6-1'], ), originalInstances=DELETE, domain=GEOMETRY)

# Delete original weaves:
del mdb.models['Model-1'].parts['CfWeave']
del mdb.models['Model-1'].parts['CfWeave_s']
del mdb.models['Model-1'].parts['Straigth_fibers']
p = mdb.models['Model-1'].parts['Fibers']

# Resin matrix creation:
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), 0.0))
a.Instance(name='Fibers-2', part=p, dependent=ON)
a.InstanceFromBooleanCut(name='ResinMatrix', instanceToBeCut=mdb.models['Model-1'].rootAssembly.instances['ResinBlock-1'], cuttingInstances=(a.instances['Fibers-2'], ), originalInstances=DELETE)

# Delete original resin block:
del mdb.models['Model-1'].parts['ResinBlock']
p1 = mdb.models['Model-1'].parts['ResinMatrix']

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['Fibers-1'], a.instances['ResinMatrix-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['Fibers']
del mdb.models['Model-1'].parts['ResinMatrix']
p = mdb.models['Model-1'].parts['Composite']

# Job creation:
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
# print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')