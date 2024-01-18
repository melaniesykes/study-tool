from dash import dcc, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

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
                    style={'margin': 5, 'padding': 2}
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
    State({'form' : MATCH, 'store' : 'last_clicked'}, 'data'),
    State({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'active'),
    State({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'children'),
    State('section_tabs', 'active_tab'),
    State('mode', 'value'),
    State({'category_tabs' : ALL}, 'active_tab'),
    prevent_initial_call = True
)
def display_submission(n_clicks, last_clicked, is_active, buttons, selected_section, mode, category_tab):
    out_buttons = out_content = out_last_clicked = no_update
    trigger = ctx.triggered_id
    clicked_button = trigger['text_button']

    if trigger and n_clicks[clicked_button]:
        if (selected_section == 'Categories') and category_tab:
            selected_section = category_tab[0]
        
        out_active = [no_update for button in ctx.outputs_list[2]]
        if last_clicked:
            out_last_clicked = None
            # if is_active[clicked_button]:
            #     out_active[clicked_button] = False
            # else:
            start = last_clicked
            end = clicked_button

            selected_text = ' '.join(buttons[start: end + 1])
            if mode == 'add':
                out_active = [False for button in is_active]
            if mode in ('add', 'move'):
                out_content = [selected_section, selected_text]
            if mode in ('delete', 'move'):
                non_selected_text = buttons[:start] + buttons[end + 1:]
                out_buttons = button_section(non_selected_text, ctx.triggered_id['form'], 'words')

        else:
            out_last_clicked = clicked_button
            out_active[out_last_clicked] = True
    else:
        raise PreventUpdate

    return out_buttons, out_content, out_active, out_last_clicked 


@callback(
    Output('concept_data', 'data', allow_duplicate = True),
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    State('nav_selection', 'data'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def save_submission(form_update, form_update_ids, nav_selection, concept_data):
    trigger = ctx.triggered_id
    if trigger:
        update_index = form_update_ids.index(trigger)
        [selected_section, selected_text] = form_update[update_index]
        selected_text = selected_text.replace(',', '').replace('.', '')
        path = '-'.join(nav_selection)
        out_data = Patch()
        new_id = '-'.join(nav_selection + [str(concept_data[path]['max_id'])])
        out_data[path][selected_section][new_id] = selected_text
        out_data[path]['max_id'] += 1
    else:
        raise PreventUpdate
    return out_data


