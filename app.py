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

root_concept = {'' : []}

nav_section = html.Div([
    dcc.Store(id = 'nav_selection'),
    dcc.Store(id = 'concept_data', data = root_concept),
    dcc.Store(id = 'add_mode'),
    dcc.Store(id = 'concepts_unselected'),
    dcc.Store(id = 'last_concept_click'),

    html.Div(
        cyto.Cytoscape(
            id = 'concept_network',
            layout = {'name' : network_layout},
            elements = [],
            stylesheet = network_stylesheet(),
            style = {'width': '100%', 'height' : '50vh'}
        )
    ),
    # dcc.Markdown('#### Questions'),
    html.Div(id = 'quiz')
])


def text_form(form_type):
    return dbc.Form(
        dmc.Textarea(id = {'input' : 'input', 'form' : form_type}, autosize = True, value = test_text),
        id = {'form' : form_type}, style = {'padding': 3, 'background-color' : '#f8f9fa'},
        prevent_default_on_submit=True
    )
    
app.layout = dbc.Row([
    dbc.Col(nav_section),
    dbc.Col([
        dcc.Markdown(id = 'selected_concept_label'),
        html.Div(select_something_section(root_concept), id = 'concept_details_section'),
        dcc.Store('last_category_type', data = 'Supersets'),
        dcc.Store('property_path', data = {'parent': '', 'property_path' : []}),
        
        # html.Br(),
        # dcc.Markdown('Mode'),
        # dbc.RadioItems(options = ['add', 'move', 'delete'], value = 'add', id = 'mode', inline = True),

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