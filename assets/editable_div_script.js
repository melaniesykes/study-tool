window.dash_clientside = window.dash_clientside || {};

window.dash_clientside.clientside = {
    get_edited_content: function(trigger, element_id) {
        if (!(typeof element_id === 'string' || element_id instanceof String)) {
            element_id = JSON.stringify(element_id, Object.keys(element_id).sort());
        };
        var el = document.getElementById(element_id)
        var content = el.innerText
        return content
    }
}