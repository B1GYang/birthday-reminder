# 创建 README.md
cat > README.md << EOL
# 生日提醒系统

一个简单的生日提醒工具，支持自动更新。

## 功能特点

- 生日提醒
- 自动更新
- 数据本地存储

## 安装步骤

1. 下载程序：
   - 访问 [Releases](https://github.com/B1GYang/birthday-reminder/releases)
   - 下载最新版本的 Source code (zip)
   - 解压到任意位置

2. 安装 Python：
   - 访问 [Python官网](https://www.python.org/downloads/)
   - 下载并安装 Python 3.11 或更高版本
   - 安装时勾选 "Add Python to PATH"

3. 安装程序：
   \`\`\`bash
   # 进入程序目录
   cd birthday-reminder

   # 创建虚拟环境
   python -m venv .venv

   # 激活虚拟环境（Windows）
   .venv\Scripts\activate

   # 安装依赖
   pip install -r requirements.txt
   \`\`\`

4. 运行程序：
   \`\`\`bash
   # 确保虚拟环境已激活
   python src/main.py
   \`\`\`

## 使用说明

1. 添加生日：
   - 点击"添加生日"按钮
   - 输入姓名和生日
   - 点击保存

2. 查看记录：
   - 点击"查看记录"按钮
   - 可以搜索、编辑或删除记录

3. 自动更新：
   - 程序启动时会自动检查更新
   - 有新版本时会提示更新

## 更新日志

### v1.0.0 (2024-03-21)
- 初始版本发布
- 基本的生日提醒功能
- 自动更新系统
- 数据本地存储
EOL

# 添加所有文件并提交
git add .
git commit -m "添加源代码文件和 README"
git push
