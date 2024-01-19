from dash import dcc, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import uuid

from dash.exceptions import PreventUpdate

def button_section(text, section, split_type):
    if split_type == 'words':
        delimiter = ' '
        suffix = ''
    else:
        delimiter = suffix = '.'
    words = text.split(delimiter) if isinstance(text, str) else [t.replace(delimiter, '') for t in text]
    section_content = []
    n = 0
    for n, word in enumerate(words):
        if word:
            section_content.append(
                dbc.Button(
                    id = {'form' : section, 'format' : split_type, 'text_button' : n},
                    children = word.strip() + suffix, 
                    type = 'button',
                    color = 'light',
                    style = {
                        'margin': 2, 
                        'padding': 3,
                        'border-radius' : '2px'
                    },
                    class_name = 'text-button'
                )
            )
    section_content.append(
        dcc.Store(
            id = {'form' : section, 'store' : 'last_clicked'},
        )
    )
    return section_content


@callback(
    Output({'form' : 'recent_sentence'}, 'children', allow_duplicate=True),
    Input({'form' : 'sentences', 'format' : 'sentences', 'text_button' : ALL}, 'n_clicks'),
    State({'form' : 'sentences', 'format' : 'sentences', 'text_button' : ALL}, 'id'),
    State({'form' : 'sentences', 'format' : 'sentences', 'text_button' : ALL}, 'children'),
    prevent_initial_call = True
)
def break_down_recent_sentence(n_clicks, sentence_buttons, sentences):
    out_buttons = no_update
    trigger = ctx.triggered_id
    if trigger:
        trigger_index = sentence_buttons.index(trigger)
        sentence = sentences[trigger_index]
        out_buttons = button_section(sentence, 'recent_sentence', 'words')
    return out_buttons

@callback(
    Output({'form' : MATCH}, 'children', allow_duplicate=True),
    Input({'form' : MATCH, 'component' : 'input_tabs'} , 'active_tab'),
    State({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'children'),
	State({'form' : MATCH, 'input' : ALL}, 'value'),
    prevent_initial_call = True
)
def switch_form_format(trigger, button_text, input_text):
    out_buttons = no_update
    form = ctx.triggered_id.get('form', None)
    active_tab = trigger.get('format_button')
    
    text = None
    if button_text:
        text = ' '.join(button_text)
    elif input_text:
        text = input_text[0]

    if (active_tab == 'text'):
        out_buttons = dmc.Textarea(id = {'input' : 'input', 'form' : form}, value = text, autosize = True)
    elif active_tab in ('words', 'sentences'):
        if text:
            out_buttons = button_section(text, form, active_tab)

    return out_buttons

@callback(
    Output({'form' : MATCH}, 'children', allow_duplicate=True),
    Output({'form' : MATCH, 'form_dummy' : 'form_dummy'}, 'data'),
    Output({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'active'),
    Output({'form' : MATCH, 'store' : 'last_clicked'}, 'data'),
    Input({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'n_clicks'),
    Input({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'id'),
    State({'form' : MATCH, 'store' : 'last_clicked'}, 'data'),
    State({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'active'),
    State({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'children'),
    State('section_tabs', 'active_tab'),
    State('mode', 'value'),
    State({'category_tabs' : ALL}, 'active_tab'),
    prevent_initial_call = True
)
def submit_concept(n_clicks, button_ids, last_clicked, is_active, buttons, selected_section, mode, category_tab):
    out_buttons = out_content = out_last_clicked = no_update
    trigger = ctx.triggered_id
    button_number = trigger['text_button']

    if trigger and n_clicks[button_number]:
        if (selected_section == 'Categories') and category_tab:
            selected_section = category_tab[0]
        
        out_active = [no_update for button in ctx.outputs_list[2]]
        if last_clicked:
            out_last_clicked = None
            # if is_active[clicked_button]:
            #     out_active[clicked_button] = False
            # else:
            start = last_clicked
            end = button_number

            selected_text = ' '.join(buttons[start: end + 1])
            if mode == 'add':
                out_active = [False for button in is_active]
            if mode in ('add', 'move'):
                out_content = [selected_section, selected_text]
            if mode in ('delete', 'move'):
                non_selected_text = buttons[:start] + buttons[end + 1:]
                out_buttons = button_section(non_selected_text, ctx.triggered_id['form'], 'words')

        else:
            out_last_clicked = button_number
            out_active[out_last_clicked] = True
    else:
        raise PreventUpdate

    return out_buttons, out_content, out_active, out_last_clicked 


def blank_concept(parent, concept_id, concept_name):
    return {
        'id' : concept_id,
        'parent' : parent, # parent concept, not necessarily same as parent node
        'text' : concept_name,
        'Labels' : [],
        'supersets' : dict(),
        'subsets' : dict(),
        'Properties' : [],
    }

@callback(
    Output('concept_data', 'data', allow_duplicate = True),
    Output('concept_network', 'elements'),
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    State('nav_selection', 'data'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def new_concept(form_update, form_update_ids, nav_selection, concept_data):
    trigger = ctx.triggered_id
    out_data = out_network = out_selection_id = no_update

    if trigger:
        update_index = form_update_ids.index(trigger)
        [selected_section, selected_text] = form_update[update_index]
        selected_text = selected_text.replace(',', '').replace('.', '')
        out_data = Patch()
        out_selection_id = str(uuid.uuid4())

        new_concept = blank_concept(nav_selection, out_selection_id, selected_text)
        
        if selected_section == 'Supersets':
            parent = out_selection_id
            child = nav_selection
            new_concept['subsets'][child] = 'explicit'
            out_data[child]['supersets'][parent] = 'reverse'
            for concept in concept_data[child]['subsets']:
                new_concept['subsets'][concept] = 'implicit'
                out_data[concept]['supersets'][parent] = 'implicit'
        else:
            parent = nav_selection
            child = out_selection_id
            if selected_section == 'Subsets':
                new_concept['supersets'][parent] = 'explicit'
                out_data[parent]['subsets'][child] = 'reverse'
                for concept in concept_data[parent]['supersets']:
                    out_data[concept]['subsets'][child] = 'implicit'
                    new_concept['supersets'][concept] = 'implicit'
            else:
                out_data[parent][selected_section].append(child) 
        out_data[out_selection_id] = new_concept        
        
        out_network = Patch()
        
        if selected_section != 'Labels':
            out_network.append({
                'data' : {'id' : out_selection_id, 'label' : selected_text}, 
                'position': {'x': 0, 'y': 0}
            })                                               
            if parent:
                out_network.append({'data': {'source': child, 'target': parent}})
    else:
        raise PreventUpdate
    return out_data, out_network