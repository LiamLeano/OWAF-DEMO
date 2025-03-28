import os # Used for encoding and decoding JSON data
import json # File path manipulation and directory operations.
import re # Pattern matching and text manipulation.
import hashlib # Hash algorithms to compare new dataset fragments

def slugify(text):
    """
    Convert a string into a file-friendly-slug:
    - Lowercase the text.
    - Replace spaces and underscores with dashes.
    - Preserve dots (for version numbers) unless at the start or end.
    - Remove any other special characters.
    """
    text = text.lower().replace(" ", "-").replace("_", "-")
    return re.sub(r'[^a-z0-9\-.]', '', text).strip(".")

def normalize_value(value):
    """
    Convert empty strings to None (JSON null) for consistency.
    """
    return value if value not in ("", None) else None

def write_file_if_different(file_path, content_str):
    """
    Write content_str to file_path only if the file does not exist or if the content hash differs.
    This minimizes unnecessary write cycles by using a SHA256 hash comparison.
    """
    new_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
            existing_hash = hashlib.sha256(existing_content.encode('utf-8')).hexdigest()
            if existing_hash == new_hash:
                print(f"Skipping write for {file_path} (content hash unchanged)")
                return
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_str)
        print(f"Written file {file_path}")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")

def cleanup_directory(directory, expected_files):
    """
    Delete any .json file in the specified directory that is not in expected_files.
    """
    for filename in os.listdir(directory):
        if filename.endswith(".json") and filename not in expected_files:
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"Deleted orphaned .json file {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

def process_table(table_obj, table_folder, schema_mapping, parent_dir):
    """
    Process a single table (subject) object.
    1. Verify a schema mapping exists for the table.
    2. Skip the primary key (first element) in each row and map the remaining values to a dictionary.
    3. Auto-fill missing media_piece_path and screenshot_path fields using the slugified values of topic, category, and name.
    4. Group entries by the "category" field.
    5. Sort the entries alphabetically by name.
    6. Write an aggregated JSON file for the entire table (subject) in the parent directory.
    7. For each category:
         - Create a folder inside the table folder.
         - Save each entry as an individual JSON file.
         - Write an aggregated JSON file for that category.
         - Cleanup any outdated JSON files in the category folder.
    Returns a list of all entries processed for this table.
    """
    table_name = table_obj["name"].lower()
    if table_name not in schema_mapping:
        print(f"No schema defined for table '{table_name}'. Skipping...")
        return

    columns = schema_mapping[table_name]
    rows = table_obj.get("rows", [])
    print(f"Number of rows found in '{table_name}':", len(rows))
    if not rows:
        print(f"No rows found in table '{table_name}'.")
        return

    all_entries = []
    data_by_category = {}

    for row in rows:
        entry = {}
        for i, key in enumerate(columns):
            entry[key] = normalize_value(row[i+1])
        
        entry["name"] = normalize_value(entry.get("name", "unknown"))
        entry["topic"] = normalize_value(entry.get("topic", "unknown"))
        entry["category"] = normalize_value(entry.get("category", "unknown"))
        
        if entry.get("file_name"):
            entry["file_name"] = slugify(entry["file_name"])

        topic = slugify(entry["topic"])
        category = slugify(entry["category"])
        file_name_slug = slugify(entry["name"])
        entry["media_piece_path"] = f"/content/{topic}/{category}/{file_name_slug}.html"
        # Only change screenshot path if it's not already set
        if not entry.get("screenshot_path"):
            entry["screenshot_path"] = f"/media/content/{topic}/{category}/{file_name_slug}.jpg"

        all_entries.append(entry)
        cat = entry.get("category", "unknown")
        if cat not in data_by_category:
            data_by_category[cat] = []
        data_by_category[cat].append(entry)

    all_entries.sort(key=lambda entry: entry.get("name", "").lower())

    aggregated_table_file = os.path.join(parent_dir, f"{table_name}.json")
    content_str = json.dumps(all_entries, indent=4)
    write_file_if_different(aggregated_table_file, content_str)

    for category, entries in data_by_category.items():
        entries.sort(key=lambda entry: entry.get("name", "").lower())
        cat_slug = slugify(category)
        cat_folder = os.path.join(table_folder, cat_slug)
        os.makedirs(cat_folder, exist_ok=True)
        expected_files = set()
        for entry in entries:
            file_name_slug = slugify(entry["name"])
            filename = f"{file_name_slug}.json"
            expected_files.add(filename)
            entry_file = os.path.join(cat_folder, filename)
            entry_str = json.dumps(entry, indent=4)
            write_file_if_different(entry_file, entry_str)
        aggregated_cat_file = os.path.join(table_folder, f"{cat_slug}.json")
        cat_content_str = json.dumps(entries, indent=4)
        write_file_if_different(aggregated_cat_file, cat_content_str)
        cleanup_directory(cat_folder, expected_files)

    return all_entries

def generate_category_lists(global_entries, output_base):
    """
    Group entries by topic and extract unique original category names for each topic.
    For each topic, write a JSON file named "{topic_slug}-categories.json" 
    in the folder "/datasets/content/{topic_slug}/".
    """
    topics = {}
    for entry in global_entries:
        topic = entry["topic"]
        topics.setdefault(topic, set()).add(entry["category"])
    
    for topic_original, categories in topics.items():
        topic_slug = slugify(topic_original)
        # Define the output folder for the topic inside the datasets/content folder.
        topic_folder = os.path.join(output_base, topic_slug)
        os.makedirs(topic_folder, exist_ok=True)
        # Build the filename e.g., "software-categories.json"
        output_file = os.path.join(topic_folder, f"{topic_slug}-categories.json")
        # Convert the set to a sorted list (using original names).
        category_list = sorted(list(categories))
        content_str = json.dumps(category_list, indent=4)
        write_file_if_different(output_file, content_str)

import os
import json
import re  # Import the regular expression module

def generate_topics_list(global_entries, output_base):
    """
    Extract unique topics from global_entries and write them to a JSON file.
    The output file is located at "/datasets/content/topics.json" and is expected
    to contain the following structure:
    
    [
        "Audio",
        "Documents",
        "Software",
        "Videos"
    ]
    
    Parameters:
      - global_entries: A list of dictionaries where each entry has a "topic" key.
      - output_base: The base directory path (e.g., "/datasets/content") where the topics.json
                     file will be saved.
    """
    # Use a set to collect unique topics, converting them to title case
    # to get the first letter of each word to uppercase
    topics_set = {entry["topic"].title() for entry in global_entries if "topic" in entry}
    
    # Convert the set to a sorted list
    topics_list = sorted(list(topics_set))
    
    # Define the output file path for topics.json
    output_file = os.path.join(output_base, "topics.json")
    
    # Convert the list to a formatted JSON string
    content_str = json.dumps(topics_list, indent=4)
    
    # Write the file only if the content has changed.
    write_file_if_different(output_file, content_str)


def main():
    """
    Main function to process the OWAF JSON database.
    1. Set paths for the database and templates.
    2. Load the input JSON file (OWAF.json) exported from SQLiteStudio.
    3. Verify the JSON structure.
    4. Define the schema mapping for each table.
    5. Process each table object to generate aggregated and individual JSON files.
    6. Aggregate all entries from all tables into a universal file named content.json.
    7. Generate category lists for each topic.
    """
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # In this script, the output for dataset fragments is in a "content" folder inside the current directory.
    output_base = os.path.join(script_dir, "content")
    os.makedirs(output_base, exist_ok=True)

    input_file = os.path.join(script_dir, "./raw-data/OWAF-raw.json")
    print("\nReading data from:", input_file)
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            db_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found. Please check the file location.")
        return

    if "objects" not in db_data:
        print("Error: The JSON structure is not as expected. Missing 'objects' key.")
        return

    script_dir = os.path.dirname(os.path.realpath(__file__))
    schema_file = os.path.join(script_dir, "./raw-data/schema/OWAF-schema.json")

    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_mapping = json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file {schema_file} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in schema file {schema_file}.")
        return

    global_entries = []
    for obj in db_data["objects"]:
        if obj.get("type") == "table":
            table_name = obj.get("name", "unknown").lower()
            topic_folder = os.path.join(output_base, table_name)
            os.makedirs(topic_folder, exist_ok=True)
            print(f"\nProcessing table '{table_name}'...")
            table_entries = process_table(obj, topic_folder, schema_mapping, output_base)
            if table_entries:
                global_entries.extend(table_entries)
    
    global_entries.sort(key=lambda entry: entry.get("name", "").lower())

    universal_file = os.path.join(script_dir, "content.json")
    universal_content = json.dumps(global_entries, indent=4)
    write_file_if_different(universal_file, universal_content)
    print(f"\nCreated universal dataset file {universal_file} with {len(global_entries)} entries.\n")

    # Generate category lists for each topic.
    generate_category_lists(global_entries, output_base)

    # Generate the topics list.
    generate_topics_list(global_entries, output_base)
    
    print("\nDataset fragments generation complete!\n")

if __name__ == "__main__":
    main()
