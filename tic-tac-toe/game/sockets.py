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
          # ai_position = int(random.choice(self.grid))
          ai_position = self.ai_logic()
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
        #check for winner if there is one, end game and declare winner
        if self.check_winner():
            return True

        #if list isn't empty then AI can move
        if self.grid: 
            #ai move
            # ai_position = int(random.choice(self.grid))
            self.turn=self.turn+1 #ai_turn
            ai_position = self.ai_logic()
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


            self.log("This is turn" + str(self.turn))
            #your turn
            self.log("Your turn")
        
        #check for winner add this to another method
        #original check for win
        if self.check_winner():
            return True
                
         #check if there's a threat
        threat = self.check_threat(self.player_spaces)
        ai_threat = self.check_threat(self.ai_spaces)

        if threat[0]:
            print 'player is a threat!'
            print threat[1]
        else:
            print 'player not a threat'


        if ai_threat[0]:
            print 'ai is a threat!'
            print ai_threat[1]
        else:
            print 'ai not a threat'

            
            # if(!ai_win && !player_win): check for tie
        return True


    # def update_spaces(self,position,spaces):
    #     if position in self.grid:
    #         self.grid.remove(position)
    #     else:
    #         print 'could not read value' + str(position)
    #     spaces.append(position)
    #     self.log('This is the position that is added ' + str(position))


    #ai logic
    def ai_logic(self):
        # check_threat
        ai_position = random.choice(self.grid)

        # turn 1 or 2 logic: turn one if middle space is not occupied by opponent, take it else take corner
        turn1 = [x for x in self.grid if x in [1,3,7,9]]
        if self.player_spaces and self.turn<=2:  
            if self.player_spaces[0]==5:
                ai_position = random.choice(turn1)
            else:
                ai_position = 5   
        elif self.turn <= 2:
            ai_position = 5    


        
        if self.turn == 3: # if its turn 3:  must choose corner or center if possible, guaranteed offensive/defensive 
            if self.player_spaces:
                # if self.player_spaces[len(self.player_spaces)-1] in [2,4,6,8]: #check if one these spaces were taken (2,4,6,8)
                turn3 = [x for x in self.grid if x in [1,3,5,7,9]]
                ai_position = random.choice(turn3)
                # if self.player_spaces[len(self.player_spaces)-1] in [1,3,7,9]: #check if one these spaces were taken (2,4,6,8)
                    # turn3 = [x for x in self.grid if x in [1,3,5,7,9]]
                    # ai_position = random.choice(turn3)
        
        if self.turn == 4:
            turn4 = [x for x in self.grid if x in [1,3,7,9]]
            if turn4:
                ai_position = random.choice(turn4)     

            # if(set([1,5]).issubset( set(self.player_spaces) )):
            # is_player_threat = self.check_threat(self.player_spaces)
            # if not is_player_threat:
            #     ai_position = is_player_threat[1]




            # if 1 and 5 in self.player_spaces:
            #     ai_position = 9
            # elif 3 and 5 in self.player_spaces:
            #     ai_position = 7
            # elif 7 and 5 in self.player_spaces:
            #     ai_position = 3
            # elif 5 and 9 in self.player_spaces:
            #     ai_position = 1




        #priority should happen after turn 3
        #check for threat or if win is possible
        is_player_threat = self.check_threat(self.player_spaces)
        ai_win = self.check_threat(self.ai_spaces)

        print 'checking threats...'
        if ai_win[0]:
            ai_position = ai_win[1]
            return ai_win[1]

        if is_player_threat[0]:
            ai_position = is_player_threat[1]
            return is_player_threat[1]



                 


        #defend
        # if self.turn == 4:
        #     if self.player_spaces:
        #         if self.player_spaces[len(self.player_spaces)-1] in


        # turn 2 logic
        # if(set([2,4,6,8]).issubset( set(self.player_spaces) )):
                
        #turn 3 check for threats or attack

        # if self.turn == 2:
            # if self.player_spaces[self.player_spaces.length-1]==:



        return ai_position



    def check_threat(self,spaces):
        threat_info = [False,0] #if threat, if there is second value should be what position it is 
        if self.player_spaces:
            for x in range(1,3):
                threat_info = self.check_threat_algo(spaces, 1,x*2,(x*(1+x))+1,threat_info)
                threat_info = self.check_threat_algo(spaces, 9,(10-(x*2)), (10-((x*(1+x))+1)),threat_info)
            # if 5 in self.player_spaces:
            for x in range(1,5):
                threat_info = self.check_threat_algo(spaces, x,5,(10-x),threat_info)                
        return threat_info

    def check_threat_algo(self,spaces,pos1,pos2,pos3,threat_info):
        if(set([pos1,pos2]).issubset( set(spaces) )):
            if pos3 in self.grid:
                threat_info[0] = True # threat is the boolean that tells you whether or not a threat is happening
                threat_info[1] = pos3
        if(set([pos1,pos3]).issubset( set(spaces) )):
            if pos2 in self.grid:
                threat_info[0] = True
                threat_info[1] = pos2
        if(set([pos2,pos3]).issubset( set(spaces) )):
            if pos1 in self.grid:
                threat_info[0] = True
                threat_info[1] = pos1
        return threat_info       


    # def check_win(self):


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


