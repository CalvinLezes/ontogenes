from owlready2 import *

# onto = get_ontology("http://test.org/onto.owl")
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

    class is_author_of(Author>>Article):
        inverse_property = has_author

def find_individual(type, name):
    individuals = onto.search(type = type)
    for individual in individuals:
        if individual.name == name:
            return individual
    return None

depression = 'anxiety'

disorders = onto.search(type = MentalDisorder)

for disorder in disorders:
    if disorder.name == depression:
        print(disorder.name)

#individual = add_individual(MentalDisorder, 'depression')

article = Article('PMC37682')

author = Author('Danila Ermilov')

article.has_author.append(author)

#print(author.is_author_of)
#print(individual.name)

string = 'asperger syndrome'

string.replace(' ', '+')

print(string)
