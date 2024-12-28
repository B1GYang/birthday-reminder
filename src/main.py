# 首先尝试导入 setuptools
try:
    from setuptools._distutils.version import StrictVersion as Version
except ImportError:
    try:
        from distutils.version import StrictVersion as Version
    except ImportError:
        Version = str  # 如果都无法导入，使用 str 作为后备方案

import customtkinter as ctk
import tkinter as tk
from tkcalendar import DateEntry, Calendar
from database import BirthdayDB
import threading
import time
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from tkinter import ttk

class BirthdayReminder:
    def __init__(self):
        # 设置工作目录
        self.set_working_directory()
        
        # 配置日志
        self.setup_logging()
        
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 创建主窗口
        self.root = ctk.CTk()
        self.root.title("生日提醒")
        self.center_main_window(300, 400)  # 主窗口居中

        # 初始化数据库
        self.db = BirthdayDB()
        # self.db.test_database()  # 注释掉这行，或者完全删除
        
        self.create_widgets()
        
        # 添加状态变量
        self.is_running = True
        
        # 启动提醒检查线程
        self.reminder_thread = threading.Thread(target=self.check_birthdays, daemon=True)
        self.reminder_thread.start()

    def set_working_directory(self):
        """确保程序在正确的工目录下运行"""
        if getattr(sys, 'frozen', False):
            # 如果是打包后的程序
            os.chdir(os.path.dirname(sys.executable))
        else:
            # 如果是源码运行
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    def setup_logging(self):
        """配置日志系统"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / "birthday_reminder.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )

    def create_widgets(self):
        # 创建标题
        title_label = ctk.CTkLabel(self.root, text="生日提醒系统", font=("微软雅黑", 20))
        title_label.pack(pady=20)

        # 创建主框架
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(padx=20, pady=10, fill="both", expand=True)

        # 添加生日按钮
        add_button = ctk.CTkButton(
            main_frame,
            text="添加生日",
            command=self.show_add_frame,
            width=200,
            height=40,
            font=("微软雅黑", 14)
        )
        add_button.pack(pady=15)

        # 查看记录按钮
        view_button = ctk.CTkButton(
            main_frame,
            text="查看记录",
            command=self.show_search_window,
            width=200,
            height=40,
            font=("微软雅黑", 14)
        )
        view_button.pack(pady=15)

        # 关于按钮
        about_button = ctk.CTkButton(
            main_frame,
            text="关于",
            command=self.show_about,
            width=200,
            height=40,
            font=("微软雅黑", 14)
        )
        about_button.pack(pady=15)

    def show_add_frame(self):
        """显示添加生日的窗口"""
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("添加生日")
        self.show_window_next_to_main(add_window, 300, 400)
        
        # 创建主框架
        frame = ctk.CTkFrame(add_window)
        frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # 姓名输入框
        name_label = ctk.CTkLabel(frame, text="姓名:")
        name_label.pack(pady=5)
        name_entry = ctk.CTkEntry(frame, width=200)
        name_entry.pack(pady=5)
        
        # 生日输入框
        birth_label = ctk.CTkLabel(frame, text="生日:")
        birth_label.pack(pady=5)
        birth_entry = ctk.CTkEntry(frame, width=200, placeholder_text="格式: YYYYMMDD")
        birth_entry.pack(pady=5)
        
        # 日期选择按钮
        def show_calendar():
            def on_date_select():
                selected_date = cal.selection_get()
                birth_entry.delete(0, 'end')
                birth_entry.insert(0, selected_date.strftime('%Y%m%d'))
                calendar_window.destroy()

            calendar_window = ctk.CTkToplevel(add_window)
            calendar_window.title("选择日期")
            
            cal = Calendar(
                calendar_window,
                selectmode='day',
                year=2024,
                month=1,
                day=1,
                locale='zh_CN',
                cursor="hand1",
                date_pattern='yyyymmdd'
            )
            cal.pack(padx=10, pady=10)
            
            ok_button = ctk.CTkButton(
                calendar_window,
                text="确定",
                command=on_date_select
            )
            ok_button.pack(pady=10)
        
        date_button = ctk.CTkButton(
            frame,
            text="选择日期",
            command=show_calendar,
            width=200
        )
        date_button.pack(pady=10)
        
        # 保存按钮
        def save_birthday():
            name = name_entry.get().strip()
            date_str = birth_entry.get().strip()
            
            if not name:
                self.show_error("请输入姓名")
                return
            
            try:
                # 尝试解析日期
                if len(date_str) != 8:
                    raise ValueError("日期格式错误")
                
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:])
                
                # 验证日期是否有效
                birth_date = datetime(year, month, day).strftime('%Y-%m-%d')
                
            except ValueError as e:
                self.show_error("请输入正确的日期格式(YYYYMMDD)\n例如：20240101")
                return
            
            if self.db.add_birthday(name, birth_date):
                self.show_success("添加成功")
                # 使用 after 延迟关闭添加窗口
                add_window.after(1000, add_window.destroy)
            else:
                self.show_error("保存失败，请查看日志")
        
        save_button = ctk.CTkButton(
            frame,
            text="保存",
            command=save_birthday,
            width=200
        )
        save_button.pack(pady=20)

    def show_search_window(self):
        """显示查询窗口"""
        search_window = ctk.CTkToplevel(self.root)
        search_window.title("查看生日记录")
        self.show_window_next_to_main(search_window, 400, 500)
        
        # 搜索框架
        search_frame = ctk.CTkFrame(search_window)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        # 姓名搜索
        name_label = ctk.CTkLabel(search_frame, text="姓名:")
        name_label.pack(pady=5)
        
        def on_search(*args):
            # 清空现有结果
            result_tree.delete(*result_tree.get_children())
            search_text = name_entry.get().strip()
            birthdays = self.db.get_all_birthdays()
            
            for birthday in birthdays:
                name = birthday[1]
                date = birthday[2]
                if not search_text or search_text in name:
                    result_tree.insert("", "end", values=(name, date))
        
        search_var = tk.StringVar()
        search_var.trace('w', on_search)
        name_entry = ctk.CTkEntry(search_frame, textvariable=search_var)
        name_entry.pack(pady=5, fill="x")
        
        # 结果显示框架
        result_frame = ctk.CTkFrame(search_window)
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 创建右键菜单
        context_menu = tk.Menu(search_window, tearoff=0)
        
        def show_edit_dialog():
            selected_item = result_tree.selection()[0]
            name, old_date = result_tree.item(selected_item)['values']
            
            edit_window = ctk.CTkToplevel(search_window)
            edit_window.title("修改生日")
            self.center_window_relative_to_parent(edit_window, search_window, 300, 200)
            
            frame = ctk.CTkFrame(edit_window)
            frame.pack(padx=20, pady=20, fill="both", expand=True)
            
            date_label = ctk.CTkLabel(frame, text=f"修改 {name} 的生日:")
            date_label.pack(pady=5)
            
            date_entry = ctk.CTkEntry(frame, placeholder_text="YYYYMMDD")
            date_entry.pack(pady=5)
            date_entry.insert(0, old_date.replace('-', ''))
            
            def save_changes():
                try:
                    new_date_str = date_entry.get().strip()
                    if len(new_date_str) != 8:
                        raise ValueError("日期格式错误")
                    
                    year = int(new_date_str[:4])
                    month = int(new_date_str[4:6])
                    day = int(new_date_str[6:])
                    
                    new_date = datetime(year, month, day).strftime('%Y-%m-%d')
                    
                    # 更新数据
                    if self.db.update_birthday(name, old_date, new_date):
                        self.show_success("修改成功")
                        edit_window.destroy()
                        on_search()  # 刷新列表
                    else:
                        self.show_error("修改失败")
                        
                except ValueError:
                    self.show_error("请输入正确的日期格式(YYYYMMDD)")
            
            save_button = ctk.CTkButton(frame, text="保存", command=save_changes)
            save_button.pack(pady=20)
        
        def delete_record():
            if not result_tree.selection():
                return
            
            selected_item = result_tree.selection()[0]
            name, date = result_tree.item(selected_item)['values']
            
            # 确认删除
            confirm_window = ctk.CTkToplevel(search_window)
            confirm_window.title("确认删除")
            self.center_window_relative_to_parent(confirm_window, search_window, 300, 150)
            
            label = ctk.CTkLabel(confirm_window, text=f"确定要删除 {name} 的生日记录吗？")
            label.pack(pady=20)
            
            def confirm_delete():
                if self.db.delete_birthday(name, date):
                    self.show_success("删除成功")
                    # 使用 after 延迟关闭确认窗口
                    confirm_window.after(1000, confirm_window.destroy)
                    on_search()  # 刷新列表
                else:
                    self.show_error("删除失败")
            
            button_frame = ctk.CTkFrame(confirm_window)
            button_frame.pack(fill="x", padx=20)
            
            confirm_btn = ctk.CTkButton(
                button_frame, 
                text="确定", 
                command=confirm_delete,
                fg_color="red",
                hover_color="#8B0000"
            )
            confirm_btn.pack(side="left", padx=10, expand=True)
            
            cancel_btn = ctk.CTkButton(
                button_frame, 
                text="取消", 
                command=confirm_window.destroy
            )
            cancel_btn.pack(side="left", padx=10, expand=True)
        
        # 添加菜单项
        context_menu.add_command(label="修改时间", command=show_edit_dialog)
        context_menu.add_separator()
        context_menu.add_command(label="删除", command=delete_record)
        
        def show_context_menu(event):
            if result_tree.selection():  # 只有选中项目时才显示菜单
                context_menu.post(event.x_root, event.y_root)
        
        # 使用Treeview显示结果
        result_tree = ttk.Treeview(
            result_frame,
            columns=("name", "date"),
            show="headings",
            height=15
        )
        result_tree.heading("name", text="姓名")
        result_tree.heading("date", text="生日")
        result_tree.column("name", width=150)
        result_tree.column("date", width=150)
        
        # 绑定右键事件
        result_tree.bind("<Button-3>", show_context_menu)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=result_tree.yview)
        result_tree.configure(yscrollcommand=scrollbar.set)
        
        result_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 初始显示所有记录
        on_search()

    def show_calendar(self):
        """显示日历选择器"""
        def on_date_select():
            selected_date = cal.selection_get()
            self.birth_entry.delete(0, 'end')
            self.birth_entry.insert(0, selected_date.strftime('%Y%m%d'))
            top.destroy()

        top = ctk.CTkToplevel(self.root)
        top.title("选择日期")
        self.show_window_next_to_main(top, 300, 300)
        
        cal = Calendar(
            top,
            selectmode='day',
            year=2024,
            month=1,
            day=1,
            locale='zh_CN',
            cursor="hand1",
            date_pattern='yyyymmdd'
        )
        cal.pack(padx=10, pady=10)
        
        ok_button = ctk.CTkButton(
            top,
            text="确定",
            command=on_date_select
        )
        ok_button.pack(pady=10)

    def add_birthday(self):
        """添加生日记录"""
        name = self.name_entry.get().strip()
        date_str = self.birth_entry.get().strip()
        
        if not name:
            self.show_error("请输入姓名")
            return
        
        try:
            # 尝试解析日期
            if len(date_str) != 8:
                raise ValueError("日期格式错误")
            
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:])
            
            # 验证日期是否有效
            birth_date = datetime(year, month, day).strftime('%Y-%m-%d')
            
        except ValueError as e:
            self.show_error("请输入正确的日期格式(YYYYMMDD)\n例如：20240101")
            return
        
        if self.db.add_birthday(name, birth_date):
            self.show_success("添加成功")
            self.name_entry.delete(0, 'end')  # 清空姓名
            self.update_birthday_list()
        else:
            self.show_error("保存失败，请查看日��")

    def show_success(self, message):
        """显示成功消息，1秒后自动关闭"""
        success_window = ctk.CTkToplevel()
        success_window.title("成功")
        success_window.geometry("200x100")
        
        # 相对于主���口居中显示
        self.center_window_relative_to_parent(success_window, self.root, 200, 100)
        
        label = ctk.CTkLabel(success_window, text=message)
        label.pack(pady=20)
        
        # 1秒后自动关闭窗口
        success_window.after(1000, success_window.destroy)

    def show_all_birthdays(self):
        """显示所有已保存的生日信息"""
        view_window = ctk.CTkToplevel(self.root)
        view_window.title("所有生日信息")
        view_window.geometry("400x300")
        
        # 创建滚动文本框
        text_box = ctk.CTkTextbox(view_window, width=380, height=280)
        text_box.pack(padx=10, pady=10)
        
        # 获取所有生日信息
        birthdays = self.db.get_all_birthdays()
        
        if not birthdays:
            text_box.insert("1.0", "暂无保存的生日信息")
        else:
            for birthday in birthdays:
                text_box.insert("end", f"姓名: {birthday[1]}\n")
                text_box.insert("end", f"生日: {birthday[2]}\n")
                text_box.insert("end", "-" * 30 + "\n")
        
        text_box.configure(state="disabled")

    def check_birthdays(self):
        """改进的生日检查方法"""
        while self.is_running:  # 使用状态变量制��环
            try:
                current_time = datetime.now()
                logging.info(f"正在检查生日 - 当前时间: {current_time}")
                
                # 获取今天的生日
                birthdays = self.db.get_todays_birthdays()
                logging.info(f"检查到的生日数量: {len(birthdays)}")
                
                if birthdays:  # 如果有生日就提醒
                    for name, birth_date, _ in birthdays:
                        logging.info(f"准备为 {name} ({birth_date}) 显示提醒")
                        # 使用队列在主线程中显示通知
                        self.root.after(100, lambda n=name, d=birth_date: self.show_notification(n, d))
                
                # 每10秒检查一次
                time.sleep(10)
                
            except Exception as e:
                logging.error(f"检查生日发生错误: {str(e)}")
                if self.is_running:  # 有在程序仍在运行时才继续
                    time.sleep(10)

    def show_notification(self, name, birth_date):
        """显示生日提醒窗口"""
        try:
            notification_window = ctk.CTkToplevel(self.root)
            notification_window.title("生日提醒")
            self.show_window_next_to_main(notification_window, 300, 200)
            
            # 保窗口显示在最前面
            notification_window.lift()
            notification_window.focus_force()
            
            # 计算年龄
            birth_year = datetime.strptime(birth_date, '%Y-%m-%d').year
            age = datetime.now().year - birth_year
            
            # 创建提醒内容
            message_label = ctk.CTkLabel(
                notification_window,
                text=f"今天是 {name} 的生日！\n已经 {age} 岁啦！",
                font=("微软雅黑", 16)
            )
            message_label.pack(pady=30)
            
            # 确认按钮
            def on_confirm():
                notification_window.destroy()
                self.root.destroy()  # 关闭主程序
            
            confirm_button = ctk.CTkButton(
                notification_window,
                text="知道了",
                command=on_confirm
            )
            confirm_button.pack(pady=20)
            
            # 设置窗口位置（屏幕右下角）
            screen_width = notification_window.winfo_screenwidth()
            screen_height = notification_window.winfo_screenheight()
            window_width = 300
            window_height = 200
            x = screen_width - window_width - 20
            y = screen_height - window_height - 40
            notification_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # 添加日志
            logging.info(f"已显示生日提醒窗口: {name}")
            
        except Exception as e:
            logging.error(f"显示提醒窗口时发生错误: {str(e)}")

    def on_closing(self):
        """程序关闭时的清理工作"""
        self.is_running = False
        self.root.destroy()

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # 注册关闭事件
        self.root.mainloop()

    def update_birthday_list(self):
        """更新生日列表显示"""
        # 清空现有列表
        for item in self.birthday_list.get_children():
            self.birthday_list.delete(item)
        
        # 获取所有生日记录
        birthdays = self.db.get_all_birthdays()
        
        # 添加记录到列表
        for birthday in birthdays:
            name = birthday[1]
            date = birthday[2]
            self.birthday_list.insert("", "end", values=(name, date))

    def clear_date(self):
        """清除日期输入"""
        self.birth_entry.delete(0, 'end')

    def search_birthdays(self):
        """搜索生日记录"""
        try:
            start_date = self.start_date.get().strip()
            end_date = self.end_date.get().strip()
            
            # 清空现有列表
            for item in self.birthday_list.get_children():
                self.birthday_list.delete(item)
            
            # 获取所有记录
            birthdays = self.db.get_all_birthdays()
            
            for birthday in birthdays:
                name = birthday[1]
                date = birthday[2]
                
                # 如果没有输入日期范围，显示所有记录
                if not start_date and not end_date:
                    self.birthday_list.insert("", "end", values=(name, date))
                    continue
                
                # 解析日期进行比较
                birth_date = datetime.strptime(date, '%Y-%m-%d')
                
                if start_date:
                    start = datetime.strptime(start_date, '%Y%m%d')
                    if birth_date < start:
                        continue
                
                if end_date:
                    end = datetime.strptime(end_date, '%Y%m%d')
                    if birth_date > end:
                        continue
                
                self.birthday_list.insert("", "end", values=(name, date))
                
        except ValueError:
            self.show_error("请输入正确的日期格式(YYYYMMDD)")

    def show_about(self):
        """显示关于信息"""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("关于")
        self.show_window_next_to_main(about_window, 400, 500)
        
        # 创建滚动文本框
        text_box = ctk.CTkTextbox(about_window, width=380, height=480)
        text_box.pack(padx=10, pady=10)
        
        # 添加关于信息
        about_text = """
