# 🚀 WorkSpace X

**你的专属工作空间一键启动引擎** | **Your Custom Workspace Launcher**

WorkSpace X 是一款基于 Python 构建的轻量级、高颜值的桌面生产力工具。它能够帮你把日常工作、学习或娱乐时需要同时打开的“一套组合”（如多个软件、特定的文件夹、经常访问的网址等）保存为 **“模式预设”**，并在你需要时**一键瞬间唤醒**整个工作流。

告别每天早上重复打开 IDE、查阅文档、启动内部服务的繁琐步骤。你的时间，应该花在真正重要的事情上。



---

## ✨ 核心特性

- 📦 **万物皆可统管**：支持添加任何本地文件、文件夹、`.exe` 可执行程序，甚至是网址（内置智能正则，完美识别公网域名、内网 IP 及 `localhost`）。
- 🎨 **双模高分屏 UI**：
  - 支持 **列表 (List)** 与 **网格 (Grid)** 视图无缝切换。
  - 底层接入 Windows 高分屏 (High DPI) 接口，字体图标刀切般锐利，拒绝模糊。
  - 网格模式下支持超长滑块 **无级实时缩放** 图标大小。
- 💾 **无限模式预设**：自由勾选应用，保存为“科研模式”、“开发模式”或“摸鱼模式”。点击预设，一键启动所有相关环境。
- ⚡ **丝滑的敏捷交互**：
  - **双击** 任意应用，执行无排队的“闪电启动”。
  - **右键** 任意应用，唤出上下文菜单，自由修改“显示备注”（别名），不破坏底层路径。
  - 支持全局鼠标滚轮操作与窗口比例自由拖拽记忆。
- 🛡️ **工业级防崩溃设计**：内置“黑匣子”全局异常捕获系统，彻底告别神秘闪退。

---
## 📸 界面截图
<img width="1279" height="756" alt="界面" src="https://github.com/user-attachments/assets/8d2a37e4-55ec-4bb5-a010-619a0ccc336e" />

---

## 📥 下载与使用 (普通用户)

本软件为**绿色免安装版**，数据完全本地化，不写注册表。

1. 前往本仓库的 [Releases 页面](https://github.com/SKYFIRE5836/WorkSpaceX/releases)。
2. 下载最新版本的 `WorkSpaceX.zip` 压缩包。
3. 将压缩包解压到你电脑上任意一个安全的目录（建议不要放在 C 盘根目录）。
4. 进入文件夹，直接双击 `WorkSpaceX.exe` 即可使用！

### 🎨 如何自定义左上角的软件图标？
在解压后的 `data` 文件夹中，有一张默认的 `icon.ico` (或 `icon.png`)。你只需要用自己喜欢的图片替换掉它（保持命名为 `icon.ico` 或 `icon.png`），下次打开软件时，窗口图标就会自动变成你的专属 Logo！

---

## 💻 源码运行与二次开发 (开发者)

如果你想亲自运行源码或进行二次开发，请确保你的电脑上安装了 **Python 3.8+**。

### 1. 克隆仓库
```bash
git clone https://github.com/SKYFIRE5836/WorkSpaceX.git
cd WorkSpaceX

```

### 2. 安装依赖库
本软件的 GUI 基于 Python 内置的 Tkinter，但涉及到 Windows 底层 API 和图像处理，需要安装以下第三方库：

```bash
pip install pywin32 Pillow

```

### 3. 运行程序

```bash
python WorkSpaceX.py

```

### 4. 重新打包
如果你修改了源码并想自己生成 .exe，请使用 PyInstaller：

```bash
pip install pyinstaller
pyinstaller -F -w -i icon.ico WorkSpaceX.py

```

### 📁 目录结构说明
```plaintext
WorkSpaceX/
├── WorkSpaceX.py          # 核心源代码
├── icon.ico               # 根目录预设图标
├── data/                  # 软件数据持久化目录 (第一次运行后自动生成)
│   ├── icon.ico           # 控制窗口左上角的自定义图标
│   ├── global_config.json # 全局配置文件 (保存了应用列表、视图状态、窗口宽度等)
│   └── profiles/          # 你的模式预设存档目录 (.json)
└── crash_log.txt          # 崩溃日志黑匣子 (仅在遭遇致命错误时生成)
```

### 📝 许可协议 (License)
本项目遵循 MIT License 开源协议。你可以自由地使用、修改和分发，但请保留原作者的版权声明。
