"""
会话管理
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid
import json
from pathlib import Path


class SessionState(BaseModel):
    """会话状态"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 会话数据
    current_url: Optional[str] = None
    current_platform: Optional[str] = None
    analyzed_pages: List[Dict] = []
    test_cases: List[Dict] = []
    exported_files: List[str] = []
    
    # 对话历史
    messages: List[Dict] = []
    
    # 元数据
    metadata: Dict[str, Any] = {}


class SessionManager:
    """会话管理器"""
    
    def __init__(self, storage_dir: str = "./data/sessions", timeout: int = 3600):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self._sessions: Dict[str, SessionState] = {}
    
    def create(self) -> SessionState:
        """创建新会话"""
        session = SessionState()
        self._sessions[session.session_id] = session
        self._save_session(session)
        return session
    
    def get(self, session_id: str) -> Optional[SessionState]:
        """获取会话"""
        if session_id in self._sessions:
            return self._sessions[session_id]
        
        # 尝试从文件加载
        session = self._load_session(session_id)
        if session:
            self._sessions[session_id] = session
        return session
    
    def get_or_create(self, session_id: Optional[str] = None) -> SessionState:
        """获取或创建会话"""
        if session_id:
            session = self.get(session_id)
            if session:
                return session
        return self.create()
    
    def update(self, session: SessionState) -> None:
        """更新会话"""
        session.updated_at = datetime.now()
        self._sessions[session.session_id] = session
        self._save_session(session)
    
    def delete(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
        
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            return True
        return False
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """添加消息"""
        session = self.get(session_id)
        if session:
            session.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self.update(session)
    
    def set_analysis(self, session_id: str, url: str, platform: str, pages: List[Dict]) -> None:
        """设置分析结果"""
        session = self.get(session_id)
        if session:
            session.current_url = url
            session.current_platform = platform
            session.analyzed_pages = pages
            self.update(session)
    
    def set_test_cases(self, session_id: str, test_cases: List[Dict]) -> None:
        """设置测试用例"""
        session = self.get(session_id)
        if session:
            session.test_cases = test_cases
            self.update(session)
    
    def add_exported_file(self, session_id: str, file_path: str) -> None:
        """添加导出文件"""
        session = self.get(session_id)
        if session:
            session.exported_files.append(file_path)
            self.update(session)
    
    def get_context_summary(self, session_id: str) -> Dict:
        """获取上下文摘要"""
        session = self.get(session_id)
        if not session:
            return {}
        
        return {
            "url": session.current_url,
            "platform": session.current_platform,
            "pages_count": len(session.analyzed_pages),
            "test_cases_count": len(session.test_cases),
            "exported_files": len(session.exported_files),
            "messages_count": len(session.messages)
        }
    
    def _save_session(self, session: SessionState) -> None:
        """保存会话到文件"""
        session_file = self.storage_dir / f"{session.session_id}.json"
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session.model_dump(), f, ensure_ascii=False, indent=2, default=str)
    
    def _load_session(self, session_id: str) -> Optional[SessionState]:
        """从文件加载会话"""
        session_file = self.storage_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return SessionState(**data)
    
    def cleanup_expired(self) -> int:
        """清理过期会话"""
        import time
        current_time = time.time()
        expired_count = 0
        
        for session_id, session in list(self._sessions.items()):
            if (current_time - session.updated_at.timestamp()) > self.timeout:
                self.delete(session_id)
                expired_count += 1
        
        return expired_count
