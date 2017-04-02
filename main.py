import interpreter as interp

text = interp.load_file()
stripped_text = interp.strip_parens(text)
tokenized_text = interp.lengthy_structured_tokenization(text)
graphs = interp.get_dependency_graphs(tokenized_text)
for paragraph_array in graphs:
    for sentence_graph in paragraph_array:
        interp.save_dependency_graph(sentence_graph)
maps = interp.analyze_verbs(graphs)
interp.generate_p1(maps)
interp.generate_p2(maps)