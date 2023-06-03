import logging
import PyPDF2
import tarfile
import os
from owlready2 import *
from article_searcher import ArticleSearcher
from article_getter import ArticleGetter
from article_analizer import ArticleAnalizer

age_options = [('allchild', 'Child (birth-18 years)'), ('newborn', 'Newborn (birth-1 month)'), ('allinfant', 'Infant (birth-23 months)'), ('infant', 'Infant: (1-23 months)'), 
               ('preschoolchild', 'Preschool Child (2-5 years)'), ('child', 'Child (6-12 years)'), ('adolescent', 'Adolescent (13-18 years)'), ('alladult', 'Adult (19+ years)'),
               ('youngadult', 'Young Adult (19-24 years)'), ('adult', 'Adult (19-44 years)'), ('middleagedaged', 'Middle Aged + Aged (45+ years)'), ('middleaged', 'Middle Aged (45-64 years)'), 
               ('aged', 'Aged (65+ years)'), ('80andover', '80 and over (80+ years)')]

def pdf_to_str(file):
    logging.info('turning pdf in str')
    pdfreader=PyPDF2.PdfReader(file)
    pageobj=pdfreader.pages
    pages=[page.extract_text() for page in pageobj]
    return ''.join(pages)

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

class OntologyCreator:

    def __init__(self, ontology_name, disorder, gender, ages, nationality, count, start_year, end_year) -> None:
        self.ontology_name = ontology_name
        self.disorder = disorder
        self.ages = ages
        self.gender = gender
        self.nationality = nationality
        self.count = count
        self.start_year = start_year
        self.end_year = end_year
        self.gene_descriptions, self.gene_names = get_genes()
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")

    
    
    def create_search_filters(self):
        disorder_search_term = self.disorder.replace(' ', '_')

        gender_filter = None
        if self.gender != 'not specified':
            gender_filter = ''.join([self.gender, '[Filter]'])

        age_filters = []
        for recieved_age in self.ages:
            for age in age_options:
                if recieved_age == age[1]:
                    age_filters.append(age[0]+'[Filter]')
        if len(age_filters) == 0:
            age_filter = None
        else:
            age_filter = '+OR+'.join(age_filters)
        year_filter = f'{self.start_year}:{self.end_year}[Publication Date]'
        return disorder_search_term, gender_filter, age_filter, year_filter
    
    def find_genes(self, article_analiser,file_name, format):
        found_genes = []

        #skip if no files was found for article
        if format is None:
            return found_genes
            
        #open pdf file, turn it into string and analise
        if format == 'pdf':
            logging.info('opening pdf file')
            try:
                with open(file_name,'rb') as pdf_file:
                    pdf_file = pdf_to_str(pdf_file)
                    genes = article_analiser.analise_article(pdf_file, self.gene_names)
                    found_genes.extend(genes)
            except:
                logging.warning(f'exception while reading pdf file {file_name}')
                os.remove(file_name)
                return found_genes

        #open tgz archive, find pdf file, turn it into string and analise
        if format == 'tgz':
            logging.info(f'start going through archive {file_name}')
            try:
                with tarfile.open(file_name) as tgz_file:
                    for member in tgz_file.getmembers():
                        if member.isfile() and member.path.endswith(".pdf"):
                            logging.info(f'found pdf file tgz archive {member.name}')
                            pdf_file = tgz_file.extractfile(member)
                            pdf_file = pdf_to_str(pdf_file)
                            genes = article_analiser.analise_article(pdf_file, self.gene_names)
                            found_genes.extend(genes)    
            except:
                logging.warning(f'exception while decomoressing data from file {file_name}')
                os.remove(file_name)
                return found_genes
            
        #remove file with article
        os.remove(file_name)
        logging.info(f'deleted file {file_name}')
        return found_genes

    def create_ontology(self):
        #create file for ontology
        with open(f"{self.ontology_name}.owl", 'w'):
            pass

        #open ontology
        onto = get_ontology(f"file://{self.ontology_name}.owl").load()
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

            class Journal(Thing):
                pass

            class Author(Thing):
                pass

            class has_disorder(Person >> MentalDisorder):
                pass

            class is_disorder_of(MentalDisorder >> Person):
                inverse_property = has_disorder

            class has_characteristic(Person >> Characteristic):
                pass

            class is_characteristic_of(Characteristic >> Person):
                inverse_property = has_characteristic

            class has_effect_on(Gene >> Person):
                pass

            class is_affected_by(Person >> Gene):
                inverse_property = has_effect_on

            class from_article(Person >> Article):
                pass

            class describes_person(Article >> Person):
                inverse_property = from_article

            class has_author(Article >> Author):
                pass

            class is_author_of(Author >> Article):
                inverse_property = has_author

            class published_in(Article >> Journal):
                pass

            class published(Journal >> Article):
                inverse_property = published_in

            class has_publication_date(Article >> str):
                pass

        #create search filters
        disorder_search_term, gender_filter, age_filter, year_filter = self.create_search_filters()

        #search aricles
        article_searcher = ArticleSearcher(disorder_search_term, self.count, age_filter, gender_filter, self.nationality, year_filter)
        articles = article_searcher.search_articles()

        if len(articles) == 0:
            logging.info('no articles found')
            return
        
        #add genes in ontology
        genes_onto = []
        for gene in self.gene_descriptions:
            new_gene = Gene(gene[0])
            new_gene.comment = gene[1]
            genes_onto.append(new_gene)

        #add disorder and search options in ontology
        disorder_onto = MentalDisorder(self.disorder)
        nationality_onto = None
        if self.nationality != '':
            nationality_onto = Nationality(self.nationality)
        gender_onto = None
        if self.gender != 'not specified':
            gender_onto = Gender(self.gender)
        ages_onto = []
        for age in self.ages:
            for age_option in age_options:
                if age == age_option[1]:                
                    age_onto = Age(age_option[0])   
                    age_onto.comment = age_option[1]
                ages_onto.append(age_onto)    
                
        article_getter = ArticleGetter()
        article_analiser = ArticleAnalizer()

        #start downloading and analising articles
        for article in articles:

            #article info
            article_id = article[0]
            article_authors = article[1]
            article_title = article[2]
            article_journal = article[3]
            article_date = article[4]

            #download article
            format, file_name = article_getter.get_article(article_id)

            found_genes = self.find_genes(article_analiser, file_name, format)

            #skip if no genes was found in file
            if len(found_genes) == 0:
                logging.info(f'didnt find any genes in file {file_name}')
                continue

            #add article, journal and authors in ontology
            article_onto = Article(article_id)
            article_onto.comment = article_title
            if article_date is not None:
                article_onto.has_publication_date.append(article_date)
            for author in article_authors:
                author_onto = Author(author)
                article_onto.has_author.append(author_onto)
            journal_onto = Journal(article_journal)
            article_onto.published_in.append(journal_onto)

            #add person and dependancies in ontology
            person = Person('person'+article[0])
            person.has_disorder.append(disorder_onto)
            if gender_onto is not None:
                person.has_characteristic.append(gender_onto)
            if nationality_onto is not None:
                person.has_characteristic.append(nationality_onto)
            for age in ages_onto:
                person.has_characteristic.append(age)
            person.from_article.append(article_onto)
            for gene in genes_onto:
                if gene.name in found_genes:
                    gene.has_effect_on.append(person)

        #save ontology
        onto.save()
        return

    def extend_ontology(self):
        #open ontology
        onto = get_ontology(f"file://{self.ontology_name}.owl").load()
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

            class Journal(Thing):
                pass

            class Author(Thing):
                pass

            class has_disorder(Person >> MentalDisorder):
                pass

            class is_disorder_of(MentalDisorder >> Person):
                inverse_property = has_disorder

            class has_characteristic(Person >> Characteristic):
                pass

            class is_characteristic_of(Characteristic >> Person):
                inverse_property = has_characteristic

            class has_effect_on(Gene >> Person):
                pass

            class is_affected_by(Person >> Gene):
                inverse_property = has_effect_on

            class from_article(Person >> Article):
                pass

            class describes_person(Article >> Person):
                inverse_property = from_article

            class has_author(Article >> Author):
                pass

            class is_author_of(Author >> Article):
                inverse_property = has_author

            class published_in(Article >> Journal):
                pass

            class published(Journal >> Article):
                inverse_property = published_in

            class has_publication_date(Article >> str):
                pass

        #create search filters
        disorder_search_term, gender_filter, age_filter, year_filter = self.create_search_filters()

        #search aricles
        article_searcher = ArticleSearcher(disorder_search_term, self.count, age_filter, gender_filter, self.nationality, year_filter)
        articles = article_searcher.search_articles()

        if len(articles) == 0:
            logging.info('no articles found')
            return
        
        genes_onto = onto.search(type = Gene)

        #add disorder and search options in ontology
        disorder_onto = MentalDisorder(self.disorder)
        nationality_onto = None
        if self.nationality != '':
            nationality_onto = Nationality(self.nationality)
        gender_onto = None
        if self.gender != 'not specified':
            gender_onto = Gender(self.gender)
        ages_onto = []
        for age in self.ages:
            for age_option in age_options:
                if age == age_option[1]:                
                    age_onto = Age(age_option[0])   
                    age_onto.comment = age_option[1]
                ages_onto.append(age_onto)    
                
        article_getter = ArticleGetter()
        article_analiser = ArticleAnalizer()

        #start downloading and analising articles
        for article in articles:

            #article info
            article_id = article[0]
            article_authors = article[1]
            article_title = article[2]
            article_journal = article[3]
            article_date = article[4]

            #download article
            format, file_name = article_getter.get_article(article_id)

            found_genes = self.find_genes(article_analiser, file_name, format)

            #skip if no genes was found in file
            if len(found_genes) == 0:
                logging.info(f'didnt find any genes in file {file_name}')
                continue

            #add article, journal and authors in ontology
            article_onto = Article(article_id)
            article_onto.comment = article_title
            if article_date is not None:
                article_onto.has_publication_date.append(article_date)
            for author in article_authors:
                author_onto = Author(author)
                article_onto.has_author.append(author_onto)
            journal_onto = Journal(article_journal)
            article_onto.published_in.append(journal_onto)

            #add person and dependancies in ontology
            person = Person('person'+article[0])
            person.has_disorder.append(disorder_onto)
            if gender_onto is not None:
                person.has_characteristic.append(gender_onto)
            if nationality_onto is not None:
                person.has_characteristic.append(nationality_onto)
            for age in ages_onto:
                person.has_characteristic.append(age)
            person.from_article.append(article_onto)
            for gene in genes_onto:
                if gene.name in found_genes:
                    gene.has_effect_on.append(person)

        #save ontology
        onto.save()
        return