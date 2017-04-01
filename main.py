import interpreter as interp

text = interp.load_file()
stripped_text = interp.strip_parens(text)
tokenized_text = interp.lengthy_structured_tokenization(text)
interp.get_dependency_graphs(tokenized_text)
