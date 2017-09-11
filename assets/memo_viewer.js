$(function(){

    // --------- basic functions ---------
    function promote(cur_state, state_list) {
        var i = state_list.indexOf(cur_state);
        i = Math.min(i + 1, state_list.length - 1);
        return state_list[i];
    }
    function demote(cur_state, state_list) {
        var i = state_list.indexOf(cur_state);
        i = Math.max(i - 1, 0);
        return state_list[i];
    }
    // --------- basic functions ---------

    var Delta = Quill.import('delta');
    var quill = new Quill('#quill-container', {
        modules: {
            toolbar: false,
            keyboard: true
        },
        scrollingContainer: '#quill-container',
        placeholder: 'Empty...',
        theme: 'bubble'
    });

    // get data
    var org_sum = decodeURI($('#data').data("summary"));
    if (org_sum.length > 0) {
        quill.setContents(JSON.parse(org_sum));
    }

    quill.enable(false)

});
