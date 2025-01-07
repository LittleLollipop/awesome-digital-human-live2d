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

    async def run(self, input: TextMessage, **kwargs) -> Optional[TextMessage]:
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
                "model": "whisper-1",  # 使用 OpenAI 的 Whisper 模型进行语音合成
                "prompt": input.data,
                "response_format": "url"  # 返回音频的 URL
            }

            logger.debug(f"[TTS] Engine input: {input.data}")
            async with self.asyncLock:
                resp = await httpxAsyncClient.post(API_URL + "/audio/transcriptions", json=payload, headers=headers)
            if resp.status_code != 200:
                raise RuntimeError(f"status_code: {resp.status_code}")
            
            audio_url = resp.json().get("url")  # 获取返回的音频 URL
            audio_content = await httpxAsyncClient.get(audio_url)  # 下载音频内容
            
            message = AudioMessage(
                data=mp3ToWav(audio_content.content),
                desc=input.data,
                format=AudioFormatType.WAV,
                sampleRate=16000,
                sampleWidth=2,
            )
            return message
            
        except Exception as e:
            logger.error(f"[TTS] Engine run failed: {e}", exc_info=True)
            return None