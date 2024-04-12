"""Convert the NCBI Gene data to a DuckDB database and export in KGX format."""

import shutil

import duckdb
import pystow

from ncbi_gene_pyobo.constants import (
    DEFAULT_INPUT_DIR,
    DEFAULT_OUTPUT_DIR,
    EDGE_HEADER,
    EDGES_TABLE_SCHEMA,
    GENE_CATEGORY,
    GENE_ID,
    IN_TAXON_PREDICATE,
    NODE_HEADER,
    NODES_TABLE_SCHEMA,
    PRIMARY_KNOWLEDGE_SOURCE,
    TAXON_CATEGORY,
    TAXON_ID,
)

ncbigene_module = pystow.module("ncbigene")


def ncbigene_2_duckdb():
    """Convert the NCBI Gene data to a DuckDB database and export in KGX format."""
    url = "https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz"
    local_storage = DEFAULT_INPUT_DIR / "gene_info.tsv"
    nodes_output = DEFAULT_OUTPUT_DIR / "nodes.tsv"
    edges_output = DEFAULT_OUTPUT_DIR / "edges.tsv"

    if not local_storage.exists():

        with pystow.ensure_open_gz(key=ncbigene_module.base.name, url=url) as tsv_file:

            # Create a table and import the TSV data
            # Since we're reading from a file-like object, we need to save it to a temporary file first
            with open(local_storage, "wb") as temp_tsv_file:
                shutil.copyfileobj(tsv_file, temp_tsv_file)

    with duckdb.connect(database=":memory:", read_only=False) as conn:
        # Load the data into DuckDB
        conn.execute(
            f"CREATE TABLE ncbigene AS SELECT * FROM read_csv_auto('{str(local_storage)}', normalize_names = true)"
        )
        # conn.execute("ALTER TABLE ncbigene RENAME COLUMN '#tax_id' TO tax_id")
        row_count = conn.execute("SELECT COUNT(*) FROM ncbigene").fetchone()[0]
        print(f"Number of rows in the table: {row_count}")
        # Nodes table
        conn.execute(f"""CREATE TABLE nodes ({NODES_TABLE_SCHEMA})""")
        conn.execute(
            f"""
                        INSERT INTO nodes ({",".join(NODE_HEADER)})
                        SELECT CONCAT('{TAXON_ID}', tax_id) AS id,
                            '{TAXON_CATEGORY}' AS category,
                                NULL AS name,
                                NULL AS description,
                                NULL AS xref,
                                'NCBI Gene' AS provided_by,
                                NULL AS synonym
                        FROM ncbigene
                        UNION ALL
                        SELECT CONCAT('{GENE_ID}', GeneID) AS id,
                                '{GENE_CATEGORY}' AS category,
                                CASE WHEN Symbol = 'NEWENTRY' THEN NULL ELSE Symbol END AS name,
                                CASE WHEN description = '-' THEN NULL ELSE description END AS description,
                                CASE WHEN dbXrefs = '-' THEN NULL ELSE dbXrefs END AS xref,
                                'NCBI Gene' AS provided_by,
                                CASE WHEN Synonyms = '-' THEN NULL ELSE Synonyms END AS synonym
                        FROM ncbigene
                    """
        )
        conn.execute(f"COPY (SELECT * FROM nodes) TO '{str(nodes_output)}' (FORMAT 'csv', DELIMITER '\t')")
        print(f"Nodes table created and written to {nodes_output}")

        # Edges table
        conn.execute(f"""CREATE TABLE edges ({EDGES_TABLE_SCHEMA})""")
        conn.execute(
            f"""
            INSERT INTO edges ({",".join(EDGE_HEADER)})
            SELECT CONCAT('{GENE_ID}', GeneID) AS subject,
                   '{IN_TAXON_PREDICATE}' AS predicate,
                   CONCAT('{TAXON_ID}', tax_id) AS object,
                   '{PRIMARY_KNOWLEDGE_SOURCE}' AS primary_knowledge_source
            FROM ncbigene
        """
        )
        conn.execute(f"COPY (SELECT * FROM edges) TO '{str(edges_output)}' (FORMAT 'csv', DELIMITER '\t')")
        print(f"Edges table created and written to {edges_output}")

        # ! EXAMPLE DEBUG CODE
        # duckdb.sql(f"CREATE TABLE ncbigene AS SELECT * FROM read_csv_auto('{str(local_storage)}')")
        # duckdb.sql("SELECT column_name FROM information_schema.columns WHERE table_name = 'ncbigene'")
        # ┌───────────────────────────────────────┐
        # │              column_name              │
        # │                varchar                │
        # ├───────────────────────────────────────┤
        # │ #tax_id                               │
        # │ GeneID                                │
        # │ Symbol                                │
        # │ LocusTag                              │
        # │ Synonyms                              │
        # │ dbXrefs                               │
        # │ chromosome                            │
        # │ map_location                          │
        # │ description                           │
        # │ type_of_gene                          │
        # │ Symbol_from_nomenclature_authority    │
        # │ Full_name_from_nomenclature_authority │
        # │ Nomenclature_status                   │
        # │ Other_designations                    │
        # │ Modification_date                     │
        # │ Feature_type                          │
        # ├───────────────────────────────────────┤
        # │                16 rows                │

        # conn.execute('SELECT * FROM ncbigene WHERE "#tax_id" == 7 LIMIT 10').df()
        # conn.execute("SELECT * FROM ncbigene WHERE ncbigene.LocusTag == 'Dmel_CG3038' LIMIT 10").df()

        # duckdb.sql("""CREATE TABLE new_table AS SELECT tax_id AS
        # id FROM ncbigene UNION ALL SELECT GeneID FROM ncbigene""")
        # conn.execute("select * from nodes limit 5").df()
        # conn.execute("SELECT DISTINCT Symbol FROM ncbigene").df()
        # conn.execute("select * from nodes limit 5").df()
        # conn.execute("select * from nodes WHERE id like '%Gene:%' and name NOT NULL limit 5").df()
        # conn.execute("select * from edges LIMIT 5").df()
