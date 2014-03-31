import logging

from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.sdjango import namespace
import random 
from random import shuffle

@namespace('/game')
class ChatNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    grid=range(1,10)
    player_spaces=[]
    ai_spaces=[]
    turn=0
    game_ended=False

    def initialize(self):
        self.logger = logging.getLogger("socketio.game")
        self.log("Socketio session started")
        self.on_reset()
        
    def log(self, message):
        self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
    
    # assign marks on start game and whoever is X goes first
    def on_start_game(self):
        arr = ['X','O']
        shuffle(arr)
        self.socket.session['player_mark'] = arr[0]
        self.socket.session['ai_mark'] = arr[1]
        mark = self.socket.session['player_mark']
        if mark == 'X':
          self.log("Your turn")
        else:
          self.log("AI turn")
          self.ai_move()
        return True    

    def on_reset(self):
        self.game_ended=False
        self.turn=0
        del self.grid[:]
        self.grid = (list(range(1,10)))
        del self.player_spaces[:]
        del self.ai_spaces[:]


    def on_move(self, position):
        #check if space occupied if it is, do not allow, if game ended do not allow any more moves
        position = int(position)
        if position not in self.grid or self.game_ended:
            return False

        #player_move
        self.player_move(position)
        
        #check for winner
        if self.check_winner():
            return True

        #ai_move
        self.ai_move()
        
        #check for winner
        if self.check_winner():
            return True
                
        #check if there's a threat
        # threat = self.check_immediate_threat(self.player_spaces)
        # ai_threat = self.check_immediate_threat(self.ai_spaces)

        # if threat[0]:
        #     print 'player is a threat!'
        #     print threat[1]
        # else:
        #     print 'player not a threat'


        # if ai_threat[0]:
        #     print 'ai is a threat!'
        #     print ai_threat[1]
        # else:
        #     print 'ai not a threat'

        return True

    # player moves 
    # turn increments, log position moved, broadcast move and show it on grid canvas
    # remove position from grid and add it to player_spaces
    def player_move(self,position):
        position = int(position)
        self.turn=self.turn+1
        self.log('You have moved to ' + str(position))
        self.broadcast_event('move', position, self.socket.session['player_mark'])
        if position in self.grid:
            self.grid.remove(position)
        self.player_spaces.append(position)
        self.log("AI turn")
        return True

    # ai moves
    # if there are still free spaces left turn increments, log position moved, broadcast move and show it on grid canvas
    # remove position from grid and add it to ai_spaces
    def ai_move(self):
        if self.grid: 
            self.turn=self.turn+1 #ai_turn
            ai_position = self.ai_logic()
            self.log('AI has moved to ' + str(ai_position))
            self.broadcast_event('move', ai_position, self.socket.session['ai_mark'])
            if ai_position in self.grid:
                self.grid.remove(ai_position)
            self.ai_spaces.append(ai_position)
            self.log("Your turn")
        return True

    #ai logic
    def ai_logic(self):
        ai_position = random.choice(self.grid)
        
        # turn 1
        # ai could be any position
        if self.turn == 1:
            return ai_position

        # turn 2 - turn that puts a stop to win setups
        # if player picks first move as corner
        if self.turn == 2:
            for x in [1,3,7,9]:
                # ai must be center if play picks center ai must pick corner
                if x in self.player_spaces:
                    ai_position = 5
                    return ai_position
                elif 5 in self.player_spaces:
                    ai_position = random.choice(self.free_spaces([1,3,7,9]))
                    return ai_position
            for x in [2,4,6,8]:
                # if player on even positions ai must be on position on top middle or below that player position
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
                   
        # turn 3
        # choose center position if possible
        # else choose randomly from free spaces (corners)
        if self.turn == 3:   
            if self.player_spaces:
                turn3 = self.free_spaces([1,3,5,7,9])
                if 5 in turn3:
                    ai_position = 5
                    return ai_position
                else:
                    ai_position = random.choice(turn3)
                           
        # turn 4 - offensive/defensive turn
        # choose center position if possible
        # check if diagnal corners have been chosen, if they have then defend against it by choosing even number
        # else choose from corners, odd numbers
        # check threats both immediate and strategic functions these methods will automatically defend against these moves 
        if self.turn == 4: 
            turn4 = self.free_spaces([1,3,7,9])
            if turn4:
                #diagnol check, i believe this works now :)
                if 5 in self.grid:
                    ai_position = 5
                    return ai_position
                elif 5 in self.ai_spaces:
                    if self.list_contains_list([1,9],self.player_spaces) or self.list_contains_list([3,7],self.player_spaces):
                        turn4 = self.free_spaces([2,4,6,8])     
                        ai_position = random.choice(turn4)
                else:
                   ai_position = random.choice(turn4)    

        is_player_threat = self.check_immediate_threat(self.player_spaces)
        ai_win = self.check_immediate_threat(self.ai_spaces)

        # print 'checking threats...'
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

    # immediate threats are like 1,2,3 or 1,5,9
    def check_immediate_threat(self,spaces):
        threat_info = [False,0] #if threat, if there is second value should be what position it is 
        if self.player_spaces:
            for x in range(1,3):
                threat_info = self.check_threat_algo(spaces, 1,x*2,(x*(1+x))+1,threat_info)
                threat_info = self.check_threat_algo(spaces, 9,(10-(x*2)), (10-((x*(1+x))+1)),threat_info)
            for x in range(1,5):
                threat_info = self.check_threat_algo(spaces, x,5,(10-x),threat_info)                                                   
        return threat_info

    # if there is no immediate threat check for strategic threat
    # strategic threats are 2,4 waiting to have a free space on 1 on your third turn
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

    #if third position provided is available on grid, then it is a threat!
    def check_threat_algo(self,spaces,pos1,pos2,pos3,threat_info):
        if self.list_contains_list([pos1,pos2],spaces):
            if pos3 in self.grid:
                threat_info[0] = True # threat is the boolean that tells you whether or not a threat is happening
                threat_info[1] = pos3
        if self.list_contains_list([pos1,pos3],spaces):
            if pos2 in self.grid:
                threat_info[0] = True
                threat_info[1] = pos2
        if self.list_contains_list([pos2,pos3],spaces):
            if pos1 in self.grid:
                threat_info[0] = True
                threat_info[1] = pos1                
        return threat_info       

    #check for winner
    def check_winner(self):
        if self.turn >= 3:
            player_win = self.check_winner_algo(self.player_spaces)
            ai_win = self.check_winner_algo(self.ai_spaces)
            
            if(player_win):
                self.log("Player Wins")
                self.broadcast_event('display_win_message', "Player Wins");
                self.game_ended=True
                return True
            elif(ai_win):
                self.log("AI Wins")
                self.broadcast_event('display_win_message', "AI Wins");
                self.game_ended=True
                return True
            elif not self.grid and not ai_win and not player_win:
                self.log("Tie")
                self.broadcast_event('display_win_message', "Tie");
                self.game_ended=True
                return True
        return False
    
    #check winner algorithm
    def check_winner_algo(self, spaces):
        win = False
        if 1 in spaces:
            for x in range(1,3):
                if self.list_contains_list([1,x*2,(x*(1+x))+1],spaces):
                    win = True
        if 5 in spaces:
            for x in range(1,5):
                if self.list_contains_list([x,5,(10-x)],spaces):
                    win = True
        if 9 in spaces:
            for x in range(1,3):
                if self.list_contains_list([ 9,(10-(x*2)),(10-((x*(1+x))+1))], spaces):
                    win = True # break # found winner
        return win

    # helper method to check if certain number pattern is in a list, example: [1,2] is in the player spaces (both must be in it)
    def list_contains_list(self,list1,list2):
        return set(list1).issubset( set(list2) )

    #helper method to check what spaces are available from grid
    def free_spaces(self,custom_spaces): #check if the grid has the given spaces free
        return [x for x in self.grid if x in custom_spaces]
