import nuke
import re

def buildContactSheet(node, aovList, utilityList):

    contactGroup = nuke.nodes.Group(name = 'Contact Sheet', inputs = [node], postage_stamp = True)
    setPos(node,contactGroup, x = -40, y = 100)
    contactGroup.begin()
    groupInput = nuke.nodes.Input() 
    
    contactSheet = nuke.nodes.ContactSheet(postage_stamp = True, label = 'Aovs Contact Sheet')
       
    count = 0
    for layer in aovList + utilityList:
        shuffle = nuke.nodes.Shuffle(inputs = [groupInput], postage_stamp = True, name = layer)
        shuffle['in'].setValue(layer)
        text = nuke.nodes.Text(name = layer, message = layer, inputs = [shuffle])
        setPos(shuffle, text, y = 100) 
        contactSheet.setInput(count,text)
        count += 1
    
    groupOutput = nuke.nodes.Output()
    groupOutput.setInput(0, contactSheet)
    setPos(contactSheet, groupOutput, y = 100)
    contactGroup.end()

    return contactGroup
    

def buildAovs(node,aovList, utilityList):

    # build layers    
    constant = nuke.nodes.Constant()
    split = splitLayer(node,aovList[0])
    split[0]['name'].setValue('input')
    split[0].setInput(0,None)

    Merge2 = nuke.nodes.Merge2(operation = 'plus', output = 'rgb', inputs = [constant,split[1]])
    setPos(split[1], Merge2, x = 300, y = 25)   
    setPos(Merge2,constant, y = -100)
    

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

    contactSheet = buildContactSheet(input, aovList, utilityList)
    setPos(input, contactSheet, x = -25, y = 100)
    switch.setInput(2, contactSheet)

    return switch

    
def buildUtility(node,utilityList):
    
    split = splitUtility(node,utilityList[0], x = 300)

    for utilityLayer in utilityList[1::]:
        split = splitUtility(split[0],utilityLayer, y = -5)

     
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

    
def splitUtility(node,utilityLayer):
    
    input = nuke.nodes.Dot(inputs = [node])
    setPos(node,input, x = 200, y = -5)
    shuffle = nuke.nodes.Shuffle(inputs = [input])
    shuffle['in'].setValue(utilityLayer)
    shuffle['postage_stamp'].setValue(True)
    shuffle['name'].setValue(utilityLayer)
    setPos(input, shuffle, x = -25, y = 200)

    return input, shuffle



def getLayers(node):

    # set aovs and utility layers
    aovList = list(set([c.split('.')[0] for c in node.channels() 
            if re.search('indirect',c) or re.search('direct',c) 
            or re.search('rgba',c) ]))
    
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
        if node.Class() == 'PostageStamp': # will need to change class to Read
            node = node
        else:
            nuke.message('Not posibble to build shader from selected node')
    
        group = nuke.nodes.Group(name = 'Shader_Build', postage_stamp = 'True', inputs =[node])
        setPos(node, group, x = -25)

        count = 1
        while nuke.exists('Shader_Build' + str(count)):
            count += 1
        
        group['name'].setValue('Shader_Build' + str(count))
        
        # begin group
        group.begin()
        groupInput = nuke.nodes.Input() 
        setPos(node,groupInput, x = -40)

        aovList = getLayers(node)[0]
        utilityList = getLayers(node)[1]
        inOut = buildAovs(node,aovList, utilityList)
        #buildUtility(groupInput,utilityList)

        input = nuke.toNode('input')
        input.setInput(0, groupInput)
                     
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
    
        group['label'].setValue(node.name())

    except (RuntimeError, TypeError):
        pass



shaderBuilder()



                                                                                                                                                                                                







