from astrbot.api import logger # 使用 astrbot 提供的 logger 接口
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult

@filter.permission_type(filter.PermissionType.ADMIN)
@filter.command("StopServeStart")
async def StopServeStart(self, event: AstrMessageEvent,StartTime: str):
    '''开始时间 以发送14:10为例，会在每天14：10拒绝服务''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
    logger.debug(f"收到开始消息,尝试设置在{StartTime}，停止LLM")
    
    yield event.plain_result(f"Hello, !") # 发送一条纯文本消息

@filter.permission_type(filter.PermissionType.ADMIN)
@filter.command("StopServeEnd")
async def StopServeEnd(self, event: AstrMessageEvent,EndTime: str):
    '''结束时间 以发送14:10为例，会在每天14：10开始服务''' # 这是 handler 的描述，将会被解析方便用户了解插件内容。非常建议填写。
    logger.debug(f"收到开始消息,尝试设置在{EndTime}，停止LLM")

@filter.event_message_type(filter.EventMessageType.ALL)