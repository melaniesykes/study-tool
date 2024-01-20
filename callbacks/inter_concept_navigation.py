from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pprint import pprint

@callback(
    Output('add_mode', 'data'),
    Output('nav_selection', 'data'),
    Input({'concept_button' : ALL}, 'n_clicks'),
    Input('concept_network', 'tapNode'),
    Input('concept_network', 'selectedNodeData'),
    State('concept_network', 'elements'),
    State({'concept_button' : ALL}, 'id'),
    State('nav_selection', 'data'),
    State({'add_button' : ALL}, 'active'),
    prevent_initial_call = True
)
def select_concept(n_clicks, clicked_concept, network_selections, concept_network,
                   button_ids, nav_selection, add_mode):
    out_add_mode = out_selection_id = selection_id = no_update
    trigger = ctx.triggered_id
    if trigger:
        if trigger == 'concept_network':
            if network_selections:
                selection_id = clicked_concept['data']['id']
            else:
                selection_id = None
        else:
            if (not concept_network) or n_clicks[button_ids.index(trigger)]:
                selection_id = trigger['concept_button']
        
        if add_mode and add_mode[0]:
            if selection_id is not None:
                add_category = ctx.states_list[3][0]['id']['add_button']
                out_add_mode = [add_category, selection_id]
                selection_id = no_update

        
        if selection_id == nav_selection:
            selection_id = no_update
        
        out_selection_id = selection_id
    return out_add_mode, out_selection_id

@callback(
    Output({'add_button' : MATCH}, 'active'),
    Input({'add_button' : MATCH}, 'n_clicks'),
    State({'add_button' : MATCH}, 'active'),
    prevent_initial_call = True
)
def toggle_add_mode(n_clicks, last_state):
    out_active = no_update
    if n_clicks:
        out_active = not last_state
    return out_active