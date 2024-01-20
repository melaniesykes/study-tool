from dash import dcc, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import uuid

from dash.exceptions import PreventUpdate

def button_section(text, section, split_type):
    if split_type == 'words':
        delimiter = ' '
        suffix = ''
    else:
        delimiter = suffix = '.'
    words = text.split(delimiter) if isinstance(text, str) else [t.replace(delimiter, '') for t in text]
    words = [word.strip() + suffix for word in words if word]
    buttons = dbc.Checklist(
        id = {'form' : section, 'format' : split_type},
        className='btn-group',
        options = [{'label' : word, 'value' : n} for n, word in enumerate(words)],
        inputClassName='btn-check',
        labelClassName='btn btn-light',
        labelCheckedClassName='active',
        name = section
    )

    section_content = [
        html.Div(buttons, className='radio-group'),
        dcc.Store(
            id = {'form' : section, 'store' : 'last_clicked'},
        )
    ]
    return section_content


@callback(
    Output({'form' : 'recent_sentence'}, 'children', allow_duplicate=True),
    Input({'form' : 'sentences', 'format' : 'sentences', 'text_button' : ALL}, 'n_clicks'),
    State({'form' : 'sentences', 'format' : 'sentences', 'text_button' : ALL}, 'id'),
    State({'form' : 'sentences', 'format' : 'sentences', 'text_button' : ALL}, 'children'),
    prevent_initial_call = True
)
def break_down_recent_sentence(n_clicks, sentence_buttons, sentences):
    out_buttons = no_update
    trigger = ctx.triggered_id
    if trigger:
        trigger_index = sentence_buttons.index(trigger)
        sentence = sentences[trigger_index]
        out_buttons = button_section(sentence, 'recent_sentence', 'words')
    return out_buttons

@callback(
    Output({'form' : MATCH}, 'children', allow_duplicate=True),
    Input({'form' : MATCH, 'component' : 'input_tabs'} , 'active_tab'),
    State({'form' : MATCH, 'format' : ALL, 'text_button' : ALL}, 'children'),
	State({'form' : MATCH, 'input' : ALL}, 'value'),
    prevent_initial_call = True
)
def switch_form_format(trigger, button_text, input_text):
    out_buttons = no_update
    form = ctx.triggered_id.get('form', None)
    active_tab = trigger.get('format_button')
    
    text = None
    if button_text:
        text = ' '.join(button_text)
    elif input_text:
        text = input_text[0]

    if (active_tab == 'text'):
        out_buttons = dmc.Textarea(id = {'input' : 'input', 'form' : form}, value = text, autosize = True)
    elif active_tab in ('words', 'sentences'):
        if text:
            out_buttons = button_section(text, form, active_tab)

    return out_buttons

@callback(
    Output({'form' : MATCH}, 'children', allow_duplicate=True),
    Output({'form' : MATCH, 'form_dummy' : 'form_dummy'}, 'data'),
    Output({'form' : MATCH, 'store' : 'last_clicked'}, 'data'),
    Output({'form' : MATCH, 'format' : ALL}, 'value'),
    Input({'form' : MATCH, 'format' : ALL}, 'value'),
    State({'form' : MATCH, 'format' : ALL}, 'options'),
    State({'form' : MATCH, 'store' : 'last_clicked'}, 'data'),
    State({'section_tabs' : ALL}, 'active_tab'),
    State('mode', 'value'),
    State('last_category_type', 'data'),
    prevent_initial_call = True
)
def new_concept_step_1(button_number, buttons, last_clicked, selected_section, mode, category_tab):
    out_buttons = out_content = out_last_clicked = no_update
    out_value = [no_update]
    trigger = ctx.triggered_id

    if trigger and button_number:
        button_number = button_number[0]
        if (selected_section == ['Categories']):
            selected_section = category_tab
        else:
            selected_section = selected_section[0] if selected_section else None

        start, end = None, None
        if button_number:
            if len(button_number) == 1:
                out_last_clicked = button_number[0]
            else:
                start, end = sorted(button_number)
                out_last_clicked = None
                out_value = [[]]
        else:
            start, end = last_clicked, last_clicked
        if (start is not None) and (end is not None):

            selected_text = ' '.join([button['label'] for button in buttons[0][start: end + 1]])
            if mode in ('add', 'move'):
                out_content = [selected_section, selected_text]
            if mode in ('delete', 'move'):
                non_selected_text = [button['label'] for button in buttons[0][:start]]
                non_selected_text.extend([button['label'] for button in buttons[0][end + 1:]])
                out_buttons = button_section(non_selected_text, ctx.triggered_id['form'], 'words')
    else:
        raise PreventUpdate

    return out_buttons, out_content, out_last_clicked, out_value


