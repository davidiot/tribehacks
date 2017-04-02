import interpreter as interp

text = interp.load_file()
stripped_text = interp.strip_parens(text)
tokenized_text = interp.lengthy_structured_tokenization(text)
graphs = interp.get_dependency_graphs(tokenized_text)
for paragraph_array in graphs:
    for sentence_graph in paragraph_array:
        print(interp.sentence_from_graph(sentence_graph))
        interp.print_dependency_graph(sentence_graph)
        print(interp.get_object_text_section(sentence_graph))
