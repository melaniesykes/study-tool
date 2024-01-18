from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import uuid

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
    Output('nav_selection', 'data', allow_duplicate=True),
    Output('concept_data', 'data', allow_duplicate = True), # create concept if needed
    Input({'potential_concept' : ALL, 'section' : ALL}, 'n_clicks'),
    State({'potential_concept' : ALL, 'section' : ALL}, 'id'),
    State({'potential_concept' : ALL, 'section' : ALL}, 'children'),
    State('concept_data', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, button_ids, buttons, concept_data, nav_selection):
    out_selection_id = out_data = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            out_selection_id = trigger['potential_concept']
            print('selected potential new concept', out_selection_id)
            if out_selection_id not in concept_data:
                button_text = buttons[concept_index]
                new_concept = blank_concept(nav_selection, out_selection_id, button_text)

                out_data = Patch()
                
                button_section = trigger['section']
                print('new concept', out_selection_id, 'in section', button_section)
                if button_section == 'Supersets':
                    parent = out_selection_id
                    child = nav_selection
                    print('adding superset', parent, 'to', child)
                    button_section = 'Subsets'
                    out_data[child]['Supersets'][parent] = None # button text now stored in new_concept
                    new_concept['Implied Subsets'].append(child)
                    child_subsets = list(concept_data[child]['Subsets'].keys())
                    child_subsets += concept_data[child]['Implied Subsets']
                    for concept in set(child_subsets):
                        if concept in concept_data:
                            new_concept['Implied Subsets'].append(concept)
                            out_data[concept]['Implied Supersets'].append(parent)
                else:
                    parent = nav_selection
                    child = out_selection_id
                    if button_section == 'Subsets':
                        print('adding subset', child, 'to', parent)
                        new_concept['Implied Supersets'].append(parent)
                        print('adding', parent, 'to', child, 'Implied supersets')
                        parent_supersets = list(concept_data[parent]['Supersets'].keys())
                        parent_supersets += concept_data[parent]['Implied Supersets']
                        for concept in set(parent_supersets):
                            if concept in concept_data:
                                out_data[concept]['Implied Subsets'].append(child)
                                new_concept['Implied Supersets'].append(concept)
                    else:
                        out_data[parent]['children'][child] = button_section 
                out_data[out_selection_id] = new_concept

                    
    return out_selection_id, out_data

@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Input({'concept' : ALL, 'nav' : ALL}, 'n_clicks'),
    State({'concept' : ALL, 'nav' : ALL}, 'id'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def select_concept_from_nav(n_clicks, button_ids, existing_selection):
    out_selection = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            selection = trigger['concept']
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
    def concept_children(cncpt):
        result = []
        for child_id in cncpt['children']:
            child_nav_id = {'concept' : child_id, 'nav' : 'child'}
            print(cncpt['text'], 'child', concept_data[child_id]['text'])
            child = html.H5(concept_data[child_id]['text'], id = child_nav_id)
            result.append(child)

        for subset_id, subset_text_or_none in cncpt['Subsets'].items():
            child = concept_data.get(subset_id, dict())
            subset_text = child.get('text', subset_text_or_none)
            print(cncpt['text'], 'subset', subset_text)
            result.append(html.H5(subset_text, id = {'concept' : subset_id, 'nav' : 'parent'}))

        for subset_id in cncpt['Implied Subsets']:
            subset_text = concept_data[subset_id]['text']
            print(cncpt['text'], 'subset', subset_text)

            result.append(html.H5(subset_text, id = {'concept' : subset_id, 'nav' : 'parent'}))
        return result
    
    def concept_self_and_children(concept_id):
        result = []
        nav_id = {'concept' : concept_id, 'nav' : 'sibling'}
        sibling = html.H4(concept_data[concept_id]['text'], id = nav_id)
        print('self and children', concept_data[concept_id]['text'])
        result.append(sibling)
        result.extend(concept_children(concept_data[concept_id]))
        return result
    
    def grandparent_tree(prnt, superset_text):
        superset_text = prnt.get('text', superset_text)
        print('grandchildren of', superset_text)
        result = [html.H3(superset_text, id = {'concept' : prnt['id'], 'nav' : 'parent'})]
        for sibling_id in prnt.get('children', set()):
            result.extend(concept_self_and_children(sibling_id))
        
        for sibling_id, sibling_text_or_none in prnt['Subsets'].items():
            if sibling_id in concept_data:
                result.extend(concept_self_and_children(sibling_id))

        for sibling_id in prnt['Implied Subsets']:
            result.extend(concept_self_and_children(sibling_id)) 
        return result       

    out_concept_label = f"## __{concept_data[selected_concept]['text']}__"
    concept = concept_data[selected_concept]
    out_children = []
    parent_id = concept['parent']

    for superset_id, superset_text_or_none in concept['Supersets'].items():
        if superset_id == parent_id:
            continue
        parent = concept_data.get(superset_id, dict())
        superset_text = parent.get('text', superset_text_or_none)
        out_children.append(html.H3(superset_text, id = {'concept' : parent['id'], 'nav' : 'super'}))

    for superset_id in concept['Implied Supersets']:
        if superset_id == parent_id:
            continue
        parent = concept_data.get(superset_id, dict())
        out_children.append(html.H3(parent['text'], id = {'concept' : parent['id'], 'nav' : 'implied super'}))

    if parent_id:
        parent = concept_data[parent_id]
        if (selected_concept not in parent['Supersets']) and (selected_concept not in parent['Supersets']):
            out_children.extend(grandparent_tree(parent, parent['text']))
        
    if out_children == []:
        out_children.extend(concept_self_and_children(selected_concept))

    return out_children, out_concept_label
   