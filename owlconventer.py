from owlready2 import *
import csv


def convert_owl_to_csv(ontology_name):
    onto = get_ontology(f"file://{ontology_name}.owl").load()

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
    individuals = onto.search(type = Article)
    article_id = None
    article_title = None
    disorder = None
    journal = None
    date = None
    authors = []
    genes =[]
    parametrs = []
    id = 1
    with open(f"{ontology_name}.csv", mode="w", encoding='utf-8') as w_file:
        file_writer = csv.writer(w_file, delimiter = ";")
        for individual in individuals:
            article_id = individual.name
            if individual.comment is not None:
                article_title = individual.comment
            for prop in individual.get_properties():
                for value in prop[individual]:
                    if prop.python_name == 'published_in':
                        journal = onto.search_one(is_a = value).name
                    if prop.python_name == 'has_publication_date':
                        date = individual.has_publication_date[0]
                    if prop.python_name == 'has_author':
                        authors.append(onto.search_one(is_a = value).name) 
                    if prop.python_name == 'describes_person':
                        person = onto.search_one(is_a = value)
                        for person_prop in person.get_properties():
                            for value in person_prop[person]:
                                if person_prop.python_name == 'has_characteristic':
                                    name = onto.search_one(is_a = value).name
                                    if name not in parametrs:
                                        parametrs.append(name) 
                                if person_prop.python_name == 'has_disorder':
                                    disorder = onto.search_one(is_a = value).name 
                                if person_prop.python_name == 'is_affected_by':
                                    gene = onto.search_one(is_a = value)
                                    gene_name = gene.name
                                    gene_description = gene.comment[0]
                                    genes.append((gene_name, gene_description))
            for gene in genes:
                file_writer.writerow([id, article_id, article_title, gene[0], gene[1], disorder, ', '.join(parametrs), journal, date, ', '.join(authors)])
                id = id+1
            article_id = None
            article_title = None
            journal = None
            disorder = None
            date = None
            authors = []
            genes =[]
            parametrs = []

                    