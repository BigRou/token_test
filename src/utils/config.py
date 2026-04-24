import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import base64


class ConfigManager:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            self.config_dir = Path(__file__).parent.parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        
        self.models_file = self.config_dir / "models.json"
        self.settings_file = self.config_dir / "settings.json"
        
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _encrypt_key(self, key: str) -> str:
        if not key:
            return ""
        return base64.b64encode(key.encode()).decode()
    
    def _decrypt_key(self, encrypted_key: str) -> str:
        if not encrypted_key:
            return ""
        try:
            return base64.b64decode(encrypted_key.encode()).decode()
        except Exception:
            return encrypted_key
    
    def load_models(self) -> List[Dict]:
        if not self.models_file.exists():
            return self._get_default_models()
        
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                models = data.get("models", [])
                for model in models:
                    if "api_key" in model:
                        model["api_key"] = self._decrypt_key(model["api_key"])
                return models
        except Exception:
            return self._get_default_models()
    
    def save_models(self, models: List[Dict]):
        models_to_save = []
        for model in models:
            model_copy = model.copy()
            if "api_key" in model_copy:
                model_copy["api_key"] = self._encrypt_key(model_copy["api_key"])
            models_to_save.append(model_copy)
        
        data = {"models": models_to_save}
        with open(self.models_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_settings(self) -> Dict:
        if not self.settings_file.exists():
            return self._get_default_settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return self._get_default_settings()
    
    def save_settings(self, settings: Dict):
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    
    def _get_default_models(self) -> List[Dict]:
        return [
            {
                "name": "qwen3.5-plus",
                "api_url": "https://coding.dashscope.aliyuncs.com/v1",
                "api_key": "",
                "protocol": "openai",
                "temperature": 0.7,
                "max_tokens": 2048,
                "remark": "通义千问"
            },
            {
                "name": "glm-5",
                "api_url": "https://coding.dashscope.aliyuncs.com/v1",
                "api_key": "",
                "protocol": "openai",
                "temperature": 0.7,
                "max_tokens": 2048,
                "remark": "智谱AI"
            },
            {
                "name": "MiniMax-M2.5",
                "api_url": "https://coding.dashscope.aliyuncs.com/v1",
                "api_key": "",
                "protocol": "openai",
                "temperature": 0.7,
                "max_tokens": 2048,
                "remark": "MiniMax"
            },
            {
                "name": "kimi-k2.5",
                "api_url": "https://coding.dashscope.aliyuncs.com/v1",
                "api_key": "",
                "protocol": "openai",
                "temperature": 0.7,
                "max_tokens": 2048,
                "remark": "月之暗面"
            }
        ]
    
    def _get_default_settings(self) -> Dict:
        return {
            "default_prompt": "请用500字左右介绍一下人工智能的发展历程和未来趋势。",
            "temperature": 0.7,
            "max_tokens": 2048,
            "default_api_url": "https://coding.dashscope.aliyuncs.com/v1",
            "default_protocol": "openai"
        }
    
    def add_model(self, model: Dict):
        models = self.load_models()
        models.append(model)
        self.save_models(models)
    
    def update_model(self, model_name: str, updated_model: Dict):
        models = self.load_models()
        for i, model in enumerate(models):
            if model["name"] == model_name:
                models[i] = updated_model
                break
        self.save_models(models)
    
    def delete_model(self, model_name: str):
        models = self.load_models()
        models = [m for m in models if m["name"] != model_name]
        self.save_models(models)
    
    def get_model(self, model_name: str) -> Optional[Dict]:
        models = self.load_models()
        for model in models:
            if model["name"] == model_name:
                return model
        return None
    
    def export_models(self, filepath: str):
        models = self.load_models()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({"models": models}, f, ensure_ascii=False, indent=2)
    
    def import_models(self, filepath: str):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            models = data.get("models", [])
            self.save_models(models)