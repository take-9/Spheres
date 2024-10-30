import bpy
from mathutils import Color
from random import random, randint
import importlib


import FilePaths

importlib.reload(FilePaths)

def GetScene(Key):
    return {
    "SCENE": bpy.data.scenes["Scene"],
    "PLANE": bpy.data.scenes["Plane"]
    }[Key]

def MatShortcuts(mat):
    tree = mat.node_tree
    addNode = tree.nodes.new
    link = tree.links.new
    unlink = tree.links.remove
    delNode = tree.nodes.remove
    
    return (tree, addNode, link, unlink, delNode)

def SetVal(node, index, val):
    node.inputs[index].default_value = val

def GetColor(divisor, addend, val=1):
    NewColor = Color()
    NewColor.hsv = (random(), random() / divisor + addend, val)
    return (NewColor.r, NewColor.g, NewColor.b, 1.0)

def RandomRot(VectorRotate):
    for ParamSet in range(1, 3, 1):
        for Axis in range(3):
            VectorRotate.inputs[ParamSet].default_value[Axis] = random()
    VectorRotate.inputs[3].default_value = random() * 4
    
def MakeColorRamp(addNode):
    ColorRamp = addNode("ShaderNodeValToRGB")
    ColorRamp.color_ramp.color_mode = "HSV"
    if random() <= 0.25:
        ColorRamp.color_ramp.elements.new(0.5)
        MidStop = True
    else:
        MidStop = False
        
    for i, element in enumerate(ColorRamp.color_ramp.elements):
        if i != 0 or MidStop != True or random() > 0.1:
            val = 1
        else:
            val = 0 
        element.color = GetColor(5, 0.8, val)
        
    return ColorRamp
    
def BakeTexture(Name, Tree, Obj, Res):
    BakeNode = Tree.nodes.new("ShaderNodeTexImage")
    BakeNode.name = "BakeNode"
    Tree.nodes.active = BakeNode
    Obj.select_set(True)
    bpy.context.view_layer.objects.active = Obj
    BakePic = bpy.data.images.new(Name, Res, Res)
    BakeNode.image = BakePic
    bpy.ops.object.bake(type="EMIT", save_mode="EXTERNAL")
    FilePath = FilePaths.GetPaths()["TEMP"] + Name + ".png"
    BakePic.save_render(filepath=FilePath)
    Tree.nodes.remove(BakeNode)
    return FilePath