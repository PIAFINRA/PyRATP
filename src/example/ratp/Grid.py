
"""
   Presentation ALEA :  REA Decembre 2003
   **************************************
"""

from PlantGL import *

class Color(Material):
    def __init__(self,r,g,b ,
                 diffuse=1,
                 specular=Color3(40,40,40),
                 emission=Color3(0,0,0),
                 shininess=0,
                 transparency=0):
        Material.__init__(self,Color3(r,g,b),diffuse,specular,
                          emission,shininess, transparency)


def _rgb(mag, cmin, cmax):
       x = (mag-cmin)/(cmax-cmin)
       blue = min((max((4*(0.75-x), 0.)), 1.))
       red  = min((max((4*(x-0.25), 0.)), 1.))
       green= min((max((4*math.fabs(x-0.5)-1., 0.)), 1.))
       return Color( int(red*255), int(green*255), int(blue*255))


from amlPy import *

class Grid:
   
   def __init__(self,nx,ny,nz,lad_num,voxelCoords,kxyz,bb):
      self.nx=nx
      self.ny=ny
      self.nz=nz
      
      self.nb_filled = size(lad_num)

      self.voxelCoords = voxelCoords
      self.lad_num=lad_num
      self.kxyz=kxyz               
      self.bb=bb
      self.numx=voxelCoords[:,0]
      self.numy=voxelCoords[:,1]
      self.numz=voxelCoords[:,2]

   def getRepresentation(self,data_array, debug = False):
      """
      getRepresentation(data_array[nb_filled voxels]) -> return a scene

      Compute the representation of a grid scene with colors
      """
      scene= Scene()

      box= Translated(Vector3(.5,.5,.5),Box(Vector3(.5,.5,.5)))

      def voxel( v, color ):
         g= Translated(Vector3(v[0],v[1],v[2]),box)
         s= Shape(g,color)
         return s

      maxs = max(data_array)
      mins = min(data_array)
      dynamic = (mins,maxs)

      print dynamic
      
      # Plot all the voxels
      k= 0
      print "length = %d"%(len(self.voxelCoords))
      for pt in self.voxelCoords:
         color= self.color_array( pt, data_array,dynamic)
         s=voxel((pt[0], pt[1], self.nz-pt[2]),color)
         if s.geometry.isValid() and s.appearance.isValid():
         	scene.add(s)
         k=k+1
      return scene
      
   def color_array(self, pt, arr,dynamic):
      # print "pt = ", pt
      k = self.kxyz[pt-1]
      interval= dynamic[1]-dynamic[0]
      if k != 0 :
         # print "k-1", k-1
         s = arr[k-1]-dynamic[0]
      else:
         # print "k", k
         s=interval

      
      r = 255
      g = 255-int((s/interval)*250)

      b = 0
      #print 'dynamic',dynamic
      #print s
      #print "(r,g,b)= ", r,g,b
      return Color(r,g,b)


from numpy import *

def MSVoxel2Grid(mvs,grid_scale,divisionsteps):
   
   setmode(1)
   # shape(a1) = (214,3)
   a1 = Extract(mvs, Scale=grid_scale, GridData="FilledVoxelCoordinates")
   # shape(a2) = (214)
   a2 = Extract(mvs, Scale=grid_scale, GridData="InterceptedAreas")
   # shape(a3) = (214)
   a3 = Extract(mvs, Scale=grid_scale, GridData="FilledVoxelVolumes")
   
   # Plot(Histogram( [int(x/10) for x in a2]))
   # shape(leaf_area_density) = (214)
   leaf_area_density=map(lambda x,y: x/y,a2,a3)
   
   # Rustine
   k=0
   for v in leaf_area_density:
      if not v:
         del a1[k]
         del a2[k]
         del a3[k]
      else:
         k+=1
   
   leaf_area_density=map(lambda x,y: x/y,a2,a3)
   
   # Plot(Histogram( [int(x*100) for x in leaf_area_density]))
   bb = Extract(mvs, BoundingBox="Dimensions")
   
   
   # conversions to numpy objects
   njx = njy = njz = divisionsteps**grid_scale
   
   # shape(lad_num) = (214)
   lad_num = array(leaf_area_density)
   #   lad_num=array([.5]*214)
   fignum
   voxelCoords = array(a1)
   
   # shape(kxyz)=(9,9,10)
   kxyz= resize(array((0)),(njx,njy,njz+1))
   
   indexCoords= voxelCoords - 1 # change of origin for RATP
   k= 1
   for c in indexCoords:
      kxyz[c]= k
      k+=1
   
   # Numbering soil surface areas
   for jx in range(njx):
      for jy in range(njy):
         kxyz[jx,jy,njz]=njy*(jx)+jy
   
   grid= Grid(njx,njy,njz,lad_num,voxelCoords,kxyz,bb)
   return grid


