import dash     # need Dash version 2.9.0 or higher
from dash import dcc, html, callback, Output, Input, State, ctx, ALL, MATCH, no_update
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


# https://github.com/plotly/dash/releases

load_dotenv()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 


def section(label):
    return dbc.Row([
        dbc.Col(dbc.Button(label, id = {'section_button' : label})),
        dbc.Col(html.Div(id = {'section_content' : label}))
    ])
    
app.layout = html.Div([
    dcc.Markdown(id = {'index' : 'main_label'}),
    dcc.Store(data = 'Labels', id = 'mode'),
    section('Labels'),
    section('Categories'),
    section('Properties'),
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
    Output('mode', 'data'),
    Input({'section_button' : ALL}, 'n_clicks'),
    prevent_initial_call = True
)
def update_mode(trigger):
    out_mode = no_update
    button = ctx.triggered_id.get('section_button', None)
    if button:
        out_mode = button
    return out_mode

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
    State('mode', 'data'),
    prevent_initial_call = True
)
def add_to_section(trigger, is_active, buttons, mode):
    print(ctx.triggered_prop_ids)
    print([button for button, i_a in zip(buttons, is_active) if i_a])
    raise PreventUpdate


if __name__ == '__main__':
	app.run(debug=True)