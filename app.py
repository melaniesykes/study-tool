import dash # need Dash version 2.9.0 or higher
from dash import dcc, html
import dash_bootstrap_components as dbc
from callbacks import *
import dash_mantine_components as dmc
import dash_cytoscape as cyto


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP]) 

server = app.server

with open('test_text.txt') as f:
      test_text = f.read()

network_layout = 'cose' # 'concentric'

nav_section = html.Div([
    dcc.Store(id = 'nav_selection', data = ''),
    dcc.Store(id = 'concept_data', data = {'' : blank_concept('', '', '')}),
    html.Div(
        cyto.Cytoscape(
            id = 'concept_network',
            layout = {'name' : network_layout},
            elements = [],
            stylesheet = [
                # Group selectors
                {
                    'selector': 'node',
                    'style': {
                        'content': 'data(label)',
                        'text-halign':'center',
                        'text-valign':'center',
                        'width':'label',
                        'height':'label',
                        'shape':'square'
                    }
                },
                {
                    'selector': 'edge',
                    'style': {
                        'source-arrow-shape': 'triangle',
                        'curve-style': 'bezier'
                }
            }
            ]
        )
    ),
    # dcc.Markdown('#### Questions'),
    html.Div(id = 'quiz')
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
        dmc.Textarea(id = {'input' : 'input', 'form' : form_type}, autosize = True, value = test_text),
        id = {'form' : form_type}, style = {'padding': 3, 'background-color' : '#f8f9fa'}
    )
    
app.layout = dbc.Row([
    dbc.Col(nav_section),
    dbc.Col([
        concept_section,
        dcc.Store('last_category_type', data = 'Subsets'),
        
        html.Br(),
        dcc.Markdown('Mode'),
        dbc.RadioItems(options = ['add', 'move', 'delete'], value = 'add', id = 'mode', inline = True),

        html.Br(),
        dbc.Card([
            dbc.CardHeader(
                dbc.Tabs(
                    children = [
                        dbc.Tab(label = 'Words', tab_id = {'format_button' : 'words', 'form' : 'recent_sentence'}),
                        dbc.Tab(label = 'Text', tab_id = {'format_button' : 'text', 'form' : 'recent_sentence'}),
                    ],
                    id = {'form' : 'recent_sentence', 'component' : 'input_tabs'} 
                )
            ),
            dbc.CardBody([
                dcc.Store({'form' : 'recent_sentence', 'form_dummy' : 'form_dummy'}),
                text_form('recent_sentence')
            ])
        ]),

        html.Br(),
        dbc.Card([
            dbc.CardHeader(
                dbc.Tabs(
                    children = [
                        dbc.Tab(label = 'Words', tab_id = {'format_button' : 'words', 'form' : 'sentences'}),
                        dbc.Tab(label = 'Sentences', tab_id = {'format_button' : 'sentences', 'form' : 'sentences'}),
                        dbc.Tab(label = 'Text', tab_id = {'format_button' : 'text', 'form' : 'sentences'})
                    ], 
                    id = {'form' : 'sentences', 'component' : 'input_tabs'},
                    active_tab = {'format_button' : 'text', 'form' : 'sentences'}
                )
            ),
            dbc.CardBody([
                dcc.Store({'form' : 'sentences', 'form_dummy' : 'form_dummy'}),
                text_form('sentences')
            ])
        ])
    ])
])

     
if __name__ == '__main__':
	app.run(debug=True)