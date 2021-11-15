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
sc = 1000

# Sin curve:
sin_x = 0.5
step = 0.01
pi_len = 12.0
period = pi / (sin_x * sc)

# Ellipse cs:
e_width = 4.5
e_height = 0.6

# Resin block:
b_width = (pi_len * pi) * 2.5
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


def find_spline_nodes(sin_x, step, pi_len, sc):
    points = []
    length = 51
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
            points.append((x, y))

        else:
            if y > 0:
                points.append((x, y))
            else:
                for j in range(0, length):
                    x += (step * j)
                    offset += (step * j)
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
a.translate(instanceList=('CfWeave-2', 'CfWeave-3', 'CfWeave-4'), vector=(-(period), 0.0, period))
a.translate(instanceList=('CfWeave-3', 'CfWeave-4'), vector=(-(period), 0.0, period))
a.translate(instanceList=('CfWeave-4', ), vector=(-(period), 0.0, period))
a.InstanceFromBooleanMerge(name='weaves', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'], ), originalInstances=DELETE, domain=GEOMETRY)
p = mdb.models['Model-1'].parts['weaves']
a.rotate(instanceList=('ResinBlock-1', 'weaves-1'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, 90.0, 0.0), angle=90.0)
a.LinearInstancePattern(instanceList=('weaves-1', ), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=4, number2=1, spacing1=(period * 4), spacing2=1)
a.Instance(name='weaves-2', part=p, dependent=ON)
a.rotate(instanceList=('weaves-2', ), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.translate(instanceList=('weaves-2', ), vector=((period * 2.5), 0.0, (period * 2.5)))
a.LinearInstancePattern(instanceList=('weaves-2', ), direction1=(0.0, 0.0, -1.0), direction2=(0.0, 1.0, 0.0), number1=4, number2=1, spacing1=(period * 4), spacing2=1)
# a.InstanceFromBooleanMerge(name='Fibers', instances=(a.instances['weaves-1'], a.instances['weaves-1-lin-2-1'], a.instances['weaves-1-lin-3-1'], a.instances['weaves-1-lin-4-1'], a.instances['weaves-2'],
#                                                      a.instances['weaves-2-lin-2-1'], a.instances['weaves-2-lin-3-1'], a.instances['weaves-2-lin-4-1'], ), originalInstances=DELETE, domain=GEOMETRY)
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), 0.02))

# Merge into composite & delete original parts:
# a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['Fibers-1'], a.instances['ResinBlock-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
# del mdb.models['Model-1'].parts['weaves']
# del mdb.models['Model-1'].parts['CfWeave']
# del mdb.models['Model-1'].parts['Fibers']
# del mdb.models['Model-1'].parts['ResinBlock']
# p = mdb.models['Model-1'].parts['Composite']

# Composite specimen creation:
# f, e = p.faces, p.edges
# t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(0.062832, 0.002, -0.011416)), sketchUpEdge=e.findAt(coordinates=(0.094248, 0.002, -0.003562)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(0.047124, 0.002, -0.027124))
# s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=0.002, transform=t)
# g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
# s.setPrimaryObject(option=SUPERIMPOSE)
# p = mdb.models['Model-1'].parts['Composite']
# p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
# s.rectangle(point1=(-0.06, 0.06), point2=(0.06, -0.06))
# s.rectangle(point1=(-0.019, 0.023), point2=(0.019, -0.015))
# f1, e1 = p.faces, p.edges
# p.CutExtrude(sketchPlane=f1.findAt(coordinates=(0.062832, 0.002, -0.011416)), sketchUpEdge=e1.findAt(coordinates=(0.094248, 0.002, -0.003562)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
# s.unsetPrimaryObject()
# del mdb.models['Model-1'].sketches['__profile__']

# Section assignment:
# c = p.cells
# cells = c.findAt(((0.028124, 0.000169, -0.024209), ), ((0.028124, 0.001017, -0.017924), ), ((0.039915, -0.001015, -0.050124), ), ((0.033631, 0.000249, -0.050124), ),
#                  ((0.042031, -0.001216, -0.050124), ), ((0.058763, 0.000249, -0.050124), ), ((0.065048, -0.001015, -0.050124), ), ((0.028124, 0.001017, -0.043057), ),
#                  ((0.028124, 0.001264, -0.036509), ), ((0.028124, 0.000169, -0.049342), ), ((0.028124, -0.000167, -0.030499), ), ((0.052493, -0.00025, -0.050124), ))
# region = regionToolset.Region(cells=cells)
# p.SectionAssignment(region=region, sectionName='Cf_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
# c = p.cells
# cells = c.findAt(((0.028124, -0.001078, -0.020467), ))
# region = regionToolset.Region(cells=cells)
# p.SectionAssignment(region=region, sectionName='Epo_sec', offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
# print('Assembly done!')

