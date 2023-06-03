import streamlit as st
from owlready2 import *
import os
import PyPDF2
import tarfile
import logging
import zlib
from article_searcher import ArticleSearcher
from article_getter import ArticleGetter
from article_analizer import ArticleAnalizer

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")

if not os.path.exists("ontology.owl"):
    with open("ontology.owl", 'w') as fp:
        pass

onto = get_ontology("file://ontology.owl").load()

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

    class has_nationality(Person >> Nationality):
        pass

    class is_nationality_of(Nationality >> Person):
        inverse_property = has_nationality

    class has_age(Person >> Age):
        pass

    class is_age_of(Age >> Person):
        inverse_property = has_age

    class has_gender(Person >> Gender):
        pass

    class is_gender_of(Gender >> Person):
        inverse_property = has_gender

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

ages = [('allchild', 'Child (birth-18 years)'), ('newborn', 'Newborn (birth-1 month)'), ('allinfant', 'Infant (birth-23 months)'), ('infant', 'Infant: (1-23 months)'), 
               ('preschoolchild', 'Preschool Child (2-5 years)'), ('child', 'Child (6-12 years)'), ('adolescent', 'Adolescent (13-18 years)'), ('alladult', 'Adult (19+ years)'),
               ('youngadult', 'Young Adult (19-24 years)'), ('adult', 'Adult (19-44 years)'), ('middleagedaged', 'Middle Aged + Aged (45+ years)'), ('middleaged', 'Middle Aged (45-64 years)'), 
               ('aged', 'Aged (65+ years)'), ('80andover', '80 and over (80+ years)')]

age_options = ['Child (birth-18 years)','Newborn (birth-1 month)', 'Infant (birth-23 months)', 'Infant: (1-23 months)', 
                                     'Preschool Child (2-5 years)', 'Child (6-12 years)', 'Adolescent (13-18 years)', 'Adult (19+ years)',
                                     'Young Adult (19-24 years)', 'Adult (19-44 years)', 'Middle Aged + Aged (45+ years)', 
                                     'Middle Aged (45-64 years)', 'Aged (65+ years)', '80 and over (80+ years)']

def find_individual(type, name):
    individuals = onto.search(type = type)
    for individual in individuals:
        if individual.name == name:
            return individual
    return None

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

def extract_tgz(file_name):
    with tarfile.open(file_name) as tgz_file:
        for member in tgz_file.getmembers():
            if member.isfile() and member.path.endswith(".pdf"):
                return tgz_file.extractfile(member)

def create_age_filter(recieved_ages):
    age_filters = []
    for recieved_age in recieved_ages:
        for age in ages:
           if recieved_age == age[1]:
               age_filters.append(age[0]+'[Filter]')
    if len(age_filters) != 0:
        return '+OR+'.join(age_filters)
    return None

def create_gender_filter(gender):
    gender_filter = None
    if gender != 'not specified':
        gender_filter = ''.join([gender, '[Filter]'])
    return gender_filter

def find_age_ontos(received_ages):
    ages_onto = []
    for recieved_age in received_ages:
        for age in ages:
            if recieved_age == age[1]:
                age_onto = None
                age_onto = find_individual(Age, age[0])
                if age_onto is None:
                    age_onto = Age(age[0])   
                    age_onto.comment = age[1]
                ages_onto.append(age_onto)    
    return ages_onto

st.title('Welcome')

txt = st.text('''
    This is an application for searching for genetic markers of mental disorders.
    Put the name of mental disorder, choose gender, age, nationality.
    Press 'Start the analysis'.   
    ''')

disorder = st.text_input('Put name of mental disorder', '', placeholder='put name of disorder here')

gender = st.radio('Choose a gender', ['not specified', 'male', 'female'])

received_ages = st.multiselect('Choose an age', age_options)

nationality = st.text_input('Put a nationality here', '')

count = st.number_input('Choose a number of articles to analise', 1, value= 10)

years = st.selectbox('Choose years', ['2019:2023', '2020:2023', '2021:2023', '2022:2023', '2023:2023'])

