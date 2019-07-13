import xml.etree.ElementTree as ET
import networkx as nx
from haversine import haversine
import time
import os
from datetime import datetime

def OSMtoGraph_Controller( OSM_list ):
    # Start with a collector graph.
    G_final = nx.Graph()
    
    for OSM_file in OSM_list:
        print('------- processing ' + OSM_file )
        start_time = time.time()
            
        G = OSMtoGraph(OSM_file)

        # Add it to the collector graph.
        G_final = nx.compose(G_final,G)

        print('Elapsed time [sec] ' + str(int(time.time()-start_time)))
    
    return G_final
        
        
def OSMtoGraph( OSM_file ):
    # Get the OSM file.
    tree = ET.parse(OSM_file)
    root = tree.getroot()
    
    # Make a blank graph.
    G = nx.Graph()

    # Node collection
    for node in root.iter('node'):
        #print node.attrib['id'], node.attrib['lat'], node.attrib['lon']
        G.add_node( int(node.attrib['id']), lat=float(node.attrib['lat']), lon=float(node.attrib['lon']) )
    
    # Edge collection
    edgelist = []
    for way in root.iter('way'):
        #print way.attrib['id']
        prevNode = 0
        edgelist = []
        for tag in way.iter('tag'):
            # If this 'way' has tag-k='highway' and tag-v is in the list, this is a road segment.
            if (tag.attrib['k']=='highway') and (tag.attrib['v'] in ['motorway','trunk','primary','secondary','tertiary','motorway_link','trunk_link','primary_link','secondary_link']):
                for nd in way.iter('nd'):
                    if prevNode == 0:                   # If this is the beginning of a road segment,
                        prevNode = int(nd.attrib['ref'])
                    else:                               # If this is not the beginning of a road segment,
                        currentNode = int(nd.attrib['ref'])
                        # Calculate 1/distance. This is a weight for the shoftest path finder.
                        distNodes   = 1.0/haversine( [G.nodes[prevNode]['lat'],    G.nodes[prevNode]['lon']   ], \
                                                     [G.nodes[currentNode]['lat'], G.nodes[currentNode]['lon']], unit='mi')
                        edgelist.append( (prevNode, currentNode, {'weight':distNodes, 'traverse':0}) )
                
                        prevNode = int(nd.attrib['ref'])
                
        #print edgelist
        G.add_edges_from(edgelist)
    
    # Remove isolated nodes.
    G.remove_nodes_from(list(nx.isolates(G)))
        
    
    return G


###### Convert OSM files to a graph, and save the graph in GML.
Directory = './MAPs_DET/'
OSM_list = [f for f in os.listdir(Directory) if f.startswith('bbox')]
OSM_list = list(map(lambda x: Directory+x, OSM_list ))

# Run the converter.
G = OSMtoGraph_Controller( OSM_list )

# Save the graph with date tag.
nx.write_gml(G, Directory+'G_' + datetime.now().strftime('%Y_%m_%d') + '.gml')

