# -*- coding: utf-8 -*-

from ..builder import TTSEngines
from ..engineBase import BaseEngine
import asyncio
from typing import Optional
from digitalHuman.utils import httpxAsyncClient
from digitalHuman.utils import logger
from digitalHuman.utils import TextMessage, AudioMessage, AudioFormatType
from digitalHuman.utils.audio import mp3ToWav

__all__ = ["OpenAIAPI"]

@TTSEngines.register("OpenAIAPI")
class OpenAIAPI(BaseEngine):
    def setup(self):
        super().setup()
        self.asyncLock = asyncio.Lock()

    async def run(self, input: TextMessage, **kwargs) -> Optional[AudioMessage]:
        try: 
            API_URL = ""  # OpenAI TTS API URL
            API_KEY = ""
            # 参数填充
            for paramter in self.parameters():
                if paramter['NAME'] == "OPENAI_API_URL":
                    API_URL = paramter['DEFAULT'] if paramter['NAME'] not in kwargs else kwargs[paramter['NAME']]
                if paramter['NAME'] == "OPENAI_API_KEY":
                    API_KEY = paramter['DEFAULT'] if paramter['NAME'] not in kwargs else kwargs[paramter['NAME']]

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'
            }
            payload = {
                "model": "tts-1",  # 使用 OpenAI 的 TTS 模型进行语音合成
                "input": input.data,  # 传入要合成的文本
                "voice": "alloy"  # 可以选择合适的声音类型
                # 移除不支持的 response_format 参数
            }

            logger.debug(f"[TTS] Engine input: {input.data}")
            async with self.asyncLock:
                resp = await httpxAsyncClient.post(API_URL + "/audio/speech", json=payload, headers=headers)  # 使用 json 发送请求
            if resp.status_code != 200:
                raise RuntimeError(f"status_code: {resp.status_code}")
            
            audio_content = resp.content  # 直接获取音频内容
            
            message = AudioMessage(
                data=mp3ToWav(audio_content),  # 直接使用音频内容
                desc=input.data,
                format=AudioFormatType.WAV,
                sampleRate=16000,
                sampleWidth=2,
            )
            return message
            
        except Exception as e:
            logger.error(f"[TTS] Engine run failed: {e}", exc_info=True)
            return None