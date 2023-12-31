from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
from .utils import *

class RoomConsumer(AsyncWebsocketConsumer):
    games = {}  # This will store the game state for all games

    async def connect(self):
        
        self.username = self.scope['url_route']['kwargs']['username']
        
        try:
            # Try to validate the UUID
            self.room_uuid = str(uuid.UUID(self.scope['url_route']['kwargs']['room_uuid']))
        except ValueError:
            # If invalid UUID, close the connection
            await self.close(code=4000)
            return # Validate the UUID
        
        self.room_group_name = f'game_{self.room_uuid}'
        
        # Initialize game if not already initialized
        if self.room_uuid not in RoomConsumer.games:
            RoomConsumer.games[self.room_uuid] = {
                'state':"lobby",
                'players': [],
                'story_teller':None,
                'last_message':None,
                
                # ... other game state variables
            }   

        all_players = RoomConsumer.games[self.room_uuid]['players']
        
        # Check if username is already taken in the room (replace with your own logic)
        for player in all_players:
            print(player)
            if(self.username == player['username']):
                await self.close(code=4001)
                return
    
        
        
        # Add player to the room
        RoomConsumer.games[self.room_uuid]['players'].append({
            'channel_name': self.channel_name,
            'username' : self.username,
            'role': None,
            'is_alive': True,
            'vote': None
        })
       
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Notify all players in the room about the new player
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'all_players' :RoomConsumer.games[self.room_uuid]['players']
            }
        )

    async def disconnect(self, close_code):
    # Remove player from room and notify others
        if RoomConsumer.games.get(self.room_uuid) and RoomConsumer.games[self.room_uuid]['state'] == "lobby":
            RoomConsumer.games[self.room_uuid]['players'] = [
                player for player in RoomConsumer.games[self.room_uuid]['players']
                if player['channel_name'] != self.channel_name
            ]

           
                # Notify other players in the room that a player has left
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_left',
                    'all_players': RoomConsumer.games[self.room_uuid]['players']
                }
            )
            
        # Check if the room is empty; if so, delete the game
        if len(RoomConsumer.games[self.room_uuid]['players']) == 0:
            del RoomConsumer.games[self.room_uuid]
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': data['type'],
                'message': data['message'],
                'channel_name': self.channel_name,
            }
        )
        self.games[self.room_uuid]['last_message'] = None

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
        
    async def player_joined(self, event):
        # Notify all connected clients that a new player has joined
        await self.send(text_data=json.dumps({
            'type' : 'player_change',
            'all_players' : event['all_players']
        }))
        
    async def player_left(self, event):
        # Notify all connected clients that a player has left
        await self.send(text_data=json.dumps({
            'type' : 'player_change',
            'all_players' : event['all_players']
        }))
        
    async def start_game(self, event):
        if(event['channel_name'] != self.games[self.room_uuid]['players'][0]['channel_name']):
            # Only the first player can start the game
            return
        
        if(self.games[self.room_uuid]['last_message'] != None):
            await self.send(text_data=json.dumps(
                self.games[self.room_uuid]['last_message']
            ))
            return
        
        self.games[self.room_uuid]['state'] = "Day"
        
        #asign roles to all players
        self.games[self.room_uuid]['players'] = assign_roles(self.games[self.room_uuid]['players'])
        
        self.games[self.room_uuid]['last_message'] = {
            'type' : 'game_state_change',
            'state' : self.games[self.room_uuid]['state'],
            'all_players' : self.games[self.room_uuid]['players'],
            'story_teller' : self.games[self.room_uuid]['story_teller']
        }

        # Notify all connected clients that the game has started
        await self.send(text_data=json.dumps(self.games[self.room_uuid]['last_message']))
        
    async def reset_game(self, event):
        if(event['channel_name'] != self.games[self.room_uuid]['players'][0]['channel_name']):
            # Only the first player can start the game
            return
        
        if(self.games[self.room_uuid]['last_message'] != None):
            await self.send(text_data=json.dumps(
                self.games[self.room_uuid]['last_message']
            ))
            return
        
        self.games[self.room_uuid]['state'] = "lobby"
        
        for player in self.games[self.room_uuid]['players']:
            player['role'] = None
            player['is_alive'] = True
            player['vote'] = None
        
        # Notify all connected clients that the game has been reset
        await self.send(text_data=json.dumps({
            'type' : 'game_state_change',
            'state' : self.games[self.room_uuid]['state'],
            'all_players' : self.games[self.room_uuid]['players'],
            'story_teller' : self.games[self.room_uuid]['story_teller']
        }))
    
    async def start_voting(self, event):
        if(event['channel_name'] != self.games[self.room_uuid]['players'][0]['channel_name']):
            # Only the first player can start the game
            return
        
        if(self.games[self.room_uuid]['last_message'] != None):
            await self.send(text_data=json.dumps(
                self.games[self.room_uuid]['last_message']
            ))
            return
        
        self.games[self.room_uuid]['state'] = "voting"
        
        #set last message
        self.games[self.room_uuid]['last_message'] = {
            'type' : 'game_state_change',
            'state' : self.games[self.room_uuid]['state'],
            'all_players' : self.games[self.room_uuid]['players'],
            'story_teller' : self.games[self.room_uuid]['story_teller']
        }
        # Notify all connected clients that voting has started
        await self.send(text_data=json.dumps(self.games[self.room_uuid]['last_message']))
        
    async def end_voting(self, event):
        
        if(self.games[self.room_uuid]['last_message'] != None):
            await self.send(text_data=json.dumps(
                self.games[self.room_uuid]['last_message']
            ))
            return
        

        if(self.games[self.room_uuid]['story_teller'] == None):
            if(event['channel_name'] != self.games[self.room_uuid]['players'][0]['channel_name']):
                return
            else:
                pass
        elif(event['channel_name'] != self.games[self.room_uuid]['players'][self.games[self.room_uuid]['story_teller']]['channel_name']):
            # Only the story teller can end the voting
            return
        
        
        if(self.games[self.room_uuid]['state'] != "Day"):
            return
        
        most_voted_index = decide_the_voted(self.games[self.room_uuid]['players'])
        
        new_state , player_out_index , next_state_message = get_next_state(self.games[self.room_uuid]['state'],self.games[self.room_uuid]['players'],most_voted_index)

        if(player_out_index != None):
            self.games[self.room_uuid]['players'][player_out_index]['is_alive'] = False
            #first player to die becomes the story teller
            if(self.games[self.room_uuid]['story_teller'] == None):
                self.games[self.room_uuid]['story_teller'] = player_out_index
          
        for player in self.games[self.room_uuid]['players']:
            player['vote'] = None
        
        self.games[self.room_uuid]['state'] = new_state

        self.games[self.room_uuid]['last_message'] = {
            'type' : 'game_state_change',
            'state' : new_state,
            'all_players' : self.games[self.room_uuid]['players'],
            'player_out' : player_out_index,
            'message' : next_state_message,
            'story_teller' : self.games[self.room_uuid]['story_teller']
             }

        # Notify all connected clients that voting has ended
        await self.send(text_data=json.dumps(self.games[self.room_uuid]['last_message']))
        
    async def end_night(self, event):


        if(self.games[self.room_uuid]['story_teller'] == None):
            if(event['channel_name'] != self.games[self.room_uuid]['players'][0]['channel_name']):
                return
            else:
                pass
        elif(event['channel_name'] != self.games[self.room_uuid]['players'][self.games[self.room_uuid]['story_teller']]['channel_name']):
            # Only the story teller can end the voting
            return
        
        if(self.games[self.room_uuid]['last_message'] != None):
            await self.send(text_data=json.dumps(
                self.games[self.room_uuid]['last_message']
            ))
            return
        
        if(self.games[self.room_uuid]['state'] != "Night"):
            return
        
        night_kill_index = event['message']
    
        new_state , player_out_index , next_state_message = get_next_state(self.games[self.room_uuid]['state'],self.games[self.room_uuid]['players'],night_kill_index)

        for player in self.games[self.room_uuid]['players']:
            player['vote'] = None
        
        self.games[self.room_uuid]['state'] = new_state

        self.games[self.room_uuid]['last_message'] = {
            'type' : 'game_state_change',
            'state' : new_state,
            'all_players' : self.games[self.room_uuid]['players'],
            'player_out' : player_out_index,
            'message' : next_state_message,
            'story_teller' : self.games[self.room_uuid]['story_teller']
             }

        # Notify all connected clients that voting has ended
        await self.send(text_data=json.dumps(self.games[self.room_uuid]['last_message']))

    async def vote_player(self,event):
        
        #skip if state is not voting
        if(self.games[self.room_uuid]['state'] != "Day"):
            return
        
        if(self.games[self.room_uuid]['last_message'] != None):
            await self.send(text_data=json.dumps(
                self.games[self.room_uuid]['last_message']
            ))
            return
        
        # Find the player who is being voted
        for player in self.games[self.room_uuid]['players']:
            if player['channel_name'] == event['channel_name']:
                player['vote'] = event['message']
                break
        
        #add last message
        self.games[self.room_uuid]['last_message'] = {
            'type' : 'player_change',
            'all_players' : self.games[self.room_uuid]['players']
        }

        # Notify all connected clients that a player has voted
        await self.send(text_data=json.dumps(self.games[self.room_uuid]['last_message']))
