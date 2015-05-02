import re


def buildAovs(node,aovList):

    constant = nuke.nodes.Constant()
    split = splitLayer(node,aovList[0])
    merge = nuke.nodes.Merge( operation = 'plus', output = 'rgb', inputs = [constant,split[1]])
    setPos(split[1], merge, x = 300, y = 25)
    
    setPos(merge,constant, y = -100)
    
    for a in aovList[1::]:
        split = splitLayer(split[0],a)
        merge = nuke.nodes.Merge( operation = 'plus', output = 'rgb', inputs = [merge,split[1]])
        setPos(split[1], merge, x = 300, y = 25)
      

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
        read = nuke.selectedNode()
        if read.Class() == 'PostageStamp': # will need to change class to Read
            read = read
        else:
            nuke.message('Not posibble to build shader from selected node')
    
        group = nuke.nodes.Group(name = 'Shader_Build', postage_stamp = 'True', inputs =[read])
        setPos(read,group)
        
        # begin group
        group.begin()
        
        groupInput = nuke.nodes.Input()
        groupOutput = nuke.nodes.Output(inputs = [groupInput])
        
        group.end()

    except:
        nuke.message('No node selected')












