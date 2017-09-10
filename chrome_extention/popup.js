$(function(){
    var port = localStorage['port'];
    var server = localStorage['server'];
    if (typeof port === "undefined") port = "8080";
    if (typeof server === "undefined") server = "0.0.0.0";

    chrome.tabs.getSelected(null, function(tab) {
        $('#pdfurl').val(tab.url);
    });

    $('#server').val(server);
    $('#port').val(port);
    $('#formpdf').attr('action', 'http://' + server + ':' + port + '/');

    $('#server').change(function(e){
        server = $('#server').val();
        $('#formpdf').attr('action', 'http://' + server + ':' + port + '/');
        localStorage['server'] = server;
    });
    $('#port').change(function(e){
        port = $('#port').val();
        $('#formpdf').attr('action', 'http://' + server + ':' + port + '/');
        localStorage['port'] = port;
    });

    var rules = {
        pdfurl: {required: true},
        pdftitle: {required: true},
        port: {required: true},
        server: {required: true}
    };
    $('#formpdf').validate({rules: rules});
});
