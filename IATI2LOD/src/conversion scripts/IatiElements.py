## By Kasper Brandt
## Last updated on 02-06-2013

from rdflib import RDF, RDFS, Literal, URIRef, Namespace, OWL
from rdflib.graph import Graph
import AttributeHelper, hashlib

class ActivityElements :
    '''Class for converting XML elements of self.iati activities to a RDFLib self.graph.'''
    
    def __init__(self, defaults): 
        '''Initializes class.
        
        Parameters
        @defaults: A dictionary of defaults.'''
        
        self.id = defaults['id'].replace(" ", "%20")
        self.default_language = defaults['language']
        self.default_currency = defaults['currency']
        self.default_finance_type = defaults['finance_type']
        self.default_flow_type = defaults['flow_type']
        self.default_aid_type = defaults['aid_type']
        self.default_tied_status = defaults['tied_status']
        self.hierarchy = defaults['hierarchy']
        self.linked_data_uri = defaults['linked_data_uri']
        self.iati = defaults['namespace']
        self.iati_custom = Namespace(defaults['namespace'] + "custom/")
        
        self.graph = Graph()
        self.graph.bind('iati', self.iati)
        self.graph.bind('iati-custom', self.iati_custom)
        self.graph.bind('activity', self.iati['activity/'])
        self.graph.bind('related-activity', self.iati['related-activity/'])
        
        self.graph.add((self.iati['activity/' + self.id],
                        RDF.type,
                        self.iati['activity']))
        
        if not self.hierarchy == None:
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-hierarchy'],
                            Literal(self.hierarchy)))
            
        if not self.linked_data_uri == None:
            self.linked_data_uri = self.linked_data_uri.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            OWL.sameAs,
                            URIRef(self.linked_data_uri)))


    def get_result(self):
        '''Returns the resulting self.graph of the activity.
        
        Returns
        @graph: The RDFLib self.graph with added statements.'''
        
        return self.graph
    
    def process_unknown_tag(self, tag):
        '''Returns the correct tag for use in unknown elements.
        
        Parameters
        @tag: The original tag.
        
        Returns
        @namespace: The RDFLib Namespace to be used.
        @name: The name of the tag.'''
        
        tag = tag.replace("{", "").replace("}", "")
        
        if ":" in tag:
            if tag[:4] == "http":
                return Namespace(tag.replace(" ", "-")), tag.rsplit('/',1)[1].replace(" ", "%20")
            
            else:
                tag = tag.split(":")[1]
                if tag[:9] == "activity-":
                    return Namespace(self.iati[tag.replace(" ", "-")]), tag.replace(" ", "%20")
                else:
                    return Namespace(self.iati["activity-" + tag.replace(" ", "-")]), str("activity-" + tag.replace(" ", "%20"))
        else:
            if tag[:9] == "activity-":
                return Namespace(self.iati[tag.replace(" ", "-")]), tag.replace(" ", "%20")
            
            else:
                return Namespace(self.iati["activity-" + tag.replace(" ", "-")]), str("activity-" + tag.replace(" ", "%20"))
    
    def convert_unknown(self, xml):
        '''Converts non-IATI standard elements up to 2 levels to a RDFLib self.graph.
        
        Parameters:
        @xml: The XML of this element.'''
        
        if not "ignore" in xml.tag:
            
            namespace, name = self.process_unknown_tag(xml.tag)
            
            children_elements = xml.findall("./")
                
            if children_elements == []:
                # No children
                if (not xml.text == None) and (not xml.text == ""):
                    if len(xml.text) > 1:
                        self.graph.add((self.iati['activity/' + self.id],
                                        namespace,
                                        Literal(xml.text)))
                        
                for key in xml.attrib:
                    key_text = xml.attrib[key]
                    if "}" in key:
                        key = key.rsplit('}',1)[1]
                    if (not key_text == None) and (not key_text == ""):
                        self.graph.add((self.iati['activity/' + self.id],
                                        URIRef(namespace + '-' + str(key).replace(" ", "-")),
                                        Literal(key_text)))
                        
            else:
                # Does have children
                
                self.graph.add((self.iati['activity/' + self.id],
                                namespace,
                                self.iati['activity/' + self.id + '/' + str(name)]))
                
                for key in xml.attrib:
                    key_text = xml.attrib[key]
                    if "}" in key:
                        key = key.rsplit('}',1)[1]
                    if (not key_text == None) and (not key_text == ""):
                        self.graph.add((self.iati['activity/' + self.id + '/' + str(name)],
                                        self.iati_custom[str(key).replace(" ", "-")],
                                        Literal(key_text)))
                
                for child in xml:
                    children_elements = child.findall("./")
                    
                    child_namespace, child_name = self.process_unknown_tag(child.tag)
                    
                    if children_elements == []:
                        # No grand-children
                        if not child.text == None:
                            if len(child.text) > 1:
                                self.graph.add((self.iati['activity/' + self.id + '/' + str(name)],
                                                child_namespace,
                                                Literal(child.text)))
                                
                        for key in child.attrib:
                            key_text = child.attrib[key]
                            if "}" in key:
                                key = key.rsplit('}',1)[1]
                            if (not key_text == None) and (not key_text == ""):
                                self.graph.add((self.iati['activity/' + self.id + '/' + str(name)],
                                                URIRef(child_namespace + '-' + str(key).replace(" ", "-")),
                                                Literal(key_text)))
                                
                    else:
                        # Has grand-children
                        
                        self.graph.add((self.iati['activity/' + self.id + '/' + str(name)],
                                        URIRef(namespace + '-' + str(child_name)),
                                        self.iati['activity/' + self.id + '/' + str(name) + '/' + str(child_name)]))
                        
                        for key in child.attrib:
                            key_text = child.attrib[key]
                            if "}" in key:
                                key = key.rsplit('}',1)[1]
                            
                            if (not key_text == None) and (not key_text == ""):
                                self.graph.add((self.iati['activity/' + self.id + '/' + str(name) + '/' + str(child_name)],
                                                self.iati_custom[str(key).replace(" ", "-")],
                                                Literal(key_text)))
                            
                        for grandchild in child:
                            grandchildren_elements = grandchild.findall("./")
                            
                            grandchild_namespace, grandchild_name = self.process_unknown_tag(grandchild.tag)
                                
                            if grandchildren_elements == []:
                                # No grand-grand-children
                                
                                if not grandchild == None:
                                    if len(grandchild.text) > 1:
                                        self.graph.add((self.iati['activity/' + self.id + '/' + str(name) + '/' + str(child_name)],
                                                        grandchild_namespace,
                                                        Literal(grandchild.text)))
                                        
                                for key in grandchild.attrib:
                                    key_text = grandchild.attrib[key]
                                    if "}" in key:
                                        key = key.rsplit('}',1)[1]
                                        
                                    if (not key_text == None) and (not key_text == ""):
                                        self.graph.add((self.iati['activity/' + self.id + '/' + str(name) + '/' + str(child_name)],
                                                        URIRef(grandchild_namespace + '-' + str(key).replace(" ", "-")),
                                                        Literal(key_text)))
                                        
                            else:
                                # Three levels
                                print "Three levels for a non-IATI element (" + str(name) + ") is not supported..."
                            
    
    def reporting_org(self, xml):
        '''Converts the XML of the reporting-org element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        ref = AttributeHelper.attribute_key(xml, 'ref')
        type = AttributeHelper.attribute_key(xml, 'type')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not ref == None:
            ref = ref.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-reporting-org'],
                            self.iati['activity/' + str(self.id) + '/reporting-org/' + str(ref)]))
            
            self.graph.add((self.iati['activity/' + str(self.id) + '/reporting-org/' + str(ref)],
                            RDF.type,
                            self.iati['organisation']))
            
            self.graph.add((self.iati['activity/' + str(self.id) + '/reporting-org/' + str(ref)],
                            self.iati['organisation-code'],
                            self.iati['codelist/OrganisationIdentifier/' + str(ref)]))
        
            if not name == None:
                self.graph.add((self.iati['activity/' + self.id + '/reporting-org/' + str(ref)],
                                RDFS.label,
                                name))
                
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/reporting-org/' + str(ref)],
                                self.iati['organisation-type'],
                                self.iati['codelist/OrganisationType/' + str(type)]))
        
        elif not name == None:
            # Create hash
            # Required: name
            
            hash = hashlib.md5()
            hash.update(name)

            hash_name = hash.hexdigest()            
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-reporting-org'],
                            self.iati['activity/' + str(self.id) + '/reporting-org/' + str(hash_name)]))
            
            self.graph.add((self.iati['activity/' + str(self.id) + '/reporting-org/' + str(hash_name)],
                            RDF.type,
                            self.iati['organisation']))
        
            self.graph.add((self.iati['activity/' + str(self.id) + '/reporting-org/' + str(hash_name)],
                            RDFS.label,
                            name))
                
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + str(self.id) + '/reporting-org/' + str(hash_name)],
                                self.iati['organisation-type'],
                                self.iati['codelist/OrganisationType/' + str(type)]))            

    
    def iati_identifier(self, xml):
        '''Converts the XML of the self.iati-identifier element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Text
        id = xml.text
        
        if not id == None:
            id = " ".join(id.split())
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-id'],
                            Literal(id)))
    
    def other_identifier(self, xml):
        '''Converts the XML of the other-identifier element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        owner_ref = AttributeHelper.attribute_key(xml, 'owner-ref')
        owner_name = AttributeHelper.attribute_key(xml, 'owner-name')
        
        # Text
        name = xml.text
        
        if not name == None:
            # Create hash
            # Required: name
            hash = hashlib.md5()
            hash.update(name)

            hash_name = hash.hexdigest()
            
            name = " ".join(name.split())
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-other-identifier'],
                            self.iati['activity/' + self.id + '/other-identifier/' + str(hash_name)]))

            self.graph.add((self.iati['activity/' + self.id + '/other-identifier/' + str(hash_name)],
                            RDFS.label,
                            Literal(name)))
            
            if not owner_ref == None:
                owner_ref = owner_ref.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/other-identifier/' + str(hash_name)],
                                self.iati['other-identifier-owner-ref'],
                                self.iati['codelist/OrganisationIdentifier/' + str(owner_ref)]))
            
            if not owner_name == None:
                self.graph.add((self.iati['activity/' + self.id + '/other-identifier/' + str(hash_name)],
                                self.iati['other-identifier-owner-name'],
                                Literal(owner_name)))
    
    def activity_website(self, xml):
        '''Converts the XML of the activity-website element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Text
        website = xml.text.replace(" ", "%20")
        
        if not website == None:
            website = "%20".join(website.split())
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-website'],
                            URIRef(website)))
    
    def title(self, xml):
        '''Converts the XML of the title element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Text
        title = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not title == None:
            self.graph.add((self.iati['activity/' + self.id],
                            RDFS.label,
                            title))
    
    def description(self, xml):
        '''Converts the XML of the description element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        type = AttributeHelper.attribute_key(xml, 'type')
        
        # Text
        description = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not description == None:
            # Create hash
            # Required: description
            hash = hashlib.md5()
            hash.update(description)

            hash_description = hash.hexdigest()
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-description'],
                            self.iati['activity/' + self.id + '/description/' + str(hash_description)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/description/' + str(hash_description)],
                            RDF.type,
                            self.iati['description']))
            
            self.graph.add((self.iati['activity/' + self.id + '/description/' + str(hash_description)],
                            self.iati['description-text'],
                            description))
            
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/description/' + str(hash_description)],
                                self.iati['description-type'],
                                self.iati['codelist/DescriptionType/' + str(type)]))
    
    def activity_status(self, xml):
        '''Converts the XML of the activity-status element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-status'],
                            self.iati['codelist/ActivityStatus/' + str(code)]))
    
    def activity_date(self, xml):
        '''Converts the XML of the activity-date element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        type = AttributeHelper.attribute_key(xml, 'type')
        iso_date = AttributeHelper.attribute_key(xml, 'iso-date')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not type == None:
            if not iso_date == None:
                self.graph.add((self.iati['activity/' + self.id],
                                self.iati[type + '-date'],
                                Literal(iso_date)))
                        
            if not name == None:
                self.graph.add((self.iati['activity/' + self.id],
                                self.iati[type + '-text'],
                                Literal(name)))
    
    def contact_info(self, xml):
        '''Converts the XML of the contact-info element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Create hash
        # Required: one of organisation, person-name, telephone, email, mailing-address
        hash = hashlib.md5()
        hash_created = False
        
        organisation_text = AttributeHelper.attribute_text(xml, 'organisation')
        if not organisation_text == None:
            hash.update(organisation_text[0])
            hash_created = True
        person_name_text = AttributeHelper.attribute_text(xml, 'person-name')
        if not person_name_text == None:
            hash.update(person_name_text[0])
            hash_created = True
        telephone_text = AttributeHelper.attribute_text(xml, 'telephone')
        if not telephone_text == None:
            hash.update(telephone_text[0])
            hash_created = True
        email_text = AttributeHelper.attribute_text(xml, 'email')
        if not email_text == None:
            hash.update(email_text[0])
            hash_created = True
        mailing_address_text = AttributeHelper.attribute_text(xml, 'mailing-address')
        if not mailing_address_text == None:
            hash.update(mailing_address_text[0])
            hash_created = True
            
        if hash_created:
            hash_contact_info = hash.hexdigest()
    
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-contact-info'],
                            self.iati['activity/' + self.id + '/contact-info/' + str(hash_contact_info)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/contact-info/' + str(hash_contact_info)],
                            RDF.type,
                            self.iati['contact-info']))        
            
            for element in xml:
                
                info = element.text
                
                if not info == None:
                    info = " ".join(info.split())
                    
                    property = "contact-info-" + str(element.tag).replace(" ", "-")
                    
                    self.graph.add((self.iati['activity/' + self.id + '/contact-info/' + str(hash_contact_info)],
                                    self.iati[property],
                                    Literal(info)))
    
    def participating_org(self, xml):
        '''Converts the XML of the participating-org element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        ref = AttributeHelper.attribute_key(xml, 'ref')
        type = AttributeHelper.attribute_key(xml, 'type')
        role = AttributeHelper.attribute_key(xml, 'role')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not ref == None:
            ref = ref.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-participating-org'],
                            self.iati['activity/' + self.id + '/participating-org/' + str(ref)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(ref)],
                            RDF.type,
                            self.iati['organisation']))
            
            self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(ref)],
                            self.iati['organisation-code'],
                            self.iati['codelist/OrganisationIdentifier/' + str(ref)]))
        
            if not name == None:
                self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(ref)],
                                RDFS.label,
                                name))
                
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(ref)],
                                self.iati['organisation-type'],
                                self.iati['codelist/OrganisationType/' + str(type)]))
                
            if not role == None:
                role = role.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(ref)],
                                self.iati['organisation-role'],
                                self.iati['codelist/OrganisationRole/' + str(role)]))
        
        elif not name == None:
            # Create hash
            # Required: name
            
            hash = hashlib.md5()
            hash.update(name)

            hash_name = hash.hexdigest()
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-participating-org'],
                            self.iati['activity/' + self.id + '/participating-org/' + str(hash_name)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(hash_name)],
                            RDF.type,
                            self.iati['organisation']))

            self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(hash_name)],
                            RDFS.label,
                            name))
                
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(hash_name)],
                                self.iati['organisation-type'],
                                self.iati['codelist/OrganisationType/' + str(type)]))
                
            if not role == None:
                role = role.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/participating-org/' + str(hash_name)],
                                self.iati['organisation-role'],
                                self.iati['codelist/OrganisationRole/' + str(role)]))            
                        
    
    def recipient_country(self, xml):
        '''Converts the XML of the recipient-country element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        percentage = AttributeHelper.attribute_key(xml, 'percentage')
        
        # Text
        country_name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-recipient-country'],
                            self.iati['activity/' + self.id + '/recipient-country/' + str(code)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/recipient-country/' + str(code)],
                            RDF.type,
                            self.iati['country']))
            
            self.graph.add((self.iati['activity/' + self.id + '/recipient-country/' + str(code)],
                            self.iati['country-code'],
                            self.iati['codelist/Country/' + str(code)]))
        
            if not country_name == None:
                self.graph.add((self.iati['activity/' + self.id + '/recipient-country/' + str(code)],
                                RDFS.label,
                                country_name))
                
            if not percentage == None:
                self.graph.add((self.iati['activity/' + self.id + '/recipient-country/' + str(code)],
                                self.iati['percentage'],
                                Literal(percentage)))
    
    def recipient_region(self, xml):
        '''Converts the XML of the recipient-region element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        percentage = AttributeHelper.attribute_key(xml, 'percentage')
        
        # Text
        region_name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-recipient-region'],
                            self.iati['activity/' + self.id + '/recipient-region/' + str(code)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/recipient-region/' + str(code)],
                            RDF.type,
                            self.iati['region']))
            
            self.graph.add((self.iati['activity/' + self.id + '/recipient-region/' + str(code)],
                            self.iati['region-code'],
                            self.iati['codelist/Region/' + str(code)]))
        
            if not region_name == None:
                self.graph.add((self.iati['activity/' + self.id + '/recipient-region/' + str(code)],
                                RDFS.label,
                                region_name))
                
            if not percentage == None:
                self.graph.add((self.iati['activity/' + self.id + '/recipient-region/' + str(code)],
                                self.iati['percentage'],
                                Literal(percentage)))
    
    def location(self, xml):
        '''Converts the XML of the location element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        percentage = AttributeHelper.attribute_key(xml, 'percentage')
        
        # Elements
        name = xml.find('name')
        descriptions = xml.findall('description')
        location_type = xml.find('location-type')
        administrative = xml.find('administrative')
        coordinates = xml.find('coordinates')
        gazetteer_entry = xml.find('gazetteer-entry')
        
        # Create hash
        # Required: one of name, description, administrative (text / country / adm1 / adm2), 
        #                  coordinates (lat / long), gazetteer entry
        
        hash = hashlib.md5()
        hash_created = False
        
        name_text = AttributeHelper.attribute_text(xml, 'name')
        if not name_text == None:
            hash.update(name_text[0])
            hash_created = True
        description_text = AttributeHelper.attribute_text(xml, 'description')
        if not description_text == None:
            hash.update(description_text[0])
            hash_created = True
        administrative_text = AttributeHelper.attribute_text(xml, 'administrative')
        if not administrative_text == None:
            hash.update(administrative_text[0])
            hash_created = True
        gazetteer_entry_text = AttributeHelper.attribute_text(xml, 'gazetteer-entry')
        if not gazetteer_entry_text == None:
            hash.update(gazetteer_entry_text[0])
            hash_created = True
        if not administrative == None:
            # Keys
            administrative_country = AttributeHelper.attribute_key(administrative, 'country')
            administrative_adm1 = AttributeHelper.attribute_key(administrative, 'adm1')
            administrative_adm2 = AttributeHelper.attribute_key(administrative, 'adm2')
            if not administrative_country == None:
                hash.update(administrative_country)
                hash_created = True
            if not administrative_adm1 == None:
                hash.update(administrative_adm1)
                hash_created = True
            if not administrative_adm2 == None:
                hash.update(administrative_adm2)
                hash_created = True
        if not coordinates == None:
            # Keys
            latitude = AttributeHelper.attribute_key(coordinates, 'latitude')
            longitude = AttributeHelper.attribute_key(coordinates, 'longitude')
            if not latitude == None:
                hash.update(latitude)
                hash_created = True
            if not longitude == None:
                hash.update(longitude)
                hash_created = True
                
        if hash_created:
            hash_location = hash.hexdigest()
    
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-location'],
                            self.iati['activity/' + self.id + '/location/' + str(hash_location)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                            RDF.type,
                            self.iati['location']))
            
            if not name == None:
                # Text
                name_text = AttributeHelper.attribute_language(name, self.default_language)
                
                if not name_text == None:
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    RDFS.label,
                                    name_text))
            
            if not descriptions == []:
                
                for description in descriptions:
                    # Keys
                    type = AttributeHelper.attribute_key(description, 'type')
                    
                    # Text
                    description_text = AttributeHelper.attribute_language(description, self.default_language)
                    
                    if not description_text == None:
                        # Create hash
                        # Required: description
            
                        hash_description = hashlib.md5()
                        
                        description_nolanguage = description.text
                        hash_description.update(description_nolanguage)
                        
                        hash_location_description = hash_description.hexdigest()
                        
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                        self.iati['location-description'],
                                        self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                                  '/description/' + str(hash_location_description)]))
                        
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                                  '/description/' + str(hash_location_description)],
                                        RDF.type,
                                        self.iati['description']))
                        
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                                  '/description/' + str(hash_location_description)],
                                        self.iati['description-text'],
                                        description_text))
                        
                        if not type == None:
                            type = type.replace(" ", "%20")
                            
                            self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                                      '/description/' + str(hash_location_description)],
                                            self.iati['description-type'],
                                            self.iati['codelist/DescriptionType/' + str(type)]))  
                        
            
            if not location_type == None:
                # Keys
                location_type_code = AttributeHelper.attribute_key(location_type, 'code')
                
                if not location_type_code == None:
                    location_type_code = location_type_code.replace(" ", "%20")
                    
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    self.iati['location-type'],
                                    self.iati['codelist/LocationType/' + str(location_type_code)]))
            
            if not administrative == None:
                # Keys
                administrative_country = AttributeHelper.attribute_key(administrative, 'country')
                administrative_adm1 = AttributeHelper.attribute_key(administrative, 'adm1')
                administrative_adm2 = AttributeHelper.attribute_key(administrative, 'adm2')
                
                # Text
                administrative_text = AttributeHelper.attribute_language(administrative, self.default_language)
                
                # Create hash
                # Required: one of administrative country / adm1 / adm2 / text
                hash_administrative = hashlib.md5()
                hash_administrative_created= False
                
                administrative_hash_text = AttributeHelper.attribute_text(xml, 'administrative')
                if not administrative_hash_text == None:
                    hash_administrative.update(administrative_hash_text[0])
                    hash_administrative_created= True
                if not administrative_country == None:
                    hash_administrative.update(administrative_country)
                    hash_administrative_created= True
                if not administrative_adm1 == None:
                    hash_administrative.update(administrative_adm1)
                    hash_administrative_created= True
                if not administrative_adm2 == None:
                    hash_administrative.update(administrative_adm2)
                    hash_administrative_created= True
                
                if hash_administrative_created:
                    hash_location_administrative = hash_administrative.hexdigest()
                
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    self.iati['location-administrative'],
                                    self.iati['activity/' + self.id + '/location/' + str(hash_location)
                                              + '/administrative/' + str(hash_location_administrative)]))            
                    
                    if not administrative_country == None:
                        administrative_country = administrative_country.replace(" ", "%20")
                        
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)
                                                  + '/administrative/' + str(hash_location_administrative)],
                                        self.iati['administrative-country'],
                                        self.iati['codelist/Country/' + str(administrative_country)]))
                        
                    if not administrative_adm1 == None:
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)
                                                  + '/administrative/' + str(hash_location_administrative)],
                                        self.iati['administrative-adm1'],
                                        Literal(administrative_adm1)))
                        
                    if not administrative_adm2 == None:
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)
                                                  + '/administrative/' + str(hash_location_administrative)],
                                        self.iati['administrative-adm2'],
                                        Literal(administrative_adm2)))
                        
                    if not administrative_text == None:
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)
                                                  + '/administrative/' + str(hash_location_administrative)],
                                        self.iati['administrative-country-text'],
                                        administrative_text))
            
            if not coordinates == None:
                # Keys
                latitude = AttributeHelper.attribute_key(coordinates, 'latitude')
                longitude = AttributeHelper.attribute_key(coordinates, 'longitude')
                precision = AttributeHelper.attribute_key(coordinates, 'precision')
                    
                if not latitude == None:
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    self.iati['latitude'],
                                    Literal(latitude)))
        
                if not longitude == None:
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    self.iati['longitude'],
                                    Literal(longitude)))
                
                if not precision == None:
                    precision = precision.replace(" ", "%20")
                    
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    self.iati['coordinates-precision'],
                                    self.iati['codelist/GeographicalPrecision/' + str(precision)]))
            
            if not gazetteer_entry == None:
                # Keys
                gazetteer_ref = AttributeHelper.attribute_key(gazetteer_entry, 'gazetteer-ref')
                
                # Text
                gazetteer_entry_text = gazetteer_entry.text
                
                if (not gazetteer_ref == None) and (not gazetteer_entry_text == None):
                    gazetteer_ref = gazetteer_ref.replace(" ", "%20")
                    
                    gazetteer_entry_text = " ".join(gazetteer_entry_text.split())
                
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                    self.iati['location-gazetteer-entry'],
                                    self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                              '/gazetteer-entry/' + str(gazetteer_ref)]))
                    
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                              '/gazetteer-entry/' + str(gazetteer_ref)],
                                    RDF.type,
                                    self.iati['gazetteer-entry']))
                    
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                              '/gazetteer-entry/' + str(gazetteer_ref)],
                                    self.iati['gazetteer-ref'],
                                    self.iati['codelist/GazetteerAgency/' + str(gazetteer_ref)]))
                    
                    self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location) + 
                                              '/gazetteer-entry/' + str(gazetteer_ref)],
                                    self.iati['gazetteer-entry'],
                                    Literal(gazetteer_entry_text)))
                    
                    if gazetteer_ref == "GEO":
                        gazetteer_entry_text = gazetteer_entry_text.replace(" ", "%20")
                        
                        self.graph.add((self.iati['activity/' + self.id + '/location/' + str(hash_location)],
                                        OWL.sameAs,
                                        URIRef("http://sws.geonames.org/" + gazetteer_entry_text)))
                                    
     
    def sector(self, xml):
        '''Converts the XML of the sector element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        vocabulary = AttributeHelper.attribute_key(xml, 'vocabulary')
        percentage = AttributeHelper.attribute_key(xml, 'percentage')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not code == None) and (not vocabulary == None):
            code = code.replace(" ", "%20")
            vocabulary = vocabulary.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-sector'],
                            self.iati['activity/' + self.id + '/sector/' + str(vocabulary) +
                                      '/' + str(code)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/sector/' + str(vocabulary) +
                                      '/' + str(code)],
                            RDF.type,
                            self.iati['sector']))
            
            self.graph.add((self.iati['activity/' + self.id + '/sector/' + str(vocabulary) +
                                      '/' + str(code)],
                            self.iati['sector-code'],
                            self.iati['codelist/Sector/' + str(code)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/sector/' + str(vocabulary) +
                                      '/' + str(code)],
                            self.iati['sector-vocabulary'],
                            self.iati['codelist/Vocabulary/' + str(vocabulary)]))
            
            if not percentage == None:
                self.graph.add((self.iati['activity/' + self.id + '/sector/' + str(vocabulary) +
                                          '/' + str(code)],
                                self.iati['percentage'],
                                Literal(percentage)))
                
            if not name == None:
                self.graph.add((self.iati['activity/' + self.id + '/sector/' + str(vocabulary) +
                                          '/' + str(code)],
                                RDFS.label,
                                name))
    
    def policy_marker(self, xml):
        '''Converts the XML of the policy-marker element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        vocabulary = AttributeHelper.attribute_key(xml, 'vocabulary')
        significance = AttributeHelper.attribute_key(xml, 'significance')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not code == None) and (not vocabulary == None):
            code = code.replace(" ", "%20")
            vocabulary = vocabulary.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-policy-marker'],
                            self.iati['activity/' + self.id + '/policy-marker/' + str(vocabulary) +
                                      '/' + str(code)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/policy-marker/' + str(vocabulary) +
                                      '/' + str(code)],
                            RDF.type,
                            self.iati['policy-marker']))
            
            self.graph.add((self.iati['activity/' + self.id + '/policy-marker/' + str(vocabulary) +
                                      '/' + str(code)],
                            self.iati['policy-marker-code'],
                            self.iati['codelist/PolicyMarker/' + str(code)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/policy-marker/' + str(vocabulary) +
                                      '/' + str(code)],
                            self.iati['policy-marker-vocabulary'],
                            self.iati['codelist/Vocabulary/' + str(vocabulary)]))
            
            if not significance == None:
                significance = significance.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/policy-marker/' + str(vocabulary) +
                                          '/' + str(code)],
                                self.iati['significance-code'],
                                self.iati['codelist/PolicySignificance/' + str(significance)]))
                
            if not name == None:
                self.graph.add((self.iati['activity/' + self.id + '/policy-marker/' + str(vocabulary) +
                                          '/' + str(code)],
                                RDFS.label,
                                name))
    
    def collaboration_type(self, xml):
        '''Converts the XML of the collaboration-type element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-collaboration-type'],
                            self.iati['codelist/CollaborationType/' + str(code)]))
    
    def finance_type(self, xml):
        '''Converts the XML of the default-finance-type element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-default-finance-type'],
                            self.iati['codelist/FinanceType/' + str(code)]))
    
    def flow_type(self, xml):
        '''Converts the XML of the default-flow-type element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-default-flow-type'],
                            self.iati['codelist/FlowType/' + str(code)]))
    
    def aid_type(self, xml):
        '''Converts the XML of the default-aid-type element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-default-aid-type'],
                            self.iati['codelist/AidType/' + str(code)]))
    
    def tied_status(self, xml):
        '''Converts the XML of the default-tied-status element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        code = AttributeHelper.attribute_key(xml, 'code')
        
        if not code == None:
            code = code.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-default-tied-status'],
                            self.iati['codelist/TiedStatus/' + str(code)]))
    
    def budget(self, xml):
        '''Converts the XML of the budget element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        type = AttributeHelper.attribute_key(xml, 'type')
        
        # Elements
        period_start = xml.find('period-start')
        period_end = xml.find('period-end')
        value = xml.find('value')
        
        # Create hash
        # Required: one of value, period-start (iso-date / text), period-end (iso-date / text)
        hash = hashlib.md5()
        hash_created = False
        
        if not period_start == None:
            # Keys
            period_start_date = AttributeHelper.attribute_key(period_start, 'iso-date')
            if not period_start_date == None:
                hash.update(period_start_date)
                hash_created = True
            period_start_text = period_start.text
            if not period_start_text == None:
                hash.update(period_start_text)
                hash_created = True
        if not period_end == None:
            # Keys
            period_end_date = AttributeHelper.attribute_key(period_end, 'iso-date')
            if not period_end_date == None:
                hash.update(period_end_date)
                hash_created = True
            period_end_text = period_end.text
            if not period_end_text == None:
                hash.update(period_end_text)
                hash_created = True
        if not value == None:
            value_text = value.text
            if not value_text == None:
                hash.update(value_text)
                hash_created = True
            
        if hash_created:
            hash_budget = hash.hexdigest()
        
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-budget'],
                            self.iati['activity/' + self.id + '/budget/' + str(hash_budget)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                            RDF.type,
                            self.iati['budget']))
            
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                self.iati['budget-type'],
                                self.iati['codelist/BudgetType/' + str(type)]))
                
            if not period_start == None:
                # Keys
                date = AttributeHelper.attribute_key(period_start, 'iso-date')
                
                # Text
                period_start_text = AttributeHelper.attribute_language(period_start, self.default_language)
                    
                if not date == None:
                    self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                    self.iati['start-date'],
                                    Literal(date)))
                
                if not period_start_text == None:
                    self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                    self.iati['start-date-text'],
                                    period_start_text))
            
            if not period_end == None:
                # Keys
                date = AttributeHelper.attribute_key(period_end, 'iso-date')
                
                # Text
                period_end_text = AttributeHelper.attribute_language(period_end, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                    self.iati['end-date'],
                                    Literal(date)))
                
                if not period_end_text == None:
                    self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                    self.iati['end-date-text'],
                                    period_end_text))
        
            if not value == None:
                # Keys
                currency = AttributeHelper.attribute_key(value, 'currency')
                value_date = AttributeHelper.attribute_key(value, 'value-date')
                
                # Text
                value_text = value.text
                
                if not value_text == None:
                    value_text = " ".join(value_text.split())
                    
                    self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                    self.iati['value'],
                                    Literal(value_text)))
        
                    if not currency == None:
                        currency = currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(currency)]))
                    
                    elif not self.default_currency == None:
                        self.default_currency = self.default_currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(self.default_currency)]))
                    
                    if not value_date == None:
                        self.graph.add((self.iati['activity/' + self.id + '/budget/' + str(hash_budget)],
                                        self.iati['value-date'],
                                        Literal(value_date)))
    
    def planned_disbursement(self, xml):
        '''Converts the XML of the planned-disbursement element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        updated = AttributeHelper.attribute_key(xml, 'updated')
        
        # Elements
        period_start = xml.find('period-start')
        period_end = xml.find('period-end')
        value = xml.find('value')
        
        # Create hash
        # Required: one of value, period-start (iso-date / text), period-end (iso-date / text)
        hash = hashlib.md5()
        hash_created = False
        
        if not period_start == None:
            # Keys
            period_start_date = AttributeHelper.attribute_key(period_start, 'iso-date')
            if not period_start_date == None:
                hash.update(period_start_date)
                hash_created = True
            period_start_text = period_start.text
            if not period_start_text == None:
                hash.update(period_start_text)
                hash_created = True
        if not period_end == None:
            # Keys
            period_end_date = AttributeHelper.attribute_key(period_end, 'iso-date')
            if not period_end_date == None:
                hash.update(period_end_date)
                hash_created = True
            period_end_text = period_end.text
            if not period_end_text == None:
                hash.update(period_end_text)
                hash_created = True
        if not value == None:
            value_text = value.text
            if not value_text == None:
                hash.update(value_text)
                hash_created = True
            
        if hash_created:
            hash_planned_disbursement = hash.hexdigest()

        
        self.graph.add((self.iati['activity/' + self.id],
                        self.iati['activity-planned-disbursement'],
                        self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)]))
        
        self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                        RDF.type,
                        self.iati['planned-disbursement']))
        
        if not updated == None:
            self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                            self.iati['updated'],
                            Literal(updated)))      
            
        if not period_start == None:
            # Keys
            date = AttributeHelper.attribute_key(period_start, 'iso-date')
            
            # Text
            period_start_text = AttributeHelper.attribute_language(period_start, self.default_language)
            
            if not date == None:
                self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                self.iati['start-date'],
                                Literal(date)))
            
            if not period_start_text == None:
                self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                self.iati['start-date-text'],
                                period_start_text))
        
        if not period_end == None:
            # Keys
            date = AttributeHelper.attribute_key(period_end, 'iso-date')
            
            # Text
            period_end_text = AttributeHelper.attribute_language(period_end, self.default_language)
            
            if not date == None:
                self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                self.iati['end-date'],
                                Literal(date)))
            
            if not period_end_text == None:
                self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                self.iati['end-date-text'],
                                period_end_text))
        
        if not value == None:
            # Keys
            currency = AttributeHelper.attribute_key(value, 'currency')
            value_date = AttributeHelper.attribute_key(value, 'value-date')
            
            # Text
            value_text = value.text
            
            if not value_text == None:
                value_text = " ".join(value_text.split())
                
                self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                self.iati['value'],
                                Literal(value_text)))
                
                if not currency == None:
                    currency = currency.replace(" ", "%20")
                    
                    self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                    self.iati['value-currency'],
                                    self.iati['codelist/Currency/' + str(currency)]))
                
                elif not self.default_currency == None:
                    self.default_currency = self.default_currency.replace(" ", "%20")
                    
                    self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                    self.iati['value-currency'],
                                    self.iati['codelist/Currency/' + str(self.default_currency)]))
                
                if not value_date == None:
                    self.graph.add((self.iati['activity/' + self.id + '/planned-disbursement/' + str(hash_planned_disbursement)],
                                    self.iati['value-date'],
                                    Literal(value_date)))
    
    def transaction(self, xml):
        '''Converts the XML of the transaction element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        ref = AttributeHelper.attribute_key(xml, 'ref')
        
        # Elements
        aid_type = xml.find('aid-type')
        descriptions = xml.findall('description')
        disbursement_channel = xml.find('disbursement-channel')
        finance_type = xml.find('finance-type')
        flow_type = xml.find('flow-type')
        provider_org = xml.find('provider-org')
        receiver_org = xml.find('receiver-org')
        tied_status = xml.find('tied-status')
        transaction_date = xml.find('transaction-date')
        transaction_type = xml.find('transaction-type')
        value = xml.find('value')
        
        # Create hash
        # Required: one of value, description, transaction date
        
        hash = hashlib.md5()
        hash_created = False
        
        value_text = AttributeHelper.attribute_text(xml, 'value')
        if not value_text == None:
            hash.update(value_text[0])
            hash_created = True
        description_text = AttributeHelper.attribute_text(xml, 'description')
        if not description_text == None:
            hash.update(description_text[0])
            hash_created = True
        if not transaction_date == None:
            # Keys
            iso_date = AttributeHelper.attribute_key(transaction_date, 'iso-date')
            if not iso_date == None:
                hash.update(iso_date)
                hash_created = True
                
        if (hash_created) or (not ref == None):
            hash_transaction = hash.hexdigest()
        
            if not ref == None:
                ref_url = ref.replace(" ", "%20")
                
                transaction_id = self.iati['activity/' + self.id + '/transaction/' + str(ref_url)]
    
                self.graph.add((transaction_id,
                                self.iati['transaction-ref'],
                                Literal(ref)))            
                
            else:
                transaction_id = self.iati['activity/' + self.id + '/transaction/' + str(hash_transaction)]
                
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-transaction'],
                            transaction_id))        
            
            self.graph.add((transaction_id,
                            RDF.type,
                            self.iati['transaction']))
            
            if not aid_type == None:
                # Keys
                code = AttributeHelper.attribute_key(aid_type, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['aid-type'],
                                    self.iati['codelist/AidType/' + str(code)]))
                    
                elif not self.default_aid_type == None:
                    self.default_aid_type = self.default_aid_type.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['aid-type'],
                                    self.iati['codelist/AidType/' + str(self.default_aid_type)]))
                
            elif not self.default_aid_type == None:
                self.default_aid_type = self.default_aid_type.replace(" ", "%20")
                
                self.graph.add((transaction_id,
                                self.iati['aid-type'],
                                self.iati['codelist/AidType/' + str(self.default_aid_type)]))
                
            if not descriptions == []:
                
                for description in descriptions:
                    # Keys
                    type = AttributeHelper.attribute_key(description, 'type')
                    
                    # Text
                    description_text = AttributeHelper.attribute_language(description, self.default_language)
                    
                    if not description_text == None:

                        # Create hash
                        # Required: description
            
                        hash_description = hashlib.md5()
                        
                        description_nolanguage = description.text
                        hash_description.update(description_nolanguage)
                    
                        hash_transaction_description = hash_description.hexdigest()
                        
                        self.graph.add((transaction_id,
                                        self.iati['transaction-description'],
                                        URIRef(transaction_id + '/description/' + str(hash_transaction_description))))
                        
                        self.graph.add((URIRef(transaction_id + '/description/' + str(hash_transaction_description)),
                                        RDF.type,
                                        self.iati['description']))
                        
                        self.graph.add((URIRef(transaction_id + '/description/' + str(hash_transaction_description)),
                                        self.iati['description-text'],
                                        description_text))
                        
                        if not type == None:
                            type = type.replace(" ", "%20")
                            
                            self.graph.add((URIRef(transaction_id + '/description/' + str(hash_transaction_description)),
                                            self.iati['description-type'],
                                            self.iati['codelist/DescriptionType/' + str(type)]))  
            
            if not disbursement_channel == None:
                # Keys
                code = AttributeHelper.attribute_key(disbursement_channel, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['disbursement-channel'],
                                    self.iati['codelist/disbursementChannel/' + str(code)]))
            
            if not finance_type == None:
                # Keys
                code = AttributeHelper.attribute_key(finance_type, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['finance-type'],
                                    self.iati['codelist/FinanceType/' + str(code)]))
                    
                elif not self.default_finance_type == None:
                    self.default_finance_type = self.default_finance_type.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['finance-type'],
                                    self.iati['codelist/FinanceType/' + str(self.default_finance_type)]))
                
            elif not self.default_finance_type == None:
                self.default_finance_type = self.default_finance_type.replace(" ", "%20")
                
                self.graph.add((transaction_id,
                                self.iati['finance-type'],
                                self.iati['codelist/FinanceType/' + str(self.default_finance_type)]))
            
            if not flow_type == None:
                # Keys
                code = AttributeHelper.attribute_key(flow_type, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['flow-type'],
                                    self.iati['codelist/FlowType/' + str(code)]))
                    
                elif not self.default_flow_type == None:
                    self.default_flow_type = self.default_flow_type.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['flow-type'],
                                    self.iati['codelist/FlowType/' + str(self.default_flow_type)]))
                
            elif not self.default_flow_type == None:
                self.default_flow_type = self.default_flow_type.replace(" ", "%20")
                
                self.graph.add((transaction_id,
                                self.iati['flow-type'],
                                self.iati['codelist/FlowType/' + str(self.default_flow_type)]))
            
            if not provider_org == None:
                # Keys
                ref = AttributeHelper.attribute_key(provider_org, 'ref')
                provider_activity_id = AttributeHelper.attribute_key(provider_org, 'provider-activity-id')
                
                # Text
                provider_org_text = provider_org.text      
                
                if not provider_org_text == None:
                    provider_org_text = " ".join(provider_org_text.split())
                    
                    self.graph.add((transaction_id,
                                    self.iati['provider-org-name'],
                                    Literal(provider_org_text)))
                
                if not ref == None:
                    ref = ref.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['provider-org'],
                                    self.iati['codelist/OrganisationIdentifier/' + str(ref)]))
                
                if not provider_activity_id == None:
                    provider_activity_id = provider_activity_id.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['provider-org-activity-id'],
                                    self.iati['activity/' + str(provider_activity_id)]))
                    
            if not receiver_org == None:
                # Keys
                ref = AttributeHelper.attribute_key(receiver_org, 'ref')
                receiver_activity_id = AttributeHelper.attribute_key(receiver_org, 'receiver-activity-id')
                
                # Text
                receiver_org_text = receiver_org.text      
                
                if not receiver_org_text == None:
                    receiver_org_text = " ".join(receiver_org_text.split())
                    
                    self.graph.add((transaction_id,
                                    self.iati['receiver-org-name'],
                                    Literal(receiver_org_text)))                
                
                if not ref == None:
                    ref = ref.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['receiver-org'],
                                    self.iati['codelist/OrganisationIdentifier/' + str(ref)]))
                
                if not receiver_activity_id == None:
                    receiver_activity_id = receiver_activity_id.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['receiver-org-activity-id'],
                                    self.iati['activity/' + str(receiver_activity_id)]))
        
            if not tied_status == None:
                # Keys
                code = AttributeHelper.attribute_key(tied_status, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['tied-status'],
                                    self.iati['codelist/TiedStatus/' + str(code)]))
                    
                elif not self.default_tied_status == None:
                    self.default_tied_status = self.default_tied_status.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['tied-status'],
                                    self.iati['codelist/TiedStatus/' + str(self.default_tied_status)]))
                
            elif not self.default_tied_status == None:
                self.default_tied_status = self.default_tied_status.replace(" ", "%20")
                
                self.graph.add((transaction_id,
                                self.iati['tied-status'],
                                self.iati['codelist/TiedStatus/' + str(self.default_tied_status)]))
            
            if not transaction_date == None:
                # Keys
                iso_date = AttributeHelper.attribute_key(transaction_date, 'iso-date')
                
                if not iso_date == None:
                    self.graph.add((transaction_id,
                                    self.iati['transaction-date'],
                                    Literal(iso_date)))
                
            if not transaction_type == None:
                # Keys
                code = AttributeHelper.attribute_key(transaction_type, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((transaction_id,
                                    self.iati['transaction-type'],
                                    self.iati['codelist/TransactionType/' + str(code)]))            
                                             
            if not value == None:
                # Keys
                currency = AttributeHelper.attribute_key(value, 'currency')
                value_date = AttributeHelper.attribute_key(value, 'value-date')
                
                # Text
                value_text = value.text
                
                if not value_text == None:
                    value_text = " ".join(value_text.split())
                    
                    self.graph.add((transaction_id,
                                    self.iati['value'],
                                    Literal(value_text)))
                    
                    if not currency == None:
                        currency = currency.replace(" ", "%20")
                        
                        self.graph.add((transaction_id,
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(currency)]))
                    
                    elif not self.default_currency == None:
                        self.default_currency = self.default_currency.replace(" ", "%20")
                        
                        self.graph.add((transaction_id,
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(self.default_currency)]))
                    
                    if not value_date == None:
                        self.graph.add((transaction_id,
                                        self.iati['value-date'],
                                        Literal(value_date)))
    
    def document_link(self, xml):
        '''Converts the XML of the document-link element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        url = AttributeHelper.attribute_key(xml, 'url')
        format = AttributeHelper.attribute_key(xml, 'format')
        
        # Elements
        titles = xml.findall('title')
        category = xml.find('category')
        languages = xml.findall('language')
        
        if not url == None:
            # Create hash
            # Required: url
            
            hash = hashlib.md5()
            hash.update(url)
            
            hash_document_link = hash.hexdigest()
            
            url = url.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-document-link'],
                            self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)]))
            
            self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                            RDF.type,
                            self.iati['document-link']))  
            
            self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                            self.iati['url'],
                            URIRef(url)))
        
            if not format == None:
                format = format.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                                self.iati['format'],
                                self.iati['codelist/FileFormat/' + str(format)]))
                
            if not titles == []:
                for title in titles:
                    # Text
                    name = AttributeHelper.attribute_language(title, self.default_language)
                    
                    if not name == None:
                        self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                                        RDFS.label,
                                        name))
                    
            if not category == None:
                # Keys
                code = AttributeHelper.attribute_key(category, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                    
                    self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                                    self.iati['document-category'],
                                    self.iati['codelist/DocumentCategory/' + str(code)]))
            
            if not languages == []:
                for language in languages:
                    # Keys
                    code = AttributeHelper.attribute_key(language, 'code')
                    
                    # Text
                    name = AttributeHelper.attribute_language(language, self.default_language)
                    
                    if not code == None:
                        self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                                        self.iati['language'],
                                        Literal(code)))
                        
                    if not name == None:
                        self.graph.add((self.iati['activity/' + self.id + 'document-link/' + str(hash_document_link)],
                                        self.iati['language-text'],
                                        name))
    
    def related_activity(self, xml):
        '''Converts the XML of the related-activity element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        ref = AttributeHelper.attribute_key(xml, 'ref')
        type = AttributeHelper.attribute_key(xml, 'type')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not ref == None:
            ref = ref.replace(" ", "%20")
            
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['related-activity'],
                            self.iati['activity/' + self.id + '/related-activity/' + str(ref)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/related-activity/' + str(ref)],
                            self.iati['activity'],
                            self.iati['activity/' + str(ref)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/related-activity/' + str(ref)],
                            self.iati['related-activity-id'],
                            Literal(ref)))
            
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.iati['activity/' + self.id + '/related-activity/' + str(ref)],
                                self.iati['related-activity-type'],
                                self.iati['codelist/RelatedActivityType/' + str(type)]))
        
            if not name == None:
                self.graph.add((self.iati['activity/' + self.id + '/related-activity/' + str(ref)],
                                RDFS.label,
                                name))
    
    def conditions(self, xml):
        '''Converts the XML of the conditions element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Elements
        conditions_container = xml.find('conditions')
        conditions = conditions_container.findall('condition')
        
        if not conditions == []:
            
            for condition in conditions:
                # Keys
                type = AttributeHelper.attribute_key(condition, 'type')
                
                # Text
                condition_text = AttributeHelper.attribute_language(condition, self.default_language)
                
                if not condition_text == None:
                    condition_text_text = condition.text
                    
                    #Create hash
                    hash = hashlib.md5()
                    hash.update(condition_text_text)
                    
                    hash_condition = hash.hexdigest()
                    
                    self.graph.add((self.iati['activity/' + self.id],
                                    self.iati['activity-condition'],
                                    self.iati['activity/' + self.id + '/condition/' + str(hash_condition)]))
                   
                    self.graph.add((self.iati['activity/' + self.id + '/condition/' + str(hash_condition)],
                                    RDF.type,
                                    self.iati['condition']))
                   
                    self.graph.add((self.iati['activity/' + self.id + '/condition/' + str(hash_condition)],
                                    RDFS.label,
                                    condition_text))
                   
                    if not type == None:
                        type = type.replace(" ", "%20")
                        
                        self.graph.add((self.iati['activity/' + self.id + '/condition/' + str(hash_condition)],
                                        self.iati['condition-type'],
                                        self.iati['codelist/ConditionType/' + str(type)]))                                          

    
    def result(self, xml):
        '''Converts the XML of the conditions element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        type = AttributeHelper.attribute_key(xml, 'type')
        aggregation_status = AttributeHelper.attribute_key(xml, 'aggregation-status')
        
        # Elements
        titles = xml.findall('title')
        descriptions = xml.findall('description')
        indicators = xml.findall('indicator')

        # Create hash
        # Required: one of title or description
        
        hash = hashlib.md5()
        hash_created = False
        
        result_title = AttributeHelper.attribute_text(xml, 'title')
        if not result_title == None:
            hash.update(result_title[0])
            hash_created = True
        result_description = AttributeHelper.attribute_text(xml, 'description')
        if not result_description == None:
            hash.update(result_description[0])
            hash_created = True
        
        if hash_created:
            hash_result = hash.hexdigest()
        
            self.graph.add((self.iati['activity/' + self.id],
                            self.iati['activity-result'],
                            self.iati['activity/' + self.id + '/result/' + str(hash_result)]))
            
            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result)],
                            RDF.type,
                            self.iati['result']))    
            
            if not titles == []:
                for title in titles:
                    # Text
                    title_text = AttributeHelper.attribute_language(title, self.default_language)
                    
                    if not title_text == None:
                        self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result)],
                                        RDFS.label,
                                        title_text))
            
            if not descriptions == []:
                for description in descriptions:
                    # Keys
                    type = AttributeHelper.attribute_key(description, 'type')
                    
                    # Text
                    description_text = AttributeHelper.attribute_language(description, self.default_language)
                    
                    if not description_text == None:
                        # Create hash
                        # Required: description
            
                        hash_description = hashlib.md5()
                        
                        description_nolanguage = description.text
                        hash_description.update(description_nolanguage)
                        
                        hash_location_description = hash_description.hexdigest()
                        
                        self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result)],
                                        self.iati['result-description'],
                                        self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                  '/description/' + str(hash_location_description)]))
                        
                        self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                  '/description/' + str(hash_location_description)],
                                        RDF.type,
                                        self.iati['description']))
                        
                        self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                  '/description/' + str(hash_location_description)],
                                        self.iati['description-text'],
                                        description_text))
                        
                        if not type == None:
                            type = type.replace(" ", "%20")
                            
                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                      '/description/' + str(hash_location_description)],
                                            self.iati['description-type'],
                                            self.iati['codelist/DescriptionType/' + str(type)]))                                   
                
            if not indicators == []:
                
                for indicator in indicators:
                    # Create hash
                    # Required: one of title or description
                    
                    hash = hashlib.md5()
                    hash_created = False
                    
                    indicator_title = AttributeHelper.attribute_text(indicator, 'title')
                    if not indicator_title == None:
                        hash.update(indicator_title[0])
                        hash_created = True
                    indicator_description = AttributeHelper.attribute_text(indicator, 'description')
                    if not indicator_description == None:
                        hash.update(indicator_description[0])
                        hash_created = True
                    
                    if hash_created:
                        hash_result_indicator = hash.hexdigest()
                    
                        # Keys
                        measure = AttributeHelper.attribute_key(indicator, 'measure')
                        ascending = AttributeHelper.attribute_key(indicator, 'ascending')
                        
                        # Elements
                        titles = indicator.findall('title')
                        descriptions = indicator.findall('description')
                        periods = indicator.findall('indicator')
                        baseline = indicator.find('baseline')
                        
                        self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result)],
                                        self.iati['result-indicator'],
                                        self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                  '/indicator/' + str(hash_result_indicator)]))
                        
                        self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                  '/indicator/' + str(hash_result_indicator)],
                                        RDF.type,
                                        self.iati['indicator']))
                        
                        if not measure == None:
                            measure = measure.replace(" ", "%20")
                            
                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                      '/indicator/' + str(hash_result_indicator)],
                                            self.iati['indicator-measure'],
                                            self.iati['codelist/IndicatorMeasure/' + str(measure)]))
                        
                        if not ascending == None:
                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                      '/indicator/' + str(hash_result_indicator)],
                                            self.iati['indicator-ascending'],
                                            Literal(ascending)))
                        
                        else:
                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                      '/indicator/' + str(hash_result_indicator)],
                                            self.iati['indicator-ascending'],
                                            Literal('True')))                    
            
                        if not titles == []:
                            for title in titles:
                                # Text
                                title_text = AttributeHelper.attribute_language(title, self.default_language)
                                
                                if not title_text == None:
                                    self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator)],
                                                    RDFS.label,
                                                    title_text))
            
                        if not descriptions == []:
                            
                            for description in descriptions:
                                # Keys
                                type = AttributeHelper.attribute_key(description, 'type')
                                
                                # Text
                                description_text = AttributeHelper.attribute_language(description, self.default_language)
                                
                                # Create hash
                                # Required: description
                    
                                hash_indicator_description = hashlib.md5()
                                
                                description_nolanguage = description.text
                                hash_indicator_description.update(description_nolanguage)
                                
                                hash_result_indicator_description = hash_indicator_description.hexdigest()
                                
                                if not description_text == None:
                                    self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator)],
                                                    self.iati['indicator-description'],
                                                    self.iati['activity/' + self.id + '/result' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator) + '/description/' + 
                                                              str(hash_result_indicator_description)]))
                                    
                                    self.graph.add((self.iati['activity/' + self.id + '/result' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator) + '/description/' + 
                                                              str(hash_result_indicator_description)],
                                                    RDF.type,
                                                    self.iati['description']))
                                    
                                    self.graph.add((self.iati['activity/' + self.id + '/result' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator) + '/description/' + 
                                                              str(hash_result_indicator_description)],
                                                    self.iati['description-text'],
                                                    description_text))
                                    
                                    if not type == None:
                                        type = type.replace(" ", "%20")
                                        
                                        self.graph.add((self.iati['activity/' + self.id + '/result' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator) + '/description/' + 
                                                              str(hash_result_indicator_description)],
                                                        self.iati['description-type'],
                                                        self.iati['codelist/DescriptionType/' + str(type)]))                                   
                                
                        
                        if not periods == []:
                            
                            for period in periods:
                                # Elements
                                period_start = period.find('period-start')
                                period_end = period.find('period-end')
                                target = period.find('target')
                                actual = period.find('actual')
                                
                                # Create hash
                                # Required: one of period-start (iso-date / text), period-end (iso-date / text)
                                hash_indicator_period = hashlib.md5()
                                hash_indicator_period_created= False
                                
                                if not period_start == None:
                                    # Keys
                                    period_start_date = AttributeHelper.attribute_key(period_start, 'iso-date')
                                    if not period_start_date == None:
                                        hash_indicator_period.update(period_start_date)
                                        hash_indicator_period_created = True
                                    period_start_text = period_start.text
                                    if not period_start_text == None:
                                        hash_indicator_period.update(period_start_text)
                                        hash_indicator_period_created = True
                                if not period_end == None:
                                    # Keys
                                    period_end_date = AttributeHelper.attribute_key(period_end, 'iso-date')
                                    if not period_end_date == None:
                                        hash_indicator_period.update(period_end_date)
                                        hash_indicator_period_created = True
                                    period_end_text = period_end.text
                                    if not period_end_text == None:
                                        hash_indicator_period.update(period_end_text)
                                        hash_indicator_period_created = True
                                
                                if hash_indicator_period_created:
                                
                                    hash_result_indicator_period = hash_indicator_period.hexdigest()
                                    
                                    self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator)],
                                                    self.iati['indicator-period'],
                                                    self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                              str(hash_result_indicator_period)]))
                                    
                                    self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                              str(hash_result_indicator_period)],
                                                    RDF.type,
                                                    self.iati['period']))                                             
                                    
                                    if not period_start == None:
                                        # Keys
                                        date = AttributeHelper.attribute_key(period_start, 'iso-date')
                                        
                                        # Text
                                        period_start_text = AttributeHelper.attribute_language(period_start, self.default_language)
                                        
                                        if not date == None:
                                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                                      '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                                      str(hash_result_indicator_period)],
                                                            self.iati['start-date'],
                                                            Literal(date)))
                                        
                                        if not period_start_text == None:
                                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                                      '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                                      str(hash_result_indicator_period)],
                                                            self.iati['start-date-text'],
                                                            period_start_text))
                                        
                                    if not period_end == None:
                                        # Keys
                                        date = AttributeHelper.attribute_key(period_end, 'iso-date')
                                        
                                        # Text
                                        period_end_text = AttributeHelper.attribute_language(period_end, self.default_language)
                                        
                                        if not date == None:
                                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                                      '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                                      str(hash_result_indicator_period)],
                                                            self.iati['end-date'],
                                                            Literal(date)))
                                        
                                        if not period_end_text == None:
                                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                                      '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                                      str(hash_result_indicator_period)],
                                                            self.iati['end-date-text'],
                                                            period_end_text))
                                    
                                    if not target == None:
                                        # Keys
                                        value = AttributeHelper.attribute_key(target, 'value')
                                        
                                        if not value == None:
                                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                                      '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                                      str(hash_result_indicator_period)],
                                                            self.iati['period-target'],
                                                            Literal(value)))
                                        
                                    if not actual == None:
                                        # Keys
                                        value = AttributeHelper.attribute_key(actual, 'value')
                                        
                                        if not value == None:
                                            self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                                      '/indicator/' + str(hash_result_indicator) + '/period/' +
                                                                      str(hash_result_indicator_period)],
                                                            self.iati['period-actual'],
                                                            Literal(value)))
                                
                        if not baseline == None:
                            # Keys
                            year = AttributeHelper.attribute_key(baseline, 'year')
                            value = AttributeHelper.attribute_key(baseline, 'value')
                            
                            # Elements
                            comment = baseline.find('comment')                      
                            
                            if not value == None:
                                self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                          '/indicator/' + str(hash_result_indicator)],
                                                self.iati['baseline-value'],
                                                Literal(value)))
                                
                            if not year == None:
                                self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                          '/indicator/' + str(hash_result_indicator)],
                                                self.iati['baseline-year'],
                                                Literal(year)))
                            
                            if not comment == None:
                                # Text
                                comment_text = AttributeHelper.attribute_language(comment, self.default_language)
                                
                                if not comment_text == None:
                                    self.graph.add((self.iati['activity/' + self.id + '/result/' + str(hash_result) + 
                                                              '/indicator/' + str(hash_result_indicator)],
                                                    self.iati['baseline-comment'],
                                                    comment_text))


class CodelistElements :
    '''Class for converting XML elements of IATI codelists to a RDFLib self.graph.'''
    
    def __init__(self, defaults): 
        '''Initializes class.
        
        Parameters
        @defaults: A dictionary of defaults.'''
        
        self.id = defaults['id']
        self.default_language = defaults['language']
        
        self.iati = Namespace(defaults['namespace'])
        self.codelist = Namespace(self.iati['codelist/'])
        self.codelist_uri = Namespace(self.codelist[str(self.id) + '/'])
        
        self.graph = Graph()
        
        self.graph.bind('iati', self.iati)
        self.graph.bind('codelist', self.codelist)
        self.graph.bind(self.id, self.codelist_uri)

    def get_result(self):
        '''Returns the resulting self.graph of the activity.
        
        Returns
        @graph: The RDFLib self.graph with added statements.'''
        
        return self.graph
    
    def code(self, xml, code, language, category_code):
        '''Converts the XML of the code element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        code = xml.text
        
        if not code == None:
            code = " ".join(code.split())
            
            self.graph.add((self.codelist[str(self.id)],
                            self.iati['codelist-member'],
                            self.codelist_uri[code]))
            
            self.graph.add((self.codelist_uri[code],
                            self.iati['member-of-codelist'],
                            self.codelist[str(self.id)]))
            
            self.graph.add((self.codelist_uri[code],
                            self.iati['code'],
                            Literal(code)))
            
            self.graph.add((self.codelist_uri[code],
                            RDF.type,
                            self.iati['codelist-code']))            
    
    def language(self, xml, code, language, category_code):
        '''Converts the XML of the language element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Skipped
        
        skip = True
        
    def name(self, xml, code, language, category_code):
        '''Converts the XML of the name element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        if not language == None:
            name = AttributeHelper.attribute_language(xml, language[0])
        else:
            name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not code == None) and (not name == None):            
            self.graph.add((self.codelist_uri[code[0]],
                            RDFS.label,
                            name))

    def description(self, xml, code, language, category_code):
        '''Converts the XML of the description element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        if not language == None:
            description = AttributeHelper.attribute_language(xml, language[0])
        else:
            description = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not code == None) and (not description == None):            
            self.graph.add((self.codelist_uri[code[0]],
                            RDFS.comment,
                            description))

    def abbreviation(self, xml, code, language, category_code):
        '''Converts the XML of the abbreviation element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        if not language == None:
            abbreviation = AttributeHelper.attribute_language(xml, language[0])
        else:
            abbreviation = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not code == None) and (not abbreviation == None):            
            self.graph.add((self.codelist_uri[code[0]],
                            self.iati['abbreviation'],
                            abbreviation))

    def category(self, xml, code, language, category_code):
        '''Converts the XML of the category element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        category = xml.text
        
        if not category == None:
            category = " ".join(category.split())

            self.graph.add((self.codelist['category/' + category],
                            RDF.type,
                            self.iati['codelist-category']))
            
            self.graph.add((self.codelist_uri[code[0]],
                            self.iati['in-category'],
                            self.codelist['category/' + category]))
            
            self.graph.add((self.codelist['category/' + category],
                            self.iati['has-member'],
                            self.codelist_uri[code[0]]))
            
            self.graph.add((self.codelist['category/' + category],
                            self.iati['code'],
                            Literal(category)))

    def category_name(self, xml, code, language, category_code):
        '''Converts the XML of the category-name element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        if not language == None:
            name = AttributeHelper.attribute_language(xml, language[0])
        else:
            name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not category_code == None) and (not name == None):            
            self.graph.add((self.codelist['category/' + category_code[0]],
                            RDFS.label,
                            name))

    def category_description(self, xml, code, language, category_code):
        '''Converts the XML of the category-description element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.
        @code: A list of codes or None.
        @language: A list of languages or None.
        @category_code: A list of category codes or None.'''
        
        # Text
        if not language == None:
            description = AttributeHelper.attribute_language(xml, language[0])
        else:
            description = AttributeHelper.attribute_language(xml, self.default_language)
        
        if (not category_code == None) and (not description == None):            
            self.graph.add((self.codelist['category/' + category_code[0]],
                            RDFS.comment,
                            description))

