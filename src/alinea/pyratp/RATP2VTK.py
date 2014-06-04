from openalea.plantgl import *
import numpy as np

def RATP2VTK(scene, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
    '''    Paraview file
           variable = liste de float
           scene  = scene plant GL
            T = all.Tesselator()
            sce[0].apply(T)
            T.result


    '''
#    print 'len(scene)', len(scene)
#    print 'len(variable)', len(variable)
#    print "varname",varname
#    print 'variable', variable

    if len(variable)<len(scene):
      variable=np.zeros(len(scene))

    T = all.Tesselator()
    VertexCoords=[]
    TrianglesVertexIDs=[]
    triangleColor = []

    for k,i in enumerate(scene):
         i.apply(T) #Applique Tesselator
         TS = T.result
         for vertex in TS.pointList:
              VertexCoords.append([vertex[0],vertex[1],-vertex[2]])

         ShapeNumTri = len(TS.pointList) #nbr points dans  TriangleSet
         for tri in TS.indexList:
              TrianglesVertexIDs.append([tri[0]+k*ShapeNumTri,tri[1]+k*ShapeNumTri,tri[2]+k*ShapeNumTri])
              triangleColor.append(variable[k])

    numvertex = len(VertexCoords)
    numTriangles = len(TrianglesVertexIDs)
    # write the node code here.
        # Write the output file following VTK file format for 3D view with Paraview
        # Works only with triangles P1 i.e. defined with 3 points
        #... Input:
            #... Triangles - self attribute
            #... Variable to be plotted - var
            #... Corresponding variable name - varname
        #... Output:
            #... a VTK file - filename
    print nomfich
    f=open(nomfich,'w')
    # Set the header
    f.write('# vtk DataFile Version 3.0\n')
    f.write('vtk output\n')
    f.write('ASCII\n')
    f.write('DATASET UNSTRUCTURED_GRID\n')
    f.write('POINTS '+str(numvertex)+' float\n')

    # Write vertex coordinates
    for i in VertexCoords:
     f.write(str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
    f.write('\n')

    # Write elements connectivity
    f.write('CELLS '+str(numTriangles)+' '+str(numTriangles*4)+'\n')
    for i in  TrianglesVertexIDs:
     f.write('3 '+str(i[0])+' '+str(i[1])+' '+str(i[2])+'\n')
    f.write('\n')

    # Write elements type i.e. 5 for triangles
    f.write('CELL_TYPES '+str(numTriangles)+'\n')
    for i in  TrianglesVertexIDs:
        f.write('5\n')
    f.write('\n')

    # Write data for each triangle
    f.write('CELL_DATA '+str(numTriangles)+'\n')

    f.write('FIELD FieldData 1 \n');
    f.write(varname +' 1 '+str(numTriangles)+' float\n')
    for i in triangleColor:
          f.write(str(i).strip('[]')+'\n')

    f.write('\n')

    f.close()

    # return outputs
    return   triangleColor