# # Seeding and meshing:
# c = p.cells
# pickedRegions = c.findAt(((0.028124, 0.000169, -0.024209), ), ((0.028124, 0.001017, -0.017924), ), ((0.039915, -0.001015, -0.050124), ), ((0.033631, 0.000249, -0.050124), ),
#                          ((0.042031, -0.001216, -0.050124), ), ((0.058763, 0.000249, -0.050124), ), ((0.065048, -0.001015, -0.050124), ), ((0.028124, 0.001017, -0.043057), ),
#                          ((0.028124, 0.001264, -0.036509), ), ((0.028124, 0.000169, -0.049342), ), ((0.028124, -0.001078, -0.020467), ), ((0.028124, -0.000167, -0.030499), ),
#                          ((0.052493, -0.00025, -0.050124), ))
# p.setMeshControls(regions=pickedRegions, elemShape=TET, technique=FREE)
# elemType1 = mesh.ElemType(elemCode=C3D20R)
# elemType2 = mesh.ElemType(elemCode=C3D15)
# elemType3 = mesh.ElemType(elemCode=C3D10)
# pickedRegions = (cells, )
# p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2, elemType3))
# p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
# p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# # Set Assignment:
# f = p.faces
# faces = f.findAt(((0.018699, 7.4e-05, 0.036779), ), ((0.018699, -7.4e-05, 0.038619), ), ((0.018699, -7.4e-05, 0.026053), ), ((0.018699, -7.4e-05, 0.051186), ),
#                  ((0.018699, 7.4e-05, 0.024213), ), ((0.018699, 7.4e-05, 0.049345), ), ((0.018699, 0.001106, 0.047969), ))
# p.Set(faces=faces, name='XBack')
# f = p.faces
# faces = f.findAt(((0.056699, -7.4e-05, 0.036785), ), ((0.056699, 7.4e-05, 0.038613), ), ((0.056699, 7.4e-05, 0.026047), ), ((0.056699, 7.4e-05, 0.051179), ),
#                  ((0.056699, -7.4e-05, 0.024219), ), ((0.056699, -7.4e-05, 0.049351), ), ((0.056699, 0.001145, 0.025208), ))
# p.Set(faces=faces, name='XFront')
# f = p.faces
# faces = f.findAt(((0.036785, 7.4e-05, 0.056699), ), ((0.038613, -7.4e-05, 0.056699), ), ((0.026047, -7.4e-05, 0.056699), ), ((0.051179, -7.4e-05, 0.056699), ),
#                  ((0.024219, 7.4e-05, 0.056699), ), ((0.049351, 7.4e-05, 0.056699), ), ((0.050191, 0.001145, 0.056699), ))
# p.Set(faces=faces, name='ZFront')
# f = p.faces
# faces = f.findAt(((0.036779, -7.4e-05, 0.018699), ), ((0.038619, 7.4e-05, 0.018699), ), ((0.026053, 7.4e-05, 0.018699), ), ((0.051186, 7.4e-05, 0.018699), ),
#                  ((0.024213, -7.4e-05, 0.018699), ), ((0.049345, -7.4e-05, 0.018699), ), ((0.027429, 0.001106, 0.018699), ))
# p.Set(faces=faces, name='ZBack')
# f = p.faces
# faces = f.findAt(((0.031366, 0.002, 0.044032), ))
# p.Set(faces=faces, name='YTop')
# f = p.faces
# faces = f.findAt(((0.044032, -0.002, 0.044032), ))
# p.Set(faces=faces, name='YBottom')
# a.regenerate()

# # Refrence point:
# a.ReferencePoint(point=(0.056699, -0.002, 0.056699))
# r1 = a.referencePoints
# refPoints1 = (r1[60], )
# a.Set(referencePoints=refPoints1, name='RP')
# regionDef = mdb.models['Model-1'].rootAssembly.sets['RP']

# # History output:
# mdb.models['Model-1'].HistoryOutputRequest(name='RPHistory', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3', 'U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE)
# mdb.models['Model-1'].Equation(name='ConstraintEqn', terms=((1.0, 'Composite-1.XFront', 1), (-1.0, 'RP', 1)))

# # Boundary conditions:
# region = a.instances['Composite-1'].sets['XBack']
# mdb.models['Model-1'].DisplacementBC(name='XBackSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
# region = a.instances['Composite-1'].sets['ZBack']
# mdb.models['Model-1'].DisplacementBC(name='ZBackSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
# region = a.instances['Composite-1'].sets['YBottom']
# mdb.models['Model-1'].DisplacementBC(name='YBaseSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)

# # Loads:
# region = a.sets['RP']
# mdb.models['Model-1'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=15.0, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)


# Job creation:
mdb.Job(name='Job-1', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['Job-1'].submit(consistencyChecking=OFF)
# print('Job submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
