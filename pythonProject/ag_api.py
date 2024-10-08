from franz.openrdf.connect import ag_connect
from franz.openrdf.vocabulary import RDF

conn = ag_connect('util', host='localhost', port=10035, user='XXXXXXX', password='XXXXXXX')

owl_named_individual = conn.createURI("http://www.w3.org/2002/07/owl#NamedIndividual")
owl_datatype_property = conn.createURI("http://www.w3.org/2002/07/owl#DatatypeProperty")
owl_annotation_property = conn.createURI("http://www.w3.org/2002/07/owl#AnnotationProperty")
owl_object_property = conn.createURI("http://www.w3.org/2002/07/owl#ObjectProperty")
owl_class = conn.createURI("http://www.w3.org/2002/07/owl#Class")
rdfs_label_property = conn.createURI("http://www.w3.org/2000/01/rdf-schema#label")
subclass_of_property = conn.createURI("http://www.w3.org/2000/01/rdf-schema#subClassOf")
skos_pref_label_property = conn.createURI("http://www.w3.org/2004/02/skos/core#prefLabel")
ontology_string = "http://www.semanticweb.org/mdebe/ontologies/2024/7/util/"

# Given the last part of an IRI will return the full IRI string
# E.g., given "Person" returns "http://www.semanticweb.org/ontologies/2022/titutuli/nivedita/drmo#Person"
def make_iri_string (iri_name):
    return ontology_string + iri_name

# Finds a class with the IRI class_name
# If no such class exists, returns None
# Note: when we refer to "IRI name" we mean last part of the IRI after the ontology prefix
# E.g., IRI name of "http://www.semanticweb.org/ontologies/2022/1/CfHA_Ontology/Person" is "Person"
def find_class (class_name):
    iri_str = make_iri_string(class_name)
    class_object = conn.createURI(iri_str)
    for _ in conn.getStatements(class_object, RDF.TYPE, owl_class):
        return class_object
    print(f'Error {class_name} is not a class')
    return None

# Returns a list with all the instances of the class where the class is specified by name
# Note wherever it says X_name it means the IRI name of X If no class with that IRI name returns None
# If the class has no instances returns an empty list.
def find_instances_of_class(class_object):
    if class_object is None:
        return None
    class_set = set()
    statements = conn.getStatements(None, RDF.TYPE, class_object)
    with statements:
        for statement in statements:
            class_set.add(statement.getSubject())
    return class_set


# Finds a property (annotation, object, or datatype) from the IRI name
def find_property(prop_str):
    iri_str = make_iri_string(prop_str)
    prop = conn.createURI(iri_str)
    for _ in conn.getStatements(prop, RDF.TYPE, owl_datatype_property):
        return prop
    for _ in conn.getStatements(prop, RDF.TYPE, owl_annotation_property):
        return prop
    for _ in conn.getStatements(prop, RDF.TYPE, owl_object_property):
        return prop
    print(f'Error {prop} is not a property')
    return None

def find_subclasses(class_object):
    subclass_statements = conn.getStatements(None, subclass_of_property, class_object)
    subclass_set = set()
    for sc_statement in subclass_statements:
        subclass_set.add(sc_statement.getSubject())
    return subclass_set

# Finds an instance from the IRI name
def find_instance_from_iri(iri_name):
    iri_string = make_iri_string(iri_name)
    instance_iri = conn.createURI(iri_string)
    statements = conn.getStatements(instance_iri, RDF.TYPE, owl_named_individual)
    with statements:
        for statement in statements:
            if len(statements) > 1:
                print(f'Warning two or more Individuals with ID: {instance_iri} using first one')
                return statement.getSubject()
            elif len(statements) == 1:
                return statement.getSubject()
    return None

# Finds an object based on its rdfs:label. Note this will also work for prefLabel and altLabel
# as long as the reasoner has run because they are sub-properties of rdfs:label
# If no object with that label, returns None
def find_object_from_label(label_string):
    statements = conn.getStatements(None, rdfs_label_property, label_string)
    kg_object = None
    with statements:
        for statement in statements:
            kg_object = statement.getSubject()
    return kg_object


# Gets the value of a single valued property using the IRI name of the instance and the IRI name of the property
# If the property has multiple values prints a warning and returns the first one
# If the property has no value returns None Note: if not sure whether property has multiple values, best to use get_values
def get_value(instance, owl_property):
    if instance is None:
        print("Error no object with iri name: {instance}")
        return None
    statements = conn.getStatements(instance, owl_property, None)
    with statements:
        for statement in statements:
            if len(statements) > 1:
                print(f'Warning: two or more values for property: {owl_property}. Using first one.')
                return statement.getObject()
            elif len(statements) == 1:
                return statement.getObject()
    print(f'Error: No property value for: {instance, owl_property}.')
    return None

