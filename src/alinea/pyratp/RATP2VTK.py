from openalea.plantgl import *
import numpy as np

def RATP2VTK(scene, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
    '''    Display leaves colored by voxel values with Paraview
           Scene is written in VTK Format as an unstructured grid
           Inputs: ... a RATP variable = liste de float
                   ... a scene plant GL composed of triangulated leaves
           Outputs: ... a VTK file
            T = all.Tesselator()
            sce[0].apply(T)
            T.result
    '''

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
              VertexCoords.append([vertex[0],vertex[1],vertex[2]])

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

def RATPVOXELS2VTK(grid, variable,varname="Variable",nomfich="C:\tmpRATP\RATPOUT.vtk"):
    '''    Display Voxels colored by variable with Paraview
           RATP Grid is written in VTK Format as a structured grid
           Inputs: ... a RATP variable = liste de float
                   ... a RATP grid
           Outputs: ... a VTK file
    '''

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
    f.write('DATASET RECTILINEAR_GRID\n')
    f.write('DIMENSIONS '+str(grid.njx+1)+' '+str(grid.njy+1)+' '+str(grid.njz+1)+'\n')

    f.write('Z_COORDINATES '+str(grid.njz+1)+' float\n')

    for i in  range(grid.njz-1,-1,-1):
       z = -100*grid.dz[i]*(i)#MARC +100*grid.zorig
##
       f.write(str(z)+' ')
    f.write(str(z)+' ')#MARC +100*grid.zorig)+' ')
##    f.write(str(0.0)+' ')

    f.write('\n')

    f.write('Y_COORDINATES '+str(grid.njy+1)+' float\n')
    for i in range(grid.njy+1):
       y = 100*grid.dy*i
##       +100*grid.yorig
       f.write(str(y)+' ')
    f.write('\n')


    f.write('X_COORDINATES '+str(grid.njx+1)+' float\n')
    for i in  range(grid.njx+1):
       x = 100*grid.dx*i
##       +100*grid.xorig
       f.write(str(x)+' ')
    f.write('\n')
    # Write data for each voxels
    numVoxels = (grid.njx)*(grid.njy)*(grid.njz)

    f.write('CELL_DATA '+str(numVoxels)+'\n')

    f.write('SCALARS '+varname+' float 1 \n')
    f.write('LOOKUP_TABLE default\n')
    #For a non vegetative voxel set to the voxel value to the default value
    #DefaultValue = 0.0
    #Utiliser grid.kxyz
    for ik in range(grid.njz):
      for ij in range(grid.njy):
        for ii in range(grid.njx):
          k =grid.kxyz[ii,ij,ik]-1 #Get the voxel id number
          if (k>=0):              #If the voxel k gets some vegetation then
           #print k
           f.write(str(variable[k])+'\n')
          else:
           f.write(str(0.0)+'\n')
#          f.write(str(ik)+'\n')


    f.write('\n')

    f.close()