生日提醒系统 v1.0.0

使用说明：

1. 添加生日
   - 点击"添加生日"按钮
   - 输入姓名
   - 输入或选择生日日期
   - 日期格式：YYYYMMDD（如：20240101）
   - 点击"保存"完成添加

2. 查看记录
   - 点击"查看记录"按钮
   - 搜索框输入姓名可快速查找
   - 显示所有已添加���生日信息

3. 提醒功能
   - 程序会自动检查今天是否有人过生日
   - 如果有，会弹出提醒窗口
   - 点击"知道了"关闭提醒

4. 其他说明
   - 程序启动时自动运行
   - 支持最小化到系统托盘
   - 日期格式统一为：YYYYMMDD

开发者：B1GYang
版本：1.0.0
发布日期：2024-12-29
"""
        
        text_box.insert("1.0", about_text)
        text_box.configure(state="disabled")  # 设置为只读

    def center_main_window(self, width, height):
        """将主窗口居中显示"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def show_window_next_to_main(self, window, width, height):
        """在主窗口右侧显示子窗口"""
        # 获取主窗口位置和大小
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        main_width = self.root.winfo_width()
        
        # 设置子窗口位置（在主窗口右侧）
        x = main_x + main_width + 10  # 10是窗口之间的间距
        y = main_y
        
        # 确保窗口不会超出屏幕
        screen_width = window.winfo_screenwidth()
        if x + width > screen_width:
            x = main_x - width - 10  # 如果右边放不下，就放在左边
        
        window.geometry(f"{width}x{height}+{x}+{y}")

    def center_window_relative_to_parent(self, window, parent, width, height):
        """相对于父窗口居中显示"""
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        window.geometry(f"{width}x{height}+{x}+{y}")

if __name__ == "__main__":
    app = BirthdayReminder()
    app.run() 