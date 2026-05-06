# 双人成行 角色模型替换工具 (It Takes Two Model Swapper)

## 📦 项目结构

```
it-takes-two-model-tool/
├── main.py              # 程序入口
├── config.py            # 配置管理
├── scanner.py           # 游戏目录 & .pak 文件自动扫描
├── unpacker.py          # UnrealPak 解包封装
├── model_replacer.py    # 模型替换 & FBX 处理
├── repacker.py          # 资源封包 & 备份恢复
├── backup_manager.py    # 备份管理
├── ui/
│   ├── app.py           # 主窗口
│   ├── pages.py         # 向导页面
│   ├── widgets.py       # 自定义组件
│   └── theme.py         # 主题样式
└── utils/
    ├── path_utils.py    # 路径工具
    └── unreal_helpers.py# UE 文件格式辅助
```

## ⚙️ 前置依赖

```bash
# Python 3.11+
pip install customtkinter pillow
```

## 🚀 快速开始

```bash
python main.py
```

## 🔧 第三方工具需求

| 模块       | 依赖工具        | 获取地址                                        |
|-----------|----------------|-----------------------------------------------|
| 资源解包   | UnrealPak      | 引擎自带的 UnrealPak.exe / UE4Editor |
| 模型替换   | Blender (Python API) | https://www.blender.org/             |
| FBX 处理   | FBX SDK 或 Blender | https://www.blender.org/             |

## 📖 工作流程

```
[扫描游戏目录] → [选择 .pak 文件] → [解包资源]
    ↓
[导入 FBX 模型] → [骨骼重定向] → [材质匹配]
    ↓
[封包资源] → [自动备份原文件] → [替换完成]
```
