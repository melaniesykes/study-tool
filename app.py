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
	dbc.Button('Words', id = {'button' : 'words'}),
	dbc.Button('Sentences', id = {'button' : 'sentences'}),
	dbc.Button('Text', id = {'button' : 'text'}),
	dbc.Form(dcc.Input(id = {'text' : 'text'}), id = 'form')
	
])

def button_section(text, delimiter):
    words = text.split(delimiter)
    suffix = delimiter if delimiter == '.' else ''
    section_content = []
    for n, word in enumerate(words):
        if word:
            section_content.append(
                dbc.Button(
                    id = {'text_button' : n},
                    children = word + suffix, 
                    type = 'button',
                    outline = True,
                    color = 'primary'
                )
            )
    section_content.append(
        dbc.Button(
            id = {'submit_button' : n},
            children = 'SUBMIT', 
            color = 'secondary'
        )
    )
    return section_content

@callback(
    Output({'text_button' : ALL}, 'color'),
    Output({'text_button' : ALL}, 'disabled'),
    Output('section', 'data'),
    Input({'section_button' : ALL}, 'n_clicks'),
    State({'text_button' : ALL}, 'children'),
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
    Output('form', 'children'),
    Input({'button' : ALL}, 'n_clicks'),
    State({'text_button' : ALL}, 'children'),
	State({'text' : ALL}, 'value'),
    prevent_initial_call = True
)
def switch_form_format(trigger, button_text, input_text):
    out_buttons = no_update
    button = ctx.triggered_id.get('button', None)
    text = None
    if input_text:
        text = input_text[0]
    elif button_text:
        text = ' '.join(button_text)
    if text:
        if button == 'words':
            out_buttons = button_section(text, ' ')
        elif button == 'sentences':
            out_buttons = button_section(text, '.')
        elif button == 'text':
            out_buttons = dcc.Input(text, id = {'text' : 'text'})

    return out_buttons

@callback(
    Output({'text_button' : MATCH}, 'active', allow_duplicate=True),
    Input({'text_button' : MATCH}, 'n_clicks'),
    State({'text_button' : MATCH}, 'active'),
    prevent_initial_call = True
)
def activate_text_button(trigger, is_active):
    out_active = no_update
    if ctx.triggered:
        out_active = not is_active
    return out_active

@callback(
    Output({'text_button' : ALL}, 'active', allow_duplicate=True),
    Output({'section_content' : ALL}, 'children'),
    Input('form', 'n_submit'),
    State({'text_button' : ALL}, 'active'),
    State({'text_button' : ALL}, 'children'),
    State('section', 'data'),
    State({'section_content' : ALL}, 'id'),
    State('form', 'n_submit_timestamp'),
    prevent_initial_call = True
)
def add_to_section(trigger, is_active, buttons, mode, sections, submit_time):
    if ctx.triggered_id:
        out_active = [False for button in is_active]
        out_content = [no_update for section in sections]
        selected_text = [button for button, i_a in zip(buttons, is_active) if i_a]
        selected_text = ' '.join(selected_text)
        mode_index = sections.index({'section_content' : mode})
        out_mode_content = Patch()
        out_mode_content.append(dbc.Button(selected_text, id = {'section' : mode, 't' : submit_time}))
        out_content[mode_index] = out_mode_content
    else:
        raise PreventUpdate
    return out_active, out_content        


if __name__ == '__main__':
	app.run(debug=True)