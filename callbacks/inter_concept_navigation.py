from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pprint import pprint

def blank_concept(parent, concept_id, concept_name):
    return {
        'id' : concept_id,
        'parent' : parent, # original parent, not necessarily the parent shown in nav tree
        'text' : concept_name,
        'children' : dict(), # concepts which should be SHOWN as children in nav tree
        'Labels' : dict(),
        'Supersets' : dict(),
        'Subsets' : dict(),
        'Implied Supersets' : [], # concepts only
        'Implied Subsets' : [], # concepts only
        'Properties' : dict(),
    }

@callback(
    Output('nav_selection', 'data'),
    Input({'potential_concept' : ALL, 'section' : ALL}, 'n_clicks'),
    Input('concept_network', 'tapNode'),
    State({'potential_concept' : ALL, 'section' : ALL}, 'id'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, concept_network, button_ids):
    out_selection_id = no_update
    trigger = ctx.triggered_id
    if trigger:
        if trigger == 'concept_network':
            out_selection_id = concept_network['data']['id']
        else:
            concept_index = button_ids.index(trigger)
            if n_clicks[concept_index]:
                out_selection_id = trigger['potential_concept']
                                
    return out_selection_id

@callback(
    Output('selected_concept_label', 'children'),
    Input('nav_selection', 'data'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def display_nav(selected_concept, concept_data):    
    out_concept_label = f"## __{concept_data[selected_concept]['text']}__"
    return out_concept_label
   