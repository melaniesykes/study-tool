from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

from dash.exceptions import PreventUpdate

def button_section(text, section):
    if section == 'words':
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
                    id = {'form' : section, 'text_button' : n},
                    children = word.strip() + suffix, 
                    type = 'button',
                    outline = True,
                    color = 'primary'
                )
            )
    section_content.append(
        dbc.Button(
            id = {'form' : section, 'submit_button' : n},
            children = 'SUBMIT', 
            color = 'secondary',
            type = 'submit'
        )
    )
    return section_content

@callback(
    Output({'form' : ALL, 'text_button' : ALL}, 'color'),
    Output({'form' : ALL, 'text_button' : ALL}, 'disabled'),
    Output('section_content', 'children', allow_duplicate = True),
    Input('nav_structure', 'data'),
    Input('section_tabs', 'active_tab'),
    State({'form' : ALL, 'text_button' : ALL}, 'children'),
    State('concept_data', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def select_section(nav_structure, selected_tab, text_buttons, concept_data, nav_selection):
    print('data', concept_data)
    print('nav_structre', nav_structure)
    if ctx.triggered_id:
        out_color = []
        out_disabled = []
        path = '-'.join(nav_selection)
        buttons = concept_data[path][selected_tab]
        button_ids = nav_structure[path][selected_tab]
        out_content = [
            dbc.Button(button_text, id = {'potential_concept' : button_id})
            for button_id, button_text in zip(button_ids, buttons)
        ]

        for button in text_buttons:
            if (button in buttons):
                out_color.append('success')
                out_disabled.append(True)
            else:
                out_color.append('primary')
                out_disabled.append(False)
    else:
        raise PreventUpdate
    return out_color, out_disabled, out_content

@callback(
    Output({'form' : MATCH}, 'children', allow_duplicate=True),
    Input({'form' : MATCH, 'format_button' : ALL}, 'n_clicks'),
    State({'form' : MATCH, 'text_button' : ALL}, 'children'),
	State({'form' : MATCH, 'input' : ALL}, 'value'),
    prevent_initial_call = True
)
def switch_form_format(trigger, button_text, input_text):
    out_buttons = no_update
    button = ctx.triggered_id.get('format_button', None)
    form = ctx.triggered_id.get('form', None)

    if button_text and (button == 'text'):
        text = ' '.join(button_text)
        out_buttons = dmc.Textarea(id = {'input' : 'input', 'form' : form}, value = text, autosize = True)
    elif input_text and (button == 'button'):
        text = input_text[0]    
        if text:
            out_buttons = button_section(text, form)

    return out_buttons

@callback(
    Output({'form' : MATCH, 'text_button' : MATCH}, 'active', allow_duplicate=True),
    Input({'form' : MATCH, 'text_button' : MATCH}, 'n_clicks'),
    State({'form' : MATCH, 'text_button' : MATCH}, 'active'),
    prevent_initial_call = True
)
def activate_text_button(trigger, is_active):
    out_active = no_update
    if ctx.triggered:
        out_active = not is_active
    return out_active

@callback(
    Output({'form' : 'words'}, 'children', allow_duplicate=True),
    Input({'form' : 'sentences', 'text_button' : ALL}, 'n_clicks'),
    State({'form' : 'sentences', 'text_button' : ALL}, 'id'),
    State({'form' : 'sentences', 'text_button' : ALL}, 'children'),
    prevent_initial_call = True
)
def break_down_sentence(n_clicks, sentence_buttons, sentences):
    out_buttons = no_update
    trigger = ctx.triggered_id
    if trigger:
        trigger_index = sentence_buttons.index(trigger)
        sentence = sentences[trigger_index]
        out_buttons = button_section(sentence, 'words')
    return out_buttons





@callback(
    Output('section_content', 'children', allow_duplicate = True),
    Output('concept_data', 'data', allow_duplicate = True),
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    State('nav_selection', 'data'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def add_to_section(form_update, form_update_ids, nav_selection, concept_data):
    trigger = ctx.triggered_id
    if trigger:
        update_index = form_update_ids.index(trigger)
        [mode, selected_text] = form_update[update_index]
        selected_text = selected_text.replace(',', '').replace('.', '')
        path = '-'.join(nav_selection)
        out_data = Patch()
        out_data[path][mode].append(selected_text)
        new_id = '-'.join(nav_selection + [str(concept_data[path]['max_id'])])
        out_data[path]['max_id'] += 1
        out_mode_content = Patch()
        out_mode_content.append(dbc.Button(selected_text, id = {'potential_concept' : new_id}))
        out_content = out_mode_content
        
    else:
        raise PreventUpdate
    return out_content, out_data

@callback(
    Output({'form' : MATCH}, 'children', allow_duplicate=True),
    Output({'form' : MATCH, 'form_dummy' : 'form_dummy'}, 'data'),
    Output({'form' : MATCH, 'text_button' : ALL}, 'active', allow_duplicate=True),
    Input({'form' : MATCH}, 'n_submit'),
    State({'form' : MATCH, 'text_button' : ALL}, 'active'),
    State({'form' : MATCH, 'text_button' : ALL}, 'children'),
    State('section_tabs', 'active_tab'),
    State('mode', 'value'),
    prevent_initial_call = True
)
def handle_submission(trigger, is_active, buttons, selected_section, mode):
    out_buttons = out_content = no_update
    out_active = [no_update for button in buttons]
    if ctx.triggered_id and trigger:
        selected_text = [button for button, i_a in zip(buttons, is_active) if i_a]
        selected_text = ' '.join(selected_text)
        if mode == 'add':
            out_active = [False for button in is_active]
        if mode in ('add', 'move'):
            out_content = [selected_section, selected_text]
        if mode in ('delete', 'move'):
            non_selected_text = [button for button, i_a in zip(buttons, is_active) if not i_a]
            out_buttons = button_section(non_selected_text, ctx.triggered_id['form'])
    else:
        raise PreventUpdate
    return out_buttons, out_content, out_active
