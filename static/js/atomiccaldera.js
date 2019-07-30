function restRequest(type, data, callback, endpoint='/plugin/atomiccaldera/rest') {
	$.ajax({
		url: endpoint,
		type: type,
		contentType: 'application/json',
		data: JSON.stringify(data),
		success: function(data) { callback(data); },
		error: function(xhr, ajaxOptions, throwError) { console.log(throwError); }
	});
}

function updateButtonState(selector, state) {
    (state === 'valid') ?
        $(selector).attr('class','button-success atomic-button') :
        $(selector).attr('class','button-notready atomic-button');
}

function updateNavButtonState(selector, state) {
    (state === 'valid') ?
        $(selector).attr('class','row-toolbar-button') :
        $(selector).attr('class','row-toolbar-button-notready row-toolbar-button');
}
