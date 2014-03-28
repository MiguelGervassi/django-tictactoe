// socket.io specific code
var socket = io.connect("/chat");
var player_spaces = [];
var ai_spaces = [];

socket.on('connect', function () {
    $('#chat').addClass('connected');
    socket.emit('join', window.room); 
    socket.emit('start_game');
});

socket.on('announcement', function (msg) {
    $('#lines').append($('<p>').append($('<em>').text(msg)));
});

socket.on('nicknames', function (nicknames) {
    $('#nicknames').empty().append($('<span>Online: </span>'));
    for (var i in nicknames) {
	  $('#nicknames').append($('<b>').text(nicknames[i]));
    }
});

socket.on('player_move', function(position, mark) {
    if(mark=="X"){
        $('#'+position).html("<img src='static/images/X.png' class='myimageclass'>");
        $('#'+position).unbind("click");
    }else{
        $('#'+position).html("<img src='static/images/O.png' class='myimageclass'>");
        $('#'+position).unbind("click");
    }        
});


socket.on('ai_move', function(position, mark) {
    if(mark=="X"){
        $('#'+position).html("<img src='static/images/X.png' class='myimageclass'>");
        $('#'+position).unbind("click");
    }else{
        $('#'+position).html("<img src='static/images/O.png' class='myimageclass'>");
        $('#'+position).unbind("click");
}


});

socket.on('disable_board', function() {
    $("#tic-tac-toe").find("table,td").unbind("click");
});


socket.on('display_win_message', function(message) {
    $('#display_win_message').html("<h1 style='color:green;'>"+message+"</h1>");
});





// socket.on('ai_move', ailogic);

// function ai_logic(position, mark) {
//     ai_spaces.push(position)
//     $('#'+position).parent().html(mark);
// }

    


socket.on('msg_to_room', message);

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
    $('#set-nickname').submit(function (ev) {
        socket.emit('nickname', $('#nick').val(), function (set) {
            if (set) {
                clear();
                return $('#chat').addClass('nickname-set');
            }
            $('#nickname-err').css('visibility', 'visible');
        });
        return false;
    });

    $('#send-message').submit(function () {
	    message('me', $('#message').val());
	    socket.emit('user message', $('#message').val());
	    clear();
	    $('#lines').get(0).scrollTop = 10000000;
	    return false;
    });


   $(".position").click(function(){
        socket.emit('move', this.id); //id of button is position on grid
        return false;
    });

   $(".start_btn").click(function(){
        socket.emit('start_game'); //id of button is position on grid
        return false;
    });


    $(".reset_btn").click(function(e){ 
        location.reload();
    // $.ajax({
    //     url: '{% url "room" %}',
    //     success: function(data) {
    //         $("#canvas").html(data);
    //     }
    //   });
    });


    function clear () {
        $('#message').val('').focus();
    };


});
