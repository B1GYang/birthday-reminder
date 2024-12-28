import sqlite3
import logging
from datetime import datetime
import threading
import queue
import os

class BirthdayDB:
    def __init__(self):
        self._local = threading.local()
        self._queue = queue.Queue()
        
        try:
            # 配置日志到用户文档目录
            log_dir = os.path.expanduser('~\\Documents\\BirthdayReminder\\logs')
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, 'birthday_reminder.log')
            
            # 配置日志
            logging.basicConfig(
                filename=log_path,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                encoding='utf-8',
                force=True  # 强制重新配置日志
            )
            
            logging.info("=== 数据库服务启动 ===")
            
            # 确保数据目录存在
            db_dir = os.path.expanduser('~\\Documents\\BirthdayReminder')
            os.makedirs(db_dir, exist_ok=True)
            
            # 初始化数据库
            self.create_table()
            
        except Exception as e:
            logging.error(f"数据库初始化错误: {str(e)}")
            raise

    def create_table(self):
        try:
            conn, cursor = self._get_connection()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS birthdays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birth_date DATE NOT NULL,
                    last_reminder DATE
                )
            ''')
            conn.commit()
        except Exception as e:
            logging.error(f"创建表错误: {str(e)}")
            raise

    def add_birthday(self, name, birth_date):
        """添加生日记录"""
        try:
            conn, cursor = self._get_connection()
            
            # 先检查是否已存在相同记录
            cursor.execute('''
                SELECT COUNT(*) FROM birthdays 
                WHERE name = ? AND birth_date = ?
            ''', (name, birth_date))
            
            if cursor.fetchone()[0] > 0:
                logging.info(f"生日记录已存在: {name} - {birth_date}")
                return True
            
            # 添加新记录
            cursor.execute('''
                INSERT INTO birthdays (name, birth_date, last_reminder)
                VALUES (?, ?, NULL)
            ''', (name, birth_date))
            conn.commit()
            
            logging.info(f"成功添加生日记录: {name} - {birth_date}")
            
            # 验证添加是否成功
            cursor.execute('''
                SELECT * FROM birthdays 
                WHERE name = ? AND birth_date = ?
            ''', (name, birth_date))
            result = cursor.fetchone()
            logging.info(f"验证新添加的记录: {result}")
            
            return True
        except Exception as e:
            logging.error(f"添加生日记录错误: {str(e)}")
            return False

    def _get_connection(self):
        """获取当前线程的数据库连接"""
        try:
            if not hasattr(self._local, 'conn'):
                # 使用用户文档目录存储数据库
                db_dir = os.path.expanduser('~\\Documents\\BirthdayReminder')
                os.makedirs(db_dir, exist_ok=True)
                db_path = os.path.join(db_dir, 'birthdays.db')
                
                # 记录数据库路径
                logging.info(f"使用数据库路径: {db_path}")
                
                # 添加超时和错误处理
                self._local.conn = sqlite3.connect(
                    db_path,
                    timeout=20,
                    isolation_level=None  # 自动提交
                )
                self._local.cursor = self._local.conn.cursor()
                
                # 启用外键约束
                self._local.cursor.execute('PRAGMA foreign_keys = ON')
                
                # 测试连接
                self._local.cursor.execute('SELECT CURRENT_TIMESTAMP')
                result = self._local.cursor.fetchone()
                logging.info(f"数据库连接测试成功: {result}")
                
            return self._local.conn, self._local.cursor
            
        except Exception as e:
            logging.error(f"数据库连接错误: {str(e)}")
            # 如果连接失败，确保清理
            if hasattr(self._local, 'conn'):
                try:
                    self._local.conn.close()
                except:
                    pass
                delattr(self._local, 'conn')
            raise

    def get_todays_birthdays(self):
        """获取今天的生日"""
        try:
            conn, cursor = self._get_connection()
            
            # 先记录当前时间用于调试
            current_time = datetime.now()
            today = current_time.strftime('%m-%d')
            logging.info(f"当前时间: {current_time}, 检查日期: {today}")
            
            # 使用更简单的查询条件，先找到所有今天的生日
            cursor.execute('''
                SELECT name, birth_date, last_reminder
                FROM birthdays
                WHERE strftime('%m-%d', birth_date) = strftime('%m-%d', 'now', 'localtime')
            ''')
            
            all_today_birthdays = cursor.fetchall()
            logging.info(f"今天的所有生日: {all_today_birthdays}")
            
            # 过滤出需要提醒的生日
            results = []
            current_date = current_time.strftime('%Y-%m-%d')
            
            for name, birth_date, last_reminder in all_today_birthdays:
                # 如果从未提醒过，或者最后提醒日期不是今天
                if last_reminder is None or last_reminder != current_date:
                    results.append((name, birth_date, last_reminder))
                    logging.info(f"需要提醒: {name}, 生日: {birth_date}, 上次提醒: {last_reminder}")
                else:
                    logging.info(f"今天已提醒过: {name}, 生日: {birth_date}, 上次提醒: {last_reminder}")
            
            logging.info(f"需要提醒的生日数量: {len(results)}")
            return results
            
        except Exception as e:
            logging.error(f"获取今日生日错误: {str(e)}")
            return []

    def update_reminder(self, name, birth_date):
        """更新提醒时间"""
        try:
            conn, cursor = self._get_connection()
            
            # 获取当前日期（不包含时间）
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # 先检查当前状态
            cursor.execute('''
                SELECT last_reminder 
                FROM birthdays 
                WHERE name = ? AND birth_date = ?
            ''', (name, birth_date))
            current_reminder = cursor.fetchone()
            logging.info(f"更新前的提醒状态 - {name}: {current_reminder}")
            
            # 更新提醒时间为今天的日期
            cursor.execute('''
                UPDATE birthdays
                SET last_reminder = ?
                WHERE name = ? AND birth_date = ?
            ''', (current_date, name, birth_date))
            conn.commit()
            
            # 验证更新
            cursor.execute('''
                SELECT name, birth_date, last_reminder 
                FROM birthdays 
                WHERE name = ? AND birth_date = ?
            ''', (name, birth_date))
            result = cursor.fetchone()
            logging.info(f"更新后的记录 - {name}: {result}")
            
        except Exception as e:
            logging.error(f"更新提醒时间错误: {str(e)}")

    def get_all_birthdays(self):
        """获取所有保存的生日信息"""
        try:
            conn, cursor = self._get_connection()
            cursor.execute('''
                SELECT id, name, birth_date, last_reminder
                FROM birthdays
                ORDER BY strftime('%m-%d', birth_date)
            ''')
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"获取所有生日记录错误: {str(e)}")
            return []

    def get_birthday_count(self):
        """获取生日记录总数"""
        try:
            conn, cursor = self._get_connection()
            cursor.execute('SELECT COUNT(*) FROM birthdays')
            return cursor.fetchone()[0]
        except Exception as e:
            logging.error(f"获取生日记录数量错误: {str(e)}")
            return 0

    def test_database(self):
        """测试数据库中的记录"""
        try:
            # 直接查询所有记录
            conn, cursor = self._get_connection()
            cursor.execute('''
                SELECT name, birth_date, last_reminder,
                       strftime('%m-%d', birth_date) as birthday_md,
                       strftime('%m-%d', 'now') as today_md
                FROM birthdays
            ''')
            results = cursor.fetchall()
            logging.info("=== 数据库测试开始 ===")
            logging.info(f"当前时间: {datetime.now()}")
            for row in results:
                logging.info(f"数据库记录: {row}")
            logging.info("=== 数据库测试结束 ===")
        except Exception as e:
            logging.error(f"测试数据库时发生错误: {str(e)}")

    def close(self):
        """关闭数据库连接"""
        if hasattr(self._local, 'conn'):
            try:
                self._local.conn.close()
                delattr(self._local, 'conn')
                logging.info("数据库连接已关闭")
            except Exception as e:
                logging.error(f"关闭数据库连接时出错: {str(e)}")

    def __del__(self):
        """析构函数，确保关闭连接"""
        self.close() 

    def update_birthday(self, name, old_date, new_date):
        """更新生日日期"""
        try:
            conn, cursor = self._get_connection()
            cursor.execute('''
                UPDATE birthdays 
                SET birth_date = ?
                WHERE name = ? AND birth_date = ?
            ''', (new_date, name, old_date))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"更新生日记录时出错: {str(e)}")
            return False

    def delete_birthday(self, name, date):
        """删除生日记录"""
        try:
            conn, cursor = self._get_connection()
            cursor.execute('''
                DELETE FROM birthdays 
                WHERE name = ? AND birth_date = ?
            ''', (name, date))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"删除生日记录时出错: {str(e)}")
            return False 