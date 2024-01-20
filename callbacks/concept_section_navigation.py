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
    buttons = [
        dbc.Button(
            concept_data[concept_id]['text'], 
            id = {'concept_button' : concept_id}
        )
        for concept_id in concepts
    ]
    buttons.append(
        dbc.Button('+', color = 'success', outline = True, id = {'mode_button' : category_type})
    )
    return buttons

def categories_section(category_type, content = None):
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

def properties_section(concept_data, nav_selection):
    concepts = concept_data[nav_selection]['Properties']
    buttons = [
        dbc.Button(
            concept_data[concept_id]['text'], 
            id = {'concept_button' : concept_id}
        )
        for concept_id in concepts
    ]
    buttons.append(dbc.Button('+', color = 'success', outline = True, id = {'mode_button' : 'Properties'}))
    return buttons

@callback(
    Output({'section_content' : ALL}, 'children'),
    Output({'category_content' : ALL}, 'children'),
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
    if trigger:
        if trigger in ('concept_data', 'nav_selection', 'last_category_type'):
            if selected_tab == ['Categories']:
                out_category_content = [categories_content(concept_data, nav_selection, category_type)]
            else:
                out_section_content = [properties_section(concept_data, nav_selection)]
        
        else:
            if selected_tab == ['Categories']:
                content = categories_content(concept_data, nav_selection, category_type)
                out_section_content = [categories_section(category_type, content = content)]
            else:
                out_section_content = [properties_section(concept_data, nav_selection)]
    else:
        raise PreventUpdate
    return out_section_content, out_category_content


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
                categories_section(category_type),
                id = {'section_content' : 'existence_dummy'})
        ])
    ]

def no_concept_selection(concept_data):
    concepts = [
        dbc.Button(concept_data[button_id]['text'], id = {'concept_button' : button_id})
        for button_id in concept_data['']
    ]
    if not concepts:
        concepts = dcc.Markdown('## Select some text to create a concept.')
    return concepts

@callback(
    Output('selected_concept_label', 'children'),
    Output('concept_details_section', 'children'),
    Input('nav_selection', 'data'),
    State('concept_data', 'data'),
    State('selected_concept_label', 'children'),
    State('last_category_type', 'data'),
    prevent_initial_call = True
)
def display_concept_details(selected_concept, concept_data, previous_selection, category_type):    
    out_concept_label = out_concept_details_section = no_update
    if selected_concept:
        out_concept_label = [f"## __{concept_data[selected_concept]['text']}__"]
        if previous_selection in (None, []):
            out_concept_details_section = html.Div(
                id = 'concept_section',
                children = concept_details_section(category_type)
            )
    elif previous_selection:
        out_concept_label = None
        out_concept_details_section = html.Div(
            id = {'no_selection' : 'existence_dummy'},
            children = no_concept_selection(concept_data)
        )
        
    return out_concept_label, out_concept_details_section