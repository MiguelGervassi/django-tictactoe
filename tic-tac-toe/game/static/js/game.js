// socket.io specific code
var socket = io.connect("/game");

socket.on('connect', function () {
    socket.emit('start_game');
});

socket.on('move', function(position, mark) {
    if(mark=="X"){
        $('#'+position).html("<div class='mark-x'></div>");
    }else{
        $('#'+position).html("<div class='mark-o'></div>");
    }        
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

// DOM manipulation
$(function () {
   $(".position").click(function(){
        socket.emit('move', this.id); //id of button is position on grid
        return false;
    });

    $(".reset_btn").click(function(e){ 
        // location.reload();
        socket.emit('reset')
        socket.emit('start_game');
        $(".position").html("<div class='mark'></div>");
        $("#display_win_message").html("")
    });
});
