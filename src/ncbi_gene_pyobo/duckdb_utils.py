import shutil

import duckdb
import pystow

from ncbi_gene_pyobo.constants import DEFAULT_INPUT_DIR

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

    
    if not filtered_tsv.exists():
        create_filtered_tsv(str(local_storage), str(filtered_tsv))
    
    with duckdb.connect(database=":memory:", read_only=False) as conn:
        # Load the data into DuckDB
        conn.execute(f"CREATE TABLE ncbigene AS SELECT * FROM read_csv_auto('{str(filtered_tsv)}')")
        row_count = conn.execute("SELECT COUNT(*) FROM ncbigene").fetchone()[0]
        print(f"Number of rows in the table: {row_count}")
        import pdb; pdb.set_trace()
        # ! EXAMPLE DEBUG CODE
        # duckdb.sql(f"CREATE TABLE ncbigene AS SELECT * FROM read_csv_auto('{str(filtered_tsv)}')")
        # duckdb.sql('SELECT * FROM ncbigene WHERE "#tax_id" == 7 LIMIT 10')
        # duckdb.sql("SELECT * FROM ncbigene WHERE ncbigene.LocusTag == 'Dmel_CG3038' LIMIT 10")

            


def create_filtered_tsv(local_storage, filtered_tsv):
    with duckdb.connect(database=":memory:", read_only=False) as conn:
        # Load the data into DuckDB
        conn.execute(f"CREATE TABLE ncbigene AS SELECT * FROM read_csv_auto('{local_storage}')")
        row_count = conn.execute("SELECT COUNT(*) FROM ncbigene").fetchone()[0]

        # Get the list of all columns
        columns = conn.execute("PRAGMA table_info(ncbigene)").fetchall()
        column_names = [col[1] for col in columns]

        # Identify columns to exclude
        columns_to_include = []
        for col_name in column_names:
            # Properly quote the column name to handle special characters
            quoted_col_name = f'"{col_name}"'
            # Check if all values are '-' or None
            query = f"""SELECT COUNT(*) FROM ncbigene WHERE {quoted_col_name} IS NULL 
                            OR CAST({quoted_col_name} AS VARCHAR) == '-'"""
            count = conn.execute(query).fetchone()[0]
            if count < row_count:
                columns_to_include.append(quoted_col_name)
        
        # Create a new table excluding the invalid columns
        if columns_to_include:
            columns_str = ", ".join(columns_to_include)
            conn.execute(f"CREATE TABLE filtered_ncbigene AS SELECT {columns_str} FROM ncbigene")
            print("Filtered table created successfully.")
        else:
            print("No valid columns found to create a new table.")

        # Write the filtered table to a TSV file
        conn.execute(f"COPY filtered_ncbigene TO '{filtered_tsv}' (FORMAT 'csv', DELIMITER '\t', HEADER)")

def read_sql_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


def all_values_are_hyphen(column):
    return all(value == "-" for value in column)
