import pandas as pd
import os
import shutil
from config import OUTPUT_DIR, OUTPUT_CSV_DIR, USER_DIR

class DataCollator:
    def __init__(self):
        USER_DIR.mkdir(exist_ok=True)
        self.system_output_file = OUTPUT_DIR / "system_output.xlsx"
        self.user_output_file = USER_DIR / "output.xlsx"

    def collate_csv_to_excel(self):
        """
        Collates multiple CSV files into a single Excel file with sheets
        named after the prefix of the CSV filenames.

        Args:
            output_excel_filename (str): The name of the output Excel file.
        """
        if not os.path.exists(OUTPUT_CSV_DIR):
            print(f"Error: The directory {OUTPUT_CSV_DIR} does not exist.")
            return

        # Dictionary to hold dataframes grouped by their prefix (sheet name)
        grouped_data = {}

        for filename in os.listdir(OUTPUT_CSV_DIR):
            if filename.endswith(".csv"):
                filepath = os.path.join(OUTPUT_CSV_DIR, filename)
                try:
                    # Extract the prefix
                    parts = filename.split('_')
                    prefix = "_".join(parts[:-2])

                    # Read the CSV file
                    df = pd.read_csv(filepath)

                    # Append the dataframe to the list for its corresponding prefix
                    if prefix not in grouped_data:
                        grouped_data[prefix] = []
                    grouped_data[prefix].append(df)

                except Exception as e:
                    print(f"Error processing file {filename}: {e}")

        # Write the collated data to an Excel file
        try:
            with pd.ExcelWriter(self.system_output_file, engine='xlsxwriter') as writer:
                for prefix, dfs in grouped_data.items():
                    # Concatenate all dataframes for the current prefix
                    combined_df = pd.concat(dfs, ignore_index=True)
                    # Write to a sheet named after the prefix
                    combined_df.to_excel(writer, sheet_name=prefix, index=False)
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