import nltk, re
from nltk.collocations import *
from owlready2 import *
import PyPDF2
from pathlib import Path
import itertools
import argparse

def get_genes():
    genes = []
    result = []
    regex = re.compile(
        r"""
        (?P<id>.*?)\s+
        (?P<name>.*?)\s+
        (?P<size>.*?)\s+
        (?P<annotation>.*)\s+
        """, re.VERBOSE)
    with open("genes.txt") as f:
        for line in f:
            match = regex.match(line)
            if match:
                genes.append(match.group("name"))
                result.append([
                    match.group("name"),
                    match.group("annotation")
                ])
            else:
                pass
    return result, genes

def pdf_to_str(file_name):
    pdffileobj=open(file_name,'rb')
    pdfreader=PyPDF2.PdfReader(pdffileobj)
    pageobj=pdfreader.pages
    pages=[page.extract_text() for page in pageobj]
    return ''.join(pages)

def preprocess(document):
    sentences = nltk.sent_tokenize(document)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    return sentences

def create_argparser():
    parser = argparse.ArgumentParser(description="Program to find markers of mental disorders")
    parser.add_argument("-d","--disorder", help = "name of disorder", required=True)
    parser.add_argument("-n", "--number", help="number of articles to analise")
    parser.add_argument("-o", "--ontology", help="name of file to write ontology in. Must be .owl format",
                        default="onto.owl")
    return parser

parser = create_argparser
args = parser.parse_args()
disorder = args.disorder
onto_file = args.ontology
gene_descriptions, gene_names = get_genes()

#disorder = 'depression'

path = Path(f'./articles/{disorder}/pdf')

article_dir = [e for e in path.iterdir()]

sentences = []

for pdf_file in article_dir:
    article = pdf_to_str(pdf_file)
    sentences.append(preprocess(article))

def frequency_calc(sentences):
    sentences = list(itertools.chain(*sentences))
    sentences = list(itertools.chain(*sentences))
    freq1 = nltk.FreqDist(w for w in sentences if w.isalnum())
    key = nltk.FreqDist()
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    for w in freq1:
        key[w] = bigram_measures.likelihood_ratio(freq1[w], (freq1[w], freq1.N()), freq1.N())
    chosen_genes = []
    for gene in gene_descriptions:
        gene_name = gene[0]
        frequency = freq1.freq(gene_name)
        if frequency > 0.00001:
            #print(gene_name, freq1.freq(gene_name))
            chosen_genes.append(gene)

onto = get_ontology("file://" + onto_file).load()

with onto:
    class Gene(Thing):
        pass

    class MentalDisorder(Thing):
        pass

    class Person(Thing):
        pass

    class Characteristic(Thing):
        pass

    class Nationality(Characteristic):
        pass

    class Age(Characteristic):
        pass

    class Gender(Characteristic):
        pass

    class Article(Thing):
        pass

    class Author(Thing):
        pass

    class has_disorder(Person >> MentalDisorder):
        pass

    class has_nationality(Person >> Nationality):
        pass

    class has_age(Person >> Age):
        pass

    class has_gender(Person >> Gender):
        pass

    class has_effect_on(Gene >> Person):
        pass

    class has_source(Person >> Article):
        pass

    class has_author(Article >> Author):
        pass

depression = MentalDisorder("depression")
person = Person("person")
person.has_disorder.append(depression)
for gene in chosen_genes:
    new_gene = Gene(gene[0])
    new_gene.has_effect_on.append(person)
    new_gene.comment = gene[1]

onto.save()
# for k,v in key.most_common(10):
#     print(f'{k:10s} {v:9.3f}')
#print(finder.nbest(bigram_measures.pmi, 10))

# f = open('text.txt')
# raw = f.read()
#sentences = preprocess(raw)
#sentences = nltk.sent_tokenize(text)
#list = []
#for sent in sentences:
#    if "References" in sent:
#        break
#    if find(sent) != None:
#        list.append(sent)
#print(genes)
#sentences = [nltk.ne_chunk(sent, binary=True) for sent in sentences]

