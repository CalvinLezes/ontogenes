import logging
from owlready2 import *

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

class OntologyCreator:
    def __init__(self, disorder, ages, nationality, gender) -> None:
        self.disorder = MentalDisorder(disorder)
        self.ages = [Age(age) for age in ages]
        self.nationality = Nationality(nationality)
        self.gender = Gender(gender)
        logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")

    def update_ontology(self, article_info, genes):
        person = Person('Person from' + article_info[0])
        article = Article(article_info[0])
        article.comment = article_info[2]
        authors = [Author(author) for author in article_info[1]]
        for author in authors:
            article.has_author.append(author)
        for age in self.ages:
            person.has_age.append(age)
        person.has_gender.append(self.gender)
        person.has_nationality.append(self.nationality)
        person.has_disorder.append(self.disorder)
        person.has_source.append(article)
        for gene in genes:
            gen = Gene(gene)
            gen.has_effect_on.append(person)
        

