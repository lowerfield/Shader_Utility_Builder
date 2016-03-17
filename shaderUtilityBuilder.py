import nuke
import nukescripts
import re
import math
import os

__all__ = ['shaderBuilder']

class shaderBuilderPanel(nukescripts.PythonPanel):

    def __init__(self, aovList):
        nukescripts.PythonPanel.__init__( self, "Shader Builder Panel")

        self.columnNames = ('Build', 'Utility')
        
        self.aovColumnNames = []

        for aov in aovList:
            for column in self.columnNames:
                columnName = aov + '_' + column
                self.columnName = nuke.Boolean_Knob(columnName, aov)
                self.columnName.setFlag(nuke.STARTLINE)
                self.aovColumnNames.append(self.columnName)
        
        for column in self.columnNames:
            self.column = nuke.Tab_Knob(column,column)
            self.addKnob(self.column)
            for aov in self.aovColumnNames:
                if re.search(column, aov.name()):
                    self.addKnob(aov)

        defaultBuild = ('diffuse', 'specular', 'reflection', 'refraction', 'sss', 
                        'emission', 'transmission', 'incandescence')
        defaultUtility = ('depth', 'normal', 'object', 'reference', 'world', 
                        'matte', 'reflectance', 'roughness', 'texture', 'shadow', 
                        'occlusion' )        
        defaultIgnore = ('unoccluded', 'pure')

        # set defaults,  MAKE THIS MORE EFFICIENT
        for k in self.aovColumnNames:
            if re.search('Build', k.name()):
                for n in defaultBuild:
                    if re.search(n, k.name()):
                        k.setValue(True)
                for n in defaultUtility:
                    if re.search(n, k.name()):
                        k.setValue(False)
                for n in defaultIgnore:
                    if re.search(n, k.name()):
                        k.setValue(False)

            elif re.search('Utility', k.name()):
                for n in defaultUtility:
                    if re.search(n, k.name()):
                        k.setValue(True)

            #elif re.search('Ignore', k.name()):
            #    for n in defaultIgnore:
            #        if re.search(n, k.name()):
            #            k.setValue(True)
                        
        # set minimum size               
        width = (max(aovList, key = len)) * 10
        height = (len(self.aovColumnNames)/2) * 22
        self.setMinimumSize(200, height)
                                           
    # CALLBACKS
    def knobChanged(self, knob):
        # return lists
        self.buildList = [k.label() for k in self.aovColumnNames if re.search('Build', k.name()) and k.value() == True]

        self.utilityList = [k.label() for k in self.aovColumnNames if re.search('Utility', k.name()) and k.value() == True]

        #self.IgnoreList = [k.label() for k in self.aovColumnNames if re.search('Ignore', k.name()) and k.value() == True]

    def showModalDialog(self):
        nukescripts.PythonPanel.showModalDialog(self)
        return self.buildList, self.utilityList
        
    
def buildAovs(node,aovList,utilityList,unpremult):

    # build layers    
    shuffle = nuke.nodes.Shuffle(inputs = [unpremult], red = 'black', green = 'black', blue = 'black', alpha = 'black')
    remove = nuke.nodes.Remove(inputs = [shuffle], operation = 'keep', channels = 'rgb')
    split = splitLayer(node,aovList[0])
    split[0]['name'].setValue('input')
    split[0].setInput(0,None)
        
    Merge2 = nuke.nodes.Merge2(operation = 'plus', output = 'rgb', inputs = [remove,split[1]])
    setPos(split[1], Merge2, x = 300, y = 0)   
    setPos(Merge2,shuffle, y = -100)

    for a in aovList[1::]:
        split = splitLayer(split[0],a)
        Merge2 = nuke.nodes.Merge2(operation = 'plus', output = 'rgb', inputs = [Merge2,split[1]])
        setPos(split[1], Merge2, x = 300, y = 0)
        print a
    else:
        pass
    
    # copy alpha and switch to bty by default
    input = nuke.nodes.Dot(inputs = [split[0]])
    setPos(split[0],input, x = 0, y = 185)
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
    crop = nuke.nodes.Crop(inputs = [input], reformat = True)
    crop['box'].setExpression('bbox.x',0)
    crop['box'].setExpression('bbox.y',1)
    crop['box'].setExpression('bbox.r',2)
    crop['box'].setExpression('bbox.t',3)
    
    contactSheet = nuke.nodes.LayerContactSheet(inputs = [crop])
    contactSheet['showLayerNames'].setExpression('contactSheet')
    setPos(input, contactSheet, x = -34, y = 95)
    switch.setInput(2, contactSheet)
    
    return premult

    
def buildUtility(node, utilityList):
    
    split = splitUtility(node, utilityList[0])
    setPos(split[0], split[0], x=50, y = 10)
    setPos(split[1], split[1], x=50, y = 10)

    for utilityLayer in utilityList[1::]:
        split = splitUtility(split[0], utilityLayer)

def splitLayer(node,layer):
    
    input = nuke.nodes.Dot(inputs = [node])
    setPos(node,input, x = 0, y = 300)
    shuffle = nuke.nodes.Shuffle(inputs = [input])
    shuffle['in'].setValue(layer)
    shuffle['postage_stamp'].setValue(True)
    shuffle['name'].setValue(layer)
    remove = nuke.nodes.Remove(inputs = [shuffle], operation = 'keep', channels = 'rgb')
    setPos(input, shuffle, x = 100, y = -25)
    setPos(shuffle, remove, y = 100)
    
    return input, remove
    

def splitUtility(node, utilityLayer):

    input = nuke.nodes.Dot(inputs = [node])
    setPos(node,input, x = 100, y = 0)
    shuffle = nuke.nodes.Shuffle(inputs = [input])
    shuffle['in'].setValue(utilityLayer)
    shuffle['postage_stamp'].setValue(True)
    shuffle['name'].setValue(utilityLayer)
    remove = nuke.nodes.Remove(inputs = [shuffle], operation = 'keep', channels = 'rgb')
    setPos(input, shuffle, x = -34, y = 50)

    return input, shuffle

def getLayers(node):

    aovList =[]
    
    for c in node.channels():
                aovList.append(c.split('.')[0])
    
    aovList = sorted(list(set(aovList)))
    
    
    return aovList,


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
        
        aovList = getLayers(node)[0]
        aovs = shaderBuilderPanel(aovList).showModalDialog()
        aovList = aovs[0]
        utilityList = aovs[1]

        name = os.path.basename(node['file'].value()).split('.')[0]
        group = nuke.nodes.Group(name = name, postage_stamp = 'True', inputs =[node])
        setPos(node, group, x = -25)
        
        count = 1
        while nuke.exists( name + str(count)):
            count += 1
        
        group['name'].setValue( name + '_' +str(count))
        
        group['label'].setValue('Shader_Build')

        # begin group
        group.begin()
        groupInput = nuke.nodes.Input() 
        setPos(node,groupInput, x = -40)
        setPos(node,groupInput, x = -40, y = 50)
        
        unpremult = nuke.nodes.Unpremult(channels = 'all', inputs = [groupInput])
        unpremult['disable'].setExpression('btyBypass || contactSheet')
        setPos(groupInput, unpremult, y = 25)
        
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