gene_descriptions, gene_names = get_genes()

genes_onto = []

for gene in gene_descriptions:
    new_gene = Gene(gene[0])
    new_gene.comment = gene[1]
    genes_onto.append(new_gene)


def start_anilise():
    if disorder == '':
        st.write('You must put the name of disorder')
        return
    disorder_search_term = disorder.replace(' ', '_')
    gender_filter = create_gender_filter(gender)
    age_filter = create_age_filter(received_ages)
    year_filter = f'{years}[Publication Date]'
    article_searcher = ArticleSearcher(disorder_search_term, count, age_filter, gender_filter, nationality, year_filter)
    articles = article_searcher.search_articles()

    if len(articles) == 0:
        st.write('No articles found with these parametrs. (Advice: check for typos)')
        return
    
    st.write(f"Found {len(articles)} articles")

    disorder_onto = find_individual(MentalDisorder, disorder)
    if disorder_onto is None:
        disorder_onto = MentalDisorder(disorder)
    nationality_onto = None
    if nationality != '':
        nationality_onto = find_individual(Nationality, nationality)
        if nationality_onto is None:
            nationality_onto = Nationality(nationality)
    gender_onto = None
    if gender != 'not specified':
        gender_onto = find_individual(Gender, gender)
        if gender_onto is None:
            gender_onto = Gender(gender)
    ages_onto = find_age_ontos(received_ages)

    article_getter = ArticleGetter()
    article_analiser = ArticleAnalizer()
    for article in articles:
        format, file_name = article_getter.get_article(article[0])
        found_genes = []
        if format == 'pdf':
            logging.info('opening pdf file')
            with open(file_name,'rb') as pdf_file:
                pdf_file = pdf_to_str(pdf_file)
                genes = article_analiser.analise_article(pdf_file, gene_names)
                found_genes.extend(genes)
        if format == 'tgz':
            logging.info(f'start going through archive {file_name}')
            try:
                with tarfile.open(file_name) as tgz_file:
                    for member in tgz_file.getmembers():
                        if member.isfile() and member.path.endswith(".pdf"):
                            logging.info(f'found pdf file tgz archive {member.name}')
                            pdf_file = tgz_file.extractfile(member)
                            pdf_file = pdf_to_str(pdf_file)
                            genes = article_analiser.analise_article(pdf_file, gene_names)
                            found_genes.extend(genes)    
            except zlib.error:
                logging.warn(f'exception while decomoressing data from file {file_name}')
                os.remove(file_name)
                continue  
        if format is None:
            continue  
        os.remove(file_name)
        logging.info(f'deleted file {file_name}')
        if len(found_genes) == 0:
            logging.info(f'didnt find any genes in file {file_name}')
            continue

        article_onto = find_individual(Article, article[0])
        if article_onto is None:
            article_onto = Article(article[0])
            article_onto.comment = article[2]
            if article[4] is not None:
                article_onto.has_publication_date.append(article[4])
            for author in article[1]:
                author_onto = Author(author)
                article_onto.has_author.append(author_onto)
        journal_onto = find_individual(Journal, article[3])
        if journal_onto is None:
            journal_onto = Journal(article[3])
        article_onto.published_in.append(journal_onto)
        person = find_individual(Person, 'person'+article[0])
        if person is None:
            person = Person('person'+article[0])
        person.has_disorder.append(disorder_onto)
        if gender_onto is not None:
            person.has_gender.append(gender_onto)
        if nationality_onto is not None:
            person.has_nationality.append(nationality_onto)
        for age in ages_onto:
            person.has_age.append(age)
        person.from_article.append(article_onto)
        for gene in genes_onto:
            if gene.name in found_genes:
                gene.has_effect_on.append(person)
    onto.save()
    st.write('Finished the analysis, check your ontology.owl file')

result = st.button('Start the analysis')

if result:
    start_anilise()
    with open('ontology.owl') as file:
        btn = st.download_button(
            label="Download ontology",
            data=file,
            file_name="ontology.owl",
          )