import tiktoken

def count_tokens(text: str, encoding_name='cl100k_base'):
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))