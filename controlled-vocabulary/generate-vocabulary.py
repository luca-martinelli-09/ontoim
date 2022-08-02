# %%
import pandas as pd
from rdflib import Namespace, Literal, URIRef, Graph, DCTERMS, RDF, RDFS
from rdflib.namespace import XSD, DC, SKOS
import pandas as pd


def getAttributes(row, removeLevel=True):
    o = {}

    if removeLevel:
        for k in row.keys():
            ks = k.split("_")[1:]

            row["_".join(ks)] = row.pop(k)

    for k in row.keys():
        ks = k.split("_")

        if not pd.isna(row[k]):
            cl = o
            for l in ks[:-1]:
                try:
                    cl = cl[l]
                except KeyError:
                    cl[l] = {}
                    cl = cl[l]

            cl[ks[-1]] = row[k]

    return o


def getJSONData(df):
    numLevels = int(df.columns[-1][1])

    jsonData = {}

    for _, row in df.iterrows():
        cl = jsonData
        for l in range(1, numLevels):
            lID = row[f"l{l}_identifier"]

            if not pd.isna(lID):
                try:
                    cl = cl[lID]["narrower"]
                except KeyError:
                    rowLevel = row[[
                        col for col in row.keys()
                        if col.startswith(f"l{l}_")
                    ]]

                    newLevel = getAttributes(rowLevel)

                    if newLevel:
                        cl[lID] = newLevel
                        cl[lID]["narrower"] = {}

                        cl = cl[lID]["narrower"]

        rowLevel = row[[
            col for col in row.keys()
            if col.startswith(f"l{numLevels}_")
        ]]
        lID = row[f"l{numLevels}_identifier"]

        if not pd.isna(lID):
            cl[lID] = getAttributes(rowLevel)

    return jsonData


def addConceptToScheme(g, ns, scheme, conceptInfo, conceptType, broader=None, topConcept=True):
    concept = URIRef(ns[str(conceptInfo["identifier"])])

    g.add((concept, RDF.type, SKOS.Concept))
    g.add((concept, RDF.type, conceptType))

    g.add((concept, DCTERMS.identifier, Literal(conceptInfo["identifier"])))

    try:
        labels = conceptInfo["label"]
        if type(labels) == dict:
            for lang in labels.keys():
                label = Literal(labels[lang], lang=lang)
                g.add((concept, RDFS.label, label))
                g.add((concept, SKOS.prefLabel, label))
        else:
            label = Literal(labels)
            g.add((concept, RDFS.label, label))
            g.add((concept, SKOS.prefLabel, label))
    except:
        pass

    try:
        definitions = conceptInfo["definition"]
        if type(definitions) == dict:
            for lang in definitions.keys():
                definition = Literal(definitions[lang], lang=lang)
                g.add((concept, SKOS.definition, definition))
        else:
            definition = Literal(definitions)
            g.add((concept, SKOS.definition, definition))
    except:
        pass

    try:
        examples = conceptInfo["example"]
        if type(examples) == dict:
            for i in examples.keys():
                example = Literal(examples[i])
                g.add((concept, SKOS.example, example))
        else:
            example = Literal(examples)
            g.add((concept, SKOS.example, example))
    except:
        pass

    g.add((concept, SKOS.inScheme, scheme))

    if topConcept:
        g.add((scheme, SKOS.hasTopConcept, concept))
    
    if broader:
        g.add((broader, SKOS.narrower, concept))
        g.add((concept, SKOS.broader, broader))
    
    try:
        for nID in conceptInfo["narrower"]:
            narrower = conceptInfo["narrower"][nID]
            addConceptToScheme(g, ns, scheme, narrower, conceptType, concept, False)
    except:
        pass


def createVocabulary(vocabularyInfo):
    vocabularyName = vocabularyInfo["name"]

    ONTOIM = Namespace("https://w3id.org/ontoim/")
    NAMESPACE = Namespace(
        f"https://w3id.org/ontoim/controlled-vocabulary/{vocabularyName}/")

    g = Graph()

    g.bind("xsd", XSD)
    g.bind("dct", DCTERMS)
    g.bind("dc", DC)
    g.bind("skos", SKOS)
    g.bind("rdfs", RDFS)
    g.bind("ontoim", ONTOIM)

    # Create scheme

    SCHEME = URIRef(NAMESPACE)

    g.add((SCHEME, RDF.type, SKOS.ConceptScheme))

    try:
        labels = vocabularyInfo["label"]
        if type(labels) == dict:
            for lang in labels.keys():
                label = Literal(labels[lang], lang=lang)
                g.add((SCHEME, RDFS.label, label))
                g.add((SCHEME, DCTERMS.title, label))
        else:
            label = Literal(labels)
            g.add((SCHEME, RDFS.label, label))
            g.add((SCHEME, DCTERMS.title, label))
    except:
        pass

    try:
        descriptions = vocabularyInfo["description"]
        if type(descriptions) == dict:
            for lang in descriptions.keys():
                description = Literal(descriptions[lang], lang=lang)
                g.add((SCHEME, RDFS.comment, description))
                g.add((SCHEME, DCTERMS.description, description))
        else:
            description = Literal(descriptions)
            g.add((SCHEME, RDFS.comment, description))
            g.add((SCHEME, DCTERMS.description, description))
    except:
        pass

    try:
        creators = vocabularyInfo["creator"]
        if type(creators) == dict:
            for i in creators.keys():
                creator = URIRef(creators[i])
                g.add((SCHEME, DCTERMS.creator, creator))
        else:
            creator = URIRef(creators)
            g.add((SCHEME, DCTERMS.creator, creator))
    except:
        pass

    # Populate scheme
    df = None
    try:
        df = pd.read_csv(f"{vocabularyName}/{vocabularyName}.csv")
    except:
        pass

    if not df is None:
        conceptsData = getJSONData(df)

        for cID in conceptsData:
            concept = conceptsData[cID]
            addConceptToScheme(g, NAMESPACE, SCHEME, concept,
                            ONTOIM[vocabularyInfo["element"]])
    else:
        print(vocabularyName, "is empty")

    # Save graph
    g.serialize(f"{vocabularyName}/{vocabularyName}.ttl", "turtle")
    g.serialize(f"{vocabularyName}/{vocabularyName}.rdf", "pretty-xml")


vocabularies = pd.read_csv("vocabularies.csv", index_col="name")

for vocabularyName, vocabulary in vocabularies.iterrows():
    vocabularyInfo = getAttributes(vocabulary, False)
    vocabularyInfo["name"] = vocabularyName

    createVocabulary(vocabularyInfo)
# %%
