from dash import callback, Output, Input, State, ctx, ALL, html, dcc, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pprint import pprint

from dash.exceptions import PreventUpdate

def labels_section(concept_data, nav_selection):
    labels = concept_data[nav_selection]['Labels']
    return ','.join(labels)


def categories_content(concept_data, nav_selection, category_type):
    concepts = concept_data[nav_selection][category_type.lower()]
    buttons = [dbc.Button('+', color = 'success', outline = True, id = {'add_button' : category_type})]
        
    buttons.extend([
        dbc.Button(
            concept_data[concept_id]['text'], 
            id = {'concept_button' : concept_id}
        )
        for concept_id in concepts
    ])

    return buttons

def add_categories_section(category_type, content = None):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Belongs To', tab_id = 'Supersets'),
                dbc.Tab(label = 'Contains', tab_id = 'Subsets'),
            ], id = {'category_tabs' : 'existence_dummy'}, active_tab = category_type)
        ),
        dbc.CardBody(content, id = {'category_content' : 'existence_dummy'}
        )
    ])


def add_properties_section(concept_data, nav_selection):
    concept = concept_data[nav_selection]
    properties = concept['Properties']
    buttons = [dbc.Button('+', color = 'success', outline = True, id = {'mode_button' : 'Properties'})]
        
    buttons.extend([
        dbc.Button(
            concept_data[property_id]['text'], 
            id = {'property_button' : property_id}
        )
        for property_id in properties
    ])
    for superset_id in concept['supersets']:
        superset = concept_data[superset_id]
        if superset['Properties']:
            buttons.append(dcc.Markdown(superset['text']))
            buttons.extend([
                dbc.Button(
                    concept_data[superset_property_id]['text'], 
                    id = {'superset_property_button' : superset_property_id}
                )
                for superset_property_id in superset['Properties']
            ])
    return buttons

@callback(
    Output('last_category_type', 'data'),
    Input({'category_tabs' : ALL}, 'active_tab'),
    prevent_initial_call = True
)
def update_category_tab(category_tabs):
    out_category_type = no_update
    
    if category_tabs and category_tabs[0]:
        out_category_type = category_tabs[0]

    return out_category_type

def concept_details_section(category_type):
    return [
        dbc.Card([
            dbc.CardHeader(
                dbc.Tabs([
                    dbc.Tab(label = 'Categories', tab_id = 'Categories'),
                    dbc.Tab(label = 'Properties', tab_id = 'Properties'),
                ], id = {'section_tabs' : 'existence_dummy'})
            ),
            dbc.CardBody(
                add_categories_section(category_type),
                id = {'section_content' : 'existence_dummy'})
        ])
    ]

def select_something_section(concept_data):
    concepts = [
        dbc.Button(concept_data[button_id]['text'], id = {'concept_button' : button_id})
        for button_id in concept_data['']
    ]
    select_concept = dcc.Markdown('## Select a concept to edit it.')
    if concepts:
        concepts.insert(0, select_concept)
    else:
        concepts = [dcc.Markdown('## Select some text to create a concept.'), select_concept]
    return concepts


@callback(
    Output({'section_content' : ALL}, 'children'),
    Output({'category_content' : ALL}, 'children'),
    Output('concept_details_section', 'children'),
    Output('selected_concept_label', 'children'),
    Input('concept_data', 'data'),
    Input({'section_tabs' : ALL}, 'active_tab'),
    Input('nav_selection', 'data'),
    Input('last_category_type', 'data'),
    prevent_initial_call = True
)
def update_section(concept_data, selected_tab, nav_selection, category_type):
    trigger = ctx.triggered_id
    outputs_list = ctx.outputs_list
    out_section_content = [no_update for o in outputs_list[0]]
    out_category_content = [no_update for o in outputs_list[1]]
    out_concept_label = out_concept_details = no_update

    if trigger:
        if nav_selection:
            out_concept_label = [f"## __{concept_data[nav_selection]['text']}__"]
            if trigger in ('concept_data', 'nav_selection', 'last_category_type'):
                if selected_tab == ['Categories']:
                    out_category_content = [categories_content(concept_data, nav_selection, category_type)]
                elif selected_tab == ['Properties']:
                    out_section_content = [add_properties_section(concept_data, nav_selection)]
                elif not outputs_list[0]:
                    out_concept_details = concept_details_section(category_type)

            else:
                if selected_tab == ['Categories']:
                    content = categories_content(concept_data, nav_selection, category_type)
                    out_section_content = [add_categories_section(category_type, content = content)]
                else:
                    out_section_content = [add_properties_section(concept_data, nav_selection)]
        else:
            out_concept_label = None
            out_concept_details = select_something_section(concept_data)
    else:
        raise PreventUpdate
    return out_section_content, out_category_content, out_concept_details, out_concept_label