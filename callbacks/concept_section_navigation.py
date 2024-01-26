from dash import callback, Output, Input, State, ctx, ALL, no_update, MATCH
from pprint import pprint
from utils import no_updates, flattened_triggers, value_if_exists
from concept_section_content import *

from dash.exceptions import PreventUpdate

@callback(
    Output({'add_label_button' : MATCH}, 'active'),
    Input({'add_label_button' : MATCH}, 'n_clicks'),
    State({'add_label_button' : MATCH}, 'active'),
    prevent_initial_call = True
)
def toggle_add_label_mode(n_clicks, last_state):
    out_active = no_update
    if n_clicks:
        out_active = not last_state
    return out_active



@callback(
    Output('last_category_type', 'data'),
    Input({'tabs' : ALL, 'tab_type' : 'category'}, 'active_tab'),
    prevent_initial_call = True
)
def update_category_tab(category_tabs):
    out_category_type = no_update
    
    if category_tabs and category_tabs[0]:
        out_category_type = category_tabs[0]

    return out_category_type

@callback(
    Output({'section_content' : ALL}, 'children'),
    Output({'category_content' : ALL}, 'children'),
    Output('concept_details_section', 'children'),
    Output({'selected_concept_label' : ALL}, 'children'),
    Output({'selected_concept_labels_list' : ALL}, 'children'),
    Output({'tabs' : ALL, 'tab_type' : 'section'}, 'active_tab'),
    Output({'copy' : 'pins', 'concept_buttons' : ALL}, 'options'),
    Input('concept_data', 'data'),
    Input({'tabs' : ALL, 'tab_type' : 'section'}, 'active_tab'),
    Input('nav_selection', 'data'),
    Input('last_category_type', 'data'),
    Input('property_path', 'data'),
    Input('pins', 'data'),
    State({'add_label_button' : ALL}, 'active'),
    prevent_initial_call = True
)
def update_section(concept_data, selected_tab, nav_selection, category_type, property_path, pins, adding_label):
    if not ctx.triggered_id:
        raise PreventUpdate
    
    triggers = flattened_triggers(ctx.triggered_prop_ids)
    outs = no_updates(ctx.outputs_list)
    out_section_content, out_category_content, out_concept_details, out_concept_label, out_labels_label, out_tab, out_pins = outs
    
    if nav_selection == 'pins':
        out_concept_label = ['PINS'] if out_concept_label else out_concept_label
        out_labels_label = [None] if out_labels_label else out_labels_label
        out_concept_details = edit_pins_section(concept_data, pins)
        triggers = None
    elif nav_selection:
        out_concept_label = [f"## __{concept_data[nav_selection]['text']}__"] if out_concept_label else out_concept_label
        out_labels_label = [labels_section(concept_data, nav_selection, adding_label)] if out_labels_label else out_labels_label
    else:
        out_concept_label = [None] if out_concept_label else []
        out_labels_label = [None] if out_labels_label else out_labels_label
        out_concept_details = select_something_section(concept_data, pins)
        triggers = None

    match triggers:
        case {'property_path' : _}:
            if property_path['property_path']:
                if out_section_content:
                    if selected_tab != ['Properties']:
                        out_tab = ['Properties']
                    out_section_content = [add_properties_section(concept_data, property_path, nav_selection)]
                else:
                    prop_label = f"## __{concept_data[nav_selection]['text']}__"
                    labels = labels_section(concept_data, nav_selection, adding_label)
                    content = add_properties_section(concept_data, property_path, nav_selection)
                    out_concept_details = concept_details_section(concept_data, content, labels = labels, prop_label = prop_label)
                triggers = None

    match triggers:
        case None:
            pass
        case {'pins' : _}:
            out_pins = [[{
                'label' : concept_data[concept_id]['text'], 
                'value' : concept_id
            } for concept_id in pins]]
        case {'concept_data' : _} | {'nav_selection' : _} | {'last_category_type' : _}:
            if (not out_section_content):
                labels = labels_section(concept_data, nav_selection, adding_label)
                content = categories_content(concept_data, nav_selection, category_type)
                content = add_categories_section(category_type, content = content)
                out_concept_details = concept_details_section(concept_data, content, pins, labels = labels)
            elif selected_tab == ['Categories']:
                out_category_content = [categories_content(concept_data, nav_selection, category_type)]
            elif selected_tab == ['Properties']:
                out_section_content = [add_properties_section(concept_data, property_path, nav_selection)]
        case {'tab_type' : 'section'}: # section tabs
            if selected_tab == ['Categories']:
                content = categories_content(concept_data, nav_selection, category_type)
                out_section_content = [add_categories_section(category_type, content = content)]
            else:
                out_section_content = [add_properties_section(concept_data, property_path, nav_selection)]

    return out_section_content, out_category_content, out_concept_details, out_concept_label, out_labels_label, out_tab, out_pins