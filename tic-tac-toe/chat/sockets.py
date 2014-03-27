import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
import random 
from random import shuffle


@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []
    grid= range(1,10)
    player_spaces=[]
    ai_spaces=[]
    turn=0

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")
        self.on_reset()
        
    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
    def on_join(self, room):
        self.room = room
        self.join(room)
        self.on_reset()
        return True
        
    def on_start_game(self):
        arr = ['X','O']
        shuffle(arr)
        self.socket.session['player_mark'] = arr[0]
        self.socket.session['ai_mark'] = arr[1]
        self.log(arr[0])
        self.log(arr[1])    
        mark = self.socket.session['player_mark']
        if mark == 'X':
          self.log("Your turn")
        else:
          self.turn=self.turn+1
          self.log("AI turn")
          ai_position = int(random.choice(self.grid))
          self.broadcast_event('ai_move', ai_position, self.socket.session['ai_mark'])
          
          if ai_position in self.grid:
            self.grid.remove(ai_position)
        
          self.ai_spaces.append(ai_position)
          self.log("Your turn")
        return True    

    def on_nickname(self, nickname):
        # self.log('Nickname: {0}'.format(nickname))
        # self.nicknames.append(nickname)
        # self.socket.session['nickname'] = nickname
        # self.broadcast_event('announcement', '%s has connected' % nickname)
        # self.broadcast_event('nicknames', self.nicknames)
        return True, nickname

    def recv_disconnect(self):
        # Remove nickname from the list.
        # self.log('Disconnected')
        # nickname = self.socket.session['nickname']
        # self.nicknames.remove(nickname)
        # self.broadcast_event('announcement', '%s has disconnected' % nickname)
        # self.broadcast_event('nicknames', self.nicknames)
        # self.disconnect(silent=True)
        return True

    def on_user_message(self, msg):
        self.log('User message: {0}'.format(msg))
        self.emit_to_room(self.room, 'msg_to_room',
            self.socket.session['nickname'], msg)
        return True

    def on_reset(self):
        del self.grid[:]
        self.grid = (list(range(1,10)))
        del self.player_spaces[:]
        del self.ai_spaces[:]

    def on_move(self, position):
        #player_move
        position = int(position)
        self.turn=self.turn+1
        self.log(self.turn)
        self.log('You have moved to' + str(position))
        self.broadcast_event('player_move', position, self.socket.session['player_mark'])
        if position in self.grid:
            self.grid.remove(position)
        self.player_spaces.append(position)
        print 'player spaces are '
        for s in self.player_spaces:
            print s

        #focus on this to check for error
        if self.check_winner():
            return True


        if self.grid: #if list not empty
            #ai move
            ai_position = int(random.choice(self.grid))
            self.log('AI has moved' + str(ai_position))
            self.broadcast_event('ai_move', ai_position, self.socket.session['ai_mark'])
            if ai_position in self.grid:
                self.grid.remove(ai_position)
            self.ai_spaces.append(ai_position)
            
            print 'ai spaces are'
            for s in self.ai_spaces:
                print s
     
            # free spaces
            print 'free spaces are'
            for s in self.grid:
                print s

            #your turn
            self.log("Your turn")
        
        #check for winner add this to another method
        #original check for win
        if self.check_winner():
            return True
                

            
            # if(!ai_win && !player_win): check for tie
        return True


    # def update_spaces(self,position,spaces):
    #     if position in self.grid:
    #         self.grid.remove(position)
    #     else:
    #         print 'could not read value' + str(position)
    #     spaces.append(position)
    #     self.log('This is the position that is added ' + str(position))

    #check for winner
    def check_winner(self):
        if self.turn >= 3:
            player_win = self.check_winner_algo(self.player_spaces)
            self.log(player_win)
            ai_win = self.check_winner_algo(self.ai_spaces)
            self.log(ai_win)

            if(player_win):
                self.log("Player Wins")
                self.broadcast_event('disable_board')
                self.on_reset()
                return True
            elif(ai_win):
                self.log("AI Wins")
                self.broadcast_event('disable_board')
                self.on_reset()
                return True
            elif not self.grid and not ai_win and not player_win:
                self.log("Tie")
                self.broadcast_event('disable_board')
                self.on_reset()
                return True
        return False
    
    #check winner algorithm
    def check_winner_algo(self, spaces):
        win = False
        if 1 in spaces:
            for x in range(1,3):
                if(set([1,x*2,(x*(1+x))+1]).issubset( set(spaces) )):
                    win = True
        if 5 in spaces:
            for x in range(1,5):
                if(set([x,5,(10-x)]).issubset( set(spaces) )):
                    win = True
        if 9 in spaces:
            for x in range(1,3):
                # self.log(str(9)+","+str(10-(x*2))+","+str(10-((x*(1+x))+1))+"\n")
                if(set([  9, (10-(x*2)), (10-((x*(1+x))+1))  ]).issubset( set(spaces) )):
                    win = True # break # found winner
        return win


