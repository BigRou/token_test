from abc import ABC, abstractmethod
from typing import Dict, Generator, Tuple, Optional
import time


class BaseAPI(ABC):
    def __init__(self, api_url: str, api_key: str, model_name: str,
                 temperature: float = 0.7, max_tokens: int = 2048):
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        pass
    
    @abstractmethod
    def stream_request(self, prompt: str, start_time: float) -> Generator[Tuple[Optional[str], float], None, None]:
        """流式请求，start_time用于计算相对时间"""
        pass
    
    @abstractmethod
    def full_request(self, prompt: str) -> Tuple[str, float, int]:
        pass
    
    def measure_first_token_time(self, prompt: str) -> Tuple[float, str]:
        start_time = time.time()
        first_token_time = None
        full_content = ""
        
        for token, elapsed in self.stream_request(prompt, start_time):
            if first_token_time is None and token:
                first_token_time = elapsed
            if token:
                full_content += token
        
        if first_token_time is None:
            first_token_time = time.time() - start_time
        
        return first_token_time * 1000, full_content
    
    def measure_full_output(self, prompt: str) -> Dict:
        start_time = time.time()
        first_token_time = None
        full_content = ""
        
        for token, elapsed in self.stream_request(prompt, start_time):
            if first_token_time is None and token:
                first_token_time = elapsed  # 首次token的响应时间（秒）
            if token:
                full_content += token
        
        total_time = time.time() - start_time
        
        if first_token_time is None:
            first_token_time = total_time
        
        # 估算Token数：中文字符按1.5个token计算，英文按0.5个token计算
        # 简化计算：总字符数 / 2（混合中英文的平均值）
        token_count = max(len(full_content) // 2, 1) if full_content else 0
        
        speed = token_count / total_time if total_time > 0 else 0
        
        return {
            "first_token_time": first_token_time,  # 单位：秒
            "total_time": total_time,
            "token_count": token_count,
            "speed": speed,
            "content": full_content,
            "success": True,
            "error": None
        }