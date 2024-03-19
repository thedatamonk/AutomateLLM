import tiktoken
from jsonschema import validate
from jsonschema.exceptions import ValidationError

EMBEDDING_CTX_LENGTH = 8191
EMBEDDING_ENCODING = 'cl100k_base'


def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
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


