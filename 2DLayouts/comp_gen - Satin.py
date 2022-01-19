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
overlap_len = period * 2

# Ellipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
b_width = (pi_len * pi) * 2
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
######################################################################################################################################################


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

        if y_b < y < y_a or y_b > y > y_a or y > 0:
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
a.Instance(name='CfWeave-3', part=p, dependent=ON)
a.Instance(name='CfWeave-4', part=p, dependent=ON)
a.Instance(name='CfWeave-5', part=p, dependent=ON)
a.Instance(name='CfWeave-6', part=p, dependent=ON)
a.Instance(name='CfWeave-7', part=p, dependent=ON)
a.Instance(name='CfWeave-8', part=p, dependent=ON)
a.Instance(name='ResinBlock-1', part=p1, dependent=ON)

# Weave arrangement:
a.rotate(instanceList=('CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.rotate(instanceList=('CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.translate(instanceList=('CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8'), vector=((period / 2), 0.0, -(period / 2)))
a.translate(instanceList=('CfWeave-2', ), vector=(period, 0.0, period))
a.translate(instanceList=('CfWeave-3', ), vector=((3 * period), 0.0, (2 * period)))
a.translate(instanceList=('CfWeave-4', ), vector=((2 * period), 0.0, (3 * period)))
a.translate(instanceList=('CfWeave-6', ), vector=(period, 0.0, period))
a.translate(instanceList=('CfWeave-7', ), vector=((2 * period), 0.0, (3 * period)))
a.translate(instanceList=('CfWeave-8', ), vector=((3 * period), 0.0, (2 * period)))
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-3', 'CfWeave-4'), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=3, number2=1, spacing1=(period * 4), spacing2=1)
a.LinearInstancePattern(instanceList=('CfWeave-5', 'CfWeave-6', 'CfWeave-7', 'CfWeave-8'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=3, number2=1, spacing1=(period * 4), spacing2=1)
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), -(period / 1.8)))

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'], a.instances['CfWeave-5'], a.instances['CfWeave-6'],
                                                        a.instances['CfWeave-7'], a.instances['CfWeave-8'], a.instances['ResinBlock-1'], a.instances['CfWeave-1-lin-2-1'], a.instances['CfWeave-1-lin-3-1'], a.instances['CfWeave-2-lin-2-1'],
                                                        a.instances['CfWeave-2-lin-3-1'], a.instances['CfWeave-4-lin-2-1'], a.instances['CfWeave-4-lin-3-1'], a.instances['CfWeave-3-lin-2-1'], a.instances['CfWeave-3-lin-3-1'],
                                                        a.instances['CfWeave-5-lin-2-1'], a.instances['CfWeave-5-lin-3-1'], a.instances['CfWeave-6-lin-2-1'], a.instances['CfWeave-6-lin-3-1'], a.instances['CfWeave-8-lin-2-1'],
                                                        a.instances['CfWeave-8-lin-3-1'], a.instances['CfWeave-7-lin-2-1'], a.instances['CfWeave-7-lin-3-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['CfWeave']
del mdb.models['Model-1'].parts['ResinBlock']
p = mdb.models['Model-1'].parts['Composite']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(25.132741, 2.0, 46.774822)), sketchUpEdge=e.findAt(coordinates=(18.849556, 2.0, 71.907565)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(37.699112, 2.0, 34.208453))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=(0.2 / sc), transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=((32.0 / sc), (32.0 / sc)), point2=(-(6.0 / sc), -(6.0 / sc)))
s.rectangle(point1=(-(60.0 / sc), -(60.0 / sc)), point2=((60.0 / sc), (60.0 / sc)))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(25.132741, 2.0, 46.774822)), sketchUpEdge=e1.findAt(coordinates=(18.849556, 2.0, 71.907565)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Fibre orientation assignment:
v1 = p.vertices
p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(69.699112, -2.0, 66.208453)), point1=v1.findAt(coordinates=(69.699112, -2.0, 28.208453)), point2=v1.findAt(coordinates=(69.699112, 2.0, 28.208453)), name='Datum csys-1', coordSysType=CARTESIAN)
v2 = p.vertices
p.DatumCsysByThreePoints(origin=v2.findAt(coordinates=(69.699112, -2.0, 66.208453)), point1=v2.findAt(coordinates=(31.699112, -2.0, 66.208453)), point2=v2.findAt(coordinates=(31.699112, 2.0, 66.208453)), name='Datum csys-2', coordSysType=CARTESIAN)
c = p.cells
cells = c.findAt(((55.652719, 9.1e-05, 28.208453), ), ((36.804546, -0.000322, 28.208453), ), ((61.937288, -0.000322, 28.208453), ), ((49.366609, 0.999924, 28.208453), ),
                 ((43.083425, 0.999926, 28.208453), ), ((68.216164, 0.999926, 28.208453), ))
