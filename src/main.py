from updater import AutoUpdater

class BirthdayReminder:
    def __init__(self):
        # 在初始化时添加
        self.updater = AutoUpdater()
        self.check_for_updates()
        
        # ... 其他初始化代码 ...

    def check_for_updates(self):
        """检查更新"""
        has_update, update_info = self.updater.check_for_updates()
        if has_update:
            self.show_update_dialog(update_info)

    def show_update_dialog(self, update_info):
        """显示更新对话框"""
        update_window = ctk.CTkToplevel(self.root)
        update_window.title("发现新版本")
        self.center_window_relative_to_parent(update_window, self.root, 300, 200)
        
        message = f"发现新版本 {update_info['version']}\n\n{update_info['description']}\n\n是否现在更新？"
        
        label = ctk.CTkLabel(update_window, text=message)
        label.pack(pady=20)
        
        def update():
            if self.updater.download_update(update_info):
                self.show_success("更新下载完成，程序将重启")
                update_window.after(1000, self.updater.apply_update)
            else:
                self.show_error("更新失败，请查看日志")
            update_window.destroy()
        
        button_frame = ctk.CTkFrame(update_window)
        button_frame.pack(fill="x", padx=20)
        
        update_btn = ctk.CTkButton(
            button_frame,
            text="更新",
            command=update
        )
        update_btn.pack(side="left", padx=10, expand=True)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="取消",
            command=update_window.destroy
        )
        cancel_btn.pack(side="left", padx=10, expand=True) 