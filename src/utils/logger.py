import os
import logging
from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, logs_dir: str = None):
        if logs_dir is None:
            self.logs_dir = Path(__file__).parent.parent.parent / "logs"
        else:
            self.logs_dir = Path(logs_dir)
        
        self._ensure_logs_dir()
        self._setup_logger()
    
    def _ensure_logs_dir(self):
        if not self.logs_dir.exists():
            self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _setup_logger(self):
        self.logger = logging.getLogger("token_test")
        self.logger.setLevel(logging.DEBUG)
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        log_filename = f"log_{datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = self.logs_dir / log_filename
        
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def success(self, message: str):
        self.logger.info(f"[SUCCESS] {message}")
    
    def log_test_start(self, model_name: str, prompt: str):
        self.info(f"开始测试模型: {model_name}")
        self.debug(f"提示词: {prompt[:100]}...")
    
    def log_first_token(self, model_name: str, time_s: float):
        self.success(f"{model_name} - 首次Token响应: {time_s:.2f}s")
    
    def log_test_complete(self, model_name: str, total_time: float, 
                          token_count: int, speed: float, content: str = ""):
        self.success(
            f"{model_name} - 测试完成: "
            f"总用时={total_time:.2f}s, "
            f"Token数={token_count}, "
            f"速度={speed:.2f}/s"
        )
        # 记录返回内容的前200字符
        if content:
            content_preview = content[:200].replace('\n', ' ')
            self.debug(f"{model_name} - 返回内容: {content_preview}...")
    
    def log_test_error(self, model_name: str, error: str):
        self.error(f"{model_name} - 测试失败: {error}")
    
    def log_api_request(self, model_name: str, url: str):
        self.debug(f"{model_name} - 发送请求到: {url}")
    
    def log_all_tests_complete(self, success_count: int, total_count: int):
        self.success(f"所有测试完成: 成功={success_count}, 总数={total_count}")