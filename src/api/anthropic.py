import requests
import json
import time
from typing import Dict, Generator, Tuple, Optional
from .base import BaseAPI


class AnthropicCompatibleAPI(BaseAPI):
    def __init__(self, api_url: str, api_key: str, model_name: str,
                 temperature: float = 0.7, max_tokens: int = 2048):
        super().__init__(api_url, api_key, model_name, temperature, max_tokens)
        self.endpoint = f"{api_url.rstrip('/')}/messages"
        self.api_version = "2023-06-01"
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "Content-Type": "application/json"
        }
    
    def _get_body(self, prompt: str, stream: bool = True) -> Dict:
        return {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.max_tokens,
            "stream": stream
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        try:
            headers = self._get_headers()
            body = self._get_body("Hello", stream=False)
            body["max_tokens"] = 10
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=body,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "连接成功"
            else:
                error_msg = response.json().get("error", {}).get("message", "未知错误")
                return False, f"连接失败: {error_msg}"
        except requests.exceptions.Timeout:
            return False, "连接超时"
        except requests.exceptions.ConnectionError:
            return False, "网络连接错误"
        except Exception as e:
            return False, f"连接失败: {str(e)}"
    
    def stream_request(self, prompt: str, start_time: float) -> Generator[Tuple[Optional[str], float], None, None]:
        """流式请求，使用传入的start_time计算相对时间"""
        headers = self._get_headers()
        body = self._get_body(prompt, stream=True)
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=body,
                stream=True,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "请求失败")
                yield error_msg, time.time() - start_time
                return
            
            for line in response.iter_lines():
                if not line:
                    continue
                
                line_text = line.decode('utf-8')
                if line_text.startswith("data: "):
                    data_str = line_text[6:]
                    
                    try:
                        data = json.loads(data_str)
                        event_type = data.get("type", "")
                        
                        if event_type == "content_block_delta":
                            delta = data.get("delta", {})
                            text = delta.get("text", "")
                            if text:
                                # 使用传入的start_time计算相对时间
                                elapsed = time.time() - start_time
                                yield text, elapsed
                        elif event_type == "message_stop":
                            break
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.Timeout:
            yield None, time.time() - start_time
        except Exception as e:
            yield str(e), time.time() - start_time
    
    def full_request(self, prompt: str) -> Tuple[str, float, int]:
        headers = self._get_headers()
        body = self._get_body(prompt, stream=False)
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=body,
                timeout=120
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code != 200:
                error_msg = response.json().get("error", {}).get("message", "请求失败")
                return error_msg, elapsed_time, 0
            
            data = response.json()
            content_blocks = data.get("content", [])
            content = ""
            for block in content_blocks:
                if block.get("type") == "text":
                    content += block.get("text", "")
            
            usage = data.get("usage", {})
            token_count = usage.get("output_tokens", len(content.split()))
            
            return content, elapsed_time, token_count
        except Exception as e:
            return str(e), time.time() - start_time, 0