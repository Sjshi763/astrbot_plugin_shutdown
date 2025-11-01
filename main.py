import os
import json
import asyncio
from datetime import datetime, time
from astrbot.api import logger # 使用 astrbot 提供的 logger 接口
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from astrbot.core.utils.astrbot_path import get_astrbot_data_path

@register("astrbot_plugin_shutdown", "Sjshi763", "用命令定时暂停 AstrBot服务LLM，以解决某些大英雄要看腿", "1.0.0", "https://github.com/Zhalslar/astrbot_plugin_shutdown")
class ShutdownPlugin(Star):
    def __init__(self, context: Context) -> None:
        super().__init__(context)
        self.scheduler = AsyncIOScheduler()
        self.shutdown_enabled = False
        self.shutdown_start_time = None
        self.shutdown_end_time = None
        
        # 配置文件路径
        self.config_file = os.path.join(get_astrbot_data_path(), "astrbot_shutdown_config.json")
        
        # 加载配置
        self.load_config()
        
        # 初始化定时任务
        self.init_scheduler()
        
        # 启动调度器
        self.scheduler.start()
        
        logger.info("Shutdown plugin initialized.")

    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.shutdown_enabled = config.get('enabled', False)
                    self.shutdown_start_time = config.get('start_time')
                    self.shutdown_end_time = config.get('end_time')
                    logger.info(f"Loaded shutdown config: enabled={self.shutdown_enabled}, start_time={self.shutdown_start_time}, end_time={self.shutdown_end_time}")
            else:
                self.save_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def save_config(self):
        """保存配置文件"""
        try:
            config = {
                'enabled': self.shutdown_enabled,
                'start_time': self.shutdown_start_time,
                'end_time': self.shutdown_end_time
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            logger.info("Saved shutdown config")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def init_scheduler(self):
        """初始化定时任务"""
        if self.shutdown_enabled and self.shutdown_start_time and self.shutdown_end_time:
            # 添加开始暂停任务
            self.scheduler.add_job(
                self.start_shutdown,
                'cron',
                hour=int(self.shutdown_start_time.split(':')[0]),
                minute=int(self.shutdown_start_time.split(':')[1]),
                id='start_shutdown'
            )
            
            # 添加结束暂停任务
            self.scheduler.add_job(
                self.end_shutdown,
                'cron',
                hour=int(self.shutdown_end_time.split(':')[0]),
                minute=int(self.shutdown_end_time.split(':')[1]),
                id='end_shutdown'
            )
            
            logger.info(f"Scheduled shutdown: {self.shutdown_start_time} - {self.shutdown_end_time}")

    async def start_shutdown(self):
        """开始暂停服务"""
        logger.info("Starting LLM service shutdown")
        self.shutdown_enabled = True
        self.save_config()

    async def end_shutdown(self):
        """结束暂停服务"""
        logger.info("Ending LLM service shutdown")
        self.shutdown_enabled = False
        self.save_config()

    def is_shutdown_time(self):
        """检查当前是否在暂停时间内"""
        if not self.shutdown_enabled or not self.shutdown_start_time or not self.shutdown_end_time:
            return False
            
        now = datetime.now().time()
        start_time = datetime.strptime(self.shutdown_start_time, "%H:%M").time()
        end_time = datetime.strptime(self.shutdown_end_time, "%H:%M").time()
        
        # 处理跨天情况
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:
            return now >= start_time or now <= end_time

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("StopServeStart")
    async def StopServeStart(self, event: AstrMessageEvent, start_time: str):
        '''开始时间 以发送14:10为例，会在每天14：10拒绝服务''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
        logger.debug(f"收到开始消息,尝试设置在{start_time}，停止LLM")
        
        try:
            # 验证时间格式
            datetime.strptime(start_time, "%H:%M")
            self.shutdown_start_time = start_time
            self.shutdown_enabled = True
            
            # 重新调度任务
            self.scheduler.remove_all_jobs()
            self.init_scheduler()
            
            self.save_config()
            yield event.plain_result(f"已设置暂停开始时间: {start_time}")
        except ValueError:
            yield event.plain_result("时间格式错误，请使用 HH:MM 格式，例如：14:10")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("StopServeEnd")
    async def StopServeEnd(self, event: AstrMessageEvent, end_time: str):
        '''结束时间 以发送14:10为例，会在每天14：10开始服务''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
        logger.debug(f"收到结束消息,尝试设置在{end_time}，开始服务")
        
        try:
            # 验证时间格式
            datetime.strptime(end_time, "%H:%M")
            self.shutdown_end_time = end_time
            self.shutdown_enabled = True
            
            # 重新调度任务
            self.scheduler.remove_all_jobs()
            self.init_scheduler()
            
            self.save_config()
            yield event.plain_result(f"已设置暂停结束时间: {end_time}")
        except ValueError:
            yield event.plain_result("时间格式错误，请使用 HH:MM 格式，例如：14:10")

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("StopServeStatus")
    async def StopServeStatus(self, event: AstrMessageEvent):
        '''查看当前暂停服务状态'''
        status = "已启用" if self.shutdown_enabled else "已禁用"
        current_time = datetime.now().strftime("%H:%M")
        is_shutdown = "是" if self.is_shutdown_time() else "否"
        
        status_msg = f"暂停服务状态: {status}\n"
        status_msg += f"当前时间: {current_time}\n"
        status_msg += f"是否在暂停时间内: {is_shutdown}\n"
        
        if self.shutdown_start_time:
            status_msg += f"暂停开始时间: {self.shutdown_start_time}\n"
        else:
            status_msg += f"暂停开始时间: 未设置\n"
            
        if self.shutdown_end_time:
            status_msg += f"暂停结束时间: {self.shutdown_end_time}"
        else:
            status_msg += f"暂停结束时间: 未设置"
        
        yield event.plain_result(status_msg)

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("StopServeDisable")
    async def StopServeDisable(self, event: AstrMessageEvent):
        '''禁用暂停服务功能'''
        self.shutdown_enabled = False
        self.scheduler.remove_all_jobs()
        self.save_config()
        yield event.plain_result("已禁用暂停服务功能")

    @filter.on_llm_request()
    async def on_llm_request(self, event: AstrMessageEvent, req):
        """LLM请求钩子，在暂停时间内拒绝服务"""
        if self.is_shutdown_time():
            logger.info("LLM service is currently shutdown, rejecting request")
            # 设置一个空的响应，阻止LLM请求
            req.prompt = ""
            # 发送拒绝消息
            await event.send(event.plain_result("当前时间在暂停服务时间内，LLM服务暂时不可用。"))

    async def terminate(self):
        """插件终止时清理资源"""
        self.scheduler.shutdown()
        logger.info("Shutdown plugin terminated.")
