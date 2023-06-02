import nltk
from nltk.corpus import stopwords
import logging
nltk.download('stopwords')

class ArticleAnalizer:

    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")

    def tokenise_sentense(self, sent, stop_words):
        sent = nltk.word_tokenize(sent)
        sent = [word for word in sent if not word in stop_words]
        sent = nltk.pos_tag(sent)
        sent = nltk.ne_chunk(sent)
        return sent 

    def preprocess(self, document):
        sentences = nltk.sent_tokenize(document)
        stop_words = set(stopwords.words('english'))
        sentences = [self.tokenise_sentense(sent, stop_words) for sent in sentences]
        return sentences

    def analise_article(self, article, genes):
        sentences = self.preprocess(article)  
        logging.info('preprocessed article')
        found_genes = []
        for sent in sentences:
            for word in sent:
                if type(word) is nltk.tree.tree.Tree:
                    if(word[0][0] in genes and word[0][0] not in found_genes):
                        logging.info(f'found gene {word[0][0]}')
                        found_genes.append(word[0][0])
        logging.info("finished analisis")
        return found_genes