import streamlit as st
import os
import pip
from ontology_creator import OntologyCreator
from owlconventer import convert_owl_to_csv

age_options = ['Child (birth-18 years)','Newborn (birth-1 month)', 'Infant (birth-23 months)', 'Infant: (1-23 months)', 
                                     'Preschool Child (2-5 years)', 'Child (6-12 years)', 'Adolescent (13-18 years)', 'Adult (19+ years)',
                                     'Young Adult (19-24 years)', 'Adult (19-44 years)', 'Middle Aged + Aged (45+ years)', 
                                     'Middle Aged (45-64 years)', 'Aged (65+ years)', '80 and over (80+ years)']

st.title('Welcome')

txt = st.text('''
    This is an application for searching for genetic markers of mental disorders.
    You can create a new ontology or expand already existing one.
    You can download result in .owl or .csv formats.
    Fill in or choose search parametrs and press start.
    ''')

disorder = st.text_input('Put name of mental disorder', '', placeholder='put name of disorder here')

gender = st.radio('Choose a gender', ['not specified', 'male', 'female'])

received_ages = st.multiselect('Choose an age', age_options)

nationality = st.text_input('Put a nationality here', '')

count = st.number_input('Choose a number of articles to analise', 1, value = 10)

start_year = st.selectbox('Choose start year', range(1923,2024), 95)
end_year = st.selectbox('Choose end year', range(1923,2024), 100)

page = st.radio('Create new or expand existing ontology?', ['Create', 'Extend'])


ontology_name = st.text_input('Choose a name for ontology', '')
start_button = st.button('Start')
if page == 'Create':
    if start_button:
        if ontology_name == '':
            st.write('Ontology name cant be empty')
        elif os.path.exists(f'{ontology_name}.owl'):
            st.write('Ontology with this name already exists')
        elif start_year > end_year:
            st.write('Start year must be less then end year')
        elif disorder == '':
            st.write('You must put the name of disorder')
        else:
            st.write('Started creating ontology, please wait')
            ontology_creator = OntologyCreator(ontology_name, disorder, gender, received_ages, nationality, count, start_year, end_year)
            ontology_creator.create_ontology()
            with open(f'{ontology_name}.owl') as file:
                btn = st.download_button(
                label="Download .owl",
                data=file,
                file_name=f'{ontology_name}.owl',
            )
            convert_owl_to_csv(ontology_name)
            with open(f'{ontology_name}.csv') as csv_file:
                csv_btn = st.download_button(
                label='Download .csv',
                data = csv_file,
                file_name=f'{ontology_name}.csv',
            )

if page == 'Extend':
    if start_button:
        
        if ontology_name == '':
            st.write('Ontology name cant be empty')
        elif not os.path.exists(f'{ontology_name}.owl'):
            st.write('Ontology with this name doesnt exist')
        elif start_year > end_year:
            st.write('Start year must be less then end year')
        elif disorder == '':
            st.write('You must put the name of disorder')
        else:
            st.write('Started creating ontology, please wait')
            ontology_creator = OntologyCreator(ontology_name, disorder, gender, received_ages, nationality, count, start_year, end_year)
            ontology_creator.extend_ontology()
            with open(f'{ontology_name}.owl') as file:
                btn = st.download_button(
                label="Download .owl",
                data=file,
                file_name=f'{ontology_name}.owl',
            )
            convert_owl_to_csv(ontology_name)
            with open(f'{ontology_name}.csv') as csv_file:
                csv_btn = st.download_button(
                label='Download .csv',
                data = csv_file,
                file_name=f'{ontology_name}.csv',
            )

if start_year > end_year:
    st.write('Start year must be less then end year')
if disorder == '':
    st.write('You must put the name of disorder')