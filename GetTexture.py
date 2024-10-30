import bpy
from random import random, randint
from matplotlib.pyplot import imread
from os import remove as rm

import importlib

import Helpers
import FilePaths

importlib.reload(Helpers)
importlib.reload(FilePaths)

def GetTexture(min, max, AddNode):
    match randint(min, max):
        case 1:
            Texture = AddNode("ShaderNodeTexBrick")
            Helpers.SetVal(Texture, 2, (0, 0, 0, 1))
            Helpers.SetVal(Texture, 4,  (random() ** 3) * 97 + 3)
            Helpers.SetVal(Texture, 6, 0)
            Helpers.SetVal(Texture, 8, random() * 4 + 2)
            Helpers.SetVal(Texture, 9, random() * 2)
            MaxOutput = 0
        case 2:
            Texture = AddNode("ShaderNodeTexChecker")
            Helpers.SetVal(Texture, 2, (0, 0, 0, 1))
            Helpers.SetVal(Texture, 3, random() * 9 + 1)
            MaxOutput = 1
        case 3:
            Texture = AddNode("ShaderNodeTexMagic")
            Texture.turbulence_depth = randint(1, 10)
            Helpers.SetVal(Texture, 1, random() * 2 + 1)
            Helpers.SetVal(Texture, 2, 2 * random() - 1)
            MaxOutput = 1
        case 4:
            Texture = AddNode("ShaderNodeTexMusgrave")
            Helpers.SetVal(Texture, 2, random() * 15 + 5)
            Texture.musgrave_dimensions = str(randint(2, 3)) + "D"
            MaxOutput = 0
        case 5:
            Texture = AddNode("ShaderNodeTexNoise")
            Helpers.SetVal(Texture, 2, random() * 2 + 1)
            Helpers.SetVal(Texture, 4, random()/ 2 + 0.5)
            Helpers.SetVal(Texture, 5, random() * 8 - 4)
            MaxOutput = 1
        case 6:
            Texture = AddNode("ShaderNodeTexVoronoi")
            MaxOutput = 1
    return (Texture, MaxOutput)


def TextureCreator(UseFilter, name, Mat, Utility, IndependentTransform=True):
    
    Plane = bpy.data.objects["TestPlane"]
    PlaneMat = bpy.data.materials["Plane"]
    
    addNode = Mat.node_tree.nodes.new
    delNode = Mat.node_tree.nodes.remove
    
    BadTexture = True
    
    NewTexAttempts = 0
    
    while (NewTexAttempts <= 20 and BadTexture):
        
        AttemptName = name + str(NewTexAttempts)
        
        TexGroup = addNode("ShaderNodeGroup")
        TexGroup.node_tree = bpy.data.node_groups.new(AttemptName, "ShaderNodeTree")
        
        addTexNode = TexGroup.node_tree.nodes.new
        linkTex = TexGroup.node_tree.links.new
        
        TexGroup.location = (-600, -150)
        
        TexOutput = addTexNode("NodeGroupOutput")
        TexGroup.outputs.new("Texture", "Texture")
        
        TexX = -200
        Textures = []
        for t in range (randint(2, 4)):
            (Texture, MaxOutput) = GetTexture(1, 6, addTexNode)
            Textures.append(Texture)
            Textures[t].location = (TexX, -0)
            TexX -= 200
            if t == 0:
                linkTex(Textures[0].outputs[randint(0, MaxOutput)], TexOutput.inputs[0])
                
            else:
                linkTex(Textures[t].outputs[randint(0, MaxOutput)], Textures[t - 1].inputs[0])
        
        if (IndependentTransform):
            TextureCoordinate = addTexNode("ShaderNodeTexCoord")
            TextureCoordinate.location = (TexX - 200, 0)

            InvertRotate = addTexNode("ShaderNodeVectorRotate")
            Helpers.RandomRot(InvertRotate)
            InvertRotate.location = (TexX, 0)
            
        else:
            Input = addTexNode("NodeGroupInput")
            Input.location = (TexX - 200, 0)
            TexGroup.inputs.new("NodeSocketVector", "Transform")
            linkTex(Input.outputs[0], Textures[-1].inputs[0])

        Thresh = Utility.node_tree.nodes["Threshold"].inputs[1]
        Thresh.default_value = 0.0
        
        if(not UseFilter):
            break
    
        ############################################################################
        
        CurrentTexAttempts = 0
        BadTexture = True
        
        PlaneTexInstance = PlaneMat.node_tree.nodes.new("ShaderNodeGroup")
        PlaneTexInstance.node_tree = bpy.data.node_groups[AttemptName]
        PlaneUtil = PlaneMat.node_tree.nodes.new("ShaderNodeGroup")
        PlaneUtil.node_tree = Utility.node_tree
        PlaneUtil.location = (200, 0)
        PlaneMat.node_tree.links.new(PlaneTexInstance.outputs[0], PlaneUtil.inputs[0])
        PlaneMat.node_tree.links.new(PlaneUtil.outputs[1], PlaneMat.node_tree.nodes["Output"].inputs[0])
        PlaneNodes = PlaneMat.node_tree.nodes
        
        ThreshMod = 1.0
        
        bpy.context.window.scene = Helpers.GetScene("PLANE")
        
        while (CurrentTexAttempts <= 4 and BadTexture):
            ThreshMod /= 2
            
            FilePath = Helpers.BakeTexture("temp", PlaneMat.node_tree, Plane, 128)
            
            PixSum = 0
            Samples = 100
            for i in range(Samples):
                PixSum += imread(FilePath)[randint(0, 127)][randint(0, 127)]
                
            rm(FilePath)
            
            PixAvg = PixSum / Samples
            print("#############################")
            print("Average Value: " + str(PixAvg))
            
                
            if (0.2 <= PixAvg <= 0.8):
                BadTexture = False
            elif (PixAvg <= 0.2):
                Thresh.default_value += ThreshMod
                
                print("Change: +")
                print("New Threshold: " + str(Thresh.default_value))
                print("#############################")

            elif (PixAvg >= 0.8):
                Thresh.default_value -= ThreshMod
                
                print("Change: -")
                print("New Threshold: " + str(Thresh.default_value))
                print("#############################")
            
            CurrentTexAttempts += 1

        PlaneNodes.remove(PlaneTexInstance)
        PlaneNodes.remove(PlaneUtil)
        NewTexAttempts += 1
        print("CURRENT TEXTURE CORRECTION ENDING")
        print("#############################")
        
        if (BadTexture):
            delNode(TexGroup)
            

    bpy.context.window.scene = Helpers.GetScene("SCENE")
    
    if IndependentTransform:
        linkTex(TextureCoordinate.outputs[3], InvertRotate.inputs[0])
        linkTex(InvertRotate.outputs[0], Textures[-1].inputs[0])
        return (TexGroup, InvertRotate)
    else:
        return TexGroup