import shutil

import duckdb
import pystow

from ncbi_gene_pyobo.constants import DEFAULT_INPUT_DIR, GENE_CATEGORY, GENE_ID, NODES_TABLE_SCHEMA, TAXON_CATEGORY, TAXON_ID

ncbigene_module = pystow.module("ncbigene")


def ncbigene_2_duckdb():
    # Define the URL for the NCBI gene info file
    url = "https://ftp.ncbi.nlm.nih.gov/gene/DATA/gene_info.gz"
    local_storage = DEFAULT_INPUT_DIR / "gene_info.tsv"
    filtered_tsv = DEFAULT_INPUT_DIR / "filtered_ncbigene.tsv"

    if not local_storage.exists():

        with pystow.ensure_open_gz(key=ncbigene_module.base.name, url=url) as tsv_file:

            # Create a table and import the TSV data
            # Since we're reading from a file-like object, we need to save it to a temporary file first
            with open(local_storage, "wb") as temp_tsv_file:
                shutil.copyfileobj(tsv_file, temp_tsv_file)
    
    with duckdb.connect(database=":memory:", read_only=False) as conn:
        # Load the data into DuckDB
        conn.execute(f"CREATE TABLE ncbigene AS SELECT * FROM read_csv_auto('{str(local_storage)}')")
        conn.execute("ALTER TABLE ncbigene RENAME COLUMN '#tax_id' TO tax_id")
        row_count = conn.execute("SELECT COUNT(*) FROM ncbigene").fetchone()[0]
        print(f"Number of rows in the table: {row_count}")
        conn.execute(f"""
                        CREATE TABLE nodes ({NODES_TABLE_SCHEMA})
                     """)
        conn.execute(f"""
            INSERT INTO nodes (id, category)
            SELECT '{TAXON_ID}' || tax_id AS id,
                   '{TAXON_CATEGORY}' AS category 
            FROM ncbigene 
            UNION ALL 
            SELECT '{GENE_ID}' || GeneID AS id,
                   '{GENE_CATEGORY}' AS category                        
            FROM ncbigene
        """)
        
        import pdb; pdb.set_trace()
        
        
        
        
        
        
        
        
        
        
        
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
        
        # duckdb.sql('SELECT * FROM ncbigene WHERE "#tax_id" == 7 LIMIT 10')
        # duckdb.sql("SELECT * FROM ncbigene WHERE ncbigene.LocusTag == 'Dmel_CG3038' LIMIT 10")

        # duckdb.sql("CREATE TABLE new_table AS SELECT tax_id AS id FROM ncbigene UNION ALL SELECT GeneID FROM ncbigene")
        # conn.execute("select * from nodes limit 5").df()


