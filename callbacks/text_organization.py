from dash import dcc, callback, Output, Input, State, ctx, ALL, MATCH, Patch, no_update, html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import uuid
from dash_extensions import EventListener

from dash.exceptions import PreventUpdate

def button_section(text, section, split_type):
    if split_type == 'words':
        delimiter = ' '
        suffix = ''
    else:
        delimiter = suffix = '.'
    words = text.split(delimiter) if isinstance(text, str) else [t.replace(delimiter, '') for t in text]
    words = [word.strip() + suffix for word in words if word]
    events = [
        {'event': 'click', 'props': ['type']}, # support auxclick, mousedown, mouseup?
        # {'event': 'keydown', 'props': ['type', 'key', 'altKey', 'ctrlKey', 'shiftKey']},
        {'event': 'dblclick', 'props' : ['type']}
    ]
    section_content = [
        EventListener(
            dbc.RadioItems(
                id = {'form' : section, 'format' : split_type},
                className='btn-group',
                options = [{'label' : word, 'value' : n} for n, word in enumerate(words)],
                inputClassName='btn-check',
                labelClassName='btn btn-light',
                labelCheckedClassName='active',
                name = section
            ),
            events = events,
            logging = True,
            id = {'form' : section, 'format' : split_type, 'component' : 'event_listener'}
        ),
        dcc.Store(
            id = {'form' : section, 'format' : split_type, 'component' : 'last_two_clicks'},
            data = [None, None]
        )
    ]

    return section_content


@callback(
    Output({'form' : 'recent_sentence'}, 'children', allow_duplicate=True),
    Input('current_sentence', 'data'),
    State('sentences', 'data'),
    prevent_initial_call = True
)
def break_down_recent_sentence(selected_sentence_index, sentences):
    out_buttons = no_update
    trigger = ctx.triggered_id
    if trigger:
        sentence = sentences[selected_sentence_index] + '.'
        out_buttons = button_section(sentence, 'recent_sentence', 'words')
    return out_buttons

@callback(
    Output('current_sentence', 'data'),
    Input({'form' : ALL, 'format' : 'sentences'}, 'value'),
    Input('sentences', 'data'),
    prevent_initial_call = True
)
def choose_sentence(selected_sentence, sentences):
    out_current_sentence = no_update
    trigger = ctx.triggered_id
    if trigger:
        out_current_sentence = 0
        if (trigger != 'sentences') and selected_sentence and selected_sentence[0]:
            out_current_sentence = selected_sentence[0]

    return out_current_sentence

@callback(
    Output({'form' : 'sentences'}, 'children', allow_duplicate=True),
    Output('sentences', 'data'),
    Input({'form' : 'sentences', 'component' : 'input_tabs'} , 'active_tab'),
    State({'form' : 'sentences', 'input' : ALL}, 'value'),
    State('sentences', 'data'),
    prevent_initial_call = True
)
def store_text(trigger, input_text, sentences):
    out_buttons = out_sentences = no_update
    form = ctx.triggered_id.get('form', None)
    active_tab = trigger.get('format_button')
    
    if input_text:
        text = input_text[0]
        out_sentences = [t.strip() for t in input_text[0].split('.') if t]
    else:
        text = '. '.join([sentence for sentence in sentences])        

    if (active_tab == 'text'):
        out_buttons = dmc.Textarea(id = {'input' : 'input', 'form' : form}, value = text, autosize = True)
    elif active_tab in ('words', 'sentences'):
        if text:
            out_buttons = button_section(text, form, active_tab)

    return out_buttons, out_sentences

@callback(
    Output({'form' : MATCH, 'form_dummy' : 'form_dummy'}, 'data'),
    Output({'form' : MATCH, 'format' : ALL}, 'value'),
    Output({'form' : MATCH, 'format' : ALL}, 'options'),
    Output({'form' : MATCH, 'format' : ALL, 'component' : 'last_two_clicks'}, 'data'),
    Input({'form' : MATCH, 'format' : ALL, 'component' : 'event_listener'}, 'n_events'),
    State({'form' : MATCH, 'format' : ALL}, 'value'),
    State({'form' : MATCH, 'format' : ALL, 'component' : 'last_two_clicks'}, 'data'),
    State({'form' : MATCH, 'format' : ALL, 'component' : 'event_listener'}, 'event'),
    State({'form' : MATCH, 'format' : ALL}, 'options'),
    State({'tabs' : ALL, 'tab_type' : 'section'}, 'active_tab'),
    # State('mode', 'value'),
    State('last_category_type', 'data'),
    State({'add_label_button' : ALL}, 'active'),
    prevent_initial_call = True
)
def new_concept_step_1(n_events, selections, last_two_clicks, event, buttons, selected_section, category_tab, add_label_mode):
    trigger = ctx.triggered_id
    if (not (trigger and selections)) or (not selections[0]):
        raise PreventUpdate

    out_content = no_update
    out_selections = [no_update]
    out_buttons = [no_update]
    out_last_two_clicks = [no_update]
    
    event = event[0]['type'] if event[0] else None
    selections = selections[0]
    last_two_clicks = last_two_clicks[0]

    if event == 'click':
        if selections == last_two_clicks[-1]:
            out_selections = [[]]
            selections = None
        out_last_two_clicks = [[last_two_clicks[-1], selections]]

    elif event == 'dblclick':
        if add_label_mode and add_label_mode[0]:
            selected_section = 'Labels'
        elif (selected_section == ['Categories']):
            selected_section = category_tab
        else:
            selected_section = selected_section[0] if selected_section else None

        click1, click2 = last_two_clicks
        if click1 and click2:
            start, end = sorted(last_two_clicks)
        elif click2:
            start = end = click2
        out_last_two_clicks = [[None, None]]
        out_selections = [[]]

        selected_text = ' '.join([button['label'] for button in buttons[0][start: end + 1]])
        # remove non-alphanumeric characters from beginning and end while avoiding regex
        n = 0
        for n, c in enumerate(selected_text):
            if c.isalnum():
                break
        selected_text = selected_text[n:]
        n = 0
        for n, c in enumerate(reversed(selected_text)):
            if c.isalnum():
                break
        if n != 0:
            selected_text = selected_text[:-n]
        mode = 'add' # TODO bring back mode
        if mode in ('add', 'move'):
            out_content = [selected_section, selected_text]
        if mode in ('delete', 'move'):
            non_selected_text = [button['label'] for button in buttons[0][:start]]
            non_selected_text.extend([button['label'] for button in buttons[0][end + 1:]])
            out_buttons = button_section(non_selected_text, ctx.triggered_id['form'], 'words')

    return out_content, out_selections, out_buttons, out_last_two_clicks


