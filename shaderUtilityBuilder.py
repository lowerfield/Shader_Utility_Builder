import re


def buildAovs(node,aovList):

    # build layers
    constant = nuke.nodes.Constant()
    split = splitLayer(node,aovList[0])
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
    switch = nuke.nodes.Switch(inputs = [copy, input], label = 'beauty switch', which = 1)
    setPos(copy, switch, y = 100)
    


      

def getLayers(node):

    # set aovs and utility layers
    aovList = sorted(list(set([c.split('.')[0] for c in node.channels() 
            if re.search('indirect',c) or re.search('direct',c) 
            or re.search('rgba',c) ])))[::-1]
    
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

def main():

    # Create shader build group 
    try:
        node = nuke.selectedNode()
        if node.Class() == 'PostageStamp': # will need to change class to Read
            node = node
        else:
            nuke.message('Not posibble to build shader from selected node')
    
        group = nuke.nodes.Group(name = 'Shader_Build', postage_stamp = 'True', inputs =[node])
        setPos(node,group)
        
        # begin group
        group.begin()

        aovList = getLayers(node)
        buildAovs(node,aovList[0])
        
        groupInput = nuke.nodes.Input()
        groupOutput = nuke.nodes.Output(inputs = [groupInput])
        
        group.end()

    except:
        nuke.message('No node selected')













