import logging
import requests
import xml.etree.ElementTree as ET

class ArticleSearcher:

    def __init__(self, disorder, number_of_articles, age_filter, gender_filter, nationality, year_filter) -> None:
        self.disorder = disorder
        self.number_of_articles = number_of_articles
        self.age_filter = age_filter
        self.gender_filter = gender_filter
        self.nationality = nationality
        self.year_filter = year_filter
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")

    def make_request(self, link):
        response = requests.get(link)
        if response.status_code == 200:
            logging.info(f"Made request to {link}")
        else: 
            logging.warning(f"Failed to make request to {link}")
        return ET.fromstring(response.text)

    def make_search_link(self):
        base_link = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&usehistory=y"
        if self.nationality is not None:
            search_term = f"term={self.disorder}+AND+Genetics+AND+{self.nationality}+ffrft[Filter]+humans[Filter]"
        else:
            search_term = f"term={self.disorder}+AND+Genetics+ffrft[Filter]+humans[Filter]"
        if self.age_filter is not None:
            search_term = '+'.join([search_term, self.age_filter])
        if self.gender_filter is not None:
            search_term = '+'.join([search_term, self.gender_filter])
        search_term = '+'.join([search_term, self.year_filter])
        search_link = '&'.join([base_link, search_term])
        return search_link

    def make_fetch_link(self, webenv, querykey, retstart, retmax):
        base_link = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
        search_options = f"db=pubmed&query_key={querykey}&WebEnv={webenv}&retstart={retstart}&retmax={retmax}&retmode=xml"
        search_link = "".join([base_link, search_options])
        return search_link
    
    def get_article_info(self, response, articles):
        for article in response.findall('PubmedArticle'):
            pmc_id = None
            authors = []
            title = None
            for article_id in article.findall('PubmedData/ArticleIdList/ArticleId'):
                id_type = article_id.attrib['IdType']
                if id_type == "pmc":
                    pmc_id = article_id.text
            if pmc_id is None:
                logging.info(f"article with id {article.find('MedlineCitation/PMID').text} doesnt have a full text in pmc")
                continue
            else:
                for author in article.findall('MedlineCitation/Article/AuthorList/Author'):
                    forename = author.find('ForeName')
                    lastname = author.find('LastName')
                    if forename is not None:
                        name = '_'.join([forename.text.replace(' ', '_'), lastname.text.replace(' ', '_')])
                        authors.append(name)
                title = article.find('MedlineCitation/Article/ArticleTitle').text
                journal_title = article.find('MedlineCitation/Article/Journal/Title').text.replace(' ', '_')
                ArticleDate = article.find('MedlineCitation/DateCompleted')
                if ArticleDate is None:
                    date = None
                else:
                    year = ArticleDate.find('Year').text
                    month = ArticleDate.find('Month').text
                    day = ArticleDate.find('Day').text
                    date = '.'.join([year, month, day])
                articles.append((pmc_id, authors, title, journal_title, date))
        return articles
    
    def search_articles(self):
        search_link = self.make_search_link() 
        response = self.make_request(search_link) #make search request
        count = response.find("Count").text
        articles_count = int(count) #total number of articles found
        webenv = response.find("WebEnv").text
        querykey = response.find("QueryKey").text #parameters for fetch search

        articles = []



        logging.info(f"Total number of articles found is {articles_count}")
        if articles_count == 0: #if didn't find any articles return empty array
            return articles

        retstart = 0 #start index of articles

        if self.number_of_articles is not None:
            number_of_articles = min(articles_count, self.number_of_articles) #number of articles to fetch
        
        retmax = min(500, number_of_articles) #max number of articles returned in one request
        
        for retstart in range(0, number_of_articles, retmax):
            if(number_of_articles-retstart < retmax):
                retmax = number_of_articles-retstart
            fetch_link = self.make_fetch_link(webenv, querykey, retstart, retmax)
            response = self.make_request(fetch_link)
            articles = self.get_article_info(response, articles)
        return articles, articles_count   