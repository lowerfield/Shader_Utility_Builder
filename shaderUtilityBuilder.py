

def setPos(inputNode, node, x = 0, y = 100):

    # node positioning function
    node.setXYpos(int(inputNode['xpos'].value()) + x, int(inputNode['ypos'].value()) + y)
    
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












