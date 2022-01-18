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
step = 0.5
pi_len = 6.0
period = pi / (sin_x * sc)

# Fibre cs:
fibre_diameter = 0.1
fibre_spacing = 0.12
fibre_cols = 36

# Ellipse cs:
e_width = 4.5
e_height = 0.6

# Fiber prop:
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

# # Load displacement:
# l_disp = 15.0

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


# New model database creation:
Mdb()
session.journalOptions.setValues(replayGeometry=COORDINATE, recoverGeometry=COORDINATE)
print('Running script...')

# Sin spline nodes:
points = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)

# Sin wave sketch short:
s = mdb.models['Model-1'].ConstrainedSketch(name='__sweep__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Spline(points=points)
s.unsetPrimaryObject()

# Sin wave sketch short:
s2 = mdb.models['Model-1'].ConstrainedSketch(name='__sweep1__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.Spline(points=points)
s2.unsetPrimaryObject()

# Weave cross-section sketch:
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, transform=(0.499980071344579, -0.866036909293288, 0.0, -0.0, 0.0, 1.0, -0.866036909293288, -0.499980071344579, -0.0, 0.0, 0.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.setPrimaryObject(option=STANDALONE)
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(fibre_diameter / 2, 0.0))
s1.unsetPrimaryObject()
print('Sketching done!')

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

# Part creation:
p = mdb.models['Model-1'].Part(name='CfWeave', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['CfWeave']
p.BaseSolidSweep(sketch=s1, path=s)

p1 = mdb.models['Model-1'].Part(name='CfBase', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p1 = mdb.models['Model-1'].parts['CfBase']
p1.BaseSolidSweep(sketch=s3, path=s2)

print('Part creation done!')

# Delete sketches:
del mdb.models['Model-1'].sketches['__sweep__']
del mdb.models['Model-1'].sketches['__profile__']

# Material creation:
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P1, f_P2, f_P3, f_G1, f_G2, f_G3), ))

# Section creation:
mdb.models['Model-1'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)

# Assembly creation:
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)

# Weave arrangement:
for i in range(fibre_cols + 1):
    a.Instance(name='CfWeave-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave-' + str(i + 1), ), vector=(0.0, 0.0, (fibre_spacing * i)))
for i in range((fibre_cols - 2) + 1):
    a.Instance(name='CfWeave2-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave2-' + str(i + 1), ), vector=(0.0, fibre_spacing, (fibre_spacing * (i + 1))))
    a.Instance(name='CfWeave2n-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave2n-' + str(i + 1), ), vector=(0.0, -fibre_spacing, (fibre_spacing * (i + 1))))
for i in range((fibre_cols - 4) + 1):
    a.Instance(name='CfWeave3-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave3-' + str(i + 1), ), vector=(0.0, (fibre_spacing * 2), (fibre_spacing * (i + 2))))
    a.Instance(name='CfWeave3n-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave3n-' + str(i + 1), ), vector=(0.0, -(fibre_spacing * 2), (fibre_spacing * (i + 2))))
for i in range((fibre_cols - 8) + 1):
    a.Instance(name='CfWeave4-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave4-' + str(i + 1), ), vector=(0.0, (fibre_spacing * 3), (fibre_spacing * (i + 4))))
    a.Instance(name='CfWeave4n-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave4n-' + str(i + 1), ), vector=(0.0, -(fibre_spacing * 3), (fibre_spacing * (i + 4))))
for i in range((fibre_cols - 16) + 1):
    a.Instance(name='CfWeave5-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave5-' + str(i + 1), ), vector=(0.0, (fibre_spacing * 4), (fibre_spacing * (i + 8))))
    a.Instance(name='CfWeave5n-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave5n-' + str(i + 1), ), vector=(0.0, -(fibre_spacing * 4), (fibre_spacing * (i + 8))))
