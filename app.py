import dash # need Dash version 2.9.0 or higher
from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks import *
import dash_mantine_components as dmc


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 

nav_section = html.Div([
    dcc.Store(id = 'nav_selection', data = []),
    dcc.Store(id = 'concept_data', data = {'' : blank_concept()}),
    html.Div(id = 'nav_display')
])

concept_section = html.Div([
    dcc.Markdown(id = 'selected_concept_label'),
    dbc.Card([
        dbc.CardHeader(
            dbc.Tabs([
                dbc.Tab(label = 'Labels', tab_id = 'Labels'),
                dbc.Tab(label = 'Categories', tab_id = 'Categories'),
                dbc.Tab(label = 'Properties', tab_id = 'Properties'),
            ], id = 'section_tabs')
        ),
        dbc.CardBody(id = 'section_content')
    ])
], id = 'concept_section')

def text_form(form_type):
    return dbc.Form(
        dmc.Textarea(id = {'input' : 'input', 'form' : form_type}, autosize = True),
        id = {'form' : form_type}
    )
    
app.layout = dbc.Row([
    dbc.Col(nav_section),
    dbc.Col([
        concept_section,
        
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

     
if __name__ == '__main__':
	app.run(debug=True)