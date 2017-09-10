$(function(){

    var SIZES = ['small', false, 'large', 'huge'];

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


    // --------- core ---------
    function clear_data() {
        $('#db').empty();
    }

    function list_up_images(n_im) {
        return;
        for (var i = 0; i < Math.min(n_im, 10); i++) {
            var id_str = i.toString();
            for (var i = 0; i < 3 - id_str.length; i++) {
                id_str = '0' + id_str;
            }
            // var cur_url = "../static/19_-" + id_str + ".png";
            $('#db').append('<img src="' + cur_url + '">');
        }
    }

    function get_values(keys) {
        var input_data = {keys: keys.join(",")};
        console.log(input_data);
        clear_data();
        $.ajax({
            url: './load',
            type: 'POST',
            dataType: 'json',
            data: input_data,
            timeout: 5000,
        }).done(function(data) {
            console.log(data);
            for (key in data) {
                $('#db').append('<div>key: ' + key + '</div>');
                $('#db').append('<div>value: ' + data[key] + '</div>');
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
            alert('search: failure');
        });
    }

    function update(input_data) {
        $.ajax({
            url: './save',
            type: 'POST',
            data: input_data,
            timeout: 5000
        }).done(function(data) { // console.log(data);
            var keys = [];
            for (key in input_data) {
                keys.push(key);
            }
            get_values(keys);
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            console.log(textStatus);
            console.log(errorThrown);
            alert('update: failure');
        });
    }
    // --------- core ---------

    // --------- bindings ---------
    $('#searchbtn').on('click', function() {
        if($('#skey').val() == null) {
            return;
        }
        get_values([$('#skey').val()]);
    });

    $('#updatebtn').on('click', function() {
        if($('#ukey').val() == null) {
            return;
        }
        if($('#uvalue').val() == null) {
            return;
        }
        var data = {};
        data[$('#ukey').val()] = $('#uvalue').val();
        update(data);
    });
    // --------- bindings ---------

});
