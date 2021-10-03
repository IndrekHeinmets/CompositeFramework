from abaqus import *
from abaqusConstants import *
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

# Beam:
b_len = 10

# Material:
mat_name = 'Steel'
YsM = 210000000000.0
PsR = 0.33

# Cross-sections:
cs1_name = 'Box'
cs1_a = 0.1
cs1_b = 0.2
cs1_t = 0.02

cs2_name = 'Pipe'
cs2_r = 0.1
cs2_t = 0.02

cs3_name = 'I-beam'
cs3_h = 0.2
cs3_l = 0.1
cs3_b = 0.1
cs3_t = 0.02

currently_used = 'Pipe'

# Supports:
s1_name = 'LeftPinSupport'
s1_x = 0.0
s1_y = 0.0
s1_z = UNSET

s2_name = 'RightPinSupport'
s2_x = 0.0
s2_y = 0.0
s2_z = UNSET

# Loads:
l1_name = 'PointLoad'
l1_y = -6000

l2_name = 'DistLoad'
l2_y = -200

# Mesh seed factor:
mseed = 0.05

s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=int((2 * b_len) + 6))
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
s.Line(point1=(0.0, 0.0), point2=(b_len, 0.0))
s.HorizontalConstraint(entity=g[2], addUndoState=False)
p = mdb.models['Model-1'].Part(name='Beam', dimensionality=TWO_D_PLANAR, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Beam']
p.BaseWire(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Beam']
mdb.models['Model-1'].Material(name=mat_name)
mdb.models['Model-1'].materials[mat_name].Elastic(table=((YsM, PsR), ))
mdb.models['Model-1'].BoxProfile(name=cs1_name, b=cs1_b, a=cs1_a, uniformThickness=ON, t1=cs1_t)
mdb.models['Model-1'].PipeProfile(name=cs2_name, r=cs2_r, t=cs2_t)
mdb.models['Model-1'].IProfile(name=cs3_name, l=cs3_l, h=cs3_h, b1=cs3_b, b2=cs3_b, t1=cs3_t, t2=cs3_t, t3=cs3_t)
mdb.models['Model-1'].BeamSection(name=cs1_name, integration=DURING_ANALYSIS, poissonRatio=0.0, profile=cs1_name, material=mat_name, temperatureVar=LINEAR, consistentMassMatrix=False)
mdb.models['Model-1'].BeamSection(name=cs2_name, integration=DURING_ANALYSIS, poissonRatio=0.0, profile=cs2_name, material=mat_name, temperatureVar=LINEAR, consistentMassMatrix=False)
mdb.models['Model-1'].BeamSection(name=cs3_name, integration=DURING_ANALYSIS, poissonRatio=0.0, profile=cs3_name, material=mat_name, temperatureVar=LINEAR, consistentMassMatrix=False)
p = mdb.models['Model-1'].parts['Beam']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
p = mdb.models['Model-1'].parts['Beam']
p.assignBeamSectionOrientation(region=region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))
p.SectionAssignment(region=region, sectionName=currently_used, offset=0.0, offsetType=MIDDLE_SURFACE, offsetField='', thicknessAssignment=FROM_SECTION)
p = mdb.models['Model-1'].parts['Beam']
v1, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
p.ReferencePoint(point=p.InterestingPoint(edge=e[0], rule=MIDDLE))
p = mdb.models['Model-1'].parts['Beam']
p.seedPart(size=mseed, deviationFactor=0.1, minSizeFactor=0.1)
p = mdb.models['Model-1'].parts['Beam']
p.generateMesh()
p = mdb.models['Model-1'].parts['Beam']
n = p.nodes
nodes = n.getSequenceFromMask(mask=('[#0:9 #1000 ]', ), )
p.Set(nodes=nodes, name='cpSet')
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Beam']
a.Instance(name='Beam-1', part=p, dependent=ON)
mdb.models['Model-1'].StaticStep(name='bendingLoad', previous='Initial')
a = mdb.models['Model-1'].rootAssembly
v1 = a.instances['Beam-1'].vertices
verts1 = v1.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(vertices=verts1)
mdb.models['Model-1'].DisplacementBC(name=s1_name, createStepName='bendingLoad', region=region, u1=s1_x, u2=s1_y, ur3=s1_z, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
v1 = a.instances['Beam-1'].vertices
verts1 = v1.getSequenceFromMask(mask=('[#2 ]', ), )
region = regionToolset.Region(vertices=verts1)
mdb.models['Model-1'].DisplacementBC(name=s2_name, createStepName='bendingLoad', region=region, u1=s2_x, u2=s2_y, ur3=s2_z, amplitude=UNSET, fixed=OFF, distributionType=UNIFORM, fieldName='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
region = a.instances['Beam-1'].sets['cpSet']
mdb.models['Model-1'].ConcentratedForce(name=l1_name, createStepName='bendingLoad', region=region, cf2=l1_y, distributionType=UNIFORM, field='', localCsys=None)
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Beam-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges1)
mdb.models['Model-1'].LineLoad(name=l2_name, createStepName='bendingLoad', region=region, comp2=l2_y)
mdb.Job(name='BendingAnalysis', model='Model-1', description='', type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', scratch='', resultsFormat=ODB)
p = mdb.models['Model-1'].parts['Beam']
e = p.edges
edges = e.getSequenceFromMask(mask=('[#1 ]', ), )
region = regionToolset.Region(edges=edges)
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
mdb.jobs['BendingAnalysis'].submit(consistencyChecking=OFF)
