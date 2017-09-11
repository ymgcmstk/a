$(function(){

    var SIZES = ['small', false, 'large', 'huge'];
    var cur_shown = 0;
    var last_range = 0;
    var server = $("#data").data("server");
    var port = $("#data").data("port");
    var paper_id = $("#data").data("paperid");
    var title = $("#title").text();
    var title_changed = false;
    var change, quill;
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
    function crop(image_i, x, y, w, h, targ_index) {
        var image_path = './crop/' + paper_id + '/' +
            parseInt(x).toString() + '/' +
            parseInt(y).toString() + '/' +
            parseInt(w).toString() + '/' +
            parseInt(h).toString() + '/' +
            parseInt(image_i).toString();
        quill.insertEmbed(targ_index, 'image', image_path);
    }
    function set_cropper(image_i) {
        var im_id = 'image' + image_i.toString();
        var cur_image = $('#img' + im_id);
        var x = 0; var y = 0; var w = 0; var h = 0;
        cur_image.cropper({
            movable: false, scalable: false,
            zoomable: false, rotatable: false,
            autoCrop: false,
            crop: function(e) {
                x = e.x;
                y = e.y;
                w = e.width;
                h = e.height;
            },
            cropend: function(e) {
                crop(image_i, x, y, w, h, last_range);
                $(this).cropper('clear');
            },
        });
    }
    function list_up_images(n_im) {
        $("#comment").remove();
        if (n_im == 0) {
            $("#images").remove();
        }
        for (var i = 0; i < n_im; i++) {
            var cur_url = 'http://' + server + ':' + port + '/static/data_' + paper_id + '/out-' + i.toString() + '.jpg'
            var cur_id = 'image' + i.toString();
            if (i == 0) $('#slider').append('<div id="' + cur_id + '"><img id="img' + cur_id + '" src="' + cur_url + '"></div>');
            else $('#slider').append('<div id="' + cur_id + '" style="display:none;"><img id="img' + cur_id + '" src="' + cur_url + '"></div>');
        }
        $('#button-prev').show();
        $('#button-next').show();

        $('#button-prev').click(function(){
            var cur_id = 'image' + cur_shown.toString();
            $('#' + cur_id).hide();
            cur_shown = (parseInt(n_images) + parseInt(cur_shown) - 1) % parseInt(n_images);
            cur_id = 'image' + cur_shown.toString();
            $('#' + cur_id).show(0);
        });

        $('#button-next').click(function(){
            var cur_id = 'image' + cur_shown.toString();
            $('#' + cur_id).hide();
            cur_shown = (parseInt(cur_shown) + 1) % parseInt(n_images);
            cur_id = 'image' + cur_shown.toString();
            $('#' + cur_id).show(0);
        });

        for (var i = 0; i < n_im; i++) {
            // var cur_id = 'image' + i.toString();
           set_cropper(i);
        }
    }
    function save() {
        if (change.length() > 0 || title_changed) {
            console.log('start saving...');
            $.post('./save/' + paper_id, {
                summary: encodeURI(JSON.stringify(quill.getContents())),
                title: title
            });
            change = new Delta();
            title_changed = false;
            console.log('Finish saving.');
        }
    }
    // --------- basic functions ---------

    var Delta = Quill.import('delta');
    quill = new Quill('#quill-container', {
        modules: {
            toolbar: false,
            imageDrop: true, // https://github.com/kensnyder/quill-image-drop-module
            keyboard: true,
            imageResize: {
                displaySize: true
            }
        },
        scrollingContainer: '#quill-container',
        placeholder: 'Take a note...',
        theme: 'bubble'
    });

    // get data
    var n_images = $("#data").data("nimages");
    var org_sum = decodeURI($('#data').data("summary"));
    if (org_sum.length > 0) {
        quill.setContents(JSON.parse(org_sum));
    }

    // Store accumulated changes
    change = new Delta();
    quill.on('text-change', function(delta) {
        change = change.compose(delta);
    });

    // Save periodically
    setInterval(save, 5*1000);

    if (n_images < 0) {
        $("#comment").text('Processing PDF...');
        var get_n_images = setInterval(function() {
            $.get('./n_images/' + paper_id, {
            }).done(function(data) {
                n_images = data;
                if (n_images >= 0) {
                    clearInterval(get_n_images);
                    list_up_images(n_images);
                }
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.log(jqXHR);
                console.log(textStatus);
                console.log(errorThrown);
                alert('get_n_images: failure');
                clearInterval(get_n_images);
            });
        }, 5*1000);
    } else {
        list_up_images(n_images);
    }

    // Check for unsaved data
    window.onbeforeunload = function() {
        if (change.length() > 0 || title_changed) {
            save();
            return 'There are unsaved changes. Are you sure you want to leave?';
        }
    }

    quill.on('selection-change', function(range, oldRange, source) {
        if (range) last_range = range.index;
    });

    // add shortcuts
    // # how to convert character, of which keyCode and charCode are not same, into proper character
    // 1. check its keyCode for onkeydown when it is typed: https://web-designer.cman.jp/javascript_ref/keyboard/keycode/
    // 2. check its proper character by checking String.fromCharCode(<keyCode>)

    // change size
    quill.keyboard.addBinding({
        key: '¾', // corresponds to '>'
        shortKey: true,
        shiftKey: true
    }, function(range, context) {
        var cur_format = this.quill.getFormat(range);
        var cur_size = false;
        if (cur_format['size'] != null) {
            cur_size = cur_format['size'];
        }
        this.quill.formatText(range, 'size', promote(cur_size, SIZES));
    });
    quill.keyboard.addBinding({
        key: '¼', // corresponds to '<'
        shortKey: true,
        shiftKey: true
    }, function(range, context) {
        var cur_format = this.quill.getFormat(range);
        var cur_size = false;
        if (cur_format['size'] != null) {
            cur_size = cur_format['size'];
        }
        this.quill.formatText(range, 'size', demote(cur_size, SIZES));
    });
    quill.keyboard.addBinding({
        key: 'S',
        shortKey: true
    }, function(range, context) {
        save();
    });

    $('#title').blur(function(e){
        title = $('#title').text();
        title_changed = true;
    });
});

// quill.insertEmbed(10, 'image', 'https://pbs.twimg.com/profile_images/378800000220029324/fe66faeca20115da8566e51d83447ead_400x400.jpeg');
