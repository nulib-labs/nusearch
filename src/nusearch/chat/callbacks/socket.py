from typing import Any, Dict, List, Optional
from json.decoder import JSONDecodeError
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages.tool import ToolMessage
from langchain_core.outputs import LLMResult

import ast
import json

import logging

logger = logging.getLogger(__name__)

def deserialize_input(input_str):
    try:
        return ast.literal_eval(input_str)
    except (ValueError, SyntaxError):
        try:
            return json.loads(input_str)
        except JSONDecodeError:
            return input_str
    
class SocketCallbackHandler(BaseCallbackHandler):
    def __init__(self, consumer):
        self.consumer = consumer
        logger.info(f"SocketCallbackHandler initialized with consumer: {self.consumer}")

    async def on_llm_start(self, serialized: dict[str, Any], prompts: list[str], metadata: Optional[dict[str, Any]] = None, **kwargs: Dict[str, Any]):
        logger.info(f"[{self.consumer.ref}] on_llm_start called with serialized: {serialized}, prompts: {prompts}, metadata: {metadata}")
        await self.consumer.send(text_data=json.dumps({"response": str(serialized), "callback": "on_llm_start"}))

    async def on_llm_new_token(self, token: str, **kwargs: Dict[str, Any]):
        if token != "":
            logger.info(f"[{self.consumer.ref}] on_llm_new_token called with token: {token}")
            await self.consumer.send(text_data=json.dumps({"response": token, "callback": "on_llm_new_token"}))
    
    async def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        logger.info(f"on_tool_start called")
        input = deserialize_input(input_str)
        logger.info(f"[{self.consumer.ref}] on_tool_start called with serialized: {serialized}, input: {input}")
        await self.consumer.send(text_data=json.dumps({"response": str(serialized), "callback": "on_tool_start"}))

    async def on_tool_end(self, output: Any, **kwargs: Any):
        logger.info(f"[{self.consumer.ref}] on_tool_end called with output: {output}")
        await self.consumer.send(text_data=json.dumps({"response": str(output), "callback": "on_tool_end"}))
    
    async def on_agent_action(self, action: Any, color: Optional[str] = None, **kwargs: Any) -> Any:
        logger.info(f"[{self.consumer.ref}] on_agent_action called with action: {action}, color: {color}")
        await self.consumer.send(text_data=json.dumps({"response": str(action), "callback": "on_agent_action"}))

    async def on_agent_finish(self, finish, **kwargs):
        logger.info(f"[{self.consumer.ref}] on_agent_finish called with finish: {finish}")
        await self.consumer.send(text_data=json.dumps({"response": str(finish), "callback": "on_agent_finish"}))

    async def on_llm_end(self, response: LLMResult, **kwargs: Dict[str, Any]):
        logger.info(f"[{self.consumer.ref}] on_llm_end called with response: {response}")
        await self.consumer.send(text_data=json.dumps({"response": str(response), "callback": "on_llm_end"}))
