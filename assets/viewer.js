$(function(){

    var id2info = {};
    var quill;
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
    function update_editor(paper_id) {
        var summary = decodeURI(id2info[paper_id]['summary']);
        if (summary.length > 0) {
            quill.setContents(JSON.parse(summary));
        } else {
            quill.setContents(JSON.parse('{}'));
        }
        var title = decodeURI(id2info[paper_id]['title']);
        $('#title').text(title);
        $('#title').attr('href', id2info[paper_id]['url']);
    }
    // --------- basic functions ---------

    var Delta = Quill.import('delta');
    quill = new Quill('#quill-container', {
        modules: {
            toolbar: false,
            keyboard: true
        },
        scrollingContainer: '#quill-container',
        placeholder: 'Empty...',
        theme: 'bubble'
    });
    quill.enable(false);


    $('a.note').each(function(i, elem) {
        $(elem).click(function(event){
            event.preventDefault();
            var paper_id = $(this).data('paperid').toString();
            if (paper_id in id2info) {
                update_editor(paper_id);
            } else {
                $.ajax({
                    url: './load/' + paper_id,
                    type: 'POST',
                    dataType: 'json',
                    timeout: 5000,
                }).done(function(data) {
                    id2info[paper_id] = data;
                    update_editor(paper_id);
                }).fail(function(jqXHR, textStatus, errorThrown) {
                    console.log(jqXHR);
                    console.log(textStatus);
                    console.log(errorThrown);
                    alert('search: failure');
                });
            }
        });
        if (i == 0) $(elem).trigger('click');
    });

    $('#searchbtn').click(function(event){
        event.preventDefault();
        var query = $('#searchinput').val();
        if (query.length > 0) window.location.href = '/?q=' + encodeURI(query);
        else window.location.href = '/';
    });

});
