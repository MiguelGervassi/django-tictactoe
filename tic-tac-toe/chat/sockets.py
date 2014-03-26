import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
import random 
from random import shuffle


@namespace('/chat')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    nicknames = []
    grid= range(1,9)
    player_spaces=[]
    ai_spaces=[]
    turn=0

    def initialize(self):
        self.logger = logging.getLogger("socketio.chat")
        self.log("Socketio session started")
        
    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
    def on_join(self, room):
        self.room = room
        self.join(room)
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
          self.log("AI turn")
          ai_position = random.choice(self.grid)
          self.broadcast_event('ai_move', ai_position, self.socket.session['ai_mark'])
          # self.grid.remove(int(ai_position))
          self.ai_spaces.append(int(ai_position))
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
        self.grid = range(1,9)
        del self.player_spaces[:]
        del self.ai_spaces[:]

    def on_move(self, position):
        #player_move
        self.turn=self.turn+1
        self.log(self.turn)
        self.log('You have moved to' + str(position))
        self.broadcast_event('player_move', position, self.socket.session['player_mark'])
        # self.grid.remove(int(position))
        self.player_spaces.append(int(position))
        print 'player spaces are '
        for s in self.player_spaces:
            print s

        grid = self.grid
        ai_position = random.choice(grid)
        
        #ai move
        self.log('AI has moved' + str(ai_position))
        self.broadcast_event('ai_move', ai_position, self.socket.session['ai_mark'])
        # self.grid.remove(int(ai_position))
        self.ai_spaces.append(int(ai_position))
        
        print 'ai spaces are'
        for s in self.ai_spaces:
            print s
 

        print 'free spaces are'
        for s in self.grid:
            print s

        full_grid = range(1,9)
        win=''

        # if 1 in self.player_spaces:
        #     for x in 2:
        #         if(set([1,x*2,(x*(1+x))+1]).issubset( self.player_spaces )):
        #             break # found winner
        # if 5 in self.player_spaces:
        #     for x in 4:
        #         if(set([x,5,(full_grid.length-x)]).issubset( self.player_spaces )):
        #             break #found winner
        # if 9 in self.player_spaces:
        #     for x in 2:
        #         if(set([9,9-(x*2),9-((x*(1+x))+1).issubset( self.player_spaces )):
        #             break # found winner


                


        # self.broadcast_event('check_win', ai_spaces, player_spaces)
        
        #your turn
        self.log("Your turn")
        if self.turn >= 3:
            #check if player wins
            player_win = self.check_winner(self.player_spaces)
            self.log(player_win)
            ai_win = self.check_winner(self.ai_spaces)
            self.log(ai_win)
            
            if(player_win):
                self.log("Player Wins")
                self.on_reset()
            elif(ai_win):
                self.log("AI Wins")
                self.on_reset()
            
            # if(!ai_win && !player_win): check for tie


        return True


    def check_winner(self, spaces):
        win = False
        if 1 in spaces:
            for x in range(1,2):
                if(set([1,x*2,(x*(1+x))+1]).issubset( spaces )):
                    self.log("Winner is ")
                    win = True
                    # break # found winner
        if 5 in spaces:
            for x in range(1,4):
                if(set([x,5,(10-x)]).issubset( spaces )):
                    # break #found winner
                    self.log("Winner is ")
                    win = True
        if 9 in spaces:
            for x in range(1,2):
                if(set([9,10-(x*2),10-((x*(1+x))+1)]).issubset( spaces )):
                    self.log("Winner is ")
                    win = True# break # found winner
        return win


