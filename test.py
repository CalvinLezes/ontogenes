import PyPDF2
import nltk
import re
from nltk.corpus import stopwords
from article_analizer import ArticleAnalizer

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

def tokenise_sentense(sent, stop_words):
        sent = nltk.word_tokenize(sent)
        sent = [word for word in sent if not word in stop_words]
        sent = nltk.pos_tag(sent)
        sent = nltk.ne_chunk(sent)
        return sent 

grammar = r"""
    NP:  {<DT|PP\$>?<JJ>*<NN|NNS>}   # chunk determiner/possessive, adjectives and noun
         {<NNP>+}                # chunk sequences of proper nouns     
           """

def preprocess(document):
    sentences = nltk.sent_tokenize(document)
    stop_words = set(stopwords.words('english'))
    sentences = [tokenise_sentense(sent, stop_words) for sent in sentences]
    return sentences

def pdf_to_str(file_name):
    pdffileobj=open(file_name,'rb')
    pdfreader=PyPDF2.PdfReader(pdffileobj)
    pageobj=pdfreader.pages
    pages=[page.extract_text() for page in pageobj]
    return ''.join(pages)

gene_descriptions, gene_names = get_genes()

str = pdf_to_str('biomolecules-11-01759.pdf')
sentences = preprocess(str)
for sent in sentences:
     for word in sent:
          if type(word) is nltk.tree.tree.Tree:
            if word[0][0]  in gene_names:
                print(word[0][0])
#print(sentences)


#articleanalizer= ArticleAnalizer()
#print(articleanalizer.analise_article(str, gene_names))

