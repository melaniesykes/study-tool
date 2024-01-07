from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate



def concept_section(concept, existing_buttons = None, selected_tab = 'Labels'):
    return html.Div([
    dcc.Markdown(f'## __{concept}__' if concept else None, id = {'index' : 'main_label'}),
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Labels', tab_id = 'Labels'),
                dbc.Tab(label = 'Categories', tab_id = 'Categories'),
                dbc.Tab(label = 'Properties', tab_id = 'Properties'),
            ], id = 'section_tabs')
        ),
        dbc.CardBody(id = 'section_content')
    ])
])

def blank_concept(concept_name = None):
    return {
        'text' : concept_name,
        'Labels' : [],
        'Categories' : [],
        'Properties' : [],
        'max_id' : 0
    }

@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Output('concept_data', 'data', allow_duplicate = True), # create concept if needed
    Input({'potential_concept' : ALL}, 'n_clicks'),
    State({'potential_concept' : ALL}, 'id'),
    State({'potential_concept' : ALL}, 'children'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, button_ids, buttons, concept_data):
    out_selection = out_data = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            path = trigger['potential_concept']
            if path not in concept_data:
                out_data = Patch()
                concept = buttons[concept_index]
                out_data[path] = blank_concept(concept)
            out_selection = path.split('-')
    return out_selection, out_data

@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Input({'path' : ALL, 'nav' : ALL}, 'n_clicks'),
    State({'path' : ALL, 'nav' : ALL}, 'id'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def select_concept_from_nav(n_clicks, button_ids, existing_selection):
    out_selection = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            selection = trigger['path'].split('-')
            if selection != existing_selection:
                out_selection = selection
    return out_selection

def blank_nav_structure(concept_text = None):
    return {
        'text' : concept_text, 
        'children' : [], 
        'Labels' : [], 
        'Categories' : [],
        'Properties' : []
    }

@callback(
    Output('nav_structure', 'data'),
    Input('nav_selection', 'data'),
    State('nav_structure', 'data'),
    State({'potential_concept' : ALL}, 'children'),
    State('section_tabs', 'active_tab'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def display_concept(selection_path, nav_structure, buttons, active_tab, concept_data):
    out_structure = no_update
    
    path_str = '-'.join(selection_path)
    concept = nav_structure.get(path_str, None)
    
    if concept is None:
        concept_text = concept_data[path_str]['text']
        out_structure = Patch()
        out_structure[path_str] = blank_nav_structure(concept_text)
        out_structure['-'.join(selection_path[:-1])][active_tab].append(path_str)
    return out_structure

@callback(
    Output('nav_display', 'children'),
    Input('nav_structure', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def display_nav(structure, selected_concept):
    print('structure', structure)
    parent_path = '-'.join(selected_concept[:-1])
    parent_text = structure[parent_path].get('text', '')
    out_children = [html.H3(parent_text, id = {'path' : parent_path, 'nav' : 'parent'})]
    child_types = ['Labels', 'Categories', 'Properties']
    for ct1 in child_types:
        for sibling_path in structure[parent_path][ct1]:
            sibling_id = {'path' : sibling_path, 'nav' : 'sibling'}
            sibling = html.H4(structure[sibling_path]['text'], id = sibling_id)
            out_children.append(sibling)
            for ct2 in child_types:
                for child_path in structure[sibling_path][ct2]:
                    child_id = {'path' : child_path, 'nav' : 'child'}
                    child = html.H5(structure[child_path]['text'], id = child_id)
                    out_children.append(child)
    return out_children
   