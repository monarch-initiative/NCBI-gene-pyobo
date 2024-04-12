"""Command line interface for ncbi-gene-pyobo."""

import logging
from os import makedirs

import click
import fastobo
from pyobo.sources.ncbigene import get_obo

from ncbi_gene_pyobo import __version__
from ncbi_gene_pyobo.constants import DEFAULT_INPUT_DIR, DEFAULT_OUTPUT_DIR, OBO_FILENAME
from ncbi_gene_pyobo.duckdb_utils import ncbigene_2_duckdb
from ncbi_gene_pyobo.transform import DATA_SOURCES
from ncbi_gene_pyobo.transform import transform as kg_transform

# from ncbi_gene_pyobo.main import get_obo_file

__all__ = [
    "get_obo",
]

logger = logging.getLogger(__name__)

output_option = click.option(
    "-o",
    "--output-path",
    type=click.Path(),
    default=DEFAULT_INPUT_DIR / OBO_FILENAME,
    help="The output path for the OBO file.",
)
output_format_option = click.option(
    "--output-format",
    "-f",
    type=click.Choice(["owl", "json"]),
    default="owl",
    help="The output format for the edges.",
)
show_status_option = click.option("--show-status/--no-show-status", default=True)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """
    CLI for ncbi-gene-pyobo.

    :param verbose: Verbosity while running.
    :param quiet: Boolean to be quiet or verbose.
    """
    makedirs(DEFAULT_INPUT_DIR, exist_ok=True)
    makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    if verbose >= 2:
        logger.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        logger.setLevel(level=logging.INFO)
    else:
        logger.setLevel(level=logging.WARNING)
    if quiet:
        logger.setLevel(level=logging.ERROR)


@main.command("get-obo")
@output_option
def get_obo_file(output_path: str = DEFAULT_INPUT_DIR / OBO_FILENAME):
    """Get the obo file."""
    # get_obo_file(output_path)
    obo_file = get_obo()
    obo_file.write_obo(output_path, use_tqdm=True)


@main.command()
@click.option("input_dir", "-i", default=DEFAULT_INPUT_DIR, type=click.Path(exists=True))
@click.option("output_dir", "-o", default=DEFAULT_OUTPUT_DIR, type=click.Path())
@click.option("sources", "-s", default=None, multiple=True, type=click.Choice(DATA_SOURCES.keys()))
@show_status_option
def transform(*args, **kwargs) -> None:
    """
    Call project_name/transform/[source name]/ for node & edge transforms.

    :param input_dir: A string pointing to the directory to import data from.
    :param output_dir: A string pointing to the directory to output data to.
    :param sources: A list of sources to transform.
    :return: None
    """
    # call transform script for each source
    kg_transform(*args, **kwargs)

    return None


@main.command()
@click.argument("input", type=click.Path(exists=True))
@output_option
@output_format_option
def convert(input: str, output_path: str, output_format: str):
    """Convert an OBO file to a different format."""
    if not output_format:
        output_format = output_path.split(".")[-1]
    obo_doc = fastobo.load(input)
    if "default-namespace" not in obo_doc.header:
        obo_doc.header.insert(99, fastobo.header.DefaultNamespaceClause("NCBIGene"))
    if output_format == "owl":
        fastobo.dump_owl(obo_doc, output_path, format="ofn")
    elif output_format == "json":
        fastobo.dump_graph(obo_doc, output_path)
    else:
        raise ValueError(f"invalid output format: {output_format}")


@main.command("to-duckdb")
def click_ncbigene_2_duckdb():
    """Convert the NCBI Gene database to a DuckDB database."""
    ncbigene_2_duckdb()


if __name__ == "__main__":
    main()
