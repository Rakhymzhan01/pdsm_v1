#!/usr/bin/env python3
"""
Export data from remote PostgreSQL to local files for Docker initialization
"""
import pandas as pd
from sqlalchemy import create_engine
import os

# Remote database connection
remote_engine = create_engine("postgresql+psycopg2://postgres:akzhol2030@86.107.198.48:5432/karatobe")

# Tables to export
tables = ['wells', 'prod', 'pvt', 'tops']

print("🔄 Exporting data from remote database...")

# Create init directory if it doesn't exist
os.makedirs('init', exist_ok=True)

for table in tables:
    try:
        print(f"📥 Exporting table: {table}")
        df = pd.read_sql_table(table, con=remote_engine)
        
        # Export to CSV for easy import
        csv_file = f'init/{table}.csv'
        df.to_csv(csv_file, index=False)
        print(f"✅ Exported {len(df)} records from {table} to {csv_file}")
        
        # Also create SQL file for table structure and data
        sql_file = f'init/{table}.sql'
        with open(sql_file, 'w') as f:
            # Get table schema first
            schema_query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = '{table}' 
            ORDER BY ordinal_position;
            """
            
            schema_df = pd.read_sql(schema_query, con=remote_engine)
            
            # Create table SQL
            f.write(f"-- Table: {table}\n")
            f.write(f"DROP TABLE IF EXISTS {table};\n")
            f.write(f"CREATE TABLE {table} (\n")
            
            columns = []
            for _, row in schema_df.iterrows():
                col_def = f"    \"{row['column_name']}\" {row['data_type']}"
                if row['is_nullable'] == 'NO':
                    col_def += " NOT NULL"
                if row['column_default'] is not None:
                    col_def += f" DEFAULT {row['column_default']}"
                columns.append(col_def)
            
            f.write(",\n".join(columns))
            f.write("\n);\n\n")
            
            # Copy data from CSV
            f.write(f"\\COPY {table} FROM '/docker-entrypoint-initdb.d/{table}.csv' DELIMITER ',' CSV HEADER;\n")
        
        print(f"✅ Created SQL initialization file: {sql_file}")
        
    except Exception as e:
        print(f"❌ Error exporting {table}: {e}")

print("✅ Data export completed!")
print("\nNext steps:")
print("1. docker-compose up -d")
print("2. Update connection string to localhost:5432")