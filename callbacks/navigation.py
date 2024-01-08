from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

def blank_concept(concept_name = None):
    return {
        'text' : concept_name,
        'children' : dict(),
        'Labels' : dict(),
        'Categories' : dict(),
        'Properties' : dict(),
        'max_id' : 0
    }

@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Output('concept_data', 'data', allow_duplicate = True), # create concept if needed
    Input({'potential_concept' : ALL}, 'n_clicks'),
    State({'potential_concept' : ALL}, 'id'),
    State({'potential_concept' : ALL}, 'children'),
    State('concept_data', 'data'),
    State('section_tabs', 'active_tab'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, button_ids, buttons, concept_data, active_tab):
    out_selection = out_data = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            path = trigger['potential_concept']
            if path not in concept_data:
                parent_path = '-'.join(path.split('-')[:-1])
                out_data = Patch()
                out_data[parent_path]['children'][path] = active_tab
                button_text = concept_data[parent_path][active_tab][path]
                out_data[path] = blank_concept(button_text)
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


@callback(
    Output('nav_display', 'children'),
    Output('selected_concept_label', 'children'),
    Input('nav_selection', 'data'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def display_nav(selected_concept, concept_data):
    out_concept_label = f"## __{concept_data['-'.join(selected_concept)]['text']}__"
    parent_path = '-'.join(selected_concept[:-1])
    parent_text = concept_data[parent_path].get('text', '')
    out_children = [html.H3(parent_text, id = {'path' : parent_path, 'nav' : 'parent'})]
    for sibling_path in concept_data[parent_path]['children']:
        sibling_id = {'path' : sibling_path, 'nav' : 'sibling'}
        sibling = html.H4(concept_data[sibling_path]['text'], id = sibling_id)
        out_children.append(sibling)
        for child_path in concept_data[sibling_path]['children']:
            child_id = {'path' : child_path, 'nav' : 'child'}
            child = html.H5(concept_data[child_path]['text'], id = child_id)
            out_children.append(child)
    return out_children, out_concept_label
   