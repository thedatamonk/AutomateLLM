import tiktoken
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import os
import glob

EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = 'cl100k_base'


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """
    Returns the number of tokens in a text string.
    
    :param string: Input text string
    :param encoding_name: Encoding used for creating the vector embeddings
    :return: number of tokens of the input string
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def truncate_text_tokens(text, encoding_name=EMBEDDING_ENCODING, max_tokens=EMBEDDING_CTX_LENGTH):
    """Truncate a string to have `max_tokens` according to the given encoding."""
    encoding = tiktoken.get_encoding(encoding_name)
    return encoding.encode(text)[:max_tokens]

def is_valid_json(json_data, schema):
    """
    Check if the provided JSON data conforms to the given schema.

    :param json_data: A dict representing the JSON data to validate.
    :param schema: A dict representing the JSON schema to validate against.
    :return: True if json_data conforms to schema, False otherwise.
    """

    try:
        validate(instance=json_data, schema=schema)
        return True
    except ValidationError:
        return False

def load_examples(dataset_path, select_examples=None):
    """
    Load all or selected examples from a directory at `dataset_path`

    :param dataset_path: directory containing API wise code examples
    :param select_examples: List containing filenames of selected examples
    :return: dictionary where key is filename and value is the actual code snippet
    """

    if not os.path.isdir(dataset_path):
        raise FileNotFoundError(f"Directory not found: {dataset_path}")

    examples = {}
    search_pattern = os.path.join(dataset_path, '*.txt')
    for path in glob.glob(search_pattern):
        file_name = os.path.basename(path)
        
        if select_examples is None or file_name in select_examples:        
            with open(path, 'r', encoding='utf-8') as file:
                examples[file_name] = file.read()
    
    return examples

