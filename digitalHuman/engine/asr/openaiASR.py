# -*- coding: utf-8 -*-
'''
@File    :   baiduASR.py
@Author  :   一力辉 
'''

"""
API文档:
https://cloud.baidu.com/doc/SPEECH/s/qlcirqhz0
"""

from ..builder import ASREngines
from ..engineBase import BaseEngine
import io
from typing import List, Optional
from digitalHuman.utils import httpxAsyncClient
from digitalHuman.utils import AudioMessage, TextMessage
from digitalHuman.utils import logger
from digitalHuman.utils.audio import wavToMp3

__all__ = ["OpenAIAPI"]

@ASREngines.register("OpenAIAPI")
class OpenAIAPI(BaseEngine): 
    async def run(self, input: AudioMessage, **kwargs) -> Optional[TextMessage]:
        try: 
            API_URL = ""  # OpenAI API URL
            API_KEY = ""  # 你的 OpenAI API 密钥
            
            # 参数填充
            for paramter in self.parameters():
                if paramter['NAME'] == "OPENAI_API_URL":
                    API_URL = paramter['DEFAULT'] if paramter['NAME'] not in kwargs else kwargs[paramter['NAME']]
                if paramter['NAME'] == "OPENAI_API_KEY":
                    API_KEY = paramter['DEFAULT'] if paramter['NAME'] not in kwargs else kwargs[paramter['NAME']]

            headers = {
                'Authorization': f'Bearer {API_KEY}'
            }

            # 添加 model 参数
            data = {
                "model": "whisper-1"
            }

            files = {'file': ('userAudio', io.BytesIO(wavToMp3(input.data)), 'audio/mp3')}
            resp = await httpxAsyncClient.post(API_URL + "/audio/transcriptions", headers=headers, files=files, data=data)
            if resp.status_code != 200:
                raise RuntimeError(f"status_code: {resp.status_code}")
            
            logger.debug(f"[ASR] Engine response: {resp.json()}")
            result = resp.json()["text"]  # 根据 OpenAI 的响应格式调整
            message = TextMessage(data=result)
            return message
            
        except Exception as e:
            logger.error(f"[ASR] Engine run failed: {e}", exc_info=True)
            return None