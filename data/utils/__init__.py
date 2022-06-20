# Imports
import pandas as pd
import configparser
from urllib.request import urlopen
import unidecode

from rdflib import Graph, RDF, Namespace

from rdflib.namespace import XSD, FOAF, OWL, DC, XMLNS, DCTERMS, RDF, RDFS, DCAT, PROV, SKOS

# OntoPiA Namespaces

L0 = Namespace("https://w3id.org/italia/onto/l0/")
TRANSP = Namespace("https://w3id.org/italia/onto/Transparency/")
TI = Namespace("https://w3id.org/italia/onto/TI/")
SM = Namespace("https://w3id.org/italia/onto/SM/")
ROUTE = Namespace("https://w3id.org/italia/onto/Route/")
RO = Namespace("https://w3id.org/italia/onto/RO/")
PUBC = Namespace("https://w3id.org/italia/onto/PublicContract/")
PROJ = Namespace("https://w3id.org/italia/onto/Project/")
POT = Namespace("https://w3id.org/italia/onto/POT/")
POI = Namespace("https://w3id.org/italia/onto/POI/")
PARK = Namespace("https://w3id.org/italia/onto/PARK/")
MU = Namespace("https://w3id.org/italia/onto/MU/")
LANG = Namespace("https://w3id.org/italia/onto/Language/")
IOT = Namespace("https://w3id.org/italia/onto/IoT/")
INDIC = Namespace("https://w3id.org/italia/onto/Indicator/")
HER = Namespace("https://w3id.org/italia/onto/HER/")
CULTHER = Namespace("https://w3id.org/italia/onto/CulturalHeritage/")
CPV = Namespace("https://w3id.org/italia/onto/CPV/")
CPSV = Namespace("https://w3id.org/italia/onto/CPSV/")
CPEV = Namespace("https://w3id.org/italia/onto/CPEV/")
COV = Namespace("https://w3id.org/italia/onto/COV/")
CLV = Namespace("https://w3id.org/italia/onto/CLV/")
PATHS = Namespace("https://w3id.org/italia/onto/AtlasOfPaths/")
ACOND = Namespace("https://w3id.org/italia/onto/AccessCondition/")
ACCO = Namespace("https://w3id.org/italia/onto/ACCO/")

# OntoPiA Controlled Vocabularies

EVENTS_TYPE = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/public-event-types/")
LICENSES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/licenses/")
GEO_DISTRIBUTION = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/territorial-classifications/geographical-distribution/")
GEO_DISTRIBUTION = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/territorial-classifications/geographical-distribution/")
REGIONS = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/territorial-classifications/regions/")
PROVINCES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/territorial-classifications/provinces/")
COUNTRIES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/territorial-classifications/countries/")  # Note: only /italy available
CITIES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/territorial-classifications/cities/")
POI_CLASSIFICATION = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/poi-category-classification/")
ACCO_STAR_RATINGS = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-accommodation-facilities/accommodation-star-rating/")
ACCO_TYPES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-accommodation-facilities/accommodation-typology/")
PERSON_EDULEVEL = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-people/education-level/")
PERSON_TITLE = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-people/person-title/")
PERSON_PARENTAL_REL = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-people/parental-relationship-types/")
ORG_LEGAL_STATUS = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-organizations/legal-status/")
ORG_ATECO = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-organizations/ateco-2007/")
ORG_S13 = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-organizations/S13/")
CUL_SUBJ = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-culture/subject-disciplines/")
CUL_PLACES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-culture/cultural-interest-places/")
ROUTE_TYPES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-routes/route-types/")
AUTH_TYPES = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-public-services/authentication-type/")
EROGATION_CHANNELS = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-public-services/channel/")
INTERACT_LEVEL = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-public-services/interactivity-level/")
IO_SERVICE = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-public-services/service-input-output/")
LIFE_EVENTS = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-public-services/life-business-event/life-event/")
BUSINESS_EVENTS = Namespace(
    "https://w3id.org/italia/controlled-vocabulary/classifications-for-public-services/life-business-event/business-event/")

# OntoSona Namespaces

ASSO = Namespace("https://w3id.org/sona/onto/ASSO/")

# OntoSona Data

ANNCSU = Namespace("https://w3id.org/sona/data/ANNCSU/")
TOURISM_STRUCT = Namespace("https://w3id.org/sona/data/tourism/structures/")

# Get configurations from file


def getConfig(fileName):
    config = configparser.ConfigParser()
    config.read(fileName)

    return config

# Get data from CKAN OpenData portal


def getOpenData(baseURL, datasetID, resID, rawData=False, dtype=None):
    dataURI = "{}/dataset/{}/resource/{}/download".format(
        baseURL, datasetID, resID)

    if rawData:
        try:
            getDataRequest = urlopen(dataURI)

            return getDataRequest
        except:
            return None

    try:
        return pd.read_csv(dataURI, dtype=dtype)
    except:
        return None

# Standardize name
# Convert name to lower case and capitalize each word


def standardizeName(name):
    name = name.lower().title()

    if name.endswith("a'"):
        name = name.removesuffix("a'") + "à"

    return name

# Generate ID by name
# Convert in lowercase and replace special characters with dash


def genNameForID(name):
    nameID = ""

    name.replace("'", "")
    name = unidecode.unidecode(name.lower())

    # Replace special chars with -
    for char in name:
        nameID += char if char.isalnum() else "-"

    return nameID

# Generate graph with default namespaces


def createGraph():
    # Create the graph
    g = Graph()

    g.bind("xsd", XSD)
    g.bind("foaf", FOAF)
    g.bind("owl", OWL)
    g.bind("dc", DC)
    g.bind("xml", XMLNS)
    g.bind("dct", DCTERMS)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)
    g.bind("skos", SKOS)

    # L0 is for OntoPiA interoperability
    g.bind("l0", L0)

    return g

# Serialize RDF and save it in different extensions


def saveGraph(g, fileName):
    formats = [
        {"ext": "ttl", "fmt": "turtle"},
        {"ext": "rdf", "fmt": "xml"}
    ]

    for format in formats:
        ext = format["ext"]
        fmt = format["fmt"]

        with open("{}.{}".format(fileName, ext), "w", encoding="utf-8") as fp:
            fp.write(g.serialize(format=fmt))
