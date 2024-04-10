"""Constants used in the project."""

from pathlib import Path

PWD = Path(__file__).parent
DATA_DIR = PWD / "data"
OBO_FILENAME = "ncbigene-full-obo.obo"
OWL_FILENAME = "ncbigene-full-obo.owl"
JSON_FILENAME = "ncbigene-full-obo.json"


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