def blank_concept(parent, concept_id, concept_name):
    return {
        'id' : concept_id,
        'parent' : parent, # parent concept, not necessarily same as parent node
        'text' : concept_name,
        'Labels' : [],
        'supersets' : dict(),
        'subsets' : dict(),
        'Properties' : [],
    }

@callback(
    Output('concept_data', 'data', allow_duplicate = True),
    Output('concept_network', 'elements'),
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    Input('add_mode', 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    State('nav_selection', 'data'),
    State('concept_data', 'data'),
    prevent_initial_call = True
)
def new_concept_step_2(form_update, add_mode, form_update_ids, nav_selection, concept_data):
    trigger = ctx.triggered_id
    out_data = out_network = out_selection_id = no_update

    if trigger:
        if trigger == 'add_mode':
            # if add_category == 'Supersets':
            #     parent = selection_id
            #     child = nav_selection
            #     out_concept_data[selection_id]['subsets'][child] = 'explicit'
            #     out_concept_data[child]['supersets'][parent] = 'reverse'
            #     for concept in concept_data[child]['subsets']:
            #         out_concept_data[selection_id]['subsets'][concept] = 'implicit'
            #         out_concept_data[concept]['supersets'][parent] = 'implicit'
            # else:
            #     parent = nav_selection
            #     child = selection_id
            #     if add_category == 'Subsets':
            #         out_concept_data[selection_id]['supersets'][parent] = 'explicit'
            #         out_concept_data[parent]['subsets'][child] = 'reverse'
            #         for concept in concept_data[parent]['supersets']:
            #             out_concept_data[concept]['subsets'][child] = 'implicit'
            #             out_concept_data[selection_id]['supersets'][concept] = 'implicit'
            #     else:
            #         out_concept_data[parent][add_category].append(child) 
            # out_concept_data[selection_id]
            [selected_section, selection_id] = add_mode
            new_concept = concept_data[selection_id]

        else:
            update_index = form_update_ids.index(trigger)
            [selected_section, selected_text] = form_update[update_index]
            selected_text = selected_text.replace(',', '').replace('.', '')

            out_selection_id = selection_id = str(uuid.uuid4())
            new_concept = blank_concept(nav_selection, selection_id, selected_text)

        out_data = Patch()        
        if selected_section is None:
            parent = ''
            out_data[parent].append(selection_id)
        elif selected_section == 'Supersets':
            parent = selection_id
            child = nav_selection
            new_concept['subsets'][child] = 'explicit'
            out_data[child]['supersets'][parent] = 'reverse'
            for concept in concept_data[child]['subsets']:
                new_concept['subsets'][concept] = 'implicit'
                out_data[concept]['supersets'][parent] = 'implicit'
        else:
            parent = nav_selection
            child = selection_id
            if selected_section == 'Subsets':
                new_concept['supersets'][parent] = 'explicit'
                out_data[parent]['subsets'][child] = 'reverse'
                for concept in concept_data[parent]['supersets']:
                    out_data[concept]['subsets'][child] = 'implicit'
                    new_concept['supersets'][concept] = 'implicit'
            else:
                out_data[parent][selected_section].append(child) 
        out_data[selection_id] = new_concept        
    
        out_network = Patch()

        if trigger != 'add_mode':
            out_network.append({
                'data' : {'id' : selection_id, 'label' : selected_text}, 
                'position': {'x': 0, 'y': 0}
            })                                               
        if parent:
            out_network.append({'data': {'source': child, 'target': parent}})
    else:
        raise PreventUpdate
    return out_data, out_network