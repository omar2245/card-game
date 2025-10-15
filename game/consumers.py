import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from .card_data import get_card_by_number, get_dice_effect

class GameConsumer(AsyncWebsocketConsumer):
    """處理即時遊戲通訊"""
    
    async def connect(self):
        """玩家連線"""
        self.room_id = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'game_{self.room_id}'
        
        # 從 query string 取得玩家名稱
        query_string = self.scope['query_string'].decode()
        self.player_name = 'Anonymous'
        if 'player=' in query_string:
            self.player_name = query_string.split('player=')[1].split('&')[0]
        
        # 加入房間群組
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # 通知其他玩家有人加入
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'player': self.player_name
            }
        )
    
    async def disconnect(self, close_code):
        """玩家離線"""
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_left',
                'player': self.player_name
            }
        )
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """接收玩家訊息"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'play_card':
                await self.handle_play_card(data)
            elif action == 'respond':
                await self.handle_respond(data)
            elif action == 'roll_dice':
                await self.handle_roll_dice(data)
            else:
                await self.send(json.dumps({
                    'error': '未知動作'
                }))
        
        except json.JSONDecodeError:
            await self.send(json.dumps({'error': '無效的 JSON'}))
    
    async def handle_play_card(self, data):
        """處理出牌"""
        player = data.get('player')
        card_number = data.get('card_number')  # 改用 card_number
        
        # 取得卡片資料
        card_data = get_card_by_number(card_number)
        if not card_data:
            await self.send(json.dumps({
                'error': f'找不到卡片：{card_number}'
            }))
            return
        
        # 判斷對手是誰
        target = 'PlayerB' if player == 'PlayerA' else 'PlayerA'
        
        # 廣播給所有玩家
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'card_played_event',
                'player': player,
                'card_number': card_number,
                'card_name': card_data['name'],
                'card_data': card_data,
                'target': target
            }
        )
    
    async def handle_roll_dice(self, data):
        """處理擲骰子"""
        player = data.get('player')
        card_number = data.get('card_number')
        
        # 取得卡片資料
        card_data = get_card_by_number(card_number)
        if not card_data or not card_data.get('requires_dice_roll'):
            await self.send(json.dumps({
                'error': '此卡片不需要擲骰子'
            }))
            return
        
        # 擲骰子
        dice_sides = card_data.get('dice_sides', 10)
        dice_result = random.randint(0, dice_sides - 1)  # 0 到 9
        
        # 取得對應效果
        effect = get_dice_effect(card_number, dice_result)
        
        # 廣播結果
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'dice_rolled_event',
                'player': player,
                'card_number': card_number,
                'card_name': card_data['name'],
                'dice_result': dice_result,
                'dice_sides': dice_sides,
                'effect': effect
            }
        )
    
    async def handle_respond(self, data):
        """處理回應"""
        player = data.get('player')
        response = data.get('response')
        card_number = data.get('card_number')
        card_name = data.get('card_name', 'Unknown')
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'action_resolved_event',
                'player': player,
                'response': response,
                'card_number': card_number,
                'card_name': card_name,
                'original_player': 'PlayerA' if player == 'PlayerB' else 'PlayerB'
            }
        )
    
    # ===== 群組事件處理器 =====
    
    async def player_joined(self, event):
        await self.send(json.dumps({
            'event': 'player_joined',
            'player': event['player']
        }))
    
    async def player_left(self, event):
        await self.send(json.dumps({
            'event': 'player_left',
            'player': event['player']
        }))
    
    async def card_played_event(self, event):
        await self.send(json.dumps({
            'event': 'card_played',
            'player': event['player'],
            'card_number': event['card_number'],
            'card_name': event['card_name'],
            'card_data': event['card_data'],
            'target': event['target']
        }))
    
    async def dice_rolled_event(self, event):
        await self.send(json.dumps({
            'event': 'dice_rolled',
            'player': event['player'],
            'card_number': event['card_number'],
            'card_name': event['card_name'],
            'dice_result': event['dice_result'],
            'dice_sides': event['dice_sides'],
            'effect': event['effect']
        }))
    
    async def action_resolved_event(self, event):
        await self.send(json.dumps({
            'event': 'action_resolved',
            'player': event['player'],
            'response': event['response'],
            'card_number': event.get('card_number'),
            'card_name': event.get('card_name', 'Unknown'),
            'original_player': event.get('original_player', '')
        }))