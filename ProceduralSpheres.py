import bpy
import random
from os import remove as rm, makedirs
from os.path import exists
from PIL.Image import open, BICUBIC

import importlib

import FilePaths
import Helpers
import UserInput
import GetTexture

importlib.reload(FilePaths)
importlib.reload(Helpers)
importlib.reload(UserInput)
importlib.reload(GetTexture)

def OutputTexture(tree, ObjectName, SubFolder):
    for Obj in Scene.objects:
        Obj.select_set(False)
    
    FilePath = Helpers.BakeTexture(name, tree, Scene.objects[ObjectName], 1024 * 2)
    
    AABakePic = open(FilePath).resize((1024, 1024), resample=BICUBIC)
    
    SavePath = Paths["TEXTURE"] + SubFolder + "\\"
    
    if (not exists(SavePath)):
        makedirs(SavePath)
    
    AABakePic.save(SavePath + name + ".png")
    rm(FilePath)

Paths = FilePaths.GetPaths()

Scene = Helpers.GetScene("SCENE")
PlaneScene = Helpers.GetScene("PLANE")


(UseFilter, OutputSphereTextures, OutputBGTextures) = UserInput.StartupInput()

while True:
#for i in range(1):
    
    name = ""
    for i in range(50):
        name += str(random.randint(0, 9))
    
    mat = bpy.data.materials.new(name = name)
    mat.use_nodes = True
    
    (tree, addNode, link, unlink, delNode) = Helpers.MatShortcuts(mat)
    
    
    out = tree.nodes["Material Output"]

    bpy.data.objects["Sphere"].active_material = mat

    tree.nodes.remove(tree.nodes["Principled BSDF"])

    out.location = (0, 0)

    ##########################################################################

    FullStart = addNode("ShaderNodeGroup")
    FullStart.node_tree = bpy.data.node_groups["FullStart"]
    FullStart.location = (-1000, 0)

    InvertUtility = addNode("ShaderNodeGroup")
    InvertUtility.node_tree = bpy.data.node_groups["InvertUtility"]
    InvertUtility.location = (-400, -75)
    
    MakeShader = addNode("ShaderNodeGroup")
    MakeShader.node_tree = bpy.data.node_groups["MakeShader"]
    MakeShader.location = (-200, 0)

    ##########################################################################

    ColorRamp = Helpers.MakeColorRamp(addNode)
    ColorRamp.location = (-830, 150)
    
    if (random.random() < 0.1):
        ColorWonk = addNode("ShaderNodeTexVoronoi")
        Helpers.SetVal(ColorWonk, 2, random.random() * 200 - 100)
        ColorWonk.location = (-550, 150)
        link(ColorRamp.outputs[0], ColorWonk.inputs[0])
        link(ColorWonk.outputs[1], InvertUtility.inputs[1])
    else:
        link(ColorRamp.outputs[0], InvertUtility.inputs[1])

    ##########################################################################
    
    (TexGroup, InvertRotate) = GetTexture.TextureCreator(UseFilter, name, mat, InvertUtility)
    
    ############################################################################
                
    link(TexGroup.outputs[0], InvertUtility.inputs[0])
    link(InvertUtility.outputs[0], MakeShader.inputs[1])
    link(MakeShader.outputs[0], out.inputs[0])
    link(FullStart.outputs[0], MakeShader.inputs[0])
    link(FullStart.outputs[0], ColorRamp.inputs[0])
    
    ##########################################################################

    Helpers.SetVal(MakeShader.node_tree.nodes["LightImpact"], 0, random.random() ** (1/2))
    Helpers.SetVal(MakeShader.node_tree.nodes["Diffuse BSDF"], 1, random.random())
    Helpers.SetVal(MakeShader.node_tree.nodes["Math.007"], 1, random.random() * 0.5 + 0.5)

    ##########################################################################

    Starting = bpy.data.node_groups["Starting"]
    Starting.nodes["Value"].outputs[0].default_value = random.random() * 0.2 - 0.1
    
    ##########################################################################
    
    InitNoise = Starting.nodes["Noise Texture"]
    Helpers.SetVal(InitNoise, 2, random.random() * 20 + 1)
    Helpers.SetVal(InitNoise, 3, random.random() * 5 + 7.5)
    Helpers.SetVal(InitNoise, 4, random.random() * 2 - 1)

    ##########################################################################

    Helpers.RandomRot(Starting.nodes["Vector Rotate"])

    Helpers.SetVal(InvertUtility.node_tree.nodes["HueShift"], 0, random.random()    / 2 + 0.75)

    Scene.objects["Spotlight"].data.color = Helpers.GetColor(4, 0.25)[:3]
    Scene.objects["Pointlight"].data.color = Helpers.GetColor(4, 0.25)[:3]

    ##########################################################################

    BGShader = bpy.data.materials.new(name = "BG" + name)
    BGShader.use_nodes = True
    bpy.data.objects["BG"].active_material = BGShader
    
    (BGTree, BGAddNode, BGLink, BGUnlink, BGDelNode) = Helpers.MatShortcuts(BGShader)

    BGPrincipled = BGTree.nodes["Principled BSDF"]
    BGPrincipled.location = (800, 200)
    Helpers.SetVal(BGPrincipled, 0, Helpers.GetColor(2, 0.25))
    for Param in range(4, 19, 1):
        Helpers.SetVal(BGPrincipled, Param, 0)
    
    BGOut = BGTree.nodes["Material Output"]
    BGOut.location = (1200, 200)
    
    BGSwirl = BGAddNode("ShaderNodeGroup")
    BGSwirl.node_tree = bpy.data.node_groups["BGSwirl"]
    BGSwirl.location = (800, 400)

    BGMap = BGAddNode("ShaderNodeGroup")
    BGMap.node_tree = bpy.data.node_groups["BGMap"]
    BGMap.location = (600, 400)
    
    SwirlMap = BGMap.node_tree.nodes["Mapping"]
    SwirlScale = random.random() ** 4 + 0.1
    
    BGLink(BGPrincipled.outputs[0], BGOut.inputs[0])
    BGLink(BGPrincipled.outputs[0], BGSwirl.inputs[0])
    BGLink(BGMap.outputs[0], BGSwirl.inputs[1])

    ##########################################################################    

    if (random.random() < 0.1):
        Swirls = True
        for l in BGOut.inputs[0].links:
            BGUnlink(l)
        BGLink(BGSwirl.outputs[0], BGOut.inputs[0])
        for axis in range(3):
            SwirlMap.inputs[1].default_value[axis] = random.random() * 1000
            SwirlMap.inputs[2].default_value[axis] = random.random() * 10
            
            if axis == 0:
                SwirlMap.inputs[3].default_value[axis] = SwirlScale * 4
            else:
                SwirlMap.inputs[3].default_value[axis] = SwirlScale
                
        Helpers.SetVal(BGPrincipled, 6, 0.4)
    else:
        Swirls = False
        for l in BGOut.inputs[0].links:
           BGUnlink(l)
        BGLink(BGPrincipled.outputs[0], BGOut.inputs[0])
        Helpers.SetVal(BGPrincipled, 6, 0)
        
    if (random.random() < 0.1):
        Wonk = True
        BGMathUtil = BGAddNode("ShaderNodeGroup")
        BGMathUtil.node_tree = bpy.data.node_groups["MathUtility"]
        BGMathUtil.location = (200, 200)
        BGTexGroup = GetTexture.TextureCreator(UseFilter, "BG" + name, BGShader, BGMathUtil, False)
        BGTexGroup.location = (0, 200)
        BGColorRamp = Helpers.MakeColorRamp(BGAddNode)
        BGColorRamp.color_ramp.hue_interpolation = "FAR"
        BGColorRamp.location = (400, 300)
        (BGTex, BGTexMaxOutput) = GetTexture.GetTexture(3, 5, BGAddNode)
        BGMultiply = BGAddNode("ShaderNodeMath")
        BGMultiply.operation = "MULTIPLY"
        BGMultiply.location = (200, 0)
        BGLink(BGMathUtil.outputs[0], BGMultiply.inputs[0])
        BGLink(BGTex.outputs[random.randint(0, BGTexMaxOutput)], BGMultiply.inputs[1])
        BGLink(BGMap.outputs[0], BGTexGroup.inputs[0])
        BGLink(BGTexGroup.outputs[0], BGMathUtil.inputs[0])
        BGLink(BGMultiply.outputs[0], BGColorRamp.inputs[0])
        
        Helpers.SetVal(MakeShader.node_tree.nodes["Math.007"], 1, random.random() + 1)
                
        if (Swirls):
            for l in BGSwirl.inputs[0].links:
                BGUnlink(l)
            BGLink(BGColorRamp.outputs[0], BGSwirl.inputs[0])
        else:
            for l in BGOut.inputs[0].links:
                BGUnlink(l)
            BGLink(BGColorRamp.outputs[0], BGOut.inputs[0])
    else:
        Wonk = False
    
    ##########################################################################
    
    Scene.render.filepath = Paths["SPHERE"] + name + ".png"
    bpy.ops.render.render(write_still=True)
    
    ##########################################################################
    
    if (OutputSphereTextures):
        Helpers.SetVal(MakeShader.node_tree.nodes["LightImpact"], 0, 0)
        Helpers.SetVal(MakeShader.node_tree.nodes["Math.007"], 1, 0.8)
        OutputTexture(tree, "Sphere", "Spheres")
    if (OutputBGTextures and Wonk):
        OutputTexture(BGTree, "BG", "Wonky Backgrounds")