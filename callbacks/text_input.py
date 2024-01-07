from dash import Output, Input, State, MATCH, ALL, ClientsideFunction, clientside_callback

# clientside_callback(
#     ClientsideFunction(namespace='clientside', function_name='get_edited_content'),
#     Output({'input' : 'input', 'form' : MATCH}, 'value'),
#     Input({'format_button' : ALL, 'form' : MATCH}, 'n_clicks'),
#     State({'input' : 'input', 'form' : MATCH}, 'id'),
# )