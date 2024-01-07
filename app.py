import dash     # need Dash version 2.9.0 or higher
from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


load_dotenv()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 

def blank_concept(concept_name = None):
    return {
        'Name' : concept_name,
        'Labels' : [],
        'Categories' : [],
        'Properties' : []
    }

nav_section = html.Div([
    dcc.Store(id = 'nav_selection', data = []),
    dcc.Store(id = 'nav_structure', data = {'' : {'children' : []}}),
    dcc.Store(id = 'concept_data', data = {'' : blank_concept()}),
    html.Div(id = 'nav_display')
])
    
def concept_section(concept):
    def section(label):
        return dbc.Row([
            dbc.Col(dbc.Button(label, id = {'section_button' : label}), width = 1),
            dbc.Col(html.Div(id = {'section_content' : label}))
        ])
    
    return html.Div([
    dcc.Markdown(f'## __{concept}__' if concept else None, id = {'index' : 'main_label'}),
    dcc.Store(data = 'Labels', id = 'section'),
    section('Labels'),
    section('Categories'),
    section('Properties'),
])

def text_form(form_type):
    return dbc.Form(
        dcc.Input(id = {'input' : 'input', 'form' : form_type}),
        id = {'form' : form_type}
    )
    
app.layout = dbc.Row([
    dbc.Col(nav_section),
    dbc.Col([
        html.Div(concept_section(None), id = 'concept_section'),

        html.Br(),
        dcc.Markdown('Mode'),
        dbc.RadioItems(options = ['move', 'add', 'delete'], value = 'move', id = 'mode'),

        html.Br(),
        dbc.Button('Words', id ={'format_button' : 'button', 'form' : 'words'}),
        dbc.Button('Text', id = {'format_button' : 'text', 'form' : 'words'}),
        dcc.Store({'form' : 'words', 'form_dummy' : 'form_dummy'}),
        text_form('words'),

        html.Br(),
        dbc.Button('Sentences', id = {'format_button' : 'button', 'form' : 'sentences'}),
        dbc.Button('Text', id = {'format_button' : 'text', 'form' : 'sentences'}),
        dcc.Store({'form' : 'sentences', 'form_dummy' : 'form_dummy'}),
        text_form('sentences')
    ])
])

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
    Output('section', 'data'),
    Input({'section_button' : ALL}, 'n_clicks'),
    State({'form' : ALL, 'text_button' : ALL}, 'children'),
    State({'section' : ALL, 't' : ALL}, 'children'),
    State({'section' : ALL, 't' : ALL}, 'id'),
    prevent_initial_call = True
)
def select_section(trigger, text_buttons, section_buttons, section_button_ids):
    button = ctx.triggered_id.get('section_button', None)
    if button:
        out_mode = button
        mode_buttons = [text for text, i in zip(section_buttons, section_button_ids) if i['section'] == button]
        out_color = []
        out_disabled = []
        for button in text_buttons:
            if (button in mode_buttons):
                out_color.append('success')
                out_disabled.append(True)
            else:
                out_color.append('primary')
                out_disabled.append(False)
    else:
        raise PreventUpdate
    return out_color, out_disabled, out_mode

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
        out_buttons = dcc.Input(text, id = {'input' : 'input', 'form' : form})
    elif input_text and (button == 'button'):
        text = input_text[0]    
        if text:
            out_buttons = button_section(text, form)

    return out_buttons

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
    Output({'section_content' : ALL}, 'children'),
    Output('concept_data', 'data', allow_duplicate = True),
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def add_to_section(form_update, form_update_ids, nav_selection):
    trigger = ctx.triggered_id
    if trigger:
        update_index = form_update_ids.index(trigger)
        [mode, mode_index, selected_text, submit_time, n_sections] = form_update[update_index]
        selected_text = selected_text.replace(',', '').replace('.', '')
        out_mode_content = Patch()
        out_mode_content.append(dbc.Button(selected_text, id = {'section' : mode, 't' : submit_time}))
        out_content = [no_update for section in range(n_sections)]
        out_content[mode_index] = out_mode_content
        path = '-'.join(nav_selection + [])
        out_data = Patch()
        out_data[path][mode].append(selected_text)
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
    State('section', 'data'),
    State('mode', 'value'),
    State({'form' : MATCH}, 'n_submit_timestamp'),
    State({'section_content' : ALL}, 'id'),
    prevent_initial_call = True
)
def handle_submission(trigger, is_active, buttons, selected_section, mode, submit_time, sections):
    out_buttons = out_content = no_update
    out_active = [no_update for button in buttons]
    if ctx.triggered_id and trigger:
        selected_text = [button for button, i_a in zip(buttons, is_active) if i_a]
        selected_text = ' '.join(selected_text)
        selected_section_index = sections.index({'section_content' : selected_section})
        if mode == 'add':
            out_active = [False for button in is_active]
        if mode in ('add', 'move'):
            out_content = [selected_section, selected_section_index, selected_text, submit_time, len(sections)]
        if mode in ('delete', 'move'):
            non_selected_text = [button for button, i_a in zip(buttons, is_active) if not i_a]
            out_buttons = button_section(non_selected_text, ctx.triggered_id['form'])
    else:
        raise PreventUpdate
    return out_buttons, out_content, out_active


