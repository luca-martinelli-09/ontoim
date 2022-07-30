#%%
from rdflib import Namespace, Literal, URIRef, Graph, DCTERMS, RDF, RDFS
from rdflib.namespace import XSD, DC, SKOS
import pandas as pd

ONTOIM = Namespace("https://w3id.org/ontoim/")

VOCABULARY_NAME = "weather-conditions"
VOCABULARY_NS = "weathercondition"

NAMESPACE = Namespace(
    f"https://w3id.org/ontoim/controlled-vocabulary/{VOCABULARY_NAME}/")

LABELS = [
    Literal("Condizione Meteorologica", lang="it"),
    Literal("Weather Condition", lang="en")
]

DESCRIPTIONS = [
    Literal("Classificatione delle condizioni meteorologiche", lang="it"),
    Literal("Classification of weather conditions", lang="en")
]

ELEMENT_TYPE = URIRef(ONTOIM["WeatherCondition"])

CREATOR = URIRef("https://w3id.org/people/lucamartinelli")

g = Graph()

g.bind("xsd", XSD)
g.bind("dct", DCTERMS)
g.bind("dc", DC)
g.bind("skos", SKOS)
g.bind("rdfs", RDFS)
g.bind("ontoim", ONTOIM)
g.bind(VOCABULARY_NS, NAMESPACE)

SCHEME = URIRef(NAMESPACE)

# Create Concept Scheme
g.add((SCHEME, RDF.type, SKOS.ConceptScheme))

# Add labels
for l in LABELS:
  g.add((SCHEME, RDFS.label, l))
  g.add((SCHEME, DCTERMS.title, l))

# Add descriptions
for d in DESCRIPTIONS:
  g.add((SCHEME, RDFS.comment, d))
  g.add((SCHEME, DCTERMS.description, d))

# Add creator
g.add((SCHEME, DCTERMS.creator, CREATOR))

# Add data
dataset = pd.read_csv(VOCABULARY_NAME + ".csv", index_col=["code"])

for code, el in dataset.iterrows():
  element = URIRef(NAMESPACE[str(code)])

  g.add((element, RDF.type, SKOS.Concept))
  g.add((element, RDF.type, ELEMENT_TYPE))

  g.add((element, DCTERMS.identifier, Literal(code)))

  g.add((element, RDFS.label, Literal(el["it"], lang="it")))
  g.add((element, RDFS.label, Literal(el["en"], lang="en")))
  g.add((element, SKOS.prefLabel, Literal(el["it"], lang="it")))
  g.add((element, SKOS.prefLabel, Literal(el["en"], lang="en")))

  g.add((element, SKOS.definition, Literal(el["it"], lang="it")))
  g.add((element, SKOS.definition, Literal(el["en"], lang="en")))

  g.add((element, SKOS.inScheme, SCHEME))
  g.add((SCHEME, SKOS.hasTopConcept, element))

g.serialize(VOCABULARY_NAME + ".ttl", "turtle")
g.serialize(VOCABULARY_NAME + ".rdf", "xml")
# %%
