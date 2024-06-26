"""Transform module."""

import logging
from pathlib import Path
from typing import List, Optional

from ncbi_gene_pyobo.transform_utils import OntologyTransform
from ncbi_gene_pyobo.transform_utils.ontology_transform import ONTOLOGIES

DATA_SOURCES = {
    "OntologyTransform": OntologyTransform,
}


def transform(input_dir: Optional[Path], output_dir: Optional[Path], sources: List[str] = None) -> None:
    """
    Transform based on resource and class declared in DATA_SOURCES.

    :param input_dir: A string pointing to the directory to import data from.
    :param output_dir: A string pointing to the directory to output data to.
    :param sources: A list of sources to transform.
    """
    if not sources:
        # run all sources
        sources = list(DATA_SOURCES.keys())

    for source in sources:
        if source in DATA_SOURCES:
            logging.info(f"Parsing {source}")
            t = DATA_SOURCES[source](input_dir, output_dir)
            if source in ONTOLOGIES.keys():
                t.run(ONTOLOGIES[source])
            else:
                t.run()
