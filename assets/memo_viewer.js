$(function(){

    var SIZES = ['small', false, 'large', 'huge'];
    var cur_shown = 0;
    var last_range = 0;
    var server = $("#data").data("server");
    var port = $("#data").data("port");
    var paperid = $("#data").data("paperid");

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

    var paper_id = location.href.split('/');
    var paper_id = paper_id[paper_id.length-1];
    console.log('Paper ID: ' + paper_id.toString());

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
    var org_sum = decodeURI($('#data').text());
    if (org_sum.length > 16) {
        quill.setContents(JSON.parse(org_sum));
    }

    quill.enable(false)

});
