import uuid
import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.agent import Agent
from chat.callbacks.socket import SocketCallbackHandler

logger = logging.getLogger(__name__)

connections = {}

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref = str(uuid.uuid4())
        self.agent = None

    async def connect(self):
        connections[self.ref] = self.ref
        logger.info(f"WebSocket connection attempting with ref: {self.ref}...")
        await self.accept()
        logger.info("WebSocket connection established successfully")
        await self.send(text_data=json.dumps({"ref": self.ref}))

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}")
        if hasattr(self, 'ref') and self.ref in connections:
            del connections[self.ref]

    async def receive(self, text_data):
        logger.info(f"Raw WebSocket data received: {text_data}")
        
        if not text_data:
            logger.error("Received empty text_data")
            await self.send(text_data=json.dumps({"error": "Empty message received"}))
            return

        try:
            text_data_json = json.loads(text_data)
            
            query = text_data_json.get("query")
            if query:
                if not self.agent:
                    self.agent = Agent(callbacks=[SocketCallbackHandler(consumer=self)])
                
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.agent.invoke(
                        {"messages": [{"role": "user", "content": query}]},
                        config={"configurable": {"thread_id": self.ref}}
                    )
                )

                for message in response["messages"]:
                    if hasattr(message, 'name') and hasattr(message, 'content'):
                        if message.name == "nul_search":
                            await self.send(text_data=json.dumps({"type": "nul_search", "message": json.loads(message.content)}))
                        elif message.name == "open_alex":
                            await self.send(text_data=json.dumps({"type": "open_alex", "message": json.loads(message.content)}))
                        elif message.name == "digital_collections":                    
                            await self.send(text_data=json.dumps({"type": "digital_collections", "message": json.loads(message.content)}))
                    elif hasattr(message, 'content') and isinstance(message.content, list):
                        for content_item in message.content:
                            if isinstance(content_item, dict) and 'text' in content_item:
                                await self.send(text_data=json.dumps({"message": content_item['text']}))
                    elif hasattr(message, 'content'):
                        await self.send(text_data=json.dumps({"message": json.loads(message.content)}))
            else:
                logger.warning("No query found in message")
                await self.send(text_data=json.dumps({"error": "No query provided"}))
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            await self.send(text_data=json.dumps({"error": f"Invalid JSON: {str(e)}"}))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            await self.send(text_data=json.dumps({"error": str(e)}))