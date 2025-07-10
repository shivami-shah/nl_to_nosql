import re
import json
from bson.json_util import loads
from pymongo import MongoClient
from pymongo.errors import PyMongoError, OperationFailure
from config import DATABASE, HOST, PORT
from project_logger import setup_project_logger

class DBManager:
    logger = setup_project_logger("DBManager")
    
    def __init__(self):
        self.client = None
        self.db = None
        try:
            self.client = MongoClient(HOST, PORT)
            self.db = self.client[DATABASE]
            self.client.admin.command('ping') # Test connection
        except Exception as e:
            self.logger.error(f"Could not connect to MongoDB: {e}")
            
    def check_collections_in_db(self):
        if self.db is not None:
            return self.db.list_collection_names()
        return []
    
    def validate_find_query(self, collection_name: str, query: dict) -> bool:
        """
        Validates a MongoDB find query by attempting a dry run or a limited execution.

        Args:
            collection_name (str): The name of the collection to query.
            query (dict): The MongoDB query dictionary to validate.

        Returns:
            bool: True if the query is valid, False otherwise.
        """
        if self.db is None:
            self.logger.warning("Database connection not established. Cannot validate query.")
            return False
        
        if not isinstance(query, dict):
            self.logger.error(f"Find query must be a dictionary. Received: {type(query)} for collection '{collection_name}'. Query: {query}")
            return False

        try:
            collection = self.db[collection_name]
            collection.find(query).limit(0).next()
            # self.logger.info(f"Find query for collection '{collection_name}' is valid: {query}")
            return True
        except StopIteration:
            # self.logger.info(f"Find query for collection '{collection_name}' is syntactically valid: {query}")
            return True
        except OperationFailure as e:
            self.logger.error(f"Invalid find query for collection '{collection_name}': {query}. Error: {e}")
            return False
        except PyMongoError as e:
            self.logger.error(f"An unexpected PyMongo error occurred during find query validation for collection '{collection_name}': {query}. Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during find query validation for collection '{collection_name}': {query}. Error: {e}")
            return False
        
    def validate_aggregate_query(self, collection_name: str, pipeline: list) -> bool:
        """
        Validates a MongoDB aggregation pipeline for syntactic correctness and
        ensures it contains only read operations (disallowing $out and $merge).

        Args:
            collection_name (str): The name of the collection for the aggregation.
            pipeline (list): The MongoDB aggregation pipeline (list of dictionaries).

        Returns:
            bool: True if the pipeline is valid and read-only, False otherwise.
        """
        if self.db is None:
            self.logger.warning("Database connection not established. Cannot validate aggregate query.")
            return False
        
        if not isinstance(pipeline, list):
            self.logger.error(f"Aggregate pipeline must be a list. Received: {type(pipeline)} for collection '{collection_name}'. Pipeline: {pipeline}")
            return False

        # Check for disallowed write operations
        for stage in pipeline:
            if not isinstance(stage, dict):
                self.logger.error(f"Aggregation stage must be a dictionary. Received: {type(stage)} in pipeline for '{collection_name}'. Pipeline: {pipeline}")
                return False
            if "$out" in stage:
                self.logger.error(f"Aggregate pipeline contains disallowed '$out' stage for collection '{collection_name}'. Pipeline: {pipeline}")
                return False
            if "$merge" in stage:
                self.logger.error(f"Aggregate pipeline contains disallowed '$merge' stage for collection '{collection_name}'. Pipeline: {pipeline}")
                return False

        try:
            collection = self.db[collection_name]
            # Attempt to execute the pipeline up to the first result to validate syntax
            # If the pipeline is empty or yields no results, StopIteration is raised.
            collection.aggregate(pipeline).next()
            # self.logger.info(f"Aggregate query for collection '{collection_name}' is valid and read-only: {pipeline}")
            return True
        except StopIteration:
            # This is expected if the pipeline is valid but returns no documents.
            # self.logger.info(f"Aggregate query for collection '{collection_name}' is syntactically valid and read-only (no documents matched/result): {pipeline}")
            return True
        except OperationFailure as e:
            self.logger.error(f"Invalid aggregate query for collection '{collection_name}': {pipeline}. Error: {e}")
            return False
        except PyMongoError as e:
            self.logger.error(f"An unexpected PyMongo error occurred during aggregate query validation for collection '{collection_name}': {pipeline}. Error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during aggregate query validation for collection '{collection_name}': {pipeline}. Error: {e}")
            return False
     
    def validate_string_query(self, query_string: str) -> bool:
        """
        Parses a MongoDB find query string (e.g., "db.collection.find(...)")
         and validates it using the validate_find_query method.

        Args:
            query_string (str): The MongoDB find query in string format.

        Returns:
            bool: True if the parsed find query is valid, False otherwise.
        """
        if not isinstance(query_string, str):
            self.logger.error(f"Query string must be a string. Received: {type(query_string)}")
            return False

        # Regex to capture collection name, method, and arguments
        match = re.match(r"db\.(\w+)\.(\w+)\((.*)\)", query_string.strip())

        if not match:
            self.logger.error(f"Could not parse find query string format or method is not 'find': {query_string}")
            return False

        collection_name = match.group(1)
        method_name = match.group(2)
        args_string = match.group(3)

        # self.logger.info(f"Parsed query: Collection='{collection_name}', Method='{method_name}', Args='{args_string}'")

        try:
            # Attempt to parse arguments as JSON.
            # Step 1: Replace single quotes with double quotes for valid JSON
            json_compatible_args_string = args_string.replace("'", '"')
            # Step 2: Add double quotes around unquoted MongoDB keys (both field names and operators)
            json_compatible_args_string = re.sub(
                 r'([{,]\s*)([\w$]+)(?=\s*:)',
                 r'\1"\2"',
                json_compatible_args_string
            )

            parsed_args = None
            if not json_compatible_args_string.strip():
                # For methods like find() or aggregate(), empty args can be valid
                if method_name == "find":
                    parsed_args = {}
                elif method_name == "aggregate":
                    parsed_args = []
                else:
                    self.logger.error(f"Method '{method_name}' does not support empty arguments: {query_string}")
                    return False
            else:
                # Use bson.json_util.loads to handle MongoDB-specific JSON extensions
                parsed_args = loads(json_compatible_args_string)

            if method_name == "find":
                if not isinstance(parsed_args, dict):
                    self.logger.error(f"Invalid arguments for find method. Expected a dictionary. Received: {type(parsed_args)} for '{collection_name}'. Query string: {query_string}")
                    return False
                return self.validate_find_query(collection_name, parsed_args)
            elif method_name == "aggregate":
                if not isinstance(parsed_args, list):
                    self.logger.error(f"Invalid arguments for aggregate method. Expected a list (pipeline). Received: {type(parsed_args)} for '{collection_name}'. Query string: {query_string}")
                    return False
                return self.validate_aggregate_query(collection_name, parsed_args)
            else:
                self.logger.error(f"Unsupported MongoDB method for validation: {method_name} in query: {query_string}")
                return False

            return self.validate_find_query(collection_name, parsed_query_dict)

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode arguments as JSON for find query '{query_string}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during parsing or validation of find query string '{query_string}': {e}")
            return False


if __name__ == "__main__":    
    db = DBManager()
    print(db.check_collections_in_db())
    collection = "ForecastAccurray"
    query = { '$and': [{ "ChannelID": "dummy" }, { "PlantID": "dummy" }] }
    print(db.validate_find_query(collection, query))
    
    full_query = 'db.ForecastAccuracy.find({ $and: [{ "ChannelID": "dummy" }, { "PlantID": "dummy" }] })'
    print(db.validate_string_query(full_query))
    
    full_query = 'db.ForecastAccuracy.aggregate([{$group: {"_id": "$ChannelID", "sum_Quantity": {$sum: "$Quantity"}}}])'
    print(db.validate_string_query(full_query))