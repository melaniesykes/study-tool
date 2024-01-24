from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from pprint import pprint

def network_stylesheet(selection = None):
    stylesheet = [
        # Group selectors
        {
            'selector': 'node',
            'style': {
                'content': 'data(label)',
                'text-halign':'center',
                'text-valign':'center',
                'width':'label',
                'height':'label',
                'shape':'square',
                'padding' : '2px',
                'background-color' : '#6FB1FC' # prevents default selection style styling
            }
        },
        {
            'selector': 'edge',
            'style': {
                'source-arrow-shape': 'triangle',
                'curve-style': 'bezier'
            }
        },

        # Class selectors
        {
            'selector': 'node.properties',
            'style': {
                'background-color': 'darkgray',
            }
        },
        {
            'selector': 'edge.properties',
            'style': {'line-style': 'dotted', 'line-color': 'darkgray'},
        }
    ]
    if selection:
        stylesheet.append({
            'selector': f'node[id = "{selection}"]',
            'style': { 
                #'background-color': '#86B342',
                'border-width': 2,
                'border-color': '#86B342'
            }
        })
    return stylesheet


@callback(
    Output('add_mode', 'data'),
    Output('nav_selection', 'data'),
    Output('concept_network', 'stylesheet'),
    Output('property_path', 'data'),
    Input({'concept_button' : ALL}, 'n_clicks'),
    Input('last_concept_click', 'data'),
    Input('concepts_unselected', 'data'),
    Input({'property_buttons' : ALL}, 'value'),
    Input({'superset_property_buttons' : ALL}, 'value'),
    Input({'section_tabs' : ALL}, 'active_tab'),
    State('concept_network', 'elements'),
    State({'concept_button' : ALL}, 'id'),
    State('nav_selection', 'data'),
    State({'add_button' : ALL}, 'active'),
    prevent_initial_call = True
)
def select_concept(n_clicks, clicked_concept, network_selections, props, sup_props, tabs,
                   concept_network, button_ids, nav_selection, add_mode):

    out_add_mode = out_selection_id = selection_id = out_network = out_prop_path = no_update
    trigger = ctx.triggered_id
    if not trigger:
        raise PreventUpdate

    match trigger:
        case 'last_concept_click':
            clicked_id, concept_type, parent = clicked_concept
            if concept_type == 'properties':
                selection_id = parent
            else:
                selection_id = None if (clicked_id == nav_selection) else clicked_id
                
            if add_mode and add_mode[0]:
                add_category = ctx.states_list[3][0]['id']['add_button']
                out_add_mode = [add_category, selection_id]
                selection_id = no_update
            elif concept_type == 'properties':
                if selection_id == nav_selection:
                    out_prop_path = Patch()
                    out_prop_path['property_path'].append(clicked_id)
                else:
                    out_prop_path = {'parent': selection_id, 'property_path' : [clicked_id]}
            else:
                out_network = network_stylesheet(selection_id)

        case 'concepts_unselected':
            selection_id = None
            out_network = network_stylesheet()

        case {'concept_button' : concept_id}:
            if (not concept_network) or n_clicks[button_ids.index(trigger)]:
                # assume concept change: no support for add mode except for from network
                selection_id = concept_id
                out_network = network_stylesheet(selection_id)
        
        case {'property_buttons' : property_id}:
            if props and props[0]:
                out_prop_path = Patch()
                out_prop_path['property_path'] = props[0]
        
        case {'superset_property_buttons' : superset_id}:
            if sup_props and sup_props[0]:
                out_prop_path = {'parent': superset_id, 'property_path' : sup_props[0]}
        
        case {'section_tabs' : new_section}:
            out_prop_path = Patch()
            out_prop_path['property_path'] = []

    if selection_id == nav_selection:
        selection_id = no_update
        
    out_selection_id = selection_id

    if (out_selection_id != no_update) and (out_prop_path == no_update):
        out_prop_path = {'parent': out_selection_id, 'property_path' : []}
    return out_add_mode, out_selection_id, out_network, out_prop_path

@callback(
    Output('last_concept_click', 'data'),
    Input('concept_network', 'tapNode'),
    prevent_initial_call = True
)
def store_clicks(clicked_concept):
    out_clicked = no_update
    if clicked_concept and ctx.triggered_id:
        out_clicked = (
            clicked_concept['data']['id'], 
            clicked_concept['classes'],
            clicked_concept['data']['parent_concept']
        )
    return out_clicked


@callback(
    Output('concepts_unselected', 'data'),
    Input('concept_network', 'selectedNodeData'),
    prevent_initial_call = True
)
def unselect_concepts(network_selections):
    out_unselected = no_update
    if ctx.triggered_id and (not network_selections):
        out_unselected = 'placeholder'
    return out_unselected

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