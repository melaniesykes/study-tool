from dash import callback, Output, Input, State, dcc, html, ALL
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pprint import pprint, pformat
from dash.exceptions import PreventUpdate
import random

# {
#     'text' : concept_name,
#     'Labels' : [],
#     'is_property' : selected_section == 'Properties',
#     'supersets' : dict(),
#     'subsets' : dict(),
#     'Properties' : [],
#     'parent' : parent, # parent concept, not necessarily same as parent node
#     'source_property' : source
# }

@callback(
    Output('quiz', 'children'),
    Input('concept_network', 'elements'),
    Input({'selected_concept_labels_list' : ALL}, 'children'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def update_quiz(concept_network, label_added, concept_data):
    questions = []

    has_superset = []
    has_subset = []
    for concept_id, concept in concept_data.items():
        if concept_id in ('', 'pins'):
            continue
        if concept['supersets']:
            has_superset.append(concept_id)
        if concept['subsets']:
            has_subset.append(concept_id)
    for n, concept_id_1 in enumerate(has_superset):
        supersets_1 = set(concept_data[concept_id_1]['supersets'].keys())
        for concept_id_2 in has_superset[n+1:]:
            if concept_id_2 not in supersets_1:
                supersets_2 = set(concept_data[concept_id_2]['supersets'].keys())
                if concept_id_1 not in supersets_2:
                    concept_1 = concept_data[concept_id_1]
                    concept_2 = concept_data[concept_id_2]
                    c1_labels = concept_1['Labels'] + [concept_1['text']]
                    c2_labels = concept_2['Labels'] + [concept_2['text']]
                    shared_supersets = supersets_1.intersection(supersets_2)
                    if shared_supersets:
                        
                        superset_supersets = set()
                        for superset_id in shared_supersets:
                            superset_supersets |= set(concept_data[superset_id]['supersets'].keys())
                        closest_relatives = shared_supersets - superset_supersets
                        
                        for relative_id in closest_relatives:
                            relative_labels = concept_data[relative_id]['Labels'] + [concept_data[relative_id]['text']]
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
                        non_relative_labels = concept_data[non_relative_id]['Labels'] + [concept_data[non_relative_id]['text']]
                        for l1 in c1_labels:
                            for l2 in c2_labels:
                                for nr in non_relative_labels:
                                    questions.append(
                                        dcc.Markdown(f'T/(F): {l1} and {l2} are both types of {nr}')
                                    )
                    unique_1_supersets = [concept_data[concept_id]['text'] for concept_id in unique_1_supersets]


                    unique_2_supersets = supersets_2 - supersets_1
                    for non_relative_id in unique_2_supersets:
                        non_relative_labels = concept_data[non_relative_id]['Labels'] + [concept_data[non_relative_id]['text']]
                        for l1 in c1_labels:
                            for l2 in c2_labels:
                                for r in non_relative_labels:
                                    questions.append(
                                        dcc.Markdown(f'T/(F): {l1} and {l2} are both types of {r}')
                                    )
                    unique_2_supersets = [concept_data[concept_id]['text'] for concept_id in unique_2_supersets]

    return questions
