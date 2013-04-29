## By Kasper Brandt
## Last updated on 25-04-2013

import glob, sys, json, os, IatiConverter, AttributeHelper
import xml.etree.ElementTree as ET
from rdflib import Namespace, Graph, Literal, URIRef

def main():
    '''Converts Activity XMLs to Turtle files and stores these to local folder.'''
    
    # Settings
    xml_folder = "/media/Acer/School/IATI2LOD/IATI2LOD/xml/organisations/"
    turtle_folder = "/media/Acer/School/IATI-data/organisations/"
    provenance_folder = "/media/Acer/School/IATI-data/provenance/"
    Iati = Namespace("http://purl.org/collections/iati/")

    if not os.path.isdir(turtle_folder):
        os.makedirs(turtle_folder)
        
    if not os.path.isdir(provenance_folder):
        os.makedirs(provenance_folder)
    
    document_count = 1
    organisation_count = 1
    
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
        
        if not failed == True:
            root = xml.getroot()
            version = AttributeHelper.attribute_key(root, 'version')
            
            if (root.tag == 'iati-organisations') or (root.tag == 'organisations'):
                            
                # Convert each organisation in XML file to RDFLib Graph
                for organisation in xml.findall('iati-organisation'):
                    
                    try:
                        converter = IatiConverter.ConvertOrganisation(organisation)
                        graph, id, last_updated = converter.convert(Iati)
                    except TypeError as e:
                        print "Error in " + document + ":" + str(e)
                        graph = None
                    
                    if not graph == None:
                        # Write activity to Turtle and store in local folder
                        graph_turtle = graph.serialize(format='turtle')
                        
                        with open(turtle_folder + 'organisation-' + id.replace('/','%2F') + '.ttl', 'w') as turtle_file:
                            turtle_file.write(graph_turtle)
                        
                        # Add provenance from corresponding JSON file
                        json_document = document[:-4] + '.json'
                        
                        try:
                            with open(json_document, 'r') as open_json_doc:
                                json_parsed = json.load(open_json_doc)
                        except:
                            print "Could not parse file " + json_document
                            json_parsed = None
                
                        provenance_converter = IatiConverter.ConvertProvenance('organisation', json_parsed, provenance, 
                                                                               id, last_updated, version)
                        provenance = provenance_converter.convert(Iati)
                    
                    print "Progress: Organisation #" + str(organisation_count) + " in document #" + str(document_count)
                    
                    organisation_count += 1
    
                for organisation in xml.findall('organisation'):
                    
                    try:
                        converter = IatiConverter.ConvertOrganisation(organisation)
                        graph, id, last_updated = converter.convert(Iati)
                    except TypeError as e:
                        print "Error in " + document + ":" + str(e)
                        graph = None
                    
                    if not graph == None:
                        # Write activity to Turtle and store in local folder
                        graph_turtle = graph.serialize(format='turtle')
                        
                        with open(turtle_folder + 'organisation-' + id.replace('/','%2F') + '.ttl', 'w') as turtle_file:
                            turtle_file.write(graph_turtle)
                    
                        # Add provenance from corresponding JSON file
                        json_document = document[:-4] + '.json'
                        
                        try:
                            with open(json_document, 'r') as open_json_doc:
                                json_parsed = json.load(open_json_doc)
                        except:
                            print "Could not parse file " + json_document
                            json_parsed = None
                
                        provenance_converter = IatiConverter.ConvertProvenance('organisation', json_parsed, provenance, 
                                                                               id, last_updated, version)
                        provenance = provenance_converter.convert(Iati)
                    
                    print "Progress: Organisation #" + str(organisation_count) + " in document #" + str(document_count)
                    
                    organisation_count += 1
                
            elif (root.tag == 'iati-organisation') or (root.tag == 'organisation'):
                
                    try:
                        converter = IatiConverter.ConvertOrganisation(xml.getroot())
                        graph, id, last_updated = converter.convert(Iati)
                    except TypeError as e:
                        print "Error in " + document + ":" + str(e)
                        graph = None
                    
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
                
                        provenance_converter = IatiConverter.ConvertProvenance('organisation', json_parsed, provenance, 
                                                                               id, last_updated, version)
                        provenance = provenance_converter.convert(Iati)
                    
                    print "Progress: Organisation #" + str(organisation_count) + " in document #" + str(document_count)
                    
                    organisation_count += 1
                       
            document_count += 1
        
            # Write provenance graph to Turtle and store in local folder
            provenance_turtle = provenance.serialize(format='turtle')
            
            with open(provenance_folder + 'provenance-organisation-' + str(document.rsplit('/',1)[1])[:-4] + '.ttl', 'w') as turtle_file:
                turtle_file.write(provenance_turtle)
        
    print "Done!"
    
if __name__ == "__main__":
    main()