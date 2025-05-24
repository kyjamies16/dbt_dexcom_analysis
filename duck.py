import duckdb

for file in ["dbt_duckdb.db", "dev.duckdb"]:
    print(f"\nChecking: {file}")
    con = duckdb.connect(file)
    tables = con.execute("SHOW TABLES").fetchall()
    print("Tables:", tables)
