import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
import random 
from random import shuffle


@namespace('/game')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    grid= range(1,10)
    player_spaces=[]
    ai_spaces=[]
    turn=0

    def initialize(self):
        self.logger = logging.getLogger("socketio.game")
        self.log("Socketio session started")
        self.on_reset()
        
    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
    def on_join(self):
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
        threat = self.check_immediate_threat(self.player_spaces)
        ai_threat = self.check_immediate_threat(self.ai_spaces)

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

    #ai logic
    def ai_logic(self):
        ai_position = random.choice(self.grid)
        if self.turn == 1:
            return ai_position

        if self.turn == 2:
            for x in [1,3,7,9]:
                if x in self.player_spaces:
                    ai_position = 5
                    return ai_position
                elif 5 in self.player_spaces:
                    ai_position = random.choice(self.free_spaces([1,3,7,9]))
                    return ai_position

            for x in [2,4,6,8]:
                if x in self.player_spaces:
                    if x == 2:
                        ai_position = random.choice(self.free_spaces([1,3,5]))
                        return ai_position
                    if x == 4:
                        ai_position = random.choice(self.free_spaces([1,7,5]))
                        return ai_position
                    if x == 6:
                        ai_position = random.choice(self.free_spaces([9,3,5]))
                        return ai_position
                    if x == 8:
                        ai_position = random.choice(self.free_spaces([9,7,5]))
                        return ai_position        
                   
        if self.turn == 3: # if its turn 3:  must choose corner or center if possible, guaranteed offensive/defensive 
            if self.player_spaces:
                # if self.player_spaces[len(self.player_spaces)-1] in [2,4,6,8]: #check if one these spaces were taken (2,4,6,8)
                turn3 = [x for x in self.grid if x in [1,3,5,7,9]]
                if 5 in turn3:
                    ai_position = 5
                    return ai_position
                else:
                    ai_position = random.choice(turn3)
                            
        if self.turn == 4: #turn 4, check for defense and attack
            turn4 = [x for x in self.grid if x in [1,3,7,9]]
            if turn4:
                #diagnol check, i believe this works now :)
                if 5 in self.grid:
                    ai_position = 5
                    return ai_position
                elif 5 in self.ai_spaces:
                    if (set([1,9]).issubset( set(self.player_spaces)) or set([3,7]).issubset( set(self.player_spaces))):
                        turn4 = [x for x in self.grid if x in [2,4,6,8]]     
                        ai_position = random.choice(turn4)
                else:
                   ai_position = random.choice(turn4)    

                # used to give ai more randomness
                # rand = [x for x in self.grid if x in [1,4,7]]
                # for x in [4,1]:
                #     if set([8,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position    
                # for x in [4,7]:
                #     if set([2,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position    

                # rand = [x for x in self.grid if x in [3,6,9]]
                # for x in [6,3]:
                #     if set([8,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position    
                # for x in [6,9]:
                #     if set([2,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position    
                
                # rand = [x for x in self.grid if x in [1,2,3]]
                # for x in [2,3]:
                #     if set([4,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)    
                # for x in [2,1]:
                #     if set([6,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position   

                # rand = [x for x in self.grid if x in [7,8,9]]
                # for x in [8,9]:
                #     if set([4,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position    
                # for x in [8,7]:
                #     if set([6,x]).issubset( self.player_spaces ):
                #         ai_position = random.choice(rand)
                #         return ai_position      

        is_player_threat = self.check_immediate_threat(self.player_spaces)
        ai_win = self.check_immediate_threat(self.ai_spaces)

        print 'checking threats...'
        if ai_win[0]:
            ai_position = ai_win[1]
            return ai_win[1]

        # if there is no immediate threat then on turn 4, check if there is a strategic threat
        if is_player_threat[0]:
            ai_position = is_player_threat[1]
            return is_player_threat[1]
        else:
            is_player_threat = self.check_strategic_threat(self.player_spaces)
            if is_player_threat[0]: #if there is a strategic threat then assign new ai_position
                ai_position = is_player_threat[1]
                return is_player_threat[1]
        return ai_position

    def free_spaces(self,custom_spaces): #check if the grid has the given spaces free
        return [x for x in self.grid if x in custom_spaces]

    def check_immediate_threat(self,spaces):
        threat_info = [False,0] #if threat, if there is second value should be what position it is 
        if self.player_spaces:
            for x in range(1,3):
                threat_info = self.check_threat_algo(spaces, 1,x*2,(x*(1+x))+1,threat_info)
                threat_info = self.check_threat_algo(spaces, 9,(10-(x*2)), (10-((x*(1+x))+1)),threat_info)
            for x in range(1,5):
                threat_info = self.check_threat_algo(spaces, x,5,(10-x),threat_info)                                                   
        return threat_info

    def check_strategic_threat(self,spaces):
        threat_info = [False,0]
        for x in [4,7,6,9]: #2
            if x == 4 or x == 7:
                threat_info = self.check_threat_algo(spaces,2,x,1,threat_info)               
                if threat_info[0]: return threat_info
            elif x == 6 or x == 9:
                threat_info = self.check_threat_algo(spaces,2,x,3,threat_info)
                if threat_info[0]: return threat_info                                    
        for x in [6,3,4,1]: #8
            if x == 6 or x == 3:
                threat_info = self.check_threat_algo(spaces,8,x,9,threat_info)
                if threat_info[0]: return threat_info               
            elif x == 4 or x == 1:
                threat_info = self.check_threat_algo(spaces,8,x,7,threat_info)
                if threat_info[0]: return threat_info                                    
        for x in [1,7]: #6
            if x == 1:
                threat_info = self.check_threat_algo(spaces,6,x,3,threat_info)
                if threat_info[0]: return threat_info               
            elif x == 7:
                threat_info = self.check_threat_algo(spaces,6,x,9,threat_info)
                if threat_info[0]: return threat_info                                    
        for x in [3,9]: #4
            if x == 3:
                threat_info = self.check_threat_algo(spaces,4,x,1,threat_info)
                if threat_info[0]: return threat_info               
            elif x == 9:
                threat_info = self.check_threat_algo(spaces,4,x,7,threat_info)
                if threat_info[0]: return threat_info                                    
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

    #check for winner
    def check_winner(self):
        if self.turn >= 3:
            player_win = self.check_winner_algo(self.player_spaces)
            self.log(player_win)
            ai_win = self.check_winner_algo(self.ai_spaces)
            self.log(ai_win)

            if(player_win):
                self.log("Player Wins")
                self.broadcast_event('display_win_message', "Player Wins");
                self.broadcast_event('disable_board')
                self.on_reset()
                return True
            elif(ai_win):
                self.log("AI Wins")
                self.broadcast_event('display_win_message', "AI Wins");
                self.broadcast_event('disable_board')
                self.on_reset()
                return True
            elif not self.grid and not ai_win and not player_win:
                self.log("Tie")
                self.broadcast_event('display_win_message', "Tie");
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


