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

# Overlap:
overlap_len = period

# Ellipse cs:
e_width = 4.5
e_height = 1.2

# Resin block:
b_width = (pi_len * pi) * 2
b_height = 4.0

# RVE block:
RVE_size = 38.0

# Matrix props:
m_name = 'Epoxy Resin'
m_E = 3.8e9
m_P = 0.35
m_Ys = 55e6
m_Ps = 0.0

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
xzl_disp = RVE_size * strain
yl_disp = b_height * strain

# Mesh density:
md = 2.0

# History output time intervals:
hi = 20
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
s1.EllipseByCenterPerimeter(center=(0.0, 0.0), axisPoint1=(0.0, (e_width / (2 * sc))), axisPoint2=((e_height / (2 * sc)), 0.0))
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
mdb.models['Model-1'].materials[m_name].Elastic(table=((m_E, m_P), ))
mdb.models['Model-1'].materials[m_name].Plastic(scaleStress=None, table=((m_Ys, m_Ps), ))
mdb.models['Model-1'].Material(name=f_name)
mdb.models['Model-1'].materials[f_name].Elastic(type=ENGINEERING_CONSTANTS, table=((f_E1, f_E2, f_E3, f_P12, f_P13, f_P23, f_G12, f_G13, f_G23), ))

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
a.rotate(instanceList=('CfWeave-2', 'CfWeave-4'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(180.0, 0.0, 0.0), angle=180.0)
a.rotate(instanceList=('CfWeave-3', 'CfWeave-4'), axisPoint=(0.0, 0.0, 0.0), axisDirection=(0.0, -90.0, 0.0), angle=90.0)
a.translate(instanceList=('CfWeave-2', ), vector=(0.0, 0.0, (period * 2)))
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2'), direction1=(0.0, 0.0, 1.0), direction2=(0.0, 1.0, 0.0), number1=3, number2=1, spacing1=(period * 4), spacing2=1)
a.LinearInstancePattern(instanceList=('CfWeave-1', 'CfWeave-2', 'CfWeave-1-lin-2-1', 'CfWeave-1-lin-3-1', 'CfWeave-2-lin-2-1', 'CfWeave-2-lin-3-1'), direction1=(0.0, 0.0, 1.0), direction2=(1.0, 0.0, 0.0), number1=2, number2=1, spacing1=period, spacing2=1)
a.translate(instanceList=('CfWeave-1-lin-2-1-1', 'CfWeave-2-lin-2-1-1', 'CfWeave-1-lin-2-1-lin-2-1', 'CfWeave-2-lin-2-1-lin-2-1', 'CfWeave-1-lin-3-1-lin-2-1', 'CfWeave-2-lin-3-1-lin-2-1'), vector=(period, 0.0, 0.0))
a.translate(instanceList=('CfWeave-3', 'CfWeave-4'), vector=((period * 1.5), 0.0, -(period / 2)))
a.translate(instanceList=('CfWeave-3', ), vector=((period * 2), 0.0, 0.0))
a.LinearInstancePattern(instanceList=('CfWeave-3', 'CfWeave-4'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=3, number2=1, spacing1=(period * 4), spacing2=1)
a.LinearInstancePattern(instanceList=('CfWeave-4', 'CfWeave-3', 'CfWeave-4-lin-2-1', 'CfWeave-3-lin-2-1', 'CfWeave-4-lin-3-1'), direction1=(1.0, 0.0, 0.0), direction2=(0.0, 1.0, 0.0), number1=2, number2=1, spacing1=period, spacing2=1)
a.translate(instanceList=('CfWeave-4-lin-2-1-1', 'CfWeave-3-lin-2-1-1', 'CfWeave-4-lin-2-1-lin-2-1', 'CfWeave-3-lin-2-1-lin-2-1', 'CfWeave-4-lin-3-1-lin-2-1', 'CfWeave-3-lin-3-1-lin-2-1'), vector=(0.0, 0.0, period))
a.translate(instanceList=('ResinBlock-1', ), vector=(0.0, -(b_height / (2 * sc)), 0.0))

# Merge into composite & delete original parts:
a.InstanceFromBooleanMerge(name='Composite', instances=(a.instances['CfWeave-1'], a.instances['CfWeave-2'], a.instances['CfWeave-3'], a.instances['CfWeave-4'], a.instances['ResinBlock-1'], a.instances['CfWeave-1-lin-2-1'],
                                                        a.instances['CfWeave-1-lin-3-1'], a.instances['CfWeave-2-lin-2-1'], a.instances['CfWeave-2-lin-3-1'], a.instances['CfWeave-1-lin-2-1-1'], a.instances['CfWeave-2-lin-2-1-1'],
                                                        a.instances['CfWeave-1-lin-2-1-lin-2-1'], a.instances['CfWeave-1-lin-3-1-lin-2-1'], a.instances['CfWeave-2-lin-2-1-lin-2-1'], a.instances['CfWeave-2-lin-3-1-lin-2-1'],
                                                        a.instances['CfWeave-3-lin-2-1'], a.instances['CfWeave-3-lin-3-1'], a.instances['CfWeave-4-lin-2-1'], a.instances['CfWeave-4-lin-3-1'], a.instances['CfWeave-4-lin-2-1-1'],
                                                        a.instances['CfWeave-3-lin-2-1-1'], a.instances['CfWeave-4-lin-2-1-lin-2-1'], a.instances['CfWeave-3-lin-2-1-lin-2-1'], a.instances['CfWeave-4-lin-3-1-lin-2-1'], ), keepIntersections=ON, originalInstances=DELETE, domain=GEOMETRY)
del mdb.models['Model-1'].parts['CfWeave']
del mdb.models['Model-1'].parts['ResinBlock']
p = mdb.models['Model-1'].parts['Composite']

# Composite specimen creation:
f, e = p.faces, p.edges
t = p.MakeSketchTransform(sketchPlane=f.findAt(coordinates=(25.132741, 2.0, 50.265483)), sketchUpEdge=e.findAt(coordinates=(0.0, 2.0, 18.849556)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, origin=(37.699112, 2.0, 37.699112))
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=1, gridSpacing=0.002, transform=t)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=SUPERIMPOSE)
p.projectReferencesOntoSketch(sketch=s, filter=COPLANAR_EDGES)
s.rectangle(point1=((19.0 / sc), (16.0 / sc)), point2=(-(19.0 / sc), -(22.0 / sc)))
s.rectangle(point1=(-(60.0 / sc), -(60.0 / sc)), point2=((60.0 / sc), (60.0 / sc)))
f1, e1 = p.faces, p.edges
p.CutExtrude(sketchPlane=f1.findAt(coordinates=(25.132741, 2.0, 50.265483)), sketchUpEdge=e1.findAt(coordinates=(0.0, 2.0, 18.849556)), sketchPlaneSide=SIDE1, sketchOrientation=RIGHT, sketch=s, flipExtrudeDirection=OFF)
s.unsetPrimaryObject()
del mdb.models['Model-1'].sketches['__profile__']

# Cell assignment:
fibreCells1 = p.cells.findAt(((26.03186, 0.30689, 53.699112), ), ((43.083179, -0.30689, 53.699112), ), ((51.1646, 0.30689, 53.699112), ), ((44.881171, 0.999939, 53.699112), ),
                             ((36.800237, -0.999939, 53.699112), ), ((19.748429, 0.999939, 53.699112), ))
fibreCells2 = p.cells.findAt(((56.699112, 0.999937, 27.375461), ), ((56.699112, 0.999937, 52.508203), ), ((56.699112, -0.999937, 35.456393), ), ((56.699112, -0.23891, 16.605395), ),
                             ((56.699112, 0.23891, 33.660088), ), ((56.699112, -0.23891, 41.738136), ))
matrixCells = p.cells.findAt(((20.363473, -1.674724, 15.699112), ))

# Fibre orientation assignment:
v1 = p.vertices
p.DatumCsysByThreePoints(origin=v1.findAt(coordinates=(56.699112, -2.0, 53.699112)), point1=v1.findAt(coordinates=(56.699112, -2.0, 15.699112)), point2=v1.findAt(coordinates=(56.699112, 2.0, 15.699112)), name='Datum csys-1', coordSysType=CARTESIAN)
v2 = p.vertices
p.DatumCsysByThreePoints(origin=v2.findAt(coordinates=(56.699112, -2.0, 53.699112)), point1=v2.findAt(coordinates=(18.699112, -2.0, 53.699112)), point2=v2.findAt(coordinates=(18.699112, 2.0, 53.699112)), name='Datum csys-2', coordSysType=CARTESIAN)
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
p.setElementType(regions=((fibreCells1 + fibreCells2 + matrixCells), ), elemTypes=(elemType1, elemType2, elemType3))
p.seedPart(size=(md / sc), deviationFactor=0.1, minSizeFactor=0.1)
p.generateMesh()
print('Meshing done!')

# Static analysis step:
mdb.models['Model-1'].StaticStep(name='StaticAnalysis', previous='Initial')

# Set Assignment:
f = p.faces
faces = f.findAt(((18.699112, -0.999944, 27.375461), ), ((18.699112, -0.999944, 52.508203), ), ((18.699112, 0.999944, 35.456393), ), ((18.699112, -0.034353, 16.607429), ),
                 ((18.699112, 0.034353, 33.658053), ), ((18.699112, -0.034353, 41.740171), ), ((18.699112, -1.674722, 51.940355), ))
p.Set(faces=faces, name='XBack')
faces = f.findAt(((56.699112, 0.999937, 27.375461), ), ((56.699112, 0.999937, 52.508203), ), ((56.699112, -0.999937, 35.456393), ), ((56.699112, -0.23891, 16.605395), ),
                 ((56.699112, 0.23891, 33.660088), ), ((56.699112, -0.23891, 41.738136), ), ((56.699112, -0.725175, 34.742879), ))
p.Set(faces=faces, name='XFront')
faces = f.findAt(((19.748429, -0.999946, 15.699112), ), ((44.881171, -0.999946, 15.699112), ), ((36.800237, 0.999946, 15.699112), ), ((26.032214, -0.036432, 15.699112), ),
                 ((43.082826, 0.036432, 15.699112), ), ((51.164954, -0.036432, 15.699112), ), ((20.363473, -1.674724, 15.699112), ))
p.Set(faces=faces, name='ZBack')
faces = f.findAt(((19.748429, 0.999939, 53.699112), ), ((44.881171, 0.999939, 53.699112), ), ((36.800237, -0.999939, 53.699112), ), ((26.03186, 0.30689, 53.699112), ),
                 ((43.083179, -0.30689, 53.699112), ), ((51.1646, 0.30689, 53.699112), ), ((38.002761, -0.567258, 53.699112), ))
p.Set(faces=faces, name='ZFront')
faces = f.findAt(((31.365779, 2.0, 41.032445), ))
p.Set(faces=faces, name='YTop')
faces = f.findAt(((31.365779, -2.0, 28.365779), ))
p.Set(faces=faces, name='YBottom')

# Refrence point and history output:
a.ReferencePoint(point=(60.0, -2.0, 60.0))
refPoints1 = (a.referencePoints[52], )
a.Set(referencePoints=refPoints1, name='RPSet')
v = a.instances['Composite-1'].vertices
verts = v.findAt(((56.699112, 2.0, 53.699112), ))
a.Set(vertices=verts, name='CornerNodeSet')

regionDef = mdb.models['Model-1'].rootAssembly.sets['RPSet']
mdb.models['Model-1'].HistoryOutputRequest(name='RPHO', createStepName='StaticAnalysis', variables=('RF1', 'RF2', 'RF3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, numIntervals=hi)
regionDef = mdb.models['Model-1'].rootAssembly.sets['CornerNodeSet']
mdb.models['Model-1'].HistoryOutputRequest(name='CornerNodeHO', createStepName='StaticAnalysis', variables=('U1', 'U2', 'U3'), region=regionDef, sectionPoints=DEFAULT, rebar=EXCLUDE, numIntervals=hi)

# XY Shear setup:
mdb.models.changeKey(fromName='Model-1', toName='XYShear')
mdb.Model(name='YZShear', objectToCopy=mdb.models['XYShear'])
mdb.Model(name='XZShear', objectToCopy=mdb.models['XYShear'])
a = mdb.models['XYShear'].rootAssembly
a.regenerate()
# Constraint equation:
mdb.models['XYShear'].Equation(name='ConstraintEqn', terms=((1.0, 'Composite-1.XFront', 2), (-1.0, 'RPSet', 2)))
# Boundary conditions:
region = a.instances['Composite-1'].sets['XBack']
mdb.models['XYShear'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['XFront']
mdb.models['XYShear'].DisplacementBC(name='XRoller', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['XYShear'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=yl_disp, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Z Tension setup:
mdb.Model(name='ZTension', objectToCopy=mdb.models['XYShear'])
a = mdb.models['ZTension'].rootAssembly
a.regenerate()
# Constraint equation:
mdb.models['ZTension'].constraints['ConstraintEqn'].setValues(terms=((1.0, 'Composite-1.ZFront', 3), (-1.0, 'RPSet', 3)))
# Boundary conditions:s
region = a.instances['Composite-1'].sets['XBack']
mdb.models['ZTension'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['ZBack']
mdb.models['ZTension'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['YBottom']
mdb.models['ZTension'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['ZTension'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=xzl_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['ZTension'].boundaryConditions['XRoller']
a.regenerate()

# Z Compression setup:
mdb.Model(name='ZCompression', objectToCopy=mdb.models['ZTension'])
a = mdb.models['ZCompression'].rootAssembly
a.regenerate()
# Boundary conditions:
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['ZCompression'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=UNSET, u3=-xzl_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# YZ Shear setup:
a = mdb.models['YZShear'].rootAssembly
a.regenerate()
# Constraint equation:
mdb.models['YZShear'].Equation(name='ConstraintEqn', terms=((1.0, 'Composite-1.YTop', 3), (-1.0, 'RPSet', 3)))
# Boundary conditions:
region = a.instances['Composite-1'].sets['YBottom']
mdb.models['YZShear'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['YTop']
mdb.models['YZShear'].DisplacementBC(name='YRoller', createStepName='Initial', region=region, u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['YZShear'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=SET, u3=xzl_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# X Tension setup:
mdb.Model(name='XTension', objectToCopy=mdb.models['YZShear'])
a = mdb.models['XTension'].rootAssembly
a.regenerate()
# Constraint equation:
mdb.models['XTension'].constraints['ConstraintEqn'].setValues(terms=((1.0, 'Composite-1.XFront', 1), (-1.0, 'RPSet', 1)))
# Boundary conditions:
region = a.instances['Composite-1'].sets['XBack']
mdb.models['XTension'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['ZBack']
mdb.models['XTension'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['YBottom']
mdb.models['XTension'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['XTension'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=xzl_disp, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['XTension'].boundaryConditions['YRoller']
a.regenerate()

# X Compression setup:
mdb.Model(name='XCompression', objectToCopy=mdb.models['XTension'])
a = mdb.models['XCompression'].rootAssembly
a.regenerate()
# Boundary conditions:
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['XCompression'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=-xzl_disp, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# XZ Shear setup:
a = mdb.models['XZShear'].rootAssembly
a.regenerate()
# Constraint equation:
mdb.models['XZShear'].Equation(name='ConstraintEqn', terms=((1.0, 'Composite-1.XFront', 3), (-1.0, 'RPSet', 3)))
# Boundary conditions:
region = a.instances['Composite-1'].sets['XBack']
mdb.models['XZShear'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=SET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['XFront']
mdb.models['XZShear'].DisplacementBC(name='XRoller', createStepName='Initial', region=region, u1=SET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['XZShear'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=SET, u2=SET, u3=xzl_disp, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()

# Y Tension setup:
mdb.Model(name='YTension', objectToCopy=mdb.models['XZShear'])
a = mdb.models['YTension'].rootAssembly
a.regenerate()
# Constraint equation:
mdb.models['YTension'].constraints['ConstraintEqn'].setValues(terms=((1.0, 'Composite-1.YTop', 2), (-1.0, 'RPSet', 2)))
# Boundary conditions:
region = a.instances['Composite-1'].sets['XBack']
mdb.models['YTension'].DisplacementBC(name='XSupport', createStepName='Initial', region=region, u1=SET, u2=UNSET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['ZBack']
mdb.models['YTension'].DisplacementBC(name='ZSupport', createStepName='Initial', region=region, u1=UNSET, u2=UNSET, u3=SET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = a.instances['Composite-1'].sets['YBottom']
mdb.models['YTension'].DisplacementBC(name='YSupport', createStepName='Initial', region=region, u1=UNSET, u2=SET, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, distributionType=UNIFORM, fieldName='', localCsys=None)
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['YTension'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=yl_disp, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
del mdb.models['YTension'].boundaryConditions['XRoller']
a.regenerate()

# Y Compression setup:
mdb.Model(name='YCompression', objectToCopy=mdb.models['YTension'])
a = mdb.models['YCompression'].rootAssembly
a.regenerate()
# Boundary conditions:
region = mdb.models['XYShear'].rootAssembly.sets['RPSet']
mdb.models['YCompression'].DisplacementBC(name='Load', createStepName='StaticAnalysis', region=region, u1=UNSET, u2=-yl_disp, u3=UNSET, ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a.regenerate()
print('Constraining and Loading done!')

# Job creation:
mdb.Job(name='ZTensionAnalysis', model='ZTension', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='ZCompressionAnalysis', model='ZCompression', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='XYShearAnalysis', model='XYShear', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='XTensionAnalysis', model='XTension', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='XCompressionAnalysis', model='XCompression', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='YZShearAnalysis', model='YZShear', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='YTensionAnalysis', model='YTension', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='YCompressionAnalysis', model='YCompression', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
mdb.Job(name='XZShearAnalysis', model='XZShear', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
# mdb.jobs['ZTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['ZCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['XYShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['XTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['XCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['YZShearAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['YTensionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['YCompressionAnalysis'].submit(consistencyChecking=OFF)
# mdb.jobs['XZShearAnalysis'].submit(consistencyChecking=OFF)
# print('Jobs submitted for processing!')

# End of script:
print('*************************')
print('End of script, no errors!')
