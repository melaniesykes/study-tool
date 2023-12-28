import dash     # need Dash version 2.9.0 or higher
from dash import dcc, html, callback, Output, Input, State, ctx, ALL, no_update
from dotenv import load_dotenv
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate


# https://github.com/plotly/dash/releases

load_dotenv()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 


store_id_info = {'type' : 'data', 'placeholder' : True}
app.layout = html.Div([
    dcc.Markdown(id = {'index' : 'main_label'}),
    dbc.Row(dbc.Col(dbc.Button('Labels', id = {'section_button' : 'labels'}))),
    dbc.Row(dbc.Col(dbc.Button('Categories', id = {'section_button' : 'categories'}))),
    dbc.Row(dbc.Col(dbc.Button('Properties', id = {'section_button' : 'properties'}))),
	dbc.Button('Words', id = {'button' : 'words'}),
	dbc.Button('Sentences', id = {'button' : 'sentences'}),
	dbc.Button('Text', id = {'button' : 'text'}),
	html.Div(dcc.Input(id = {'text' : 'text'}), id = 'buttons')
	
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
                    outline = True,
                    color = 'primary'
                )
            )
    return section_content

@callback(
    Output('buttons', 'children'),
    Input({'button' : ALL}, 'n_clicks'),
    State({'text_button' : ALL}, 'children'),
	State({'text' : ALL}, 'value'),
    prevent_initial_call = True
)
def load_add_fragrance_data(trigger, button_text, input_text):
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

if __name__ == '__main__':
	app.run(debug=True)