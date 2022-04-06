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
# Scale:
sc = 1

# Sin curve:
sin_x = 0.5
step = 0.1
pi_len = 12.0
period = pi / (sin_x * sc)

# Ellipse cs:
e_width = 4.5
e_height = 1.2

# Fiber props:
f_name = 'Carbon Fiber'
f_E1 = 78.4e9
f_E2 = 7.11e9
f_E3 = 7.06e9
f_P12 = 0.29
f_P13 = 0.3
f_P23 = 0.47
f_G12 = 2.14e9
f_G13 = 2.1e9
f_G23 = 1.66e9

# Load displacement:
strain = 0.1
l_disp = pi_len * pi * strain

# Mesh density:
md = 1.0

# History output time intervals:
hi = 20
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
mdb.models.changeKey(fromName='Model-1', toName='WovenFibre')
mdb.Model(name='StraightFibre', objectToCopy=mdb.models['WovenFibre'])
print('Running script...')

# Plain weave spline nodes:
points = find_spline_nodes((sin_x * sc), (step / sc), (pi_len / sc), sc)

# Weave fibre path:
s = mdb.models['WovenFibre'].ConstrainedSketch(name='__sweep__', sheetSize=1)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Spline(points=points)
s.unsetPrimaryObject()

# Straight fibre path:
s2 = mdb.models['StraightFibre'].ConstrainedSketch(name='__sweep__', sheetSize=1)
g2, v2, d2, c2 = s2.geometry, s2.vertices, s2.dimensions, s2.constraints
s2.setPrimaryObject(option=STANDALONE)
s2.Line(point1=(points[0]), point2=(points[-1]))
s2.unsetPrimaryObject()

# Weave fibre cross-section:
s1 = mdb.models['WovenFibre'].ConstrainedSketch(name='__profile__', sheetSize=1, transform=(0.570373875349173, -0.821385197285151, 0.0, -0.0, 0.0, 1.0, -0.821385197285151, -0.570373875349173, -0.0, -75.0, 0.0, 0.0))
g1, v1, d1, c1 = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
s1.setPrimaryObject(option=SUPERIMPOSE)
s1.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
s1.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s1.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / (2 * sc)), 0.0))
s1.CoincidentConstraint(entity1=v1[0], entity2=g1[3], addUndoState=False)
s1.CoincidentConstraint(entity1=v1[2], entity2=g1[2], addUndoState=False)
s1.unsetPrimaryObject()

# Straight fibre cross-section:
s3 = mdb.models['StraightFibre'].ConstrainedSketch(name='__profile__', sheetSize=1, transform=(0.0, -1.0, 0.0, -0.0, 0.0, 1.0, -1.0, -0.0, -0.0, -60.0, 0.0, 0.0))
g3, v3, d3, c3 = s3.geometry, s3.vertices, s3.dimensions, s3.constraints
s3.setPrimaryObject(option=SUPERIMPOSE)
s3.ConstructionLine(point1=(-100.0, 0.0), point2=(100.0, 0.0))
s3.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
s3.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / (2 * sc)), 0.0))
s3.CoincidentConstraint(entity1=v3[0], entity2=g3[3], addUndoState=False)
s3.CoincidentConstraint(entity1=v3[2], entity2=g3[2], addUndoState=False)
s3.unsetPrimaryObject()

# Part creation:
p = mdb.models['WovenFibre'].Part(name='WovenFibre', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p1 = mdb.models['StraightFibre'].Part(name='StraightFibre', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['WovenFibre'].parts['WovenFibre']
p1 = mdb.models['StraightFibre'].parts['StraightFibre']
p.BaseSolidSweep(sketch=s1, path=s)
p1.BaseSolidSweep(sketch=s3, path=s2)
print('Part creation done!')

# Delete sketches:
del mdb.models['WovenFibre'].sketches['__sweep__']
del mdb.models['StraightFibre'].sketches['__sweep__']
del mdb.models['WovenFibre'].sketches['__profile__']
del mdb.models['StraightFibre'].sketches['__profile__']
print('Sketching done!')

# Material & Section creation:
mdb.models['WovenFibre'].Material(name=f_name)
mdb.models['StraightFibre'].Material(name=f_name)
mdb.models['WovenFibre'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P12, f_P13, f_P23, f_G12, f_G13, f_G23), ))
mdb.models['StraightFibre'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P12, f_P13, f_P23, f_G12, f_G13, f_G23), ))
mdb.models['WovenFibre'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)
mdb.models['StraightFibre'].HomogeneousSolidSection(name='Cf_sec', material=f_name, thickness=None)

