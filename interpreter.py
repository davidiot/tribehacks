import graphviz as gv
import nltk
from nltk.parse.stanford import StanfordDependencyParser as sdp

dependency_parser = sdp(
    path_to_jar="stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0.jar",
    path_to_models_jar="stanford-corenlp-full-2016-10-31/stanford-corenlp-3.7.0-models.jar"
)

## Constants
VERB = ['VB', 'VBP']
NOUN = ['NN', 'NNS', 'VBG']

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
    src = gv.Source(convert_to_dot(dependency_graph))
    src.render(output_folder + sentence_from_graph(dependency_graph), view=True)


def convert_to_dot(dependency_graph):
    """ convert dependency graph to dot format
        based on the to_dot method 
        (@link http://www.nltk.org/_modules/nltk/parse/dependencygraph.html#DependencyGraph.to_dot)
    
    :param dependency_graph: dependency graph to convert
    :return: dot graph string
    """

    # Start the digraph specification
    s = 'digraph G{\n'
    s += 'edge [dir=forward]\n'
    s += 'node [shape=oval]\n'

    # Draw the remaining nodes
    for node in sorted(dependency_graph.nodes.values(), key=lambda v: v['address']):
            s += '\n%s [label="%s %s\n(%s)"]' % (node['address'], node['address'], node['word'], node['tag'])
            for rel, deps in node['deps'].items():
                for dep in deps:
                    if rel is not None:
                        s += '\n%s -> %s [label="%s"]' % (node['address'], dep, rel)
                    else:
                        s += '\n%s -> %s ' % (node['address'], dep)
    s += "\n}"

    return s


def sentence_from_graph(dependency_graph):
    """ get original sentence from a dependency graph
    
    :param dependency_graph: nltk dependency graph
    :return: original English sentence
    """
    words = [dependency_graph.get_by_address(i)['word']
             for i in sorted(dependency_graph.nodes)
             if dependency_graph.get_by_address(i)['word'] is not None]
    return " ".join(words)

def get_right_text_section(dg, node):
    start_index = node['address']
    end_index = find_max_node_index(dg, node)

    output = ""
    for n in range(start_index, end_index + 1):
        word = dg.get_by_address(n)['word']
        if word:
            output += " " + word

    return output.strip()

def get_object_text_section(dg, node):
    start_index = node['address']
    end_index = find_max_node_index(dg, node)

    output = []
    current_verb = node if (node['tag'] in VERB) else dg.nodes[find_next_verb_index(dg, node, end_index)]

    while (current_verb['address'] and current_verb['address'] <= end_index):
        verb_phrase = current_verb['word']

        next_v_index = find_next_verb_index(dg, current_verb, end_index)

        output_length_before_parse = len(output)

        for n in range(current_verb['address'] + 1, next_v_index):
            nn = dg.nodes[n]
            word = nn['word']
            tag = nn['tag']

            if word and tag in NOUN:
                output.append(verb_phrase + " " + word)

        output_length_after_parse = len(output)
        if output_length_before_parse == output_length_after_parse:
            output.append(verb_phrase)

        current_verb = dg.nodes[next_v_index]

    return output

def find_max_node_index(dg, node):
    children = node['deps']
    children_addresses = []
    for key, value in children.items():
        children_addresses.extend(value)

    max_val = node['address']
    for address in children_addresses:
        max_child_value = find_max_node_index(dg, dg.nodes[address])
        if max_child_value > max_val:
            max_val = max_child_value

    return max_val

def find_next_verb_index(dg, node, max_index):
    start_index = node['address']
    end_index = max_index

    for n in range(start_index + 1, end_index):
        if dg.get_by_address(n)['tag'] in VERB:
            return n

    return end_index + 1

g = get_dependency_graph(load_file('input2.txt'))
cr = g.nodes[0]
# max_val = find_max_node_index(g, cr)
# next_verb_index = find_next_verb_index(g, cr)
# print(next_verb_index)
print(get_object_text_section(g, cr))