# Returns the values of a the property of an instance in a list if no values returns an empty list
def get_values (instance, owl_property):
    if instance == None:
        print("Error no object with iri name: {iri_name}")
        return None
    values = set()
    statements = conn.getStatements(instance, owl_property, None)
    with statements:
        for statement in statements:
            next_value = statement.getObject()
            values.add(next_value)
    return values

# Creates a new instance of a class and returns the new instance
def make_instance (instance_name, instance_class):
    instance_iri = conn.createURI(make_iri_string(instance_name))
    conn.add(instance_iri, RDF.TYPE, owl_named_individual)
    conn.add(instance_iri, RDF.TYPE, instance_class)
    return instance_iri

# Get the label from an object. Looks in skos:prefLabel first (which currently is usually empty)
# Then uses first value it finds in rdfs:label. If no label string returns empty string
def object_to_string(kg_object):
    pref_statements = conn.getStatements(kg_object, skos_pref_label_property, None)
    with pref_statements:
        for statement in pref_statements:
            return statement.getObject()
    l_statements = conn.getStatements(kg_object, rdfs_label_property, None)
    with l_statements:
        for statement in l_statements:
            return statement.getObject()
    print("Error: object has no label string: {kg_object}")
    return ""

# When getting values that are datatypes there is all sorts of extra stuff we usually want to strip out
# E.g., in the dest data below the result of get_value("MichaelDeBellis", "email") will be: "mdebellissf@gmail.com"^^<http://www.w3.org/2001/XMLSchema#anyURI>
# this should strip out the datatype and extra string characters so will return mdebelissf@gmail.com
def convert_to_string (literal):
        literal = str(literal)
        if "^" in literal:
            literal = literal.replace(literal[literal.find("^") + len("^"):], '') #remove the datatype
            literal = literal[1:len(literal) - 2] # remove the string characters and the remaining ^
        return literal

# Adds a new value to an instance of a property.
# Note this takes as input the actual instance and property (i.e., their IRIs) so if needed use find_instance and find_property
# Did this for efficiency, there will be times then we already have a handle on the object and property
def put_value(instance, kg_property, new_value):
    conn.add(instance, kg_property, new_value)

# Deletes a value for an instance of a property.
# Note this takes as input the actual instance and property (i.e., their IRIs) so if needed use find_instance and find_property
# Did this for efficiency, there will be times then we already have a handle on the object and property
def delete_value(instance, kg_property, old_value):
    conn.removeTriples(instance, kg_property, old_value)


# #Test data, in each case the comment below is what should be returned (with the current ontology)
# # Note: these were made for another ontology originally so these examples won't work.
# # I'm going to update them when I get a chance for drmo
# print(find_instance_from_iri("AMerry"))
# # <http://www.semanticweb.org/ontologies/2022/titutuli/nivedita/drmo#AMerry>
# print(get_values(find_instance_from_iri("AMerry"), find_property("isAuthorOf")))
# # [<http://www.semanticweb.org/ontologies/2022/titutuli/nivedita/drmo#TestDocumentAM>,...]
# print(get_value(find_instance_from_iri("AMerry"), find_property("lastName")))
# # "Merry"
# print(convert_to_string(get_value(find_instance_from_iri("AMerry"), find_property("lastName"))))
# # mdebellissf@gmail.com
# print(find_class("DentalMaterialProduct"))
# # <http://www.semanticweb.org/ontologies/2022/titutuli/nivedita/drmo#DentalMaterialProduct>
# print(find_class("Foo"))
# # Error Foo is not a class
# # None
# print(find_instances_of_class(find_class("JournalArticle")))
# # [<http://www.semanticweb.org/ontologies/2022/1/CfHA_Ontology/DanielDuffy>, <http://www.semanticweb.org/ontologies/2022/1/CfHA_Ontology/RyanMcGranaghan>,...]
# print(object_to_string(find_class("JournalArticle")))
# # "Journal Article"@en
# put_value(find_instance_from_iri("AMerry"), find_property("isAuthorOf"), make_instance("TestDocumentAM", "JournalArticle"))
# print(get_values(find_instance_from_iri("AMerry"), find_property("isAuthorOf")))
# # [<http://www.semanticweb.org/ontologies/2022/titutuli/nivedita/drmo#TestDocumentAM>,...]
# # List should include TestDocumentAM
# delete_value(find_instance_from_iri("AMerry"), find_property("isAuthorOf"), find_instance_from_iri("TestDocumentAM"))
# print(get_values(find_instance_from_iri("AMerry"), find_property("isAuthorOf")))
# # List should not include TestDocumentAM
# print(find_object_from_label("A Marie"))
# # <http://www.semanticweb.org/ontologies/2022/titutuli/nivedita/drmo#AMarie>
# # Note: always use find_object_from_iri when possible, it should be much faster
# print(find_subclasses(find_class("DentalMaterialProduct")))
# print(len(find_subclasses(find_class("DentalMaterialProduct"))))
# conn.deleteDuplicates("spo")   # So we can run the test data without creating duplicates

