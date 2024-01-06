import dash     # need Dash version 2.9.0 or higher
from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


# https://github.com/plotly/dash/releases

load_dotenv()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 


def section(label):
    return dbc.Row([
        dbc.Col(dbc.Button(label, id = {'section_button' : label}), width = 1),
        dbc.Col(html.Div(id = {'section_content' : label}))
    ])

def text_form(form_type):
    return dbc.Form(
        dcc.Input(id = {'input' : 'input', 'form' : form_type}),
        id = {'form' : form_type}
    )


    
app.layout = html.Div([
    dcc.Markdown(id = {'index' : 'main_label'}),
    dcc.Store(data = 'Labels', id = 'section'),
    section('Labels'),
    section('Categories'),
    section('Properties'),
    html.Br(),
    dcc.Markdown('Mode'),
    dcc.Store(data = 'move', id = 'mode'),
    dbc.RadioItems(options = ['move', 'add', 'delete'], value = 'move'),
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

def button_section(text, section):
    if section == 'words':
        delimiter = ' '
        suffix = ''
    else:
        delimiter = suffix = '.'
    words = text.split(delimiter)
    section_content = []
    for n, word in enumerate(words):
        if word:
            section_content.append(
                dbc.Button(
                    id = {'form' : section, 'text_button' : n},
                    children = word + suffix, 
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
    Input({'form' : ALL, 'section_button' : ALL}, 'n_clicks'),
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
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    prevent_initial_call = True
)
def add_to_section(form_update, form_update_ids):
    trigger = ctx.triggered_id
    if trigger:
        update_index = form_update_ids.index(trigger)
        [mode, mode_index, selected_text, submit_time, n_sections] = form_update[update_index]
        selected_text = selected_text.replace(',', '').replace('.', '')
        out_mode_content = Patch()
        out_mode_content.append(dbc.Button(selected_text, id = {'section' : mode, 't' : submit_time}))
        out_content = [no_update for section in range(n_sections)]
        out_content[mode_index] = out_mode_content
    return out_content

@callback(
    Output({'form' : MATCH, 'form_dummy' : 'form_dummy'}, 'data'),
    Output({'form' : MATCH, 'text_button' : ALL}, 'active', allow_duplicate=True),
    Input({'form' : MATCH}, 'n_submit'),
    State({'form' : MATCH, 'text_button' : ALL}, 'active'),
    State({'form' : MATCH, 'text_button' : ALL}, 'children'),
    State('section', 'data'),
    State({'form' : MATCH}, 'n_submit_timestamp'),
    State({'section_content' : ALL}, 'id'),
    prevent_initial_call = True
)
def handle_submission(trigger, is_active, buttons, mode, submit_time, sections):
    if ctx.triggered_id:
        out_active = [False for button in is_active]
        selected_text = [button for button, i_a in zip(buttons, is_active) if i_a]
        selected_text = ' '.join(selected_text)
        mode_index = sections.index({'section_content' : mode})
        out_content = [mode, mode_index, selected_text, submit_time, len(sections)]
    else:
        raise PreventUpdate
    # raise PreventUpdate
    return out_content, out_active


if __name__ == '__main__':
	app.run(debug=True)