def blank_concept(concept_name, selected_section, source):
    return {
        'text' : concept_name,
        'Labels' : [],
        'is_property' : selected_section in ('Properties', 'sourced_property'),
        'supersets' : dict(),
        'subsets' : dict(),
        'Properties' : [], # properties which always appply
        'source_property' : source if (selected_section == 'sourced_property') else None,
        'related_properties' : dict() # {property-which-sometimes-applies : concept-it-applies-to}
    }

@callback(
    Output('concept_data', 'data'),
    Output('concept_network', 'elements'),
    Input({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'data'),
    Input('add_mode', 'data'),
    State({'form' : ALL, 'form_dummy' : 'form_dummy'}, 'id'),
    State('nav_selection', 'data'),
    State('concept_data', 'data'),
    State('property_path', 'data'),
    prevent_initial_call = True
)
def new_concept_step_2(form_update, add_mode, form_update_ids, nav_selection, concept_data, property_path):
    trigger = ctx.triggered_id
    if not trigger:
        raise PreventUpdate
        
    out_data = out_network = no_update

    if trigger == 'add_mode':
        [selected_section, selection_id] = add_mode
        new_concept = concept_data[selection_id]

    else:
        update_index = form_update_ids.index(trigger)
        [selected_section, selected_text] = form_update[update_index]
                    
        if property_path['property_path']:
            parent = nav_selection
            nav_selection = property_path['property_path'][-1]
            selected_section = 'sourced_property'
        
        if selected_section != 'Labels':
            selection_id = str(uuid.uuid4())
            new_concept = blank_concept(selected_text, selected_section, nav_selection)

    out_data = Patch()
    match selected_section:
        case None:    
            parent = ''
            out_data[parent].append(selection_id)
            selected_section = 'independent'
        case 'Labels':
            out_data[nav_selection]['Labels'].append(selected_text)        
        case 'Supersets':
            if concept_data[nav_selection]['is_property']: # a property belongs to a category
                selected_section = 'Properties'
                parent = nav_selection
                child = selection_id
                out_data[parent][selected_section].append(child)
            elif concept_data.get(selection_id, dict()).get('is_property', False):
                raise PreventUpdate # a category cannot belng to a property
            else:
                parent = selection_id
                child = nav_selection
                new_concept['subsets'][child] = 1
                out_data[child]['supersets'][parent] = 1
                # each subset of the child is also a subset of the parent
                for concept, distance in concept_data[child]['subsets'].items():
                    new_concept['subsets'][concept] = distance + 1
                    out_data[concept]['supersets'][parent] = distance + 1
                # each superset of the parent is also a superset of the child
                for concept, distance in new_concept['supersets'].items():
                    out_data[concept]['subsets'][child] = distance + 1
                    out_data[child]['supersets'][concept] = distance + 1
        case 'Subsets':
            parent = nav_selection
            child = selection_id
            if new_concept['is_property']:
                selected_section = 'Properties'
                parent = selection_id
                child = nav_selection
                out_data[parent][selected_section].append(child)
            else:
                new_concept['supersets'][parent] = 1
                out_data[parent]['subsets'][child] = 1
                # each superset of the parent has the child as a subset
                # each superset of the parent is also a superset of the child
                for concept, distance in concept_data[parent]['supersets'].items():
                    out_data[concept]['subsets'][child] = distance + 1
                    new_concept['supersets'][concept] = distance + 1
                # each subset of the child is also a subset of the parent
                # each subset of the child has the parent as a superset
                for concept, distance in new_concept['subsets'].items():
                    out_data[parent]['subsets'][concept] = distance + 1
                    out_data[concept]['supersets'][parent] = distance + 1
        case 'sourced_property':
            # pass
            source_parent = nav_selection
            child = selection_id
            out_data[source_parent]['related_properties'][child] = parent
            out_data[parent]['Properties'].append(child)
        case _:
            parent = nav_selection
            child = selection_id
            out_data[parent][selected_section].append(child)
                
    if selected_section != 'Labels':
        out_data[selection_id] = new_concept        

    if selected_section not in ('Labels', 'sourced_property'):
        out_data[selection_id] = new_concept        

        out_network = Patch()

        if trigger != 'add_mode':
            out_network.append({
                'data' : {
                    'id' : selection_id, 
                    'label' : selected_text,
                    'parent_concept' : parent
                }, 
                'position': {'x': 0, 'y': 0},
                'classes' : selected_section.lower()
            })                                           
        if parent:
            out_network.append({
                'data': {'source': child, 'target': parent},
                'classes' : selected_section.lower()
            })

    return out_data, out_network