@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Input({'section' : ALL, 't' : ALL}, 'n_clicks'),
    State({'section' : ALL, 't' : ALL}, 'id'),
    prevent_initial_call = True
)
def select_concept_from_button(n_clicks, button_ids):
    out_selection = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            # print(trigger, n_clicks)
            out_selection = Patch()
            out_selection.append(str(concept_index))
    return out_selection

@callback(
    Output('nav_selection', 'data', allow_duplicate=True),
    Input({'path' : ALL, 'nav' : ALL}, 'n_clicks'),
    State({'path' : ALL, 'nav' : ALL}, 'id'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def select_concept_from_nav(n_clicks, button_ids, existing_selection):
    out_selection = no_update
    trigger = ctx.triggered_id
    if trigger:
        concept_index = button_ids.index(trigger)
        if n_clicks[concept_index]:
            # print(trigger, n_clicks)
            selection = trigger['path'].split('-')
            if selection != existing_selection:
                out_selection = selection
    return out_selection

@callback(
    Output('concept_section', 'children'),
    Output('concept_data', 'data', allow_duplicate = True),
    Output('nav_structure', 'data'),
    Input('nav_selection', 'data'),
    State('nav_structure', 'data'),
    State({'section' : ALL, 't' : ALL}, 'children'),
    prevent_initial_call = True
)
def display_concept(selection_path, nav_structure, buttons):
    out_data = out_structure = no_update
    
    path_str = '-'.join(selection_path)
    concept = nav_structure.get(path_str, None)
    
    if concept is None:
        concept_text = buttons[int(selection_path[-1])]
        out_data = Patch()
        out_data[path_str] = blank_concept(concept_text)
        out_structure = Patch()
        out_structure[path_str] = {'text' : concept_text, 'children' : []}
        out_structure['-'.join(selection_path[:-1])]['children'].append(path_str)
    else:
        concept_text = concept['text']
    out_concept = concept_section(concept_text)
    return out_concept, out_data, out_structure

@callback(
    Output('nav_display', 'children'),
    Input('nav_structure', 'data'),
    State('nav_selection', 'data'),
    prevent_initial_call = True
)
def display_nav(structure, selected_concept):
    print('structure', structure)
    parent_path = '-'.join(selected_concept[:-1])
    parent_text = structure[parent_path].get('text', '')
    sibling_ids = structure[parent_path]['children']
    out_children = [html.H3(parent_text, id = {'path' : parent_path, 'nav' : 'parent'})]
    for sibling_path in sibling_ids:
        sibling = html.H4(structure[sibling_path]['text'], id = {'path' : sibling_path, 'nav' : 'sibling'})
        out_children.append(sibling)
        for child_path in structure[sibling_path]['children']:
            child = html.H5(structure[child_path]['text'], id = {'path' : child_path, 'nav' : 'child'})
            out_children.append(child)
    return out_children
        
if __name__ == '__main__':
	app.run(debug=True)