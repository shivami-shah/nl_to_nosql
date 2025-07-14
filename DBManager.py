import ast
import textwrap
import pymongo
from pymongo import MongoClient
from config import DATABASE, HOST, PORT
from project_logger import setup_project_logger


class DBManager:
    logger = setup_project_logger("DBManager")

    def __init__(self):
        self.client = None
        self.db = None
        try:
            self.client = MongoClient(HOST, PORT, serverSelectionTimeoutMS=1000)
            self.db = self.client[DATABASE]
            self.client.admin.command('ping')
            self.logger.info("Connected to MongoDB.")
        except Exception as e:
            self.logger.error(f"Could not connect to MongoDB: {e}")

    def check_collections_in_db(self):
        if self.db is not None:
            return self.db.list_collection_names()
        return []

    def _is_valid_syntax(self, code_str):
        """Check if code has valid Python syntax (e.g., matching brackets)"""
        try:
            ast.parse(code_str)
            return True
        except SyntaxError as e:
            self.logger.error(f"Syntax error in query: {e}")
            return False

    def auto_fix_brackets(self, code_str):
        """Fix unbalanced (, {, [ brackets by appending the required closing brackets."""
        bracket_pairs = {'(': ')', '{': '}', '[': ']'}
        opening = set(bracket_pairs.keys())
        closing = set(bracket_pairs.values())
        stack = []

        for char in code_str:
            if char in opening:
                stack.append(bracket_pairs[char])
            elif char in closing:
                if stack and char == stack[-1]:
                    stack.pop()

        # Add missing closing brackets in reverse nesting order
        return code_str + ''.join(reversed(stack))


    def _wrap_if_not_lambda(self, query_str):
        """If not a lambda, try to wrap the raw query (e.g., db.COLLECTION.find(...)) into lambda db: ..."""
        if "lambda db" in query_str:
            return query_str  # Already correct

        try:
            stripped = query_str.strip()
            if not stripped.startswith("db."):
                raise ValueError("Query must start with 'db.'")

            parts = stripped.split(".")
            if len(parts) < 3:
                raise ValueError("Query must follow format: db.Collection.operation(...)")

            collection = parts[1]
            operation = ".".join(parts[2:])  # Everything after collection name
            return f'lambda db: db["{collection}"].{operation}'
        except Exception as e:
            self.logger.error(f"Cannot wrap query into lambda: {e}")
            return None

    def validate_query(self, query_str, attempt_fix=True):
        """
        Validate and run a MongoDB query.
        Steps:
        - Fix brackets (optional)
        - Wrap non-lambdas into lambda db: ...
        - Check syntax
        - Run the query
        """
        query_str = textwrap.dedent(query_str)

        if attempt_fix:
            query_str = self.auto_fix_brackets(query_str)

        query_str = self._wrap_if_not_lambda(query_str)
        if query_str is None:
            return False

        if not self._is_valid_syntax(query_str):
            return False

        try:
            query_lambda = eval(query_str)

            if not callable(query_lambda):
                self.logger.error("Evaluated query is not callable. Expected a lambda.")
                return False

            result = query_lambda(self.db)

            if hasattr(result, '__iter__') and not isinstance(result, dict):
                list(result)  # Force evaluation of cursor

            return query_str

        except Exception as e:
            self.logger.error(f"Query runtime error: {e}")
            return False
