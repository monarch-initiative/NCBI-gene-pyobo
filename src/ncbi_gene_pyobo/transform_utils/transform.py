"""Transform utilities."""

from pathlib import Path
from typing import Optional

from ncbi_gene_pyobo.constants import (
    CATEGORY_COLUMN,
    DESCRIPTION_COLUMN,
    ID_COLUMN,
    IRI_COLUMN,
    NAME_COLUMN,
    OBJECT_COLUMN,
    PREDICATE_COLUMN,
    PROVIDED_BY_COLUMN,
    RELATION_COLUMN,
    SAME_AS_COLUMN,
    SUBJECT_COLUMN,
    SUBSETS_COLUMN,
    SYNONYM_COLUMN,
    XREF_COLUMN,
)


class Transform:
    """Parent class for transforms, that sets up a lot of default file info."""

    def __init__(
        self,
        source_name,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Instantiate Transform object.

        :param source_name: Name of resource.
        :param input_dir: Location of input directory, defaults to None
        :param output_dir: Location of output directory, defaults to None
        :param nlp: Boolean for possibility of using NLP or not, defaults to False
        """
        # default columns, can be appended to or overwritten as necessary
        self.source_name = source_name
        self.node_header = [
            ID_COLUMN,
            CATEGORY_COLUMN,
            NAME_COLUMN,
            DESCRIPTION_COLUMN,
            XREF_COLUMN,
            PROVIDED_BY_COLUMN,
            SYNONYM_COLUMN,
            IRI_COLUMN,
            OBJECT_COLUMN,
            PREDICATE_COLUMN,
            RELATION_COLUMN,
            SAME_AS_COLUMN,
            SUBJECT_COLUMN,
            SUBSETS_COLUMN,
        ]
        self.edge_header = [
            SUBJECT_COLUMN,
            PREDICATE_COLUMN,  # was "edge_label",
            OBJECT_COLUMN,
            RELATION_COLUMN,
            PROVIDED_BY_COLUMN,
        ]

        # default dirs
        self.input_base_dir = Path(input_dir) if input_dir else self.DEFAULT_INPUT_DIR
        self.output_base_dir = Path(output_dir) if output_dir else self.DEFAULT_OUTPUT_DIR
        self.output_dir = self.output_base_dir / source_name

        # default filenames
        self.output_node_file = self.output_dir / "nodes.tsv"
        self.output_edge_file = self.output_dir / "edges.tsv"
        self.output_json_file = self.output_dir / "nodes_edges.json"
        self.subset_terms_file = self.input_base_dir / "subset_terms.tsv"

        Path.mkdir(self.output_dir, exist_ok=True, parents=True)
