import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class GroupMemberStore:
    """群成员数据存储管理器"""

    def __init__(self):
        # 数据存储目录
        self.base_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..', '..', 'plugin_data', 'astrbot_plugin_kotory'
        )
        self.file_path = os.path.join(self.base_dir, 'groupmembers.json')
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        """确保存储目录存在"""
        os.makedirs(self.base_dir, exist_ok=True)

    def _load_data(self) -> Dict:
        """加载已存储的群成员数据"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载群成员数据失败: {e}")
        return {}

    def _save_data(self, data: Dict):
        """保存群成员数据到文件"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存群成员数据失败: {e}")

    def is_cache_valid(self, group_id: str) -> bool:
        """检查指定群的缓存是否有效（24小时内更新）"""
        data = self._load_data()
        group_data = data.get(group_id)

        if not group_data:
            return False

        update_time = group_data.get('update_time')
        if not update_time:
            return False

        try:
            update_datetime = datetime.fromisoformat(update_time)
            return datetime.now() - update_datetime < timedelta(hours=24)
        except Exception:
            return False

    def get_group_members(self, group_id: str) -> Optional[List[Dict]]:
        """获取指定群的群成员列表"""
        data = self._load_data()
        group_data = data.get(group_id)
        return group_data.get('members') if group_data else None

    def save_group_members(self, group_id: str, members: List[Dict]):
        """保存指定群的群成员列表"""
        data = self._load_data()
        data[group_id] = {
            'members': members,
            'update_time': datetime.now().isoformat()
        }
        self._save_data(data)
