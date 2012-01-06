from openalea.plantgl import scenegraph as sg
from openalea.plantgl.scenegraph._pglsg import Color3

def Plot3DRATP(scene1, color):
    '''    
      Change material of scene1 elements according to RATP output (i.e. color)
      color = liste de tuple !
      scene1  = scene1 plant GL
      update each  shape appearance attribute  with a new material object for changing colors !
      
    '''
    
    # write the node code here.              
    for k,i in enumerate(scene1):
      mat = sg.Material(name=str(k),ambient=Color3(color[k]*255,color[k]*255,color[k]*255),diffuse=1.02,) 
     #mat = sg.Material(name=str(k),ambient=Color3(color[k][0],color[k][1],color[k][2]),diffuse=1.02,)                       # Create a new material   
      i.appearance =  mat       # set material to the shape
     
    return scene1,