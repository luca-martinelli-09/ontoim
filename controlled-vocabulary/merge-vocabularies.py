# %%
import os
from rdflib import Graph, DCTERMS, RDFS, Namespace
from rdflib.namespace import XSD, DC, SKOS

# %%

ONTOIM = Namespace("https://w3id.org/ontoim/")

g = Graph()

g.bind("xsd", XSD)
g.bind("dct", DCTERMS)
g.bind("dc", DC)
g.bind("skos", SKOS)
g.bind("rdfs", RDFS)
g.bind("ontoim", ONTOIM)

for dir, _, files in os.walk("./"):
    for file in files:
      if not file.endswith("controlled-vocabularies.rdf"):
        filepath = os.path.join(dir, file)
        if file.endswith(".rdf"):
          g.parse(filepath)

# %%
g.serialize("controlled-vocabularies.ttl", "turtle")
g.serialize("controlled-vocabularies.rdf", "pretty-xml")