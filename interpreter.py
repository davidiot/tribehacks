import graphviz as gv
import nltk
from nltk.parse.stanford import StanfordDependencyParser as sdp

dependency_parser = sdp(
    path_to_jar="stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0.jar",
    path_to_models_jar="stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0-models.jar"
)


def load_file(filename="input.txt"):
    """ loads a text file into a string
    
    :param filename: name of file to read
    :return: string content of file
    """
    with open(filename, "r") as f:
        return f.read()


def strip_parens(text):
    """ strips parenthesis from a string (works with nested parentheses)
        note that this method will leave the extra spaces behind, but this will not affect tokenization
    
    :param text: original string
    :return: text stripped of parenthetical words
    """
    left_parens = []
    right_parens = []
    paren_indices = []  # pairs that correspond to the [beginning, end] of each parenthetical expression

    for index, character in enumerate(text):
        if character is '(':
            left_parens.append(index)
        elif character is ')' and len(left_parens) > 0:
            right_parens.append(index)
            if len(right_parens) == len(left_parens):
                paren_indices.append([left_parens[0], right_parens[-1]])
                left_parens = []
                right_parens = []

    num_right_parens = len(right_parens)
    if num_right_parens is not 0:
        paren_indices.append([left_parens[-1 - num_right_parens + 1], right_parens[num_right_parens - 1]])

    index = 0
    output = ""
    for [beginning, end] in paren_indices:
        output += text[index:beginning]
        index = end + 1
    output += text[index:]

    return output


def lengthy_structured_tokenization(text):
    """ Tokenizes paragraphs and returns paragraphs and their associated sentences
    
    :param text: formatted text
    :return: Ordered rank 2 tensor: Outer array represents paragraphs. Inner array are sentences of the paragraph.
    """
    output = []
    paragraphs = tokenize_passage(text)

    for paragraph in paragraphs:
        sentences = nltk.sent_tokenize(paragraph)
        output.append(sentences)

    return output


def tokenize_passage(text):
    """ Tokenizes a passage by paragraph
    
    :param text: passage
    :return: array of paragraphs
    """
    output = []
    for s in text.splitlines():
        paragraph = s.strip()
        if len(paragraph) > 0:
            output.append(paragraph)
    return output


def get_dependency_graphs(tokenized_text):
    """ returns a dependency graph for each sentence in tokenized text
    
    :param tokenized_text: tokenized text array
    :return: array in same format with dependency graphs for each sentence
    """
    return [
        [get_dependency_graph(sentence) for sentence in paragraph]
        for paragraph in tokenized_text
    ]


def get_dependency_graph(text):
    """ uses Stanford CoreNLP to compute the dependency graph of a sentence
    
    :param text: English sentence (string).
    :return: nltk dependency graph
    """
    results = dependency_parser.raw_parse(text)
    dependency_graph = results.__next__()
    return dependency_graph


def print_dependency_graph(dependency_graph, output_folder="out/"):
    """ render a dependency graph using GraphVis
    
    :param dependency_graph: nltk dependency graph
    :param output_folder: path to output files
    :return: 
    """
    src = gv.Source(
        dependency_graph
            .to_dot()
            .replace("node [shape=plaintext]",
                     "node [shape=oval]")
    )
    src.render(output_folder + sentence_from_graph(dependency_graph), view=True)


def sentence_from_graph(dependency_graph):
    """ get original sentence from a dependency graph
    
    :param dependency_graph: nltk dependency graph
    :return: original English sentence
    """
    words = [dependency_graph.get_by_address(i)['word']
             for i in sorted(dependency_graph.nodes)
             if dependency_graph.get_by_address(i)['word'] is not None]
    return " ".join(words)
