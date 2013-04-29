## By Kasper Brandt
## Last updated on 24-04-2013

import glob, json, sys, os, IatiConverter, AttributeHelper
import xml.etree.ElementTree as ET
from rdflib import Namespace, Graph, Literal, URIRef

def main():
    '''Converts Activity XMLs to Turtle files and stores these to local folder.'''
    
    # Settings
    xml_folder = "/media/Acer/School/IATI2LOD/IATI2LOD/xml/activities/"
    turtle_folder = "/media/Acer/School/IATI-data/activities/"
    provenance_folder = "/media/Acer/School/IATI-data/provenance/"
    Iati = Namespace("http://purl.org/collections/iati/")
    
    if not os.path.isdir(turtle_folder):
        os.makedirs(turtle_folder)
        
    if not os.path.isdir(provenance_folder):
        os.makedirs(provenance_folder)
    
    document_count = 1
    activity_count = 1
    
    # Retrieve XML files from the XML folder
    for document in glob.glob(xml_folder + '*.xml'):
        
        failed = False
        
        provenance = Graph()
        provenance.bind('iati', Iati)
        
        # Parse the XML file
        try:
            xml = ET.parse(document)
        except ET.ParseError:
            print "Could not parse file " + document
            failed = True
            
        # Get the version
        if not failed == True:
            root = xml.getroot()
            version = AttributeHelper.attribute_key(root, 'version')
            linked_data_default = AttributeHelper.attribute_key(root, 'linked-data-default')
        
            # Convert each activity in XML file to RDFLib Graph
            for activity in xml.findall('iati-activity'):
                
                try:
                    converter = IatiConverter.ConvertActivity(activity, version, linked_data_default)
                    graph, id, last_updated, version = converter.convert(Iati)
                except TypeError as e:
                    print "Error in " + document + ":" + str(e)
                
                if not id == None:
                    print "Processing: Activity %s (# %s) in document %s (# %s)" % (str(id.replace('/','%2F')), 
                                                                                    str(activity_count),
                                                                                    str(document.rsplit('/',1)[1]), 
                                                                                    str(document_count))
                else:
                    print "WARNING: Activity (# %s) in %s (# %s) has no identifier specified" % (str(activity_count),
                                                                                                 str(document.rsplit('/',1)[1]),
                                                                                                 str(document_count)) 
                
                if not graph == None:
                    # Write activity to Turtle and store in local folder
                    graph_turtle = graph.serialize(format='turtle')
                    
                    with open(turtle_folder + id.replace('/','%2F') + '.ttl', 'w') as turtle_file:
                        turtle_file.write(graph_turtle)
                    
                    # Add provenance from corresponding JSON file
                    json_document = document[:-4] + '.json'
                    
                    try:
                        with open(json_document, 'r') as open_json_doc:
                            json_parsed = json.load(open_json_doc)
                    except:
                        print "Could not parse file " + json_document
                        json_parsed = None
            
                    provenance_converter = IatiConverter.ConvertProvenance('activity', json_parsed, provenance, 
                                                                           id, last_updated, version)
                    provenance = provenance_converter.convert(Iati)
                            
                activity_count += 1
                       
            document_count += 1
        
            # Write provenance graph to Turtle and store in local folder
            provenance_turtle = provenance.serialize(format='turtle')
            
            with open(provenance_folder + 'provenance-activity-' + str(document.rsplit('/',1)[1])[:-4] + '.ttl', 'w') as turtle_file:
                turtle_file.write(provenance_turtle)
        
    print "Done!"
    
if __name__ == "__main__":
    main()