class OrganisationElements :
    '''Class for converting XML elements of IATI organisations to a RDFLib self.graph.'''
    
    def __init__(self, defaults): 
        '''Initializes class.
        
        Parameters
        @defaults: A dictionary of defaults.'''
        
        self.id = defaults['id'].replace(" ", "%20")
        self.default_language = defaults['language']
        self.default_currency = defaults['currency']
        
        self.iati = Namespace(defaults['namespace'])
        self.iati_custom = Namespace(defaults['namespace'] + "custom/")
        self.org_uri = Namespace(self.iati['organisation/' + self.id])
        
        self.graph = Graph()
        self.graph.bind('iati', self.iati)
        self.graph.bind('iati-custom', self.iati_custom)
        self.graph.bind('owl', 'http://www.w3.org/2002/07/owl#')
        
        self.graph.add((self.org_uri,
                        RDF.type,
                        self.iati['organisation']))
        
        self.graph.add((self.org_uri,
                        OWL.sameAs,
                        self.iati['codelist/OrganisationIdentifier/' + self.id]))
        
        self.graph.add((self.iati['codelist/OrganisationIdentifier/' + self.id],
                        OWL.sameAs,
                        self.org_uri))
       

    def __update_progress(self, element):
        '''Updates the progress of the number of elements.
        
        Parameters
        @element: A string of the element name.'''
        
        try:
            self.progress[element] += 1
        except KeyError:
            self.progress[element] = 1

            
    def get_result(self):
        '''Returns the resulting self.graph of the activity.
        
        Returns
        @graph: The RDFLib self.graph with added statements.'''
        
        return self.graph
    
    def process_unknown_tag(self, tag):
        '''Returns the correct tag for use in unknown elements.
        
        Parameters
        @tag: The original tag.
        
        Returns
        @namespace: The RDFLib Namespace to be used.
        @name: The name of the tag.'''
        
        tag = tag.replace("{", "").replace("}", "")
        
        if ":" in tag:
            if tag[:4] == "http":
                return Namespace(tag.replace(" ", "-")), tag.rsplit('/',1)[1].replace(" ", "%20")
            
            else:
                tag = tag.split(":")[1]
                if tag[:9] == "organisation-":
                    return Namespace(self.iati[tag.replace(" ", "-")]), tag.replace(" ", "%20")
                else:
                    return Namespace(self.iati["organisation-" + tag.replace(" ", "-")]), str("organisation-" + tag.replace(" ", "%20"))
        else:
            if tag[:9] == "activity-":
                return Namespace(self.iati[tag.replace(" ", "-")]), tag.replace(" ", "%20")
            
            else:
                return Namespace(self.iati["organisation-" + tag.replace(" ", "-")]), str("organisation-" + tag.replace(" ", "%20"))
    
    def convert_unknown(self, xml):
        '''Converts non-IATI standard elements up to 2 levels to a RDFLib self.graph.
        
        Parameters:
        @xml: The XML of this element.'''
        
        if not "ignore" in xml.tag:
            
            namespace, name = self.process_unknown_tag(xml.tag)
            
            children_elements = xml.findall("./")
                
            if children_elements == []:
                # No children
                if (not xml.text == None) and (not xml.text == ""):
                    if len(xml.text) > 1:
                        self.graph.add((self.iati['organisation/' + self.id],
                                        namespace,
                                        Literal(xml.text)))
                        
                for key in xml.attrib:
                    key_text = xml.attrib[key]
                    if "}" in key:
                        key = key.rsplit('}',1)[1]
                    if (not key_text == None) and (not key_text == ""):
                        self.graph.add((self.iati['organisation/' + self.id],
                                        URIRef(namespace + '-' + str(key)),
                                        Literal(key_text)))
                        
            else:
                # Does have children
                
                self.graph.add((self.iati['organisation/' + self.id],
                                namespace,
                                self.iati['organisation/' + self.id + '/' + str(name)]))
                
                for key in xml.attrib:
                    key_text = xml.attrib[key]
                    if "}" in key:
                        key = key.rsplit('}',1)[1]
                    if (not key_text == None) and (not key_text == ""):
                        key = key.replace(" ", "-")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/' + str(name)],
                                        self.iati_custom[str(key)],
                                        Literal(key_text)))
                
                for child in xml:
                    children_elements = child.findall("./")
                    
                    child_namespace, child_name = self.process_unknown_tag(child.tag)
                    
                    if children_elements == []:
                        # No grand-children
                        if not child.text == None:
                            if len(child.text) > 1:
                                self.graph.add((self.iati['organisation/' + self.id + '/' + str(name)],
                                                child_namespace,
                                                Literal(child.text)))
                                
                        for key in child.attrib:
                            key_text = child.attrib[key]
                            if "}" in key:
                                key = key.rsplit('}',1)[1]
                            if (not key_text == None) and (not key_text == ""):
                                key = key.replace(" ", "-")
                                
                                self.graph.add((self.iati['organisation/' + self.id + '/' + str(name)],
                                                URIRef(child_namespace + '-' + str(key)),
                                                Literal(key_text)))
                                
                    else:
                        # Has grand-children
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/' + str(name)],
                                        URIRef(namespace + '-' + str(child_name)),
                                        self.iati['organisation/' + self.id + '/' + str(name) + '/' + str(child_name)]))
                        
                        for key in child.attrib:
                            key_text = child.attrib[key]
                            if "}" in key:
                                key = key.rsplit('}',1)[1]
                            if (not key_text == None) and (not key_text == ""):
                                key = key.replace(" ", "-")
                                
                                self.graph.add((self.iati['organisation/' + self.id + '/' + str(name) + '/' + str(child_name)],
                                                self.iati_custom[str(key)],
                                                Literal(key_text)))
                            
                        for grandchild in child:
                            grandchildren_elements = grandchild.findall("./")
                            
                            grandchild_namespace, grandchild_name = self.process_unknown_tag(grandchild.tag)
                                
                            if grandchildren_elements == []:
                                # No grand-grand-children
                                
                                if not grandchild == None:
                                    if len(grandchild.text) > 1:
                                        self.graph.add((self.iati['organisation/' + self.id + '/' + str(name) + '/' + str(child_name)],
                                                        grandchild_namespace,
                                                        Literal(grandchild.text)))
                                        
                                for key in grandchild.attrib:
                                    key_text = grandchild.attrib[key]
                                    if "}" in key:
                                        key = key.rsplit('}',1)[1]
                                    if (not key_text == None) and (not key_text == ""):
                                        key = key.replace(" ", "-")
                                        
                                        self.graph.add((self.iati['organisation/' + self.id + '/' + str(name) + '/' + str(child_name)],
                                                        URIRef(grandchild_namespace + '-' + str(key)),
                                                        Literal(key_text)))
                                        
                            else:
                                # Three levels
                                print "Three levels for a non-IATI element (" + str(name) + ") is not supported..."
    
    def reporting_org(self, xml):
        '''Converts the XML of the reporting-org element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        ref = AttributeHelper.attribute_key(xml, 'ref')
        type = AttributeHelper.attribute_key(xml, 'type')
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not ref == None:
            ref = ref.replace(" ", "%20")
            
            self.graph.add((self.org_uri,
                            self.iati['organisation-reporting-org'],
                            self.org_uri['/reporting-org/' + str(ref)]))
            
            self.graph.add((self.org_uri['/reporting-org/' + str(ref)],
                            OWL.sameAs,
                            self.iati['codelist/OrganisationIdentifier/' + str(ref)]))
            
            self.graph.add((self.org_uri['/reporting-org/' + str(ref)],
                            RDF.type,
                            self.iati['organisation']))
        
            if not name == None:
                self.graph.add((self.org_uri['/reporting-org/' + str(ref)],
                                RDFS.label,
                                name))
                
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.org_uri['/reporting-org/' + str(ref)],
                                self.iati['organisation-type'],
                                self.iati['codelist/OrganisationType/' + str(type)]))
                
        elif not name == None:
            # Create hash
            # Required: name
            
            hash = hashlib.md5()
            hash.update(name)

            hash_name = hash.hexdigest()
            
            self.graph.add((self.org_uri['/reporting-org/' + str(hash_name)],
                            RDF.type,
                            self.iati['organisation']))
            
            self.graph.add((self.org_uri['/reporting-org/' + str(hash_name)],
                            RDFS.label,
                            name))
                
            if not type == None:
                type = type.replace(" ", "%20")
                
                self.graph.add((self.org_uri['/reporting-org/' + str(hash_name)],
                                self.iati['organisation-type'],
                                self.iati['codelist/OrganisationType/' + str(type)]))            
            

    def iati_identifier(self, xml):
        '''Converts the XML of the iati-identifier element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Text
        id = xml.text
        
        if not id == None:
            id = " ".join(id.split())
            
            self.graph.add((self.org_uri,
                            self.iati['iati-identifier'],
                            Literal(id)))

    def identifier(self, xml):
        '''Converts the XML of the identifier element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Text
        id = xml.text
        
        if not id == None:
            id = " ".join(id.split())
            
            self.graph.add((self.org_uri,
                            self.iati['organisation-id'],
                            Literal(id)))

    def name(self, xml):
        '''Converts the XML of the name element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Text
        name = AttributeHelper.attribute_language(xml, self.default_language)
        
        if not name == None:
            self.graph.add((self.org_uri,
                            RDFS.label,
                            name))

    def total_budget(self, xml):
        '''Converts the XML of the total-budget element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Elements
        period_start = xml.find('period-start')
        period_end = xml.find('period-end')
        value = xml.find('value')
        
        # Create hash
        # Required: value, period_start (text / iso-date), period_end (text / iso-date)
        
        hash = hashlib.md5()
        hash_created = False
        
        if not period_start == None:
            # Keys
            period_start_date = AttributeHelper.attribute_key(period_start, 'iso-date')
            if not period_start_date == None:
                hash.update(period_start_date)
                hash_created = True
            period_start_text = period_start.text
            if not period_start_text == None:
                hash.update(period_start_text)
                hash_created = True
        if not period_end == None:
            # Keys
            period_end_date = AttributeHelper.attribute_key(period_end, 'iso-date')
            if not period_end_date == None:
                hash.update(period_end_date)
                hash_created = True
            period_end_text = period_end.text
            if not period_end_text == None:
                hash.update(period_end_text)
                hash_created = True
        if not value == None:
            value_text = value.text
            if not value_text == None:
                hash.update(value_text)
                hash_created = True
        
        if hash_created:

            hash_total_budget = hash.hexdigest()
            
            self.graph.add((self.org_uri,
                            self.iati['organisation-total-budget'],
                            self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)]))
            
            self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                            RDF.type,
                            self.iati['budget']))
                
            if not period_start == None:
                # Keys
                date = AttributeHelper.attribute_key(period_start, 'iso-date')
                
                # Text
                period_start_text = AttributeHelper.attribute_language(period_start, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                    self.iati['start-date'],
                                    Literal(date)))
                
                if not period_start_text == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                    self.iati['start-date-text'],
                                    period_start_text))
            
            if not period_end == None:
                # Keys
                date = AttributeHelper.attribute_key(period_end, 'iso-date')
                
                # Text
                period_end_text = AttributeHelper.attribute_language(period_end, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                    self.iati['end-date'],
                                    Literal(date)))
                
                if not period_end_text == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                    self.iati['end-date-text'],
                                    period_end_text))
            
            if not value == None:
                # Keys
                currency = AttributeHelper.attribute_key(value, 'currency')
                value_date = AttributeHelper.attribute_key(value, 'value-date')
                
                # Text
                value_text = value.text
                
                if not value_text == None:
                    value_text = " ".join(value_text.split())
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                    self.iati['value'],
                                    Literal(value_text)))
                    
                    if not currency == None:
                        currency = currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(currency)]))
                    
                    elif not self.default_currency == None:
                        self.default_currency = self.default_currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(self.default_currency)]))
                    
                    if not value_date == None:
                        self.graph.add((self.iati['organisation/' + self.id + '/total-budget/' + str(hash_total_budget)],
                                        self.iati['value-date'],
                                        Literal(value_date)))

    def recipient_org_budget(self, xml):
        '''Converts the XML of the recipient-org-budget element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Elements
        recipient_org = xml.find('recipient-org')
        period_start = xml.find('period-start')
        period_end = xml.find('period-end')
        value = xml.find('value')
        
        # Create hash
        # Required: value, period_start (text / iso-date), period_end (text / iso-date)
        
        hash = hashlib.md5()
        hash_created = False
        
        if not period_start == None:
            # Keys
            period_start_date = AttributeHelper.attribute_key(period_start, 'iso-date')
            if not period_start_date == None:
                hash.update(period_start_date)
                hash_created = True
            period_start_text = period_start.text
            if not period_start_text == None:
                hash.update(period_start_text)
                hash_created = True
        if not period_end == None:
            # Keys
            period_end_date = AttributeHelper.attribute_key(period_end, 'iso-date')
            if not period_end_date == None:
                hash.update(period_end_date)
                hash_created = True
            period_end_text = period_end.text
            if not period_end_text == None:
                hash.update(period_end_text)
                hash_created = True
        if not value == None:
            value_text = value.text
            if not value_text == None:
                hash.update(value_text)
                hash_created = True
        
        if hash_created:
            
            hash_recipient_org_budget = hash.hexdigest()
        
            self.graph.add((self.org_uri,
                            self.iati['organisation-recipient-org-budget'],
                            self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)]))
            
            self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                            RDF.type,
                            self.iati['budget']))
            
            if not recipient_org == None:
                # Keys
                ref = AttributeHelper.attribute_key(recipient_org, 'ref')
                
                # Text
                recipient_org_text = AttributeHelper.attribute_language(recipient_org, self.default_language)
                
                if not ref == None:
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['recipient-org-ref'],
                                    Literal(ref)))
                    
                    ref = ref.replace(" ", "%20")
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['recipient-org'],
                                    self.iati['codelist/OrganisationIdentifier/' + ref]))
                
                if not recipient_org_text == None:
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['recipient-org-name'],
                                    recipient_org_text))                     
                  
            if not period_start == None:
                # Keys
                date = AttributeHelper.attribute_key(period_start, 'iso-date')
                
                # Text
                period_start_text = AttributeHelper.attribute_language(period_start, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['start-date'],
                                    Literal(date)))
                
                if not period_start_text == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['start-date-text'],
                                    period_start_text))
            
            if not period_end == None:
                # Keys
                date = AttributeHelper.attribute_key(period_end, 'iso-date')
                
                # Text
                period_end_text = AttributeHelper.attribute_language(period_end, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['end-date'],
                                    Literal(date)))
                
                if not period_end_text == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['end-date-text'],
                                    period_end_text))
        
            if not value == None:
                # Keys
                currency = AttributeHelper.attribute_key(value, 'currency')
                value_date = AttributeHelper.attribute_key(value, 'value-date')
                
                # Text
                value_text = value.text
                
                if not value_text == None:
                    value_text = " ".join(value_text.split())
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                    self.iati['value'],
                                    Literal(value_text)))
                    
                    if not currency == None:
                        currency = currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(currency)]))
                    
                    elif not self.default_currency == None:
                        self.default_currency = self.default_currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(self.default_currency)]))
                    
                    if not value_date == None:
                        self.graph.add((self.iati['organisation/' + self.id + '/recipient-org-budget/' + str(hash_recipient_org_budget)],
                                        self.iati['value-date'],
                                        Literal(value_date)))
                    
    def recipient_country_budget(self, xml):
        '''Converts the XML of the recipient-country-budget element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Elements
        recipient_country = xml.find('recipient-country')
        period_start = xml.find('period-start')
        period_end = xml.find('period-end')
        value = xml.find('value')
        
        # Create hash
        # Required: value, period_start (text / iso-date), period_end (text / iso-date)
        
        hash = hashlib.md5()
        hash_created = False
        
        if not period_start == None:
            # Keys
            period_start_date = AttributeHelper.attribute_key(period_start, 'iso-date')
            if not period_start_date == None:
                hash.update(period_start_date)
                hash_created = True
            period_start_text = period_start.text
            if not period_start_text == None:
                hash.update(period_start_text)
                hash_created = True
        if not period_end == None:
            # Keys
            period_end_date = AttributeHelper.attribute_key(period_end, 'iso-date')
            if not period_end_date == None:
                hash.update(period_end_date)
                hash_created = True
            period_end_text = period_end.text
            if not period_end_text == None:
                hash.update(period_end_text)
                hash_created = True
        if not value == None:
            value_text = value.text
            if not value_text == None:
                hash.update(value_text)
                hash_created = True
        
        if hash_created:
            
            hash_recipient_country_budget = hash.hexdigest()
        
            self.graph.add((self.org_uri,
                            self.iati['organisation-recipient-country-budget'],
                            self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)]))
            
            self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                            RDF.type,
                            self.iati['budget']))
            
            if not recipient_country == None:
                # Keys
                code = AttributeHelper.attribute_key(recipient_country, 'code')
                
                # Text
                recipient_country_text = AttributeHelper.attribute_language(recipient_country, self.default_language)
    
                if not code == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['recipient-country-ref'],
                                    Literal(code)))
    
                    code = code.replace(" ", "%20")
    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['recipient-country'],
                                    self.iati['codelist/Country/' + code]))
                    
                if not recipient_country_text == None:
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['recipient-country-name'],
                                    recipient_country_text))            
                   
            if not period_start == None:
                # Keys
                date = AttributeHelper.attribute_key(period_start, 'iso-date')
                
                # Text
                period_start_text = AttributeHelper.attribute_language(period_start, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['start-date'],
                                    Literal(date)))
                
                if not period_start_text == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['start-date-text'],
                                    period_start_text))
            
            if not period_end == None:
                # Keys
                date = AttributeHelper.attribute_key(period_end, 'iso-date')
                
                # Text
                period_end_text = AttributeHelper.attribute_language(period_end, self.default_language)
                
                if not date == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['end-date'],
                                    Literal(date)))
                
                if not period_end_text == None:
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['end-date-text'],
                                    period_end_text))
            
            if not value == None:
                # Keys
                currency = AttributeHelper.attribute_key(value, 'currency')
                value_date = AttributeHelper.attribute_key(value, 'value-date')
                
                # Text
                value_text = value.text
                
                if not value_text == None:
                    value_text = " ".join(value_text.split())
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                    self.iati['value'],
                                    Literal(value_text)))
                    
                    if not currency == None:
                        currency = currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(currency)]))
                    
                    elif not self.default_currency == None:
                        self.default_currency = self.default_currency.replace(" ", "%20")
                        
                        self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                        self.iati['value-currency'],
                                        self.iati['codelist/Currency/' + str(self.default_currency)]))
                    
                    if not value_date == None:
                        self.graph.add((self.iati['organisation/' + self.id + '/recipient-country-budget/' + str(hash_recipient_country_budget)],
                                        self.iati['value-date'],
                                        Literal(value_date)))
                    
    def document_link(self, xml):
        '''Converts the XML of the document-link element to a RDFLib self.graph.
        
        Parameters
        @xml: The XML of this element.'''
        
        # Keys
        url = AttributeHelper.attribute_key(xml, 'url')
        format = AttributeHelper.attribute_key(xml, 'format')
        
        # Elements
        titles = xml.findall('title')
        category = xml.find('category')
        languages = xml.findall('language')
        
        if not url == None:
            # Create hash
            # Required: url
            
            hash = hashlib.md5()
            hash.update(url)
            
            hash_document_link = hash.hexdigest()
        
            self.graph.add((self.org_uri,
                            self.iati['organisation-document-link'],
                            self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)]))
            
            self.graph.add((self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)],
                            RDF.type,
                            self.iati['document-link']))    
            
            if not url == None:
                url = url.replace(" ", "%20")
                
                self.graph.add((self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)],
                                self.iati['url'],
                                URIRef(url)))
            
            if not format == None:
                format = format.replace(" ", "%20")
                
                self.graph.add((self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)],
                                self.iati['format'],
                                self.iati['codelist/FileFormat/' + str(format)]))
                
            if not titles == []:
                for title in titles:
                    # Text
                    name = AttributeHelper.attribute_language(title, self.default_language)
                    
                    self.graph.add((self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)],
                                    RDFS.label,
                                    name))
                    
            if not category == None:
                # Keys
                code = AttributeHelper.attribute_key(category, 'code')
                
                if not code == None:
                    code = code.replace(" ", "%20")
                
                    self.graph.add((self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)],
                                    self.iati['document-category'],
                                    self.iati['codelist/DocumentCategory/' + str(code)]))
            
            if not languages == []:
                for language in languages:
                    # Text
                    code = AttributeHelper.attribute_language(language, self.default_language)
                    
                    if not code == None:
                        self.graph.add((self.iati['organisation/' + self.id + '/document-link/' + str(hash_document_link)],
                                        self.iati['language'],
                                        Literal(code)))

class ProvenanceElements :
    '''Class for converting XML elements of self.iati activities to a RDFLib self.graph.'''
    
    def __init__(self, defaults, namespace): 
        '''Initializes class.
        
        Parameters
        @defaults: A dictionary of default provenance items.
        @namespace: The default RDFLib Namespace.'''
        
        self.id = defaults['id'].replace(" ", "%20")
        self.type = defaults['type']
        self.provenance = defaults['provenance']
        self.source_name = defaults['document_name']
        self.version = defaults['version']
        self.last_updated = defaults['last_updated']
        
        self.iati = namespace
        
        self.source = Namespace(self.iati['graph/' + str(self.type) + '/' + str(self.id)])
        
        self.provenance.add((self.source,
                             RDF.type,
                             self.iati['graph']))
        
        if not id == None:
            
            if not self.version == None:
                self.provenance.add((self.source,
                                     self.iati['version'],
                                     Literal(self.version)))
            
            if not self.last_updated == None:
                self.provenance.add((self.source,
                                     self.iati['last-updated'],
                                     Literal(self.last_updated)))                            
        
    def get_result(self):
        '''Returns the resulting self.graph of the activity.
        
        Returns
        @graph: The RDFLib self.graph with added statements.'''
        
        return self.provenance
    
    def maintainer(self, value):
        '''Converts the JSON of the maintainer element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-maintainer'],
                                 self.source['/maintainer']))
            
            self.provenance.add((self.source['/maintainer'],
                                 self.iati['maintainer-name'],
                                 Literal(value)))
            
            self.provenance.add((self.source['/maintainer'],
                                 RDF.type,
                                 self.iati['maintainer']))  

    def maintainer_email(self, value):
        '''Converts the JSON of the maintainer_email element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-maintainer'],
                                 self.source['/maintainer']))
            
            self.provenance.add((self.source['/maintainer'],
                                 self.iati['maintainer-email'],
                                 Literal(value)))
            
            self.provenance.add((self.source['/maintainer'],
                                 RDF.type,
                                 self.iati['maintainer']))   

    def func_id(self, value):
        '''Converts the JSON of the id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-id'],
                                 Literal(value)))
    
    def metadata_created(self, value):
        '''Converts the JSON of the metadata_created element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-metadata-created'],
                                 Literal(value)))


    def metadata_modified(self, value):
        '''Converts the JSON of the metadata_modified element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-metadata-modified'],
                                 Literal(value)))


    def relationships(self, value):
        '''Converts the JSON of the relationships element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
            
                if (not entry == 'null') or (not entry == "") or (not entry == None):
            
                    self.provenance.add((self.source,
                                         self.iati['source-document-relationship'],
                                         Literal(entry)))

    def license(self, value):
        '''Converts the JSON of the license element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-license'],
                                 Literal(value)))
            
    def author(self, value):
        '''Converts the JSON of the author element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-author'],
                                 self.source['/author']))
            
            self.provenance.add((self.source['/author'],
                                 self.iati['author-name'],
                                 Literal(value)))
            
            self.provenance.add((self.source['/author'],
                                 RDF.type,
                                 self.iati['author']))           

    def author_email(self, value):
        '''Converts the JSON of the author_email element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-author'],
                                 self.source['/author']))
            
            self.provenance.add((self.source['/author'],
                                 self.iati['author-email'],
                                 Literal(value)))
            
            self.provenance.add((self.source['/author'],
                                 RDF.type,
                                 self.iati['author']))    
            
    def download_url(self, value):
        '''Converts the JSON of the download_url element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['source-document-download-url'],
                                 URIRef(value)))
            
    def state(self, value):
        '''Converts the JSON of the state element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-state'],
                                 Literal(value)))
            
    def func_version(self, value):
        '''Converts the JSON of the version element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-version'],
                                 Literal(value)))

    def license_func_id(self, value):
        '''Converts the JSON of the license_id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-license-id'],
                                 Literal(value)))

    def resources(self, value):
        '''Converts the JSON of the resources element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value[0]:
                
                function = getattr(self, 'resources_' + str(entry))
                function(value[0][entry])

    def resources_cache_last_updated(self, value):
        '''Converts the JSON of the mimetype element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-cache-last-updated'],
                                 Literal(value)))
            
    def resources_mimetype(self, value):
        '''Converts the JSON of the mimetype element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-mimetype'],
                                 Literal(value)))
            
    def resources_resource_group_id(self, value):
        '''Converts the JSON of the resource_group_id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-resource-group-id'],
                                 Literal(value)))
            
    def resources_hash(self, value):
        '''Converts the JSON of the hash element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-hash'],
                                 Literal(value)))
            
    def resources_description(self, value):
        '''Converts the JSON of the description element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-description'],
                                 Literal(value)))
            
    def resources_format(self, value):
        '''Converts the JSON of the format element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-format'],
                                 Literal(value)))
            
    def resources_url(self, value):
        '''Converts the JSON of the url element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['resources-url'],
                                 URIRef(value)))
            
    def resources_cache_url(self, value):
        '''Converts the JSON of the cache_url element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['resources-cache-url'],
                                 URIRef(value)))
            
    def resources_webstore_url(self, value):
        '''Converts the JSON of the webstore_url element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['resources-webstore-url'],
                                 URIRef(value)))
            
    def resources_package_id(self, value):
        '''Converts the JSON of the package_id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-package-id'],
                                 Literal(value)))
            
    def resources_mimetype_inner(self, value):
        '''Converts the JSON of the mimetype_inner element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-mimetype-inner'],
                                 Literal(value)))
            
    def resources_webstore_last_updated(self, value):
        '''Converts the JSON of the webstore_last_updated element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-webstore-last-updated'],
                                 Literal(value)))
            
    def resources_last_modified(self, value):
        '''Converts the JSON of the last_modified element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-last-modified'],
                                 Literal(value)))
            
    def resources_position(self, value):
        '''Converts the JSON of the position element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-position'],
                                 Literal(value)))
            
    def resources_size(self, value):
        '''Converts the JSON of the size element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-size'],
                                 Literal(value)))
            
    def resources_id(self, value):
        '''Converts the JSON of the id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-id'],
                                 Literal(value)))
            
    def resources_resource_type(self, value):
        '''Converts the JSON of the resource_type element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-type'],
                                 Literal(value)))
            
    def resources_name(self, value):
        '''Converts the JSON of the name element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['resources-name'],
                                 Literal(value)))
            
    def tags(self, value):
        '''Converts the JSON of the tags element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''

        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
            
                if (not entry == 'null') or (not entry == "") or (not entry == None):
            
                    self.provenance.add((self.source,
                                         self.iati['source-document-tag'],
                                         Literal(entry)))
        
    def groups(self, value):
        '''Converts the JSON of the license element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
            
                if (not entry == 'null') or (not entry == "") or (not entry == None):
            
                    self.provenance.add((self.source,
                                         self.iati['source-document-group'],
                                         Literal(entry)))
                
    def name(self, value):
        '''Converts the JSON of the name element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 RDFS.label,
                                 Literal(value)))
            
    def isopen(self, value):
        '''Converts the JSON of the isopen element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-isopen'],
                                 Literal(value)))
            
    def notes_rendered(self, value):
        '''Converts the JSON of the notes_rendered element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-notes-rendered'],
                                 Literal(value)))
            
    def url(self, value):
        '''Converts the JSON of the url element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['source-document-url'],
                                 URIRef(value)))
            
    def ckan_url(self, value):
        '''Converts the JSON of the ckan_url element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['source-document-ckan-url'],
                                 URIRef(value)))
            
    def notes(self, value):
        '''Converts the JSON of the notes element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-notes'],
                                 Literal(value)))
            
    def title(self, value):
        '''Converts the JSON of the title element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-title'],
                                 Literal(value)))
            
    def ratings_average(self, value):
        '''Converts the JSON of the ratings_average element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-ratings-average'],
                                 Literal(value)))
            
    def extras(self, value):
        '''Converts the JSON of the ratings_average element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
                
                function = getattr(self, 'extras_' + str(entry.replace('-','_')))
                function(value[entry])
                    
    def extras_publisher_iati_id(self, value):
        '''Converts the JSON of the publisher_iati_id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-publisher-iati-id'],
                                 self.iati['codelist/OrganisationIdentifier/' + str("%20".join(value.split()))]))
            
    def extras_activity_period_from(self, value):
        '''Converts the JSON of the activity_period-from element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-activity-period-from'],
                                 Literal(value)))
            
    def extras_activity_period_to(self, value):
        '''Converts the JSON of the activity_period-to element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-activity-period-to'],
                                 Literal(value)))
            
    def extras_archive_file(self, value):
        '''Converts the JSON of the archive_file element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-archive-file'],
                                 Literal(value)))
            
    def extras_verified(self, value):
        '''Converts the JSON of the verified element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-verified'],
                                 Literal(value)))
            
    def extras_publisher_organization_type(self, value):
        '''Converts the JSON of the publisher_organization_type element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['extras-publisher-organization-type'],
                                 self.iati['codelist/OrganisationType/' + str(value)]))
            
    def extras_language(self, value):
        '''Converts the JSON of the language element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-language'],
                                 Literal(value)))
            
    def extras_country(self, value):
        '''Converts the JSON of the country element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['extras-country'],
                                 self.iati['codelist/Country/' + str(value)]))
            
    def extras_filetype(self, value):
        '''Converts the JSON of the filetype element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-filetype'],
                                 Literal(value)))
            
    def extras_record_updated(self, value):
        '''Converts the JSON of the record_updated element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-record-updated'],
                                 Literal(value)))
            
    def extras_activity_count(self, value):
        '''Converts the JSON of the activity_count element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-activity-count'],
                                 Literal(value)))
            
    def extras_publisher_country(self, value):
        '''Converts the JSON of the publisher_country element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            value = value.replace(" ", "%20")
            
            self.provenance.add((self.source,
                                 self.iati['extras-publisher-country'],
                                 self.iati['codelist/Country/' + str(value)]))
            
    def extras_data_updated(self, value):
        '''Converts the JSON of the data_updated element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-data-updated'],
                                 Literal(value)))
            
    def extras_publishertype(self, value):
        '''Converts the JSON of the publishertype element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-publishertype'],
                                 Literal(value)))
            
    def extras_donors(self, value):
        '''Converts the JSON of the donors element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
            
                self.provenance.add((self.source,
                                     self.iati['extras-donor'],
                                     Literal(entry)))
                
    def extras_donors_country(self, value):
        '''Converts the JSON of the donors_country element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
                entry = entry.replace(" ", "%20")
            
                self.provenance.add((self.source,
                                     self.iati['extras-donor-country'],
                                     self.iati['codelist/Country/' + str(entry)]))
                
    def extras_donors_type(self, value):
        '''Converts the JSON of the donors_country element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            for entry in value:
            
                self.provenance.add((self.source,
                                     self.iati['extras-donor-type'],
                                     Literal(entry)))
                
    def extras_department(self, value):
        '''Converts the JSON of the department element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['extras-department'],
                                 Literal(value)))
            
    def ratings_count(self, value):
        '''Converts the JSON of the ratings_count element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-ratings-count'],
                                 Literal(value)))
            
    def revision_func_id(self, value):
        '''Converts the JSON of the revision_id element to a RDFLib self.graph.
        
        Parameters
        @value: The value of the json.'''
        
        if (not value == 'null') and (not str(value) == "") and (not value == None):
            
            self.provenance.add((self.source,
                                 self.iati['source-document-revision-id'],
                                 Literal(value)))
