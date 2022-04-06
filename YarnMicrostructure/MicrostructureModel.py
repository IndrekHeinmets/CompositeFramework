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
s1.setPrimaryObject(option=STANDALONE)
s1.CircleByCenterPerimeter(center=(0.0, 0.0), point1=(fibre_diameter / 2, 0.0))
s1.unsetPrimaryObject()
print('Sketching done!')

# Part creation:
p = mdb.models['Model-1'].Part(name='CfWeave', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['CfWeave']
p.BaseSolidSweep(sketch=s1, path=s)
print('Part creation done!')

# Delete sketches:
del mdb.models['Model-1'].sketches['__sweep__']
del mdb.models['Model-1'].sketches['__profile__']

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

# End of script:
print('*************************')
print('End of script, no errors!')
