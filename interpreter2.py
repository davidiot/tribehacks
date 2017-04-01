import interpreter as interp
import spacy
import spacy.symbols as sym
from textpipeliner import PipelineEngine
from textpipeliner.pipes import *

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
print(tokenized_vals)

doc = nlp(tokenized_vals[0][0])

pipes_structure = [SequencePipe([FindTokensPipe("VERB/nsubj/NNP"),
                                 NamedEntityFilterPipe(),
                                 NamedEntityExtractorPipe()]),
                       AggregatePipe([FindTokensPipe("VERB"),
                                      FindTokensPipe("VERB/xcomp/VERB/aux/*"),
                                      FindTokensPipe("VERB/xcomp/VERB")]),
                       AnyPipe([FindTokensPipe("VERB/[acomp,amod]/ADJ"),
                                AggregatePipe([FindTokensPipe("VERB/[dobj,attr]/NOUN/det/DET"),
                                               FindTokensPipe("VERB/[dobj,attr]/NOUN/[acomp,amod]/ADJ")])])
                      ]

engine = PipelineEngine(pipes_structure, doc, [0,1,2])
engine.process()