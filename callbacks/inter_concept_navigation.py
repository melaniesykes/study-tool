from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pprint import pprint

@callback(
    Output('add_mode', 'data'),
    Output('nav_selection', 'data'),
    Output('concept_selection_change', 'data'),
    Input({'concept_button' : ALL}, 'n_clicks'),
    Input('last_concept_click', 'data'),
    Input('concepts_unselected', 'data'),
    State('concept_network', 'elements'),
    State({'concept_button' : ALL}, 'id'),
    State('nav_selection', 'data'),
    State({'add_button' : ALL}, 'active'),
    prevent_initial_call = True
)
def select_concept(n_clicks, clicked_concept, network_selections, 
                   concept_network, button_ids, nav_selection, add_mode):
    def update_selection(select = None, unselect = None):
        old_unselected = new_selected = False
        network = Patch()
        for i, element in enumerate(concept_network):
            element_id = element['data'].get('id', None)
            if element_id == unselect:
                network[i]['selected'] = False
                old_unselected = True
            elif element_id == select:
                network[i]['selected'] = True
                new_selected = True
            if None not in (old_unselected, new_selected):
                break
        return network
    
    def find_selection(select = None, unselect = None):
        old_unselected = new_selected = None
        for i, element in enumerate(concept_network):
            element_id = element['data'].get('id', None)
            if element_id == unselect:
                old_unselected = i
            elif element_id == select:
                new_selected = i
            if None not in (old_unselected, new_selected):
                break
        return old_unselected, new_selected
    out_add_mode = out_selection_id = selection_id = out_network = no_update
    trigger = ctx.triggered_id

    if trigger:
        if trigger == 'last_concept_click':
            selection_id = clicked_concept
            if add_mode and add_mode[0]:
                unselect_id, select_id = find_selection(unselect = clicked_concept, select = nav_selection)
                add_category = ctx.states_list[3][0]['id']['add_button']
                out_add_mode = [add_category, selection_id, unselect_id, select_id]
                selection_id = no_update
        elif trigger == 'concepts_unselected':
            selection_id = None
            # pass

        else:
            if (not concept_network) or n_clicks[button_ids.index(trigger)]:
                # assume concept change: no support for add mode except for from network
                selection_id = trigger['concept_button']
                out_network = find_selection(unselect = nav_selection, select = selection_id)                
                                
        if selection_id == nav_selection:
            selection_id = no_update
        
        out_selection_id = selection_id
    return out_add_mode, out_selection_id, out_network

@callback(
    Output('last_concept_click', 'data'),
    Input('concept_network', 'tapNode'),
    prevent_initial_call = True
)
def store_clicks(clicked_concept):
    out_clicked = no_update
    if clicked_concept and ctx.triggered_id:
        out_clicked = clicked_concept['data']['id']
    return out_clicked


# @callback(
#     Output('concepts_unselected', 'data'),
#     Input('concept_network', 'selectedNodeData'),
#     prevent_initial_call = True
# )
# def unselect_concepts(network_selections):
#     out_unselected = no_update
#     if ctx.triggered_id and (not network_selections):
#         out_unselected = 'placeholder'
#     return out_unselected

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