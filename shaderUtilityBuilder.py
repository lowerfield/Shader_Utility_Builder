
import nuke
import re
import math
import os

__all__ = ['shaderBuilder']

    
def buildAovs(node,aovList,utilityList,unpremult):

    # build layers    
    shuffle = nuke.nodes.Shuffle(inputs = [unpremult], red = 'black', green = 'black', blue = 'black', alpha = 'black')
    split = splitLayer(node,aovList[0])
    split[0]['name'].setValue('input')
    split[0].setInput(0,None)

    Merge2 = nuke.nodes.Merge2(operation = 'plus', output = 'rgb', inputs = [shuffle,split[1]])
    setPos(split[1], Merge2, x = 300, y = 25)   
    setPos(Merge2,shuffle, y = -100)
    
    for a in aovList[1::]:
        split = splitLayer(split[0],a)
        Merge2 = nuke.nodes.Merge2(operation = 'plus', output = 'rgb', inputs = [Merge2,split[1]])
        setPos(split[1], Merge2, x = 300, y = 25)

    # copy alpha and switch to bty by default
    input = nuke.nodes.Dot(inputs = [split[0]])
    setPos(split[0],input, x = -5, y = 100)
    copy = nuke.nodes.Copy(inputs = [Merge2, input ], channels = 'alpha')
    setPos(Merge2, copy, y = 100)
    switch = nuke.nodes.Switch(inputs = [copy, input], label = 'beauty contact switch', which = 1)
    switch['which'].setExpression('contactSheet ? 2 : btyBypass ? 1 : 0')   
    setPos(copy, switch, y = 100)
    remove = nuke.nodes.Remove(inputs = [switch], operation = 'keep', channels = 'rgba')
    setPos(switch, remove, y = +100)
    premult = nuke.nodes.Premult(inputs = [remove])
    premult['disable'].setExpression('btyBypass || contactSheet')
    setPos(remove, premult, y = 100)


    contactSheet = nuke.nodes.LayerContactSheet(inputs = [input], showLayerNames = True)
    contactSheet['showLayerNames'].setExpression('contactSheet')
    setPos(input, contactSheet, x = -25, y = 100)
    switch.setInput(2, contactSheet)

    return premult




    
def buildUtility(node, utilityList):
    
    split = splitUtility(node, utilityList[0])
    setPos(split[0], split[0], x=50)
    setPos(split[1], split[1], x=50)
    # split[0].setSelected(True)
    # split[1].setSelected(True)

    for utilityLayer in utilityList[1::]:
        split = splitUtility(split[0], utilityLayer)
        # split[0].setSelected(True)
        # split[1].setSelected(True)

    # backdrop = nukescripts.autoBackdrop()
    # backdrop['label'].setValue('Utility')

    # for nodes in nuke.selectedNodes():
    #    nodes.setSelected(True) 

     
def getLayers(node):

    # set aovs and utility layers
    aovsKeyWords = ['indirect', 'direct', 'rgba']
    
    aovList = sorted(list(set([c.split('.')[0] for c in node.channels() 
            for a in aovsKeyWords if re.search(a,c)])))[::-1]
    
    utilityList = sorted(list(set([c.split('.')[0] for c in node.channels()])))
    
    for layer in aovList:
        utilityList.remove(layer)

    return aovList, utilityList


def splitLayer(node,layer):
    
    input = nuke.nodes.Dot(inputs = [node])
    setPos(node,input, x = -5, y = 300)
    output = nuke.nodes.Shuffle(inputs = [input])
    output['in'].setValue(layer)
    output['postage_stamp'].setValue(True)
    output['name'].setValue(layer)
    setPos(input, output, x = 100, y = -25)

    return input, output

    
def splitUtility(node, utilityLayer):
    
    input = nuke.nodes.Dot(inputs = [node])
    setPos(node,input, x = 100)
    shuffle = nuke.nodes.Shuffle(inputs = [input])
    shuffle['in'].setValue(utilityLayer)
    shuffle['postage_stamp'].setValue(True)
    shuffle['name'].setValue(utilityLayer)
    setPos(input, shuffle, x = -25, y = 50)

    return input, shuffle


def getLayers(node):

    # set aovs and utility layers
    aovKeyWords = ['direct',
                   'indirect',
                   'sss',
                   'emission',
                   'transmission',
                   'obj']
    aovList = []

    # set aovs and utility layers
    for c in node.channels():
        for aov in aovKeyWords:
            if re.search(aov,c):
                aovList.append(c.split('.')[0])
    
    aovList = sorted(list(set(aovList)))

    shadow = [shadow for shadow in aovList if re.search('shadow', shadow)]

    for shadow in shadow:
        aovList.remove(shadow)

    utilityList = list(set([c.split('.')[0] for c in node.channels()]))
        
    for layer in aovList:
        utilityList.remove(layer)

    return aovList, utilityList


def setPos(inputNode, node, x = 0, y = 0):

    # node positioning function
    xpos = int(inputNode['xpos'].value()) + inputNode.screenWidth()/2
    ypos = int(inputNode['ypos'].value()) + inputNode.screenHeight()/2

    node.setXYpos(xpos + x, ypos + y)
    
    return

def shaderBuilder():

    # Create shader build group 
    try:
        node = nuke.selectedNode()
        if node.Class() in ('Read', 'Group'): # will need to change class to Read
            node = node
        else:
            nuke.message('Not posibble to build shader from selected node')

        name = os.path.basename(node['file'].value()).split('.')[0]
        group = nuke.nodes.Group(name = name, postage_stamp = 'True', inputs =[node])
        setPos(node, group, x = -25)

        count = 1
        while nuke.exists( name + str(count)):
            count += 1
        
        group['name'].setValue( name + str(count))

        group['label'].setValue('Shader_Build')
        
        # begin group
        group.begin()
        groupInput = nuke.nodes.Input() 
        setPos(node,groupInput, x = -40)
        setPos(node,groupInput, x = -40, y = 50)

        unpremult = nuke.nodes.Unpremult(channels = 'all', inputs = [groupInput])
        unpremult['disable'].setExpression('btyBypass || contactSheet')
        setPos(groupInput, unpremult, y = 50)


        aovList = getLayers(node)[0]
        utilityList = getLayers(node)[1]
        inOut = buildAovs(node,aovList, utilityList,unpremult)

        unpremultUtility = nuke.nodes.Unpremult(channels = 'all', inputs = [groupInput], name = 'Utility')
        setPos(groupInput, unpremultUtility , x = 500)
        buildUtility(unpremultUtility, utilityList)  
             
        input = nuke.toNode('input')
        input.setInput(0, unpremult)
                     
        groupOutput = nuke.nodes.Output(inputs = [inOut])
        setPos(inOut,groupOutput, y = 100)

        group.end()
        setPos(node,group, x = -40, y = 100)

        # set shader color
        group['tile_color'].setValue(16711680L)
        
        # add shader tabs
        tabKnob = nuke.Tab_Knob('shaderTab','Shader Controls')
        btyKnob = nuke.Boolean_Knob('btyBypass', 'Beauty - Aovs', 1)
        contactKnob = nuke.Boolean_Knob('contactSheet', 'Show Contact Sheet', 0)

        shaderKnobs = [tabKnob, btyKnob, contactKnob]

        for k in shaderKnobs:
            group.addKnob(k)
    


    except (RuntimeError, TypeError):
        pass






