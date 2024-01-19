from dash import callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pprint import pprint

from dash.exceptions import PreventUpdate

def labels_section(concept_data, nav_selection):
    buttons = concept_data[nav_selection]['Labels']
    return [
        dbc.Button(
            concept_data[button_id]['text'], 
            id = {'potential_concept' : button_id, 'section' : 'Labels'}
        )
        for button_id in buttons
    ]

def categories_section(category_type):
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Belongs To', tab_id = 'Supersets'),
                dbc.Tab(label = 'Contains', tab_id = 'Subsets'),
            ], id = {'category_tabs' : 'existence_dummy'}, active_tab = category_type)
        ),
        dbc.CardBody([], id = {'category_content' : 'existence_dummy'}
        )
    ])

    
def properties_section(concept_data, nav_selection):
    buttons = concept_data[nav_selection]['Properties']
    return [
        dbc.Button(
            concept_data[button_id]['text'], 
            id = {'potential_concept' : button_id, 'section' : 'Properties'}
        )
        for button_id in buttons
    ]

@callback(
    Output('section_content', 'children'),
    Input('concept_data', 'data'),
    Input('nav_selection', 'data'),
    Input('section_tabs', 'active_tab'),
    State('last_category_type', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def update_section(concept_data, selected_concept, selected_tab, category_type, nav_selection):
    if ctx.triggered_id:

        if selected_tab == 'Labels':
            out_content = labels_section(concept_data, nav_selection)
        elif selected_tab == 'Categories':
            out_content = categories_section(category_type)
        elif selected_tab == 'Properties':
            out_content = properties_section(concept_data, nav_selection)
    else:
        raise PreventUpdate
    return out_content

@callback(
    Output({'category_content' : ALL}, 'children'),
    Output('last_category_type', 'data'),
    Input({'category_tabs' : ALL}, 'active_tab'),
    State('concept_data', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def update_category_section(category_tabs, concept_data, nav_selection):

    out_content = out_category_type = no_update
    if ctx.triggered_id:
    
        buttons = dict()
        if category_tabs and category_tabs[0]:
            out_category_type = category_tabs[0]
            buttons = concept_data[nav_selection][out_category_type.lower()]
            out_content = [[
                dbc.Button(
                    concept_data[button_id]['text'], 
                    id = {'potential_concept' : button_id, 'section' : out_category_type}
                )
                for button_id in buttons
            ]]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate
    return out_content, out_category_type