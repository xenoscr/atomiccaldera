function addAbilities() {
	restRequest('PUT', {"index": "ac_ability"}, addAbilitiesCallback);
}

function addAbilitiesCallback(data) {
	alert(data);
}

function populateTacticAbilities(exploits){
    let parent = $('#ability-profile');
    clearAbilityDossier();
    $(parent).find('#ability-test').empty().append("<option disabled='disabled' selected>Select ability</option>");

    let tactic = $(parent).find('#ability-tactic-filter').find(":selected").data('tactic');
    exploits.forEach(function(ability) {
        if(tactic == ability.tactic)
            appendAbilityToList(tactic, ability);
    });
    $('#ability-property-filter').css('opacity',0.5);
    $('#ability-tactic-filter').css('opacity',1.0);
}

function appendAbilityToList(tactic, value) {
    $('#ability-profile').find('#ability-test').append($("<option></option>")
        .attr("value",value['name'])
        .attr("ability_id",value['ability_id'])
        .data("tactic", tactic)
        .data("technique", value['technique'])
        .data("name", value['name'])
        .data("description", value['description'])
        .data("executor", value['executor'])
        .data("command",value['command'])
        .data("cleanup", value['cleanup'])
        .text(value['name'] +' ('+value['platform']+')'));
}

function clearAbilityDossier(){
    $('#ability-profile .ability-table tr:last td:input,ol').each(function(){
        $(this).val('');
        $(this).empty();
    });
}

function loadAbility() {
    let parent = $('#ability-profile');
    clearAbilityDossier();

    let chosen = $('#ability-test option:selected');
    $(parent).find('#ability-id').val($(chosen).attr('ability_id'));
    $(parent).find('#ability-name').val($(chosen).data('name'));
    $(parent).find('#ability-executor').val($(chosen).data('executor'));
    $(parent).find('#ability-tactic').val($(chosen).data('tactic'));
    $(parent).find('#ability-technique-id').val($(chosen).data('technique'));
    $(parent).find('#ability-technique-name').val($(chosen).data('attack_name'));
    $(parent).find('#ability-description').val($(chosen).data('description'));
    $(parent).find('#ability-command').html(atob($(chosen).data('command')));
    $(parent).find('#ability-cleanup').val(atob($(chosen).data('cleanup')));

    for(let k in $(chosen).data('parser')) {
        $(parent).find('#ability-postconditions').append('<li>'+$(chosen).data('parser')[k].property+'</li>');
        $(parent).find('#ability-fact-name').val($(chosen).data('parser')[k].fact);
        $(parent).find('#ability-fact-regex').val($(chosen).data('parser')[k].regex);
    }
    let requirements = buildRequirements($(chosen).data('command'));
    for(let k in requirements) {
        $(parent).find('#ability-preconditions').append('<li>'+requirements[k]+'</li>');
    }
}

function buildRequirements(encodedTest){
    let matchedRequirements = atob(encodedTest).match(/#{([^}]+)}/g);
    if(matchedRequirements) {
        matchedRequirements = matchedRequirements.filter(function(e) { return e !== '#{server}' });
        matchedRequirements = matchedRequirements.filter(function(e) { return e !== '#{group}' });
        matchedRequirements = matchedRequirements.filter(function(e) { return e !== '#{files}' });
        matchedRequirements = [...new Set(matchedRequirements)];
        return matchedRequirements.map(function(val){
           return val.replace(/[#{}]/g, "");
        });
    }
    return [];
}
