from dash import callback, Output, Input, State, dcc, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pprint import pprint, pformat
from dash.exceptions import PreventUpdate
import random

'''
@callback(
    Output('quiz', 'children'),
    Input('concept_network', 'elements'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def update_quiz(concept_network, concept_data):
    questions = []
    # for element in concept_network:
    #     if 'source' in element:
    #         parent = element['source']
    #         child = element['target']

    has_superset = []
    has_subset = []
    related_concepts = []
    for concept in concept_data.values():
        if concept['supersets']:
            has_superset.append(concept['id'])
        if concept['subsets']:
            has_subset.append(concept['id'])
    for n, concept_id_1 in enumerate(has_superset):
        supersets_1 = set(concept_data[concept_id_1]['supersets'])
        for concept_id_2 in has_superset[n+1:]:
            if concept_id_2 not in supersets_1:
                supersets_2 = set(concept_data[concept_id_2]['supersets'])
                if concept_id_1 not in supersets_2:
                    concept_1 = concept_data[concept_id_1]
                    concept_2 = concept_data[concept_id_2]
                    c1_labels = [concept_data[l]['text'] for l in concept_1['Labels']] + [concept_1['text']]
                    c2_labels = [concept_data[l]['text'] for l in concept_2['Labels']] + [concept_2['text']]
                    # shared_supersets = list(supersets_1.union(supersets_2))
                    shared_supersets = supersets_1.intersection(supersets_2)
                    if shared_supersets:
                        
                        superset_supersets = set()
                        for superset_id in shared_supersets:
                            superset_supersets |= set(concept_data[superset_id]['supersets'])
                        closest_relatives = shared_supersets - superset_supersets
                        
                        for relative_id in closest_relatives:
                            relative_labels = concept_data[relative_id]['Labels']
                            relative_labels.append(concept_data[relative_id]['text'])
                            for l1 in c1_labels:
                                for l2 in c2_labels:
                                    for r in relative_labels:
                                        questions.append(
                                            dcc.Markdown(f'(T)/F: {l1} and {l2} are both types of {r}')
                                        )
                    else:
                        closest_relatives = set()
                        
                    unique_1_supersets = supersets_1 - supersets_2
                    for non_relative_id in unique_1_supersets:
                        non_relative_labels = concept_data[non_relative_id]['Labels']
                        non_relative_labels.append(concept_data[non_relative_id]['text'])
                        for l1 in c1_labels:
                            for l2 in c2_labels:
                                for nr in non_relative_labels:
                                    questions.append(
                                        dcc.Markdown(f'T/(F): {l1} and {l2} are both types of {nr}')
                                    )
                    unique_1_supersets = [concept_data[concept_id]['text'] for concept_id in unique_1_supersets]


                    unique_2_supersets = supersets_2 - supersets_1
                    for non_relative_id in unique_2_supersets:
                        non_relative_labels = concept_data[non_relative_id]['Labels']
                        non_relative_labels.append(concept_data[non_relative_id]['text'])
                        for l1 in c1_labels:
                            for l2 in c2_labels:
                                for r in non_relative_labels:
                                    questions.append(
                                        dcc.Markdown(f'T/(F): {l1} and {l2} are both types of {r}')
                                    )
                    unique_2_supersets = [concept_data[concept_id]['text'] for concept_id in unique_2_supersets]


                    # relation = [
                    #     concept_data[concept_id_1]['text'],
                    #     concept_data[concept_id_2]['text']
                    # ] + [
                    #     concept_data[relative_id]['text'] for relative_id in closest_relatives
                    # ] + [unique_1_supersets, unique_2_supersets]
                    # related_concepts.append(relation)
                    

                            


    # questions.extend([html.Br(),str(related_concepts)])# pformat(concept_data, indent = 4)])
    return questions
'''