# Assembly creation:
a = mdb.models['WovenFibre'].rootAssembly
a1 = mdb.models['StraightFibre'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
a1.DatumCsysByDefault(CARTESIAN)
a.Instance(name='WovenFibre-1', part=p, dependent=ON)
a1.Instance(name='StraightFibre-1', part=p1, dependent=ON)

# Cell assignment:
cells = p.cells.findAt(((0.0, 0.0, 2.242777), ))
cells1 = p1.cells.findAt(((0.0, 0.0, 2.242777), ))

# Fibre orientation assignment:
region = regionToolset.Region(cells=cells)
region1 = regionToolset.Region(cells=cells1)
mdb.models['WovenFibre'].parts['WovenFibre'].MaterialOrientation(region=region, orientationType=GLOBAL, axis=AXIS_1, additionalRotationType=ROTATION_NONE, localCsys=None, fieldName='', stackDirection=STACK_3)
mdb.models['StraightFibre'].parts['StraightFibre'].MaterialOrientation(region=region1, orientationType=GLOBAL, axis=AXIS_1, additionalRotationType=ROTATION_NONE, localCsys=None, fieldName='', stackDirection=STACK_3)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
p1.SectionAssignment(region=region1, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)

# Seeding and meshing:
p.setMeshControls(regions=cells, elemShape=TET, technique=FREE)
p1.setMeshControls(regions=cells, elemShape=TET, technique=FREE)
elemType1 = mesh.ElemType(elemCode=C3D20R)
elemType2 = mesh.ElemType(elemCode=C3D15)
elemType3 = mesh.ElemType(elemCode=C3D10)
p.setElementType(regions=(cells, ), elemTypes=(elemType1, elemType2, elemType3))
p1.setElementType(regions=(cells, ), elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=md, deviationFactor=0.1, minSizeFactor=0.1)
p1.seedPart(size=md, deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
p1.generateMesh()
print('Meshing done!')

# Set Assignment:
f = p.faces
f1 = p1.faces
faces = f.findAt(((0.0, 0.0, 2.242777), ))
faces1 = f1.findAt(((0.0, 0.0, 2.242777), ))
p.Set(faces=faces, name='xBack')
p1.Set(faces=faces1, name='xBack')
faces = f.findAt(((37.5, -0.099392, 2.242777), ))
faces1 = f1.findAt(((37.5, -0.099392, 2.242777), ))
p.Set(faces=faces, name='xFront')
p1.Set(faces=faces1, name='xFront')

# Static analysis step:
mdb.models['WovenFibre'].StaticStep(name='StaticAnalysis', previous='Initial')
mdb.models['StraightFibre'].StaticStep(name='StaticAnalysis', previous='Initial')

# Refrence point and history output:
a.ReferencePoint(point=(37.5, -0.099392, 2.25))
a1.ReferencePoint(point=(37.5, -0.099392, 2.25))
r1 = a.referencePoints
r2 = a1.referencePoints
refPoints1 = (r1[4], )
refPoints2 = (r2[4], )
a.Set(referencePoints=refPoints1, name='RPSet')
a1.Set(referencePoints=refPoints2, name='RPSet')

regionDef = mdb.models['WovenFibre'].rootAssembly.sets['RPSet']
regionDef = mdb.models['StraightFibre'].rootAssembly.sets['RPSet']
mdb.models['WovenFibre'].HistoryOutputRequest(name='RPHO', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), numIntervals=20, region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
mdb.models['StraightFibre'].HistoryOutputRequest(name='RPHO', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), numIntervals=20, region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
mdb.models['WovenFibre'].Equation(name='Eqn', terms=((1.0, 'WovenFibre-1.xFront', 1), (-1.0, 'RPSet', 1)))
mdb.models['StraightFibre'].Equation(name='Eqn', terms=((1.0, 'StraightFibre-1.xFront', 1), (-1.0, 'RPSet', 1)))

# Tension setup:
region = a.instances['WovenFibre-1'].sets['xBack']
region1 = a1.instances['StraightFibre-1'].sets['xBack']
mdb.models['WovenFibre'].DisplacementBC(name='xBackSup', createStepName='StaticAnalysis', region=region, u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
mdb.models['StraightFibre'].DisplacementBC(name='xBackSup', createStepName='StaticAnalysis', region=region1, u1=0.0, u2=0.0, u3=0.0, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['WovenFibre'].rootAssembly.sets['RPSet']
region1 = mdb.models['StraightFibre'].rootAssembly.sets['RPSet']
mdb.models['WovenFibre'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=l_disp, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
mdb.models['StraightFibre'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region1, u1=l_disp, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()
a1.regenerate()

mdb.Job(name='WovenTens', model='WovenFibre', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='StraightTens', model='StraightFibre', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['WovenTens'].submit(consistencyChecking=OFF)
# mdb.jobs['StraightTens'].submit(consistencyChecking=OFF)

# End of script:
print('*************************')
print('End of script, no errors!')
