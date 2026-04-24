import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Optional
import threading

from ..api.openai import OpenAICompatibleAPI
from ..api.anthropic import AnthropicCompatibleAPI
from ..utils.logger import Logger


class SpeedTester:
    def __init__(self, results_dir: str = None, logs_dir: str = None):
        if results_dir is None:
            self.results_dir = Path(__file__).parent.parent.parent / "results"
        else:
            self.results_dir = Path(results_dir)
        
        if not self.results_dir.exists():
            self.results_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = Logger(logs_dir)
        self._stop_flag = False
        self._testing = False
    
    def _create_api_client(self, model_config: Dict):
        protocol = model_config.get("protocol", "openai")
        
        if protocol == "openai":
            return OpenAICompatibleAPI(
                api_url=model_config.get("api_url", ""),
                api_key=model_config.get("api_key", ""),
                model_name=model_config.get("name", ""),
                temperature=model_config.get("temperature", 0.7),
                max_tokens=model_config.get("max_tokens", 2048)
            )
        elif protocol == "anthropic":
            return AnthropicCompatibleAPI(
                api_url=model_config.get("api_url", ""),
                api_key=model_config.get("api_key", ""),
                model_name=model_config.get("name", ""),
                temperature=model_config.get("temperature", 0.7),
                max_tokens=model_config.get("max_tokens", 2048)
            )
        else:
            raise ValueError(f"不支持的协议类型: {protocol}")
    
    def test_single_model(self, model_config: Dict, prompt: str) -> Dict:
        model_name = model_config.get("name", "未知模型")
        
        self.logger.log_test_start(model_name, prompt)
        
        try:
            api_client = self._create_api_client(model_config)
            self.logger.log_api_request(model_name, api_client.api_url)
            
            result = api_client.measure_full_output(prompt)
            
            if result.get("success", False):
                self.logger.log_first_token(model_name, result["first_token_time"])
                self.logger.log_test_complete(
                    model_name,
                    result["total_time"],
                    result["token_count"],
                    result["speed"],
                    result.get("content", "")  # 传入返回内容
                )
            else:
                self.logger.log_test_error(model_name, result.get("error", "未知错误"))
            
            result["model_name"] = model_name
            result["protocol"] = model_config.get("protocol", "openai")
            result["remark"] = model_config.get("remark", "")
            
            return result
        except Exception as e:
            self.logger.log_test_error(model_name, str(e))
            return {
                "model_name": model_name,
                "first_token_time": 0,
                "total_time": 0,
                "token_count": 0,
                "speed": 0,
                "content": "",
                "success": False,
                "error": str(e),
                "protocol": model_config.get("protocol", "openai"),
                "remark": model_config.get("remark", "")
            }
    
    def test_models(self, models: List[Dict], prompt: str,
                    progress_callback: Callable = None) -> List[Dict]:
        self._stop_flag = False
        self._testing = True
        
        results = []
        total_models = len(models)
        
        for i, model in enumerate(models):
            if self._stop_flag:
                break
            
            result = self.test_single_model(model, prompt)
            results.append(result)
            
            if progress_callback:
                progress_callback(i + 1, total_models, result)
        
        self._testing = False
        self.logger.log_all_tests_complete(
            sum(1 for r in results if r.get("success", False)),
            len(results)
        )
        
        return results
    
    def stop_test(self):
        self._stop_flag = True
    
    def is_testing(self) -> bool:
        return self._testing
    
    def save_results(self, results: List[Dict], filename: str = None):
        if filename is None:
            filename = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.results_dir / filename
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "total_models": len(results),
                "success_count": sum(1 for r in results if r.get("success", False)),
                "avg_first_token_time": sum(r.get("first_token_time", 0) for r in results) / len(results) if results else 0,
                "avg_speed": sum(r.get("speed", 0) for r in results) / len(results) if results else 0
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def export_results_csv(self, results: List[Dict], filename: str = None):
        if filename is None:
            filename = f"test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.results_dir / filename
        
        headers = ["模型名称", "首次Token(s)", "总用时(s)", "Token数", "速度(Token/s)", "状态", "错误信息"]
        
        lines = [",".join(headers)]
        
        for result in results:
            line = [
                result.get("model_name", ""),
                f"{result.get('first_token_time', 0):.2f}",
                f"{result.get('total_time', 0):.2f}",
                str(result.get("token_count", 0)),
                f"{result.get('speed', 0):.2f}",
                "成功" if result.get("success", False) else "失败",
                result.get("error", "")
            ]
            lines.append(",".join(line))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        return filepath
    
    def test_connection(self, model_config: Dict) -> tuple:
        try:
            api_client = self._create_api_client(model_config)
            return api_client.test_connection()
        except Exception as e:
            return False, str(e)