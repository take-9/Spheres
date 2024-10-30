from time import sleep

import importlib

import Helpers

importlib.reload(Helpers)

def TalkToUser(phrases, NewLine=True):
    for phrase in phrases:
        for character in phrase:
            print(character, end = "", flush=True)
            sleep(0.01)
        sleep(0.24)
        if NewLine: print()
        

def Confirm():
    TalkToUser(["got it"])
    print()
    print()

def UserInputBool(Action, IsRushing=True, Preface=[], Confirmations=True):
    
    TalkToUser(Preface) if not IsRushing else print()
    
    UserIn = ""
    while (UserIn != "yes" and UserIn != "no"):
        TalkToUser([Action])
        UserIn = input("").lower()
        if (UserIn == "yes"):
            Confirm() if Confirmations else print()
            return True
        elif (UserIn == "no"):
            Confirm() if Confirmations else print()
            return False
        else:
            TalkToUser(["I have no idea what that means"])
            
def StartupInput():
    
    IsRushing = UserInputBool("Are you in a hurry? (skips option explanations): ")
    
    UseFilterPreface = [
     "The auto filter slows the program down a bit",
     "but it makes sure that most of the boring glowing balls are purged before rendering",
     "tbh this setting is only in here bc you two like to play cookie clicker and filter yourselves",
     "so if you plan to play around with filing them manually select no and hf with the unfiltered output",
     "but if you're going to go away from the computer and run this overnight or smth just say yes",
     "aaaaaaaaaaaaanyway"]

    UseFilter = UserInputBool("Do you want to use the auto filter?", IsRushing, UseFilterPreface)

    OutputSphereTexturesPreface = [
    "Onto the next feature",
    "The program can now output the textures of the spheres",
    "Alongside the spheres themselves too ofc",
    "but it takes a pretty long time and they average out at about 1MB each",
    "then again haha funni square",
    "so decision time"]

    OutputSphereTextures = UserInputBool("Do you want to render out the spheres' textures?", IsRushing, OutputSphereTexturesPreface)
    
    OutputBGTexturesPreface = [
    "Oh yeah now that there are wonky backgrounds",
    "Whenever you get some nice wonk you can output that too"]
    
    OutputBGTextures = UserInputBool("Do you want to render out wonky backgrounds' textures?", IsRushing, OutputBGTexturesPreface)
    
    SampleRatePreface = [
    "Wall of text incoming, hope you're ready",
    "Now that you have been lured in by the cartoon woman, let's talk computer science",
    "no but fr we need to talk sample rates",
    "so like here are the options",
    "if any sample amounts are omitted it means they're just a bad tradeoff of speed to quality",
    "anyway:",
    "",
    "1 lighting sample", 
    "looks kinda trash but fast asf and nice splotchy background, all detail kinda dies tho",
    "the original project was one sample per",
    "use this if you want spheres fast",
    "",
    "5-8 lighting samples", 
    "still kinda splotchy and low quality"
    "but waaaay better lighting and detail",
    "",
    "12-16 lighting samples", 
    "good medium quality lighting and detail", 
    "no more splotches at this point and beyond tho",
    "",
    "32 lighting samples", 
    "pretty good lighting and detail by this point",
    "recommended for good quality",
    "",
    "33-128 lighting samples", 
    "I mean you can if you want to but returns deminish exponentially", 
    "128 is about where sphere quality caps",
    "",
    "129+ lighting samples", 
    "yeah I'm not even gonna let you do that", 
    "it would be a humanitarian crisis to make your computer do that",
    "Computitarian crisis?",
    "Is there like a PETA but for computers?",
    "Anyway back to the options",
    ""]
    
    ValidSampleRate = False
    
    def Check(Preface):
        ValidSampleRate = UserInputBool("Are you sure?", False, Preface, False)
        if (ValidSampleRate):
            TalkToUser(["Ok then"])
        else:
            TalkToUser(["Back to the drawing board"])
        return ValidSampleRate
    
    TalkToUser(SampleRatePreface) if not IsRushing else print()
    while (not ValidSampleRate):
        TalkToUser(["What sample rate do you want to use? "])
        try:
            UserIn = int(input(""))
            if (UserIn <= 0):
                TalkToUser("How tf do I do that")
                sleep(0.75)
                TalkToUser(["Sorry lost my cool there, let's start over"])
            elif (UserIn > 128):
                TalkToUser(["You're insane", "yeah no that's no happening"])
            elif(UserIn > 32):
                ValidSampleRate = Check(["Warning: that's pretty high"])
            elif ((2 <= UserIn <= 4) or (9 <= UserIn <= 11) or (17 <= UserIn <= 31)):
                ValidSampleRate = Check([
                "Well that sample rate didn't have a good quality to speed ratio", 
                "in testing at least"])
            else:
                TalkToUser(["got it"])
                ValidSampleRate = True
        except ValueError:
            TalkToUser(["I have no idea what that means"])
        
        print()
    
    
    Helpers.GetScene("SCENE").cycles.samples = UserIn
    
    return (UseFilter, OutputSphereTextures, OutputBGTextures)