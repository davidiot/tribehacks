import interpreter as interp

text = interp.load_file()
stripped_text = interp.strip_parens(text)
interp.find_dependencies(stripped_text)