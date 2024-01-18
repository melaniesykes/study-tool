from dash import callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from pprint import pprint

from dash.exceptions import PreventUpdate

def labels_section(concept_data, nav_selection):
    buttons = concept_data[nav_selection]['Labels']
    return [
        dbc.Button(
            concept_data.get(button_id, dict()).get('text', button_text), 
            id = {'potential_concept' : button_id, 'section' : 'Labels'}
        )
        for button_id, button_text in buttons.items()
    ]

def categories_card_content(buttons, section):
    return [
        dbc.Button(button_text, id = {'potential_concept' : button_id, 'section' : section})
        for button_id, button_text in buttons.items()
    ]

def categories_section(category_type):
    buttons = dict()
    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Belongs To', tab_id = 'Supersets'),
                dbc.Tab(label = 'Contains', tab_id = 'Subsets'),
            ], id = {'category_tabs' : 'existence_dummy'}, active_tab = category_type)
        ),
        dbc.CardBody(categories_card_content(buttons, category_type), id = {'category_content' : 'existence_dummy'})
    ])

    
def properties_section(concept_data, nav_selection):
    buttons = concept_data[nav_selection]['Properties']
    return [
        dbc.Button(
            concept_data.get(button_id, dict()).get('text', button_text), 
            id = {'potential_concept' : button_id, 'section' : 'Properties'}
        )
        for button_id, button_text in buttons.items()
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
        if 'concept_data.data' in ctx.triggered_prop_ids:
            print()
            pprint(concept_data)

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
            buttons = concept_data[nav_selection][out_category_type]
            out_content = [categories_card_content(buttons, out_category_type)]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate
    return out_content, out_category_type