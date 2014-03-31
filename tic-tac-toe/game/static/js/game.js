// socket.io specific code
var socket = io.connect("/game");

socket.on('connect', function () {
    socket.emit('join'); 
    socket.emit('start_game');
});

socket.on('move', function(position, mark) {
    if(mark=="X"){
        $('#'+position).html("<div class='mark-x'></div>");
        // $('#'+position).unbind("click");
    }else{
        $('#'+position).html("<div class='mark-o'></div>");
        // $('#'+position).unbind("click");
    }        
});

socket.on('disable_board', function() {
    $(".position").unbind("click");
});

socket.on('enable_board', function() {
    $("#tic-tac-toe").find("table,td").bind("click");
});

socket.on('display_win_message', function(message) {
    $('#display_win_message').html("<h1 style='color:green;'>"+message+"</h1>");
});

socket.on('reconnect', function () {
    $('#lines').remove();
    message('System', 'Reconnected to the server');
});

socket.on('reconnecting', function () {
    message('System', 'Attempting to re-connect to the server');
});

socket.on('error', function (e) {
    message('System', e ? e : 'A unknown error occurred');
});

function message (from, msg) {
    $('#lines').append($('<p>').append($('<b>').text(from), msg));
}

// DOM manipulation
$(function () {
   $(".position").click(function(){
        socket.emit('move', this.id); //id of button is position on grid
        return false;
    });

   $(".start_btn").click(function(){
        socket.emit('start_game'); //id of button is position on grid
        return false;
    });

    $(".reset_btn").click(function(e){ 
        // location.reload();
        socket.emit('reset')
        socket.emit('start_game');
        $(".position").html("<div class='mark'></div>");
        $("#display_win_message").html("")
        // $(".position").bind("click");
         // $(".position").prop('disabled', false).removeClass('disabled');
    });

    function clear () {
        $('#message').val('').focus();
    };


});
