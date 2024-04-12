import shutil

import duckdb
import pystow

from ncbi_gene_pyobo.constants import DEFAULT_INPUT_DIR, GENE_CATEGORY, GENE_ID, NODE_HEADER, NODES_TABLE_SCHEMA, TAXON_CATEGORY, TAXON_ID

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
        conn.execute(f"""CREATE TABLE nodes ({NODES_TABLE_SCHEMA})""")
        conn.execute(f"""
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
        
        # conn.execute('SELECT * FROM ncbigene WHERE "#tax_id" == 7 LIMIT 10').df()
        # conn.execute("SELECT * FROM ncbigene WHERE ncbigene.LocusTag == 'Dmel_CG3038' LIMIT 10").df()

        # duckdb.sql("CREATE TABLE new_table AS SELECT tax_id AS id FROM ncbigene UNION ALL SELECT GeneID FROM ncbigene")
        # conn.execute("select * from nodes limit 5").df()
        # conn.execute("SELECT DISTINCT Symbol FROM ncbigene").df()
        # conn.execute("select * from nodes limit 5").df()
        # conn.execute("select * from nodes WHERE id like '%Gene:%' and name NOT NULL limit 5").df()


