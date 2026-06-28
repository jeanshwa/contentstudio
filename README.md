# 🚀 部署操作指南（小白也能搞定版）

---

## 第一部分：首次部署（只需做一次）

### Step 1：注册 GitHub 账号

1. 打开 https://github.com 点 **Sign up**
2. 用邮箱注册，设密码，选用户名
3. 验证邮箱，完成注册

### Step 2：创建一个新的 Repository（代码仓库）

1. 登录 GitHub 后，点右上角 **"+"** → **New repository**
2. 填写：
   - Repository name: `legal-content-studio`（或你喜欢的名字）
   - Description: `律师内容工厂`
   - 选 **Public**（Streamlit 免费版需要 public）
   - ✅ 勾选 **Add a README file**
3. 点 **Create repository**

### Step 3：上传文件到 GitHub

**方法一：网页上传（最简单，推荐新手）**

1. 进入你刚创建的 repo 页面
2. 点 **Add file** → **Upload files**
3. 把下载好的这三个文件拖进去：
   - `app.py`
   - `requirements.txt`
   - `README.md`（会覆盖自动生成的那个）
4. 页面底部点 **Commit changes**

5. 接下来创建 `.streamlit` 文件夹和配置文件：
   - 回到 repo 主页
   - 点 **Add file** → **Create new file**
   - 文件名输入：`.streamlit/config.toml`（输入斜杠时 GitHub 会自动创建文件夹）
   - 把 `config.toml` 的内容粘贴进去
   - 点 **Commit changes**

**完成后你的 repo 结构应该是：**

```
legal-content-studio/
├── .streamlit/
│   └── config.toml
├── app.py
├── requirements.txt
└── README.md
```

### Step 4：部署到 Streamlit Cloud

1. 打开 https://share.streamlit.io
2. 点 **Sign in with GitHub**，授权登录
3. 点 **New app**
4. 填写：
   - Repository: 选 `你的用户名/legal-content-studio`
   - Branch: `main`
   - Main file path: `app.py`
5. 点 **Deploy!**
6. 等 2-3 分钟，部署完成后你会得到一个网址，类似：
   `https://你的用户名-legal-content-studio.streamlit.app`

### Step 5：设置 API Key（推荐用 Secrets，不用每次输入）

1. 在 Streamlit Cloud 的 dashboard 里找到你的 app
2. 点右边 **"⋮"** → **Settings**
3. 点左侧 **Secrets**
4. 输入：
   ```
   ANTHROPIC_API_KEY = "sk-ant-你的key粘贴在这里"
   ```
5. 点 **Save**

> 💡 API Key 在 https://console.anthropic.com 获取

### Step 6：手机上使用

1. 手机浏览器打开你的 Streamlit 网址
2. **iPhone**: 点分享按钮 → 「添加到主屏幕」
3. **Android**: 点浏览器菜单 → 「添加到主屏幕」
4. 之后直接从主屏幕图标打开，像 app 一样用

---

## 第二部分：以后更新 App

### 方法一：直接在 GitHub 网页上改（最方便）

1. 打开你的 GitHub repo：`github.com/你的用户名/legal-content-studio`
2. 点击要修改的文件（比如 `app.py`）
3. 点右上角 **铅笔图标 ✏️**（Edit this file）
4. 修改内容
5. 点 **Commit changes** → 写个简短描述 → 确认

> ✅ Streamlit Cloud 会自动检测到变化，几分钟内自动重新部署，不需要你做任何操作！

### 方法二：本地修改后上传（大改动时推荐）

**第一次设置 Git（只需一次）：**

```bash
# Mac 打开 Terminal，Windows 打开 Git Bash
# 安装 Git：https://git-scm.com/downloads

# 配置你的身份
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的邮箱"

# 克隆你的 repo 到电脑
cd ~/Desktop
git clone https://github.com/你的用户名/legal-content-studio.git
cd legal-content-studio
```

**每次修改的流程：**

```bash
# 1. 进入项目文件夹
cd ~/Desktop/legal-content-studio

# 2. 修改文件（用任何编辑器打开 app.py 修改）

# 3. 查看改了什么
git status

# 4. 添加修改的文件
git add .

# 5. 提交修改（引号里写这次改了什么）
git commit -m "添加了新的话题分类"

# 6. 推送到 GitHub
git push
```

> ✅ push 完成后 Streamlit Cloud 自动重新部署

### 常见更新场景

**添加新话题分类：**
在 `app.py` 里找到 `TOPICS = {` 这一段，照着现有格式加一个新的就行。

**修改帖子风格：**
在 `app.py` 里找到 `platform_instructions` 字典，修改里面的提示词。

**换 AI 模型：**
找到 `model="claude-sonnet-4-6"` 改成你想用的模型。

---

## 常见问题

**Q: 部署失败怎么办？**
A: 在 Streamlit Cloud 点 app → Manage app → 查看 logs，通常是文件名或路径问题。

**Q: 要花钱吗？**
A: GitHub 和 Streamlit Cloud 都免费。只有 Anthropic API 按用量收费（生成一篇帖子大约 $0.01-0.03）。

**Q: 别人能看到我的 API Key 吗？**
A: 如果用 Streamlit Secrets 存储，不会。如果用侧边栏输入，只在你的浏览器里，也不会。

**Q: 能改成私有 repo 吗？**
A: 可以，但需要 Streamlit Cloud 的付费版。免费版只支持 public repo（代码公开但 API key 不会暴露）。

**Q: 手机上用着卡吗？**
A: 不会，Streamlit 服务器端运行，手机只负责显示。网速正常就流畅。
