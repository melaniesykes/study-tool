from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pprint import pprint

@callback(
    Output('nav_selection', 'data'),
    Input({'concept_button' : ALL}, 'n_clicks'),
    Input('concept_network', 'tapNode'),
    Input('concept_network', 'selectedNodeData'),
    State('concept_network', 'elements'),
    State({'concept_button' : ALL}, 'id'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, clicked_concept, network_selections, concept_network, button_ids, nav_selection):
    out_selection_id = no_update
    trigger = ctx.triggered_id
    if trigger:
        if trigger == 'concept_network':
            if network_selections:
                out_selection_id = clicked_concept['data']['id']
            else:
                out_selection_id = None
        else:
            if (not concept_network) or n_clicks[button_ids.index(trigger)]:
                out_selection_id = trigger['concept_button']
        if out_selection_id == nav_selection:
            nav_selection = no_update
    return out_selection_id


   