from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate



def concept_section(concept, existing_buttons = None, selected_tab = 'Labels'):
    if existing_buttons:
        section_text_buttons = [
            dbc.Button(button_text, id = {'section' : selected_tab, 't' : t})
            for t, button_text in enumerate(existing_buttons[selected_tab])
        ]
    else:
        section_text_buttons = None
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
        dbc.CardBody(section_text_buttons, id = 'section_content')
    ])
])





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

@callback(
    Output('nav_structure', 'data'),
    Input('nav_selection', 'data'),
    State('nav_structure', 'data'),
    State({'section' : ALL, 't' : ALL}, 'children'),
    prevent_initial_call = True
)
def display_concept(selection_path, nav_structure, buttons):
    out_structure = no_update
    
    path_str = '-'.join(selection_path)
    concept = nav_structure.get(path_str, None)
    
    if concept is None:
        concept_text = buttons[int(selection_path[-1])]
        out_structure = Patch()
        out_structure[path_str] = {'text' : concept_text, 'children' : []}
        out_structure['-'.join(selection_path[:-1])]['children'].append(path_str)
        # out_concept = concept_section(concept_text)
    # else:
    #     concept_text = concept['text']
        # out_concept = concept_section(concept_text, existing_buttons=data[path_str])
    # return out_concept, 
    return out_structure

@callback(
    Output('nav_display', 'children'),
    Input('nav_structure', 'data'),
    Input('nav_selection', 'data'),
    prevent_initial_call = True
)
def display_nav(structure, selected_concept):
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
   