from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

def blank_concept(concept_name = None):
    return {
        'Name' : concept_name,
        'Labels' : [],
        'Categories' : [],
        'Properties' : []
    }

def concept_section(concept, existing_buttons = None):
    def section(section_type):
        if existing_buttons:
            section_text_buttons = [
                dbc.Button(button_text, id = {'section' : section_type, 't' : t})
                for t, button_text in enumerate(existing_buttons[section_type])
            ]
        else:
            section_text_buttons = None
        return dbc.Row([
            dbc.Col(dbc.Button(section_type, id = {'section_button' : section_type}), width = 1),
            dbc.Col(html.Div(
                id = {'section_content' : section_type},
                children = section_text_buttons
            ))
        ])
    
    return html.Div([
    dcc.Markdown(f'## __{concept}__' if concept else None, id = {'index' : 'main_label'}),
    dcc.Store(data = 'Labels', id = 'section'),
    section('Labels'),
    section('Categories'),
    section('Properties'),
])

@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Input({'section' : ALL, 't' : ALL}, 'n_clicks'),
    State({'section' : ALL, 't' : ALL}, 'id'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, button_ids):
    out_selection = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            # print(trigger, n_clicks)
            out_selection = Patch()
            out_selection.append(str(concept_index))
    return out_selection

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
            # print(trigger, n_clicks)
            selection = trigger['path'].split('-')
            if selection != existing_selection:
                out_selection = selection
    return out_selection

@callback(
    Output('concept_section', 'children'),
    Output('concept_data', 'data', allow_duplicate = True),
    Output('nav_structure', 'data'),
    Input('nav_selection', 'data'),
    State('nav_structure', 'data'),
    State('concept_data', 'data'),
    State({'section' : ALL, 't' : ALL}, 'children'),
    prevent_initial_call = True
)
def display_concept(selection_path, nav_structure, data, buttons):
    out_data = out_structure = no_update
    
    path_str = '-'.join(selection_path)
    concept = nav_structure.get(path_str, None)
    
    if concept is None:
        concept_text = buttons[int(selection_path[-1])]
        out_data = Patch()
        out_data[path_str] = blank_concept(concept_text)
        out_structure = Patch()
        out_structure[path_str] = {'text' : concept_text, 'children' : []}
        out_structure['-'.join(selection_path[:-1])]['children'].append(path_str)
        out_concept = concept_section(concept_text)
    else:
        concept_text = concept['text']
        out_concept = concept_section(concept_text, existing_buttons=data[path_str])
    return out_concept, out_data, out_structure

@callback(
    Output('nav_display', 'children'),
    Input('nav_structure', 'data'),
    Input('nav_selection', 'data'),
    prevent_initial_call = True
)
def display_nav(structure, selected_concept):
    print('structure', structure)
    parent_path = '-'.join(selected_concept[:-1])
    parent_text = structure[parent_path].get('text', '')
    sibling_ids = structure[parent_path]['children']
    out_children = [html.H3(parent_text, id = {'path' : parent_path, 'nav' : 'parent'})]
    for sibling_path in sibling_ids:
        sibling = html.H4(structure[sibling_path]['text'], id = {'path' : sibling_path, 'nav' : 'sibling'})
        out_children.append(sibling)
        for child_path in structure[sibling_path]['children']:
            child = html.H5(structure[child_path]['text'], id = {'path' : child_path, 'nav' : 'child'})
            out_children.append(child)
    return out_children
   