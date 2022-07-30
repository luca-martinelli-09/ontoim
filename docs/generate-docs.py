# %%
import dominate
from dominate.tags import *
from rdflib import OWL, Graph, SKOS, RDFS, RDF
from rdflib.namespace import DCTERMS, NamespaceManager

VOCABULARY_NAME = "weather-conditions"

g = Graph()

g.parse(f"https://w3id.org/ontoim/controlled-vocabulary/{VOCABULARY_NAME}/", format='xml')

nm = NamespaceManager(g)


def getTitle(element):
    global g

    return g.value(element, RDFS.label) or g.value(element, SKOS.prefLabel)


def hasElements(generator):
    global g

    try:
        next(generator)
        return True
    except:
        return False


conceptScheme = next(g.subjects(RDF.type, SKOS.ConceptScheme))

abstract = g.objects(conceptScheme, DCTERMS.description) if hasElements(
    g.objects(conceptScheme, DCTERMS.description)) else None

authors = g.objects(conceptScheme, DCTERMS.creator) if hasElements(
    g.objects(conceptScheme, DCTERMS.creator)) else None

titles = g.objects(conceptScheme, DCTERMS.title) if hasElements(
    g.objects(conceptScheme, DCTERMS.title)) else None
mainTitle = getTitle(conceptScheme) if titles else None

version = g.objects(conceptScheme, OWL.versionInfo) if hasElements(
    g.objects(conceptScheme, OWL.versionInfo)) else None

topConcepts = g.objects(conceptScheme, SKOS.hasTopConcept) if hasElements(
    g.objects(conceptScheme, SKOS.hasTopConcept)) else None
allConcepts = g.subjects(SKOS.inScheme, conceptScheme) if hasElements(
    g.subjects(SKOS.inScheme, conceptScheme)) else None

doc = dominate.document(title=mainTitle)

with doc.head:
    link(rel='stylesheet', href='style.css')

with doc:
    with header():
        h1(mainTitle)

        with ul(cls="vers"):
            for tit in titles:
                li(span(tit, cls="res lang", data_lang="@" + tit.language))

    with section(id="metadata", cls="info"):
        with dl():
            dt("IRI")
            dd(code(conceptScheme), cls="iri")

            if version:
                dt("Version")
                with dd().add(ul(cls="vers")):
                    for v in version:
                        li(span(v, cls="res lang", data_lang="@" + v.language))

            if authors:
                dt("Authors")
                for auth in authors:
                    dd(a(auth, href=auth))

            dt("has super-classes")
            with dd().add(ul(cls="vers rel super")):
                for type in g.objects(conceptScheme, RDF.type):
                    li(span(nm.normalizeUri(type), cls="res other", title=type))

    if abstract:
        with section(id="abstract"):
            h2("Abstract")

            with ul(cls="vers"):
                for abs in abstract:
                    li(span(abs, cls="res lang", data_lang="@" + abs.language))

    with section(id="toc"):
        h2("Table of Contents")

        with ol():
            if abstract:
                li(a("Abstract", href="#abstract"))

            if topConcepts:
                li(a("Top Concepts", href="#topConcepts"))

            if allConcepts:
                li(a("All Concepts", href="#allConcepts"))

    with section(id="topConcepts"):
        h2("Top Concepts")

        with ul(cls="subtoc"):
            for tc in topConcepts:
                conceptID = g.value(tc, DCTERMS.identifier)

                li(a(getTitle(tc), href="#" + conceptID, title=tc))

    with section(id="allConcepts"):
        h2("All Concepts")

        with ul(cls="subtoc"):
            for conc in allConcepts:
                conceptID = g.value(conc, DCTERMS.identifier)
                li(a(getTitle(conc), href="#" + conceptID))

        allConcepts = g.subjects(SKOS.inScheme, conceptScheme)
        for conc in allConcepts:
            conceptID = g.value(conc, DCTERMS.identifier)

            with div(id=conceptID, cls="entity"):
                with header():
                    h3(getTitle(conc))
                    p(code(conc, title=conc), cls="IRI")

                    with ul(cls="rel super"):
                        for tit in g.objects(conc, SKOS.prefLabel):
                            li(span(tit, cls="res lang", data_lang="@" + tit.language))
                
                try:
                    next(g.objects(conc, SKOS.definition))
                    
                    with ul(cls="vers"):
                        for desc in g.objects(conc, SKOS.definition):
                            li(span(desc, cls="res lang", data_lang="@" + desc.language))
                except:
                    pass

                with dl():
                    dt("has super-classes")
                    with dd().add(ul(cls="rel super")):
                        for type in g.objects(conc, RDF.type):
                            li(span(nm.normalizeUri(type),
                               cls="res other", title=type))

                    try:
                        next(g.objects(conc, SKOS.narrower))

                        dt("narrower")
                        with dd().add(ul(cls="rel super")):
                            for nar in g.objects(conc, SKOS.narrower):
                                conceptID = g.value(nar, DCTERMS.identifier)

                                li(a(getTitle(nar), href="#" +
                                   conceptID, cls="res", title=nar))
                    except:
                        pass

                    try:
                        next(g.objects(conc, SKOS.broader))

                        dt("broader")
                        with dd().add(ul(cls="rel super")):
                            for bro in g.objects(conc, SKOS.broader):
                                conceptID = g.value(bro, DCTERMS.identifier)

                                li(a(getTitle(bro), href="#" +
                                   conceptID, cls="res", title=bro))
                    except:
                        pass


with open(f"controlled-vocabulary/{VOCABULARY_NAME}.html", "w") as fp:
    fp.write(doc.render(pretty=False))
# %%
