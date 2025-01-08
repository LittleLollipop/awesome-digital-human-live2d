# -*- coding: utf-8 -*-
'''
@File    :   difyAgnet.py
@Author  :   一力辉 
'''

from ..builder import AGENTS
from ..agentBase import BaseAgent
import re
import json
import time
from typing import List, Union
from digitalHuman.utils import httpxAsyncClient
from digitalHuman.utils import logger
from digitalHuman.utils import AudioMessage, TextMessage

__all__ = ["OlaresAgent"]


@AGENTS.register("OlaresAgent")
class OlaresAgent(BaseAgent):

    async def createConversation(self, streaming: bool, **kwargs) -> str:
        return "" + int(time.time())

    async def run(
        self, 
        input: Union[TextMessage, AudioMessage], 
        streaming: bool,
        **kwargs
    ):
        logger.debug(f"[AGENT] Engine run with input: {input.data}")
        try:
            if isinstance(input, AudioMessage):
                raise RuntimeError("OlaresAgent does not support AudioMessage input yet")
            # 参数校验
            for paramter in self.parameters():
                if paramter['NAME'] not in kwargs:
                    raise RuntimeError(f"Missing parameter: {paramter['NAME']}")
            API_URL = kwargs["OLARES_API_URL"]  # 使用 OLARES_API_URL
            logger.debug(f"[AGENT] Using API_URL: {API_URL}")  # 添加 API_URL 的日志输出

            conversation_id = kwargs.get("conversation_id", "")
            payload = {
                "inputs": {},
                "query": input.data,  # 仅使用 input.data
                "conversation_id": conversation_id,
                "files": []
            }

            # 发送请求
            response = await httpxAsyncClient.post(API_URL, json=payload)
            data = response.json()  # 直接解析 JSON 响应
            yield data.get('answer', "没有返回答案。")  # 返回答案，如果没有则返回默认消息

        except Exception as e:
            logger.error(f"[AGENT] Engine run failed: {e}", exc_info=True)
            yield "接口请求返回错误。"