region = regionToolset.Region(cells=cells)
orientation = mdb.models['Model-1'].parts['Composite'].datums[3]
mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)
c = p.cells
c = p.cells
cells = c.findAt(((69.699112, -0.999776, 52.508203), ), ((69.699112, -0.999772, 33.658647), ), ((69.699112, -0.999772, 58.791387), ), ((69.699112, -0.35026, 46.226288), ),
                 ((69.699112, 0.350881, 39.946159), ), ((69.699112, 0.350881, 65.078903), ))
region = regionToolset.Region(cells=cells)
orientation = mdb.models['Model-1'].parts['Composite'].datums[4]
mdb.models['Model-1'].parts['Composite'].MaterialOrientation(region=region, orientationType=SYSTEM, axis=AXIS_3, localCsys=orientation, fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, additionalRotationField='', stackDirection=STACK_3)

# Section assignment:
c = p.cells
cells = c.findAt(((69.699112, -0.999776, 52.508203), ), ((55.652719, 9.1e-05, 28.208453), ), ((36.804546, -0.000322, 28.208453), ), ((61.937288, -0.000322, 28.208453), ),
                 ((49.366609, 0.999924, 28.208453), ), ((43.083425, 0.999926, 28.208453), ), ((68.216164, 0.999926, 28.208453), ), ((69.699112, -0.999772, 33.658647), ),
                 ((69.699112, -0.999772, 58.791387), ), ((69.699112, -0.35026, 46.226288), ), ((69.699112, 0.350881, 39.946159), ), ((69.699112, 0.350881, 65.078903), ))
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
c = p.cells
cells = c.findAt(((37.531804, 0.045407, 28.208453), ))
region = regionToolset.Region(cells=cells)
p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
print('Assembly done!')

# Seeding and meshing:
c = p.cells
pickedRegions = c.findAt(((69.699112, -0.999776, 52.508203), ), ((55.652719, 9.1e-05, 28.208453), ), ((36.804546, -0.000322, 28.208453), ), ((61.937288, -0.000322, 28.208453), ),
                         ((49.366609, 0.999924, 28.208453), ), ((43.083425, 0.999926, 28.208453), ), ((68.216164, 0.999926, 28.208453), ), ((69.699112, -0.999772, 33.658647), ),
                         ((69.699112, -0.999772, 58.791387), ), ((69.699112, -0.35026, 46.226288), ), ((69.699112, 0.350881, 39.946159), ), ((69.699112, 0.350881, 65.078903), ),
                         ((37.531804, 0.045407, 28.208453), ))
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

# Set Assignment:
f = p.faces
faces = f.findAt(((31.699112, -0.174353, 52.507818), ), ((31.699112, 0.173963, 33.662941), ), ((31.699112, 0.173963, 58.795682), ), ((31.699112, -0.999925, 46.225015), ),
                 ((31.699112, -0.999926, 39.941831), ), ((31.699112, -0.999926, 65.074572), ), ((31.699112, -1.674704, 64.487715), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((69.699112, -0.999776, 52.508203), ), ((69.699112, -0.999772, 33.658647), ), ((69.699112, -0.999772, 58.791387), ), ((69.699112, -0.35026, 46.226288), ),
                 ((69.699112, 0.350881, 39.946159), ), ((69.699112, 0.350881, 65.078903), ), ((69.699112, -1.6746, 29.816445), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((55.652719, 9.1e-05, 28.208453), ), ((36.804546, -0.000322, 28.208453), ), ((61.937288, -0.000322, 28.208453), ), ((49.366609, 0.999924, 28.208453), ),
                 ((43.083425, 0.999926, 28.208453), ), ((68.216164, 0.999926, 28.208453), ), ((37.531804, 0.045407, 28.208453), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((55.649793, 0.999776, 66.208453), ), ((36.800237, 0.99977, 66.208453), ), ((61.932981, 0.99977, 66.208453), ), ((49.367903, 0.182309, 66.208453), ),
                 ((43.08581, -0.183076, 66.208453), ), ((68.218549, -0.183076, 66.208453), ), ((54.885738, -0.948986, 66.208453), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((44.365779, 2.0, 53.541784), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((57.032445, -2.0, 53.541784), ))
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
# print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
