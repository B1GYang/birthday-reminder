import json
import requests
import os
import sys
import subprocess
from pathlib import Path
import logging
from packaging import version

class AutoUpdater:
    def __init__(self):
        self.github_owner = "B1GYang"
        self.github_repo = "birthday-reminder"
        self.current_version = "1.0.0"
        self.version_file_url = f"https://raw.githubusercontent.com/{self.github_owner}/{self.github_repo}/main/version.json"
        
        # 设置日志
        logging.basicConfig(
            filename="logs/updater.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )

    def check_for_updates(self):
        """检查是否有新版本可用"""
        try:
            # 获取远程版本信息
            response = requests.get(self.version_file_url)
            if response.status_code == 200:
                remote_info = response.json()
                remote_version = remote_info["version"]
                
                # 比较版本
                if version.parse(remote_version) > version.parse(self.current_version):
                    logging.info(f"发现新版本: {remote_version}")
                    return True, remote_info
                
            return False, None
            
        except Exception as e:
            logging.error(f"检查更新时发生错误: {str(e)}")
            return False, None

    def download_update(self, update_info):
        """下载更新"""
        try:
            # 下载新版本文件
            for file_info in update_info["files"]:
                url = file_info["url"]
                path = file_info["path"]
                
                # 确保目录存在
                os.makedirs(os.path.dirname(path), exist_ok=True)
                
                # 下载文件
                response = requests.get(url)
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                        
            return True
            
        except Exception as e:
            logging.error(f"下载更新时发生错误: {str(e)}")
            return False

    def apply_update(self):
        """应用更新"""
        try:
            # 重启应用
            python = sys.executable
            os.execl(python, python, *sys.argv)
            
        except Exception as e:
            logging.error(f"应用更新时发生错误: {str(e)}")
            return False 