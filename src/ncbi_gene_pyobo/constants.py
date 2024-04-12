"""Constants used in the project."""

from pathlib import Path

PWD = Path(__file__).parent
DATA_DIR = PWD / "data"
QUERIES_DIR = PWD / "sql_queries"

OBO_FILENAME = "ncbigene-full-obo.obo"
OWL_FILENAME = "ncbigene-full-obo.owl"
JSON_FILENAME = "ncbigene-full-obo.json"
SUBSET_TABLE_QUERY_FILENAME = QUERIES_DIR / "create_table_from_ncbigene.sql"


DEFAULT_INPUT_DIR = DATA_DIR / "raw"
DEFAULT_OUTPUT_DIR = DATA_DIR / "transformed"

ID_COLUMN = "id"
NAME_COLUMN = "name"
CATEGORY_COLUMN = "category"
SUBJECT_COLUMN = "subject"
PREDICATE_COLUMN = "predicate"
OBJECT_COLUMN = "object"
RELATION_COLUMN = "relation"
PROVIDED_BY_COLUMN = "provided_by"
PRIMARY_KNOWLEDGE_SOURCE_COLUMN = "primary_knowledge_source"
DESCRIPTION_COLUMN = "description"
XREF_COLUMN = "xref"
SYNONYM_COLUMN = "synonym"
IRI_COLUMN = "iri"
SAME_AS_COLUMN = "same_as"
SUBSETS_COLUMN = "subsets"

NODE_HEADER = [
    ID_COLUMN,
    CATEGORY_COLUMN,
    NAME_COLUMN,
    DESCRIPTION_COLUMN,
    XREF_COLUMN,
    PROVIDED_BY_COLUMN,
    SYNONYM_COLUMN,
]

EDGE_HEADER = [
    SUBJECT_COLUMN,
    PREDICATE_COLUMN,
    OBJECT_COLUMN,
    PRIMARY_KNOWLEDGE_SOURCE_COLUMN,
]

NODES_TABLE_SCHEMA = " VARCHAR,".join(NODE_HEADER) + " VARCHAR"
EDGES_TABLE_SCHEMA = " VARCHAR,".join(EDGE_HEADER) + " VARCHAR"

TAXON_ID = "NCBITaxon:"
GENE_ID = "NCBIGene:"
TAXON_CATEGORY = "biolink:OrganismTaxon"
GENE_CATEGORY = "biolink:Gene"

# EDGES
IN_TAXON_RELATION = "RO:0002162"
IN_TAXON_PREDICATE = "biolink:in_taxon"
PRIMARY_KNOWLEDGE_SOURCE = "infores:ncbi-gene"
