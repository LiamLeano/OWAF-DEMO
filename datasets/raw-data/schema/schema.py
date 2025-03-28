import os
import json
import sqlite3

def create_json_schema_from_sql(sql_file, json_file):
    """
    Creates a JSON schema from an SQL file, automatically excluding primary keys
    and specified columns.
    """

    try:
        #   Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        #   Construct the full path to the SQL file
        sql_file_path = os.path.join(script_dir, sql_file)

        #   Construct the full path to the JSON file
        json_file_path = os.path.join(script_dir, json_file)

        #   Read the SQL file
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()

        #   Extract table creation statements
        table_creation_statements = [
            statement for statement in sql_content.split(';')
            if 'CREATE TABLE' in statement
        ]

        #   Define columns to exclude (hashes)
        exclude_columns = ["sha256", "sha1", "md5", "crc32"]

        #   Parse table schemas
        schema = {}
        for table_statement in table_creation_statements:
            #   Extract table name
            table_name_start = table_statement.find('TABLE IF NOT EXISTS') + len(
                'TABLE IF NOT EXISTS')
            table_name_end = table_statement.find('(', table_name_start)
            table_name = table_statement[table_name_start:table_name_end].strip()

            #   Extract column names and identify primary keys
            columns_start = table_statement.find('(') + 1
            columns_end = table_statement.rfind(')')
            columns_str = table_statement[columns_start:columns_end].strip()
            columns = []
            primary_key_column = None  # Initialize primary_key_column

            for col_def in columns_str.split(','):
                col_def = col_def.strip()
                parts = col_def.split()
                col_name = parts[0].strip()
                columns.append(col_name)

                # Check for primary key definition (case-insensitive)
                if "PRIMARY" in col_def.upper() and "KEY" in col_def.upper():
                    primary_key_column = col_name
            
            #   Filter out excluded columns
            schema[table_name] = [
                col for col in columns if col and col not in exclude_columns and col != primary_key_column
            ]

        #   Write JSON schema to file
        with open(json_file_path, 'w') as f:
            json.dump(schema, f, indent=2)  #   Use indent for better formatting

        print(f"\nJSON schema created and saved to {json_file_path}\n")

    except FileNotFoundError:
        print(f"Error: SQL file '{sql_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

#   Example usage:
sql_file_path = 'OWAF-schema.sql'  #   Just the filename
json_file_path = 'OWAF-schema.json'  #   Just the filename
create_json_schema_from_sql(sql_file_path, json_file_path)