for i in range((fibre_cols - 26) + 1):
    a.Instance(name='CfWeave6-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave6-' + str(i + 1), ), vector=(0.0, (fibre_spacing * 5), (fibre_spacing * (i + 13))))
    a.Instance(name='CfWeave6n-' + str(i + 1), part=p, dependent=ON)
    a.translate(instanceList=('CfWeave6n-' + str(i + 1), ), vector=(0.0, -(fibre_spacing * 5), (fibre_spacing * (i + 13))))
a.Instance(name='Yarn', part=p1, dependent=ON)
a.translate(instanceList=('Yarn', ), vector=(0.0, 0.0, (e_width / 2) - fibre_diameter))

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Fibres', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'], a.instances['CfWeave-5'], a.instances['CfWeave-6'],
    a.instances['CfWeave-7'], a.instances['CfWeave-8'], a.instances['CfWeave-9'], a.instances['CfWeave-10'], a.instances['CfWeave-11'], a.instances['CfWeave-12'], a.instances['CfWeave-13'], a.instances['CfWeave-14'],
    a.instances['CfWeave-15'], a.instances['CfWeave-16'], a.instances['CfWeave-17'], a.instances['CfWeave-18'], a.instances['CfWeave-19'], a.instances['CfWeave-20'], a.instances['CfWeave-21'], a.instances['CfWeave-22'],
    a.instances['CfWeave-23'], a.instances['CfWeave-24'], a.instances['CfWeave-25'], a.instances['CfWeave-26'], a.instances['CfWeave-27'], a.instances['CfWeave-28'], a.instances['CfWeave-29'], a.instances['CfWeave-30'],
    a.instances['CfWeave-31'], a.instances['CfWeave-32'], a.instances['CfWeave-33'], a.instances['CfWeave-34'], a.instances['CfWeave-35'], a.instances['CfWeave-36'], a.instances['CfWeave-37'], a.instances['CfWeave2-1'],
    a.instances['CfWeave2n-1'], a.instances['CfWeave2-2'], a.instances['CfWeave2n-2'], a.instances['CfWeave2-3'], a.instances['CfWeave2n-3'], a.instances['CfWeave2-4'], a.instances['CfWeave2n-4'], a.instances['CfWeave2-5'],
    a.instances['CfWeave2n-5'], a.instances['CfWeave2-6'], a.instances['CfWeave2n-6'], a.instances['CfWeave2-7'], a.instances['CfWeave2n-7'], a.instances['CfWeave2-8'], a.instances['CfWeave2n-8'], a.instances['CfWeave2-9'],
    a.instances['CfWeave2n-9'], a.instances['CfWeave2-10'], a.instances['CfWeave2n-10'], a.instances['CfWeave2-11'], a.instances['CfWeave2n-11'], a.instances['CfWeave2-12'], a.instances['CfWeave2n-12'], a.instances['CfWeave2-13'],
    a.instances['CfWeave2n-13'], a.instances['CfWeave2-14'], a.instances['CfWeave2n-14'], a.instances['CfWeave2-15'], a.instances['CfWeave2n-15'], a.instances['CfWeave2-16'], a.instances['CfWeave2n-16'], a.instances['CfWeave2-17'],
    a.instances['CfWeave2n-17'], a.instances['CfWeave2-18'], a.instances['CfWeave2n-18'], a.instances['CfWeave2-19'], a.instances['CfWeave2n-19'], a.instances['CfWeave2-20'], a.instances['CfWeave2n-20'], a.instances['CfWeave2-21'],
    a.instances['CfWeave2n-21'], a.instances['CfWeave2-22'], a.instances['CfWeave2n-22'], a.instances['CfWeave2-23'], a.instances['CfWeave2n-23'], a.instances['CfWeave2-24'], a.instances['CfWeave2n-24'], a.instances['CfWeave2-25'],
    a.instances['CfWeave2n-25'], a.instances['CfWeave2-26'], a.instances['CfWeave2n-26'], a.instances['CfWeave2-27'], a.instances['CfWeave2n-27'], a.instances['CfWeave2-28'], a.instances['CfWeave2n-28'], a.instances['CfWeave2-29'],
    a.instances['CfWeave2n-29'], a.instances['CfWeave2-30'], a.instances['CfWeave2n-30'], a.instances['CfWeave2-31'], a.instances['CfWeave2n-31'], a.instances['CfWeave2-32'], a.instances['CfWeave2n-32'], a.instances['CfWeave2-33'],
    a.instances['CfWeave2n-33'], a.instances['CfWeave2-34'], a.instances['CfWeave2n-34'], a.instances['CfWeave2-35'], a.instances['CfWeave2n-35'], a.instances['CfWeave3-1'], a.instances['CfWeave3n-1'], a.instances['CfWeave3-2'],
    a.instances['CfWeave3n-2'], a.instances['CfWeave3-3'], a.instances['CfWeave3n-3'], a.instances['CfWeave3-4'],a.instances['CfWeave3n-4'], a.instances['CfWeave3-5'], a.instances['CfWeave3n-5'], a.instances['CfWeave3-6'],
    a.instances['CfWeave3n-6'], a.instances['CfWeave3-7'], a.instances['CfWeave3n-7'], a.instances['CfWeave3-8'], a.instances['CfWeave3n-8'], a.instances['CfWeave3-9'], a.instances['CfWeave3n-9'], a.instances['CfWeave3-10'],
    a.instances['CfWeave3n-10'], a.instances['CfWeave3-11'], a.instances['CfWeave3n-11'], a.instances['CfWeave3-12'], a.instances['CfWeave3n-12'], a.instances['CfWeave3-13'], a.instances['CfWeave3n-13'], a.instances['CfWeave3-14'],
    a.instances['CfWeave3n-14'], a.instances['CfWeave3-15'], a.instances['CfWeave3n-15'], a.instances['CfWeave3-16'], a.instances['CfWeave3n-16'], a.instances['CfWeave3-17'], a.instances['CfWeave3n-17'], a.instances['CfWeave3-18'],
    a.instances['CfWeave3n-18'], a.instances['CfWeave3-19'], a.instances['CfWeave3n-19'], a.instances['CfWeave3-20'], a.instances['CfWeave3n-20'], a.instances['CfWeave3-21'], a.instances['CfWeave3n-21'], a.instances['CfWeave3-22'],
    a.instances['CfWeave3n-22'], a.instances['CfWeave3-23'], a.instances['CfWeave3n-23'], a.instances['CfWeave3-24'], a.instances['CfWeave3n-24'], a.instances['CfWeave3-25'], a.instances['CfWeave3n-25'], a.instances['CfWeave3-26'],
    a.instances['CfWeave3n-26'], a.instances['CfWeave3-27'], a.instances['CfWeave3n-27'], a.instances['CfWeave3-28'], a.instances['CfWeave3n-28'], a.instances['CfWeave3-29'], a.instances['CfWeave3n-29'], a.instances['CfWeave3-30'],
    a.instances['CfWeave3n-30'], a.instances['CfWeave3-31'], a.instances['CfWeave3n-31'], a.instances['CfWeave3-32'], a.instances['CfWeave3n-32'], a.instances['CfWeave3-33'], a.instances['CfWeave3n-33'], a.instances['CfWeave4-1'],
    a.instances['CfWeave4n-1'], a.instances['CfWeave4-2'], a.instances['CfWeave4n-2'], a.instances['CfWeave4-3'], a.instances['CfWeave4n-3'], a.instances['CfWeave4-4'], a.instances['CfWeave4n-4'], a.instances['CfWeave4-5'],
    a.instances['CfWeave4n-5'], a.instances['CfWeave4-6'], a.instances['CfWeave4n-6'], a.instances['CfWeave4-7'], a.instances['CfWeave4n-7'], a.instances['CfWeave4-8'], a.instances['CfWeave4n-8'], a.instances['CfWeave4-9'],
    a.instances['CfWeave4n-9'], a.instances['CfWeave4-10'], a.instances['CfWeave4n-10'], a.instances['CfWeave4-11'], a.instances['CfWeave4n-11'], a.instances['CfWeave4-12'], a.instances['CfWeave4n-12'], a.instances['CfWeave4-13'],
    a.instances['CfWeave4n-13'], a.instances['CfWeave4-14'], a.instances['CfWeave4n-14'], a.instances['CfWeave4-15'], a.instances['CfWeave4n-15'], a.instances['CfWeave4-16'], a.instances['CfWeave4n-16'], a.instances['CfWeave4-17'],
    a.instances['CfWeave4n-17'], a.instances['CfWeave4-18'], a.instances['CfWeave4n-18'], a.instances['CfWeave4-19'], a.instances['CfWeave4n-19'], a.instances['CfWeave4-20'], a.instances['CfWeave4n-20'], a.instances['CfWeave4-21'],
    a.instances['CfWeave4n-21'], a.instances['CfWeave4-22'], a.instances['CfWeave4n-22'], a.instances['CfWeave4-23'], a.instances['CfWeave4n-23'], a.instances['CfWeave4-24'], a.instances['CfWeave4n-24'], a.instances['CfWeave4-25'],
    a.instances['CfWeave4n-25'], a.instances['CfWeave4-26'], a.instances['CfWeave4n-26'], a.instances['CfWeave4-27'], a.instances['CfWeave4n-27'], a.instances['CfWeave4-28'], a.instances['CfWeave4n-28'], a.instances['CfWeave4-29'],
    a.instances['CfWeave4n-29'], a.instances['CfWeave5-1'], a.instances['CfWeave5n-1'], a.instances['CfWeave5-2'], a.instances['CfWeave5n-2'], a.instances['CfWeave5-3'], a.instances['CfWeave5n-3'], a.instances['CfWeave5-4'],
    a.instances['CfWeave5n-4'], a.instances['CfWeave5-5'], a.instances['CfWeave5n-5'], a.instances['CfWeave5-6'], a.instances['CfWeave5n-6'], a.instances['CfWeave5-7'], a.instances['CfWeave5n-7'], a.instances['CfWeave5-8'],
    a.instances['CfWeave5n-8'], a.instances['CfWeave5-9'], a.instances['CfWeave5n-9'], a.instances['CfWeave5-10'], a.instances['CfWeave5n-10'], a.instances['CfWeave5-11'], a.instances['CfWeave5n-11'], a.instances['CfWeave5-12'],
    a.instances['CfWeave5n-12'], a.instances['CfWeave5-13'], a.instances['CfWeave5n-13'], a.instances['CfWeave5-14'], a.instances['CfWeave5n-14'], a.instances['CfWeave5-15'], a.instances['CfWeave5n-15'], a.instances['CfWeave5-16'],
    a.instances['CfWeave5n-16'], a.instances['CfWeave5-17'], a.instances['CfWeave5n-17'], a.instances['CfWeave5-18'], a.instances['CfWeave5n-18'], a.instances['CfWeave5-19'], a.instances['CfWeave5n-19'], a.instances['CfWeave5-20'],
    a.instances['CfWeave5n-20'], a.instances['CfWeave5-21'], a.instances['CfWeave5n-21'], a.instances['CfWeave6-1'], a.instances['CfWeave6n-1'], a.instances['CfWeave6-2'], a.instances['CfWeave6n-2'], a.instances['CfWeave6-3'],
    a.instances['CfWeave6n-3'], a.instances['CfWeave6-4'], a.instances['CfWeave6n-4'], a.instances['CfWeave6-5'], a.instances['CfWeave6n-5'], a.instances['CfWeave6-6'], a.instances['CfWeave6n-6'], a.instances['CfWeave6-7'],
    a.instances['CfWeave6n-7'], a.instances['CfWeave6-8'], a.instances['CfWeave6n-8'], a.instances['CfWeave6-9'], a.instances['CfWeave6n-9'], a.instances['CfWeave6-10'], a.instances['CfWeave6n-10'], a.instances['CfWeave6-11'],
    a.instances['CfWeave6n-11'], ), originalInstances=DELETE, domain=GEOMETRY)

