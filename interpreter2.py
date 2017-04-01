import interpreter as interp
import spacy
import spacy.symbols as sym

nlp = spacy.load('en')

def spacy_tokenization(text):
    output = []
    paragraphs = interp.tokenize_passage(text)

    for paragraph in paragraphs:
        doc = nlp(paragraph)
        sentences = [sent.string.strip() for sent in doc.sents]
        output.append(sentences)
        return output

tokenized_vals = spacy_tokenization(interp.load_file('input2.txt'))
doc = nlp(tokenized_vals[0][0])
print(doc)

verbs = set()
for possible_verb in doc:
    if possible_verb.pos == sym.VERB:
        # s = ""
        # for c in possible_verb.subtree:
        #     s += c.text + "---"
        # print(s)

        span = doc[possible_verb.i : possible_verb.right_edge.i + 1]
        # print(span[0])

        print(possible_verb.text, possible_verb.lemma, possible_verb.lemma_, possible_verb.tag, possible_verb.tag_, possible_verb.pos, possible_verb.pos_)

        verbs.add(possible_verb)
