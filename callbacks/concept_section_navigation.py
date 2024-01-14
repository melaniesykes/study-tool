from dash import callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from dash.exceptions import PreventUpdate

def labels_section(concept_data, nav_selection):
    path = '-'.join(nav_selection)
    buttons = concept_data[path]['Labels']
    return [
        dbc.Button(button_text, id = {'potential_concept' : button_id})
        for button_id, button_text in buttons.items()
    ]

def categories_card_content(buttons):
    return [
        dbc.Button(button_text, id = {'potential_concept' : button_id})
        for button_id, button_text in buttons.items()
    ]

def categories_section(concept_data, nav_selection, category_tabs):
    path = '-'.join(nav_selection)
    
    buttons = dict()
    if category_tabs and category_tabs[0]:
        buttons = concept_data[path][category_tabs[0]]

    return dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Belongs To', tab_id = 'Supersets'),
                dbc.Tab(label = 'Contains', tab_id = 'Subsets'),
            ], id = {'category_tabs' : 'existence_dummy'})
        ),
        dbc.CardBody(categories_card_content(buttons), id = {'category_content' : 'existence_dummy'})
    ])

    
def properties_section(concept_data, nav_selection):
    path = '-'.join(nav_selection)
    buttons = concept_data[path]['Properties']
    return [
        dbc.Button(button_text, id = {'potential_concept' : button_id})
        for button_id, button_text in buttons.items()
    ]

@callback(
    Output('section_content', 'children'),
    Input('concept_data', 'data'),
    Input('nav_selection', 'data'),
    Input('section_tabs', 'active_tab'),
    State({'category_tabs' : ALL}, 'active_tab'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def update_section(concept_data, selected_concept, selected_tab, category_tabs, nav_selection):
    if ctx.triggered_id:
        if selected_tab == 'Labels':
            out_content = labels_section(concept_data, nav_selection)
        elif selected_tab == 'Categories':
            out_content = categories_section(concept_data, nav_selection, category_tabs)
        elif selected_tab == 'Properties':
            out_content = properties_section(concept_data, nav_selection)
    else:
        raise PreventUpdate
    return out_content

@callback(
    Output({'category_content' : ALL}, 'children'),
    Input({'category_tabs' : ALL}, 'active_tab'),
    State('concept_data', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def update_section(category_tabs, concept_data, nav_selection):
    out_content = no_update
    if ctx.triggered_id:
        path = '-'.join(nav_selection)
    
        buttons = dict()
        if category_tabs and category_tabs[0]:
            buttons = concept_data[path][category_tabs[0]]
        out_content = [categories_card_content(buttons)]
    return out_content