del mdb.models['Model-1'].parts['CfWeave']
p = mdb.models['Model-1'].parts['CfBase']
p1 = mdb.models['Model-1'].parts['Fibres']

# Composite specimen creation:
p.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=10.0)
f1, e1, d1 = p.faces, p.edges, p.datums
t = p.MakeSketchTransform(sketchPlane=d1[2], sketchUpEdge=e1.findAt(coordinates=(18.242115, 0.961099, 0.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(8.98655, 10.0, -0.029281))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=1, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=(-4, 10), point2=(4, -10))
s.rectangle(point1=(-3, 8.5), point2=(3, -8.5))
f, e, d2 = p.faces, p.edges, p.datums
p.CutExtrude(sketchPlane=d2[2], sketchUpEdge=e.findAt(coordinates=(18.242115, 0.961099, 0.0)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

p1 = mdb.models['Model-1'].parts['Fibres']
p1.DatumPlaneByPrincipalPlane(principalPlane=XZPLANE, offset=10.0)
p1 = mdb.models['Model-1'].parts['Fibres']
f1, e1, d1 = p1.faces, p1.edges, p1.datums
t = p1.MakeSketchTransform(sketchPlane=d1[2], sketchUpEdge=e1.findAt(coordinates=(18.0, 1.012118, 2.09)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(8.998734, 10.0, 2.160166))
s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=1, transform=t)
g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
p1.projectReferencesOntoSketch(sketch=s1, filter=COPLANAR_EDGES)
s1.rectangle(point1=(-10, 4), point2=(10, -4))
s1.rectangle(point1=(-8.5, 3), point2=(8.5, -3))
f, e, d2 = p1.faces, p1.edges, p1.datums
p1.CutExtrude(sketchPlane=d2[2], sketchUpEdge=e.findAt(coordinates=(18.0, 1.012118, 2.09)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s1, flipExtrudeDirection=OFF)
s1.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# # Fibre orientation assignment:
# v1 = p.vertices
# p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(56.699112, -2.0, 56.699112)), point1=v1.findAt(coordinates=(56.699112, -2.0, 18.699112)), point2=v1.findAt(coordinates=(56.699112, 2.0, 18.699112)), name='Datum csys-1', coordSysType=CARTESIAN)
# v2 = p.vertices
# p.DatumCsysByThreePoints(origin=v2.findAt(coordinates=(56.699112, -2.0, 56.699112)), point1=v2.findAt(coordinates=(18.699112, -2.0, 56.699112)), point2=v2.findAt(coordinates=(18.699112, 2.0, 56.699112)), name='Datum csys-2', coordSysType=CARTESIAN)
# c = p.cells
# cells = c.findAt(((38.598564, 0.07419, 18.699112), ), ((49.366029, -0.07419, 18.699112), ), ((51.164355, -0.999926, 18.699112), ), ((36.800237, 0.999926, 18.699112), ),
#                  ((24.233288, -0.07419, 18.699112), ), ((26.032194, 0.07419, 18.699112), ))
# region = regionToolset.Region(cells=cells)
# orientation = mdb.models['Model-1'].parts['Composite'].datums[3]
# mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)
# c = p.cells
# cells = c.findAt(((18.699112, -0.07419, 38.598564), ), ((18.699112, 0.999926, 51.164355), ), ((18.699112, 0.07419, 49.366029), ), ((18.699112, -0.999926, 36.800237), ),
#                  ((18.699112, 0.07419, 24.233288), ), ((18.699112, -0.07419, 26.032194), ))
# region = regionToolset.Region(cells=cells)
# orientation = mdb.models['Model-1'].parts['Composite'].datums[4]
# mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# # Section assignment:
# c = p.cells
# cells = c.findAt(((38.598564, 0.07419, 18.699112), ), ((49.366029, -0.07419, 18.699112), ), ((51.164355, -0.999926, 18.699112), ), ((18.699112, -0.07419, 38.598564), ),
#                  ((18.699112, 0.999926, 51.164355), ), ((18.699112, 0.07419, 49.366029), ), ((18.699112, -0.999926, 36.800237), ), ((36.800237, 0.999926, 18.699112), ),
#                  ((18.699112, 0.07419, 24.233288), ), ((24.233288, -0.07419, 18.699112), ), ((26.032194, 0.07419, 18.699112), ), ((18.699112, -0.07419, 26.032194), ))
# region = regionToolset.Region(cells=cells)
# p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
# c = p.cells
# cells = c.findAt(((18.699112, -0.659536, 43.275667), ))
# region = regionToolset.Region(cells=cells)
# p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
# print('Assembly done!')

# # Seeding and meshing:
# c = p.cells
# pickedRegions = c.findAt(((38.598564, 0.07419, 18.699112), ), ((49.366029, -0.07419, 18.699112), ), ((51.164355, -0.999926, 18.699112), ), ((18.699112, -0.07419, 38.598564), ),
#                          ((18.699112, 0.999926, 51.164355), ), ((18.699112, 0.07419, 49.366029), ), ((18.699112, -0.999926, 36.800237), ), ((36.800237, 0.999926, 18.699112), ),
#                          ((18.699112, 0.07419, 24.233288), ), ((24.233288, -0.07419, 18.699112), ), ((26.032194, 0.07419, 18.699112), ), ((18.699112, -0.07419, 26.032194), ),
#                          ((18.699112, -0.659536, 43.275667), ))
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

# # Set Assignment:
# f = p.faces
# faces = f.findAt(((18.699112, 0.07419, 24.233288), ), ((18.699112, -0.07419, 26.032194), ), ((18.699112, -0.999926, 36.800237), ), ((18.699112, -0.07419, 38.598564), ),
#                  ((18.699112, 0.999926, 51.164355), ), ((18.699112, 0.07419, 49.366029), ), ((18.699112, -0.659536, 43.275667), ))
# p.Set(faces=faces, name='XBack')
# faces = f.findAt(((56.699112, -0.075227, 24.238169), ), ((56.699112, 0.075227, 26.027313), ), ((56.699112, -0.99999, 36.800237), ), ((56.699112, 0.075227, 38.593684), ),
#                  ((56.699112, 0.99999, 51.164355), ), ((56.699112, -0.075227, 49.370911), ), ((56.699112, -0.774314, 31.613679), ))
# p.Set(faces=faces, name='XFront')
# faces = f.findAt(((36.800237, 0.999926, 18.699112), ), ((24.233288, -0.07419, 18.699112), ), ((26.032194, 0.07419, 18.699112), ), ((38.598564, 0.07419, 18.699112), ),
#                  ((49.366029, -0.07419, 18.699112), ), ((51.164355, -0.999926, 18.699112), ), ((44.688925, -0.659536, 18.699112), ))
# p.Set(faces=faces, name='ZBack')
# faces = f.findAt(((36.800237, 0.99999, 56.699112), ), ((24.238169, 0.075227, 56.699112), ), ((26.027313, -0.075227, 56.699112), ), ((38.593684, -0.075227, 56.699112), ),
#                  ((49.370911, 0.075227, 56.699112), ), ((51.164355, -0.99999, 56.699112), ), ((55.72765, -1.551284, 56.699112), ))
# p.Set(faces=faces, name='ZFront')
# faces = f.findAt(((44.032445, 2.0, 31.365779), ))
# p.Set(faces=faces, name='YTop')
# faces = f.findAt(((44.032445, -2.0, 44.032445), ))
# p.Set(faces=faces, name='YBottom')

# # History output:
# regionDef = mdb.models['Model-1'].rootAssembly.allInstances['Composite-1'].sets['XFront']
# mdb.models['Model-1'].HistoryOutputRequest(name='DispHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)

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
# # # mdb.jobs['TensionAnalysis'].submit(consistencyChecking=OFF)
# # # mdb.jobs['ShearAnalysis'].submit(consistencyChecking=OFF)
# # # mdb.jobs['CompressionAnalysis'].submit(consistencyChecking=OFF)
# # # print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
