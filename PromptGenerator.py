import os
from DataReader import DataReader
from config import COLLECTION_INFO_DIR
from project_logger import setup_project_logger

class PromptGenerator:
    logger = setup_project_logger("PromptGenerator")
    
    def __init__(self):
        COLLECTION_INFO_DIR.mkdir(exist_ok=True)
    
    def _create_query_types_list(self, query_types:list):
        """Create a list of query types based on the provided query types dictionary

        Args:
            query_types (list): A list of dictionaries, where each dictionary represents a query type. Each dictionary should have keys for 'section', 'subsections', and 'examples'.

        """
        self.query_types_list = []
        
        for item in query_types:
            section = item["section"]
            subsections = item["subsections"]
            examples = item["examples"]
            
            for i in range(len(subsections)):
                self.query_types_list.append({
                    "section": section,
                    "subsection": subsections[i],
                    "example": examples[i]
                })

    def generate_prompts(self):        
        reader = DataReader()
        prompt1_template, prompt2_template, prompt3_template, prompt4_template = reader.read_prompts_files()
        query_types = reader.read_query_types_file()
        
        self._create_query_types_list(query_types)
        self.collections_info = [reader.read_collection_info_file(file) for file in os.listdir(COLLECTION_INFO_DIR) if str(file).endswith(".json")]
        
        all_template_sets = []
        
        for collection_info in self.collections_info:
            collection_name = collection_info["name"]
            schema = str(collection_info["schema"])
            mappings = str(collection_info["mappings"])
            nle = str(collection_info["nle"])
            
            prompt1 = prompt1_template.replace("COLLECTION_NAME", collection_name).replace("SCHEMA", schema).replace("NLE", nle)
            prompt2 = prompt2_template.replace("COLLECTION_NAME", collection_name).replace("SCHEMA", schema).replace("NLE", nle)
            prompt3 = prompt3_template.replace("COLLECTION_NAME", collection_name).replace("SCHEMA", schema).replace("NLE", nle)
            prompt4 = prompt4_template.replace("COLLECTION_NAME", collection_name).replace("SCHEMA", schema).replace("NLE", nle)
            
            for query_type in self.query_types_list:
                final_prompt1 = prompt1.replace("TYPE_OF_QUERY", f'{query_type["section"]}\n{query_type["subsection"]}')
                final_prompt2 = prompt2.replace("TYPE_OF_QUERY", f'{query_type["section"]}\n{query_type["subsection"]}')
                final_prompt3 = prompt3.replace("TYPE_OF_QUERY", f'{query_type["section"]}\n{query_type["subsection"]}')
                final_prompt4 = prompt4.replace("TYPE_OF_QUERY", f'{query_type["section"]}\n{query_type["subsection"]}')
                final_prompt1 = final_prompt1.replace("EXAMPLE", f'{query_type["example"]}')
                final_prompt2 = final_prompt2.replace("EXAMPLE", f'{query_type["example"]}')
                final_prompt3 = final_prompt3.replace("EXAMPLE", f'{query_type["example"]}')
                final_prompt4 = final_prompt4.replace("EXAMPLE", f'{query_type["example"]}')
                
                all_template_sets.append({"collection" : collection_name, "query_type": query_type,
                                          "prompt1": final_prompt1, "prompt2": final_prompt2, 
                                          "prompt3": final_prompt3, "prompt4": final_prompt4
                                        })
            self.logger.info(f"Generated queries templates for {collection_name}")
        self.logger.info(f"Finished generating queries templates")
        return all_template_sets


if __name__ == "__main__":
    gen = PromptGenerator()
    print(gen.generate_prompts())