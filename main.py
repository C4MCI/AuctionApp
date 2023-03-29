from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import redis
from typing import Dict
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.status import HTTP_200_OK
from fastapi import HTTPException
import datetime
import json
import random
import math
from bson import json_util


app = FastAPI()
redis = redis.Redis(host="redis", port="6379", decode_responses=True)


origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://0.0.0.0",
    "http://0.0.0.0:8000",
    "http://localhost:5173",
    "http://0.0.0.0:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class User(BaseModel):
    id: str
    username: str
    email: str
    password: str



def create_auct_items(id, url):
    null = None
    r = random.randint(1, 100)
    min_price = random.randint(5000, 20000)
    random_item = {
        "id": id,
        'bidder_id': null,
        'item_name': f'Painting number {r}',
        'item_description': f'Description for painting number {r}',
        'min_price': min_price,
        'price_step': math.floor(min_price / 10),
        'bid': null,
        'start': json.dumps(datetime.datetime.now().astimezone().isoformat()),
        'ends': null,
        'completed': False,
        'url': url
    }
    
    redis.set(str(id), json.dumps(random_item))


url_list = ['https://t4.ftcdn.net/jpg/05/52/46/69/360_F_552466931_ofmluvRbBIJfPBDofWFvHTv1IEm6fx8h.jpg', 'https://i.guim.co.uk/img/media/b88d8f13523271d145004c15ee8b208a34e271af/0_388_2982_1789/master/2982.jpg?width=700&quality=85&auto=format&fit=max&s=a793e4f0ae755a8816b579f32ef5cf15', 'https://t3.ftcdn.net/jpg/05/42/91/52/360_F_542915248_rsKAgYvH4sSo0Lq7Ia38iTdgFFl3nrDw.jpg']
for i in range(3):
    create_auct_items(i, url_list[i])


def getRegisterId():
    if not redis.get('registerid'):
        registerId = 0
    else:
        registerId = redis.get('registerid')

    registerId = int(registerId)
    registerId += 1
    redis.set('registerid', registerId)
    return registerId


class AuctionConnectionManager:
    def __init__(self):
        self.auction_connections: Dict[any, list] = {}

    async def connect(self, websocket : WebSocket, auction_id):
        await websocket.accept()
        item_found = json.loads(redis.get(str(auction_id)))
        if (item_found['ends'] and datetime.datetime.fromisoformat(json.loads(item_found['ends'])) < datetime.datetime.now().astimezone()) or item_found['completed'] == True:
            item_found['completed'] = True
            await self.send_personal_message('The auction is already finished!', websocket)
            await self.send_personal_message(f"{item_found['item_name']} was sold for {item_found['bid']} to bidder #{item_found['bidder_id']}", websocket)
            await self.send_personal_message("", websocket, json_data={"completed": True})
            redis.set(str(auction_id), json.dumps(item_found))
            return
        
        curr_bid = item_found['bid']
        if curr_bid:
            await self.send_personal_message('The auction has already started!', websocket, curr_bid)


        if not self.auction_connections.get(auction_id):
            self.auction_connections[auction_id] = []
            
        self.auction_connections[auction_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, auction_id):
        self.auction_connections[auction_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket,
                                    cur_price=None, json_data=None):
        await websocket.send_text(message)
        if cur_price:
            await websocket.send_json({'new_price': cur_price})
        if json_data:
            await websocket.send_json({'json_data': json_data})

    async def broadcast(self, message: str, auction_id: int, new_price=None, ends=None):
        for connection in self.auction_connections.get(auction_id):
            await connection.send_text(message)
            payload = {}
            if new_price:
                payload = {'new_price': new_price}
            if ends:
                payload.update(ends=ends)
            if payload.keys():
                await connection.send_json(payload)


manager = AuctionConnectionManager()


@app.get('/auction/{id}', status_code=HTTP_200_OK)
async def auction(id: int):
    auction_item = json.loads(redis.get(str(id)))
    return {'item': auction_item}


@app.get('/auctions', status_code=HTTP_200_OK)
async def auctions():
    auction_items = [json.loads(redis.get(str(i))) for i in range(3)]
    return auction_items

@app.post('/register')
async def register(user: User):
    if redis.get(user.email):
        raise HTTPException(status_code=400, detail="User with this email already exists")
    
    user.id = str(getRegisterId())
    redis.set(user.email, user.json())
    return {"detail": "Registration successful"}

@app.post('/login')
async def login(user: User):
    if not redis.get(user.email):
        raise HTTPException(status_code=400, detail="User with this email not exists. Please register first.")
    
    if json.loads(redis.get(user.email))['password'] != user.password:
        raise HTTPException(status_code=400, detail=f"{json.loads(redis.get(user.email))['password']}\n\n\n {user.password}")
    
    return {
        'id' : json.loads(redis.get(user.email))['id'],
        'username' : json.loads(redis.get(user.email))['username']}
    
    
    




@app.websocket('/auction/{id}/ws/{participant_id}')
async def auction(websocket: WebSocket, id: int, participant_id: int):
    await manager.connect(websocket, id)
    try:
        while True:
            data = await websocket.receive_json()
            item = json.loads(redis.get(str(id)))
            step = item['price_step'] | 0
            current_bid = item['bid'] or 0
            min_new_bid = current_bid + step if current_bid != item['min_price'] else current_bid
            new_bid = data.get('bid')

            if not new_bid:
                continue
            if participant_id == item['bidder_id'] or not new_bid > current_bid:
                continue
            if item['min_price'] <= new_bid >= min_new_bid:
                item['bid'] = new_bid
                item['bidder_id'] = participant_id
                item['ends'] = json.dumps((datetime.datetime.now().astimezone() + datetime.timedelta(seconds=60)).isoformat())
                redis.set(str(id), json.dumps(item))
                await manager.broadcast(f'Participant {participant_id} has bid ${item["bid"]}', auction_id=id, new_price=new_bid, ends=item['ends'])

    except WebSocketDisconnect:
        await manager.disconnect(websocket, id)
        await manager.broadcast(f'Participant {participant_id} has left the auction.', auction_id=id)







@app.get('/')
def hello():
    return 'Hello'

