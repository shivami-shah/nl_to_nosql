import pandas as pd
import os
import shutil
from config import OUTPUT_DIR, OUTPUT_CSV_DIR, USER_DIR, PERMENANT_QUERY_TYPES_FILE
from DataReader import DataReader
from project_logger import setup_project_logger

class DataCollator:
    logger = setup_project_logger("DataCollator")
    
    def __init__(self):
        USER_DIR.mkdir(exist_ok=True)
        self.system_output_file = OUTPUT_DIR / "system_output.xlsx"
        self.user_output_file = USER_DIR / "output.xlsx"
        self.reader = DataReader()

    def collate_csv_to_excel(self):
        """
        Collates multiple CSV files into a single Excel file with sheets
        named after the collection_name of the CSV filenames.

        Args:
            output_excel_filename (str): The name of the output Excel file.
        """
        if not os.path.exists(OUTPUT_CSV_DIR):
            print(f"Error: The directory {OUTPUT_CSV_DIR} does not exist.")
            return

        # Dictionary to hold dataframes grouped by their collection_name (sheet name)
        grouped_data = {}
        query_types = self.reader.read_query_types_file(file=PERMENANT_QUERY_TYPES_FILE)

        for filename in os.listdir(OUTPUT_CSV_DIR):
            if filename.endswith(".csv"):
                filepath = os.path.join(OUTPUT_CSV_DIR, filename)
                try:
                    # Extract the collection_name
                    parts = filename.split('_')
                    collection_name = "_".join(parts[:-2])
                    
                    section_no = int(parts[-2])-1
                    subsection_no = int(str(parts[-1])[1:].split('.')[0])-1
                    section_details = query_types[section_no]
                    section = section_details["section"]
                    subsection = section_details["subsections"][subsection_no]
                                        
                    # Read the CSV file
                    df = pd.read_csv(filepath)
                    # Remove duplicate "Question" column values
                    records = len(df)
                    df = df.drop_duplicates(subset="Question")
                    dropped_records = records - len(df)
                    if dropped_records > 0:
                        self.logger.info(f"Dropped {dropped_records} duplicate records for {section} - {subsection}")
                    df["Section"] = section
                    df["Subsection"] = subsection

                    # Append the dataframe to the list for its corresponding collection_name
                    if collection_name not in grouped_data:
                        grouped_data[collection_name] = []
                    grouped_data[collection_name].append(df)

                except Exception as e:
                    print(f"Error processing file {filename}: {e}")

        # Write the collated data to an Excel file
        try:
            with pd.ExcelWriter(self.system_output_file, engine='xlsxwriter') as writer:
                for collection_name, dfs in grouped_data.items():
                    # Concatenate all dataframes for the current collection_name
                    combined_df = pd.concat(dfs, ignore_index=True)
                    # Write to a sheet named after the collection_name
                    combined_df.to_excel(writer, sheet_name=collection_name, index=False)
            print(f"Successfully collated CSVs into {self.system_output_file}")
        except Exception as e:
            print(f"Error writing to Excel file {self.system_output_file}: {e}")

    def copy_system_to_user_output(self):
        """
        Creates a copy of the system_output.xlsx file and places it in the user directory
        as output.xlsx.
        """
        if not self.system_output_file.exists():
            print(f"Error: Source file not found at {self.system_output_file}. Please run collate_csv_to_excel first.")
            return

        try:
            shutil.copy2(self.system_output_file, self.user_output_file)
            print(f"Successfully copied '{self.system_output_file.name}' to '{self.user_output_file}'")
        except FileNotFoundError:
            print(f"Error: Source file '{self.system_output_file.name}' not found during copy operation.")
        except Exception as e:
            print(f"Error copying file: {e}")

if __name__ == "__main__":
    collator = DataCollator()
    collator.collate_csv_to_excel()
    collator.copy_system_to_user_output()