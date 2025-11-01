# AstrBot 定时暂停服务插件

这是一个用于定时暂停 AstrBot 服务 LLM 功能的插件，可以在指定时间段内暂停 LLM 服务，适合需要在特定时间限制机器人使用的场景。

## 功能特性

- 🕐 定时暂停 LLM 服务
- 📅 支持跨天时间设置
- 💾 配置持久化存储
- 🎛️ WebUI 配置界面支持
- 🔧 管理员权限控制

## 安装方法

1. 将插件文件夹 `astrbot_plugin_shutdown` 放置在 `data/plugins/` 目录下
2. 在 AstrBot WebUI 的插件管理页面启用此插件
3. 重启 AstrBot 或重载插件

## 使用方法

### 命令控制（管理员权限）

#### 设置暂停开始时间
```
/StopServeStart 14:10
```
设置每天 14:10 开始暂停 LLM 服务

#### 设置暂停结束时间
```
/StopServeEnd 18:00
```
设置每天 18:00 结束暂停 LLM 服务

#### 查看当前状态
```
/StopServeStatus
```
查看暂停服务的当前状态和配置信息

#### 禁用暂停功能
```
/StopServeDisable
```
禁用定时暂停服务功能

### WebUI 配置

1. 打开 AstrBot WebUI
2. 进入插件管理页面
3. 找到 "shutdown" 插件，点击 "管理"
4. 在配置界面中可以设置：
   - 是否启用定时暂停功能
   - 暂停开始时间（HH:MM 格式）
   - 暂停结束时间（HH:MM 格式）

### 时间格式
- 使用 24 小时制，格式为 `HH:MM`

### 暂停期间行为
- 在暂停时间内，所有 LLM 请求都会被拒绝
- 用户会收到 "当前时间在暂停服务时间内，LLM服务暂时不可用。" 的提示

# 致谢 我是用这东西改的 AstrBot 定时重启插件
- Zhalslar 
- 仓库地址：https://github.com/Zhalslar/astrbot_plugin_restart