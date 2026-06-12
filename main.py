import random
from typing import List, Dict, Optional

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent
import astrbot.api.message_components as Comp

from .group_member_store import GroupMemberStore

@register("astrbot_plugin_kotory", "kotory77", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context,config: Optional[Dict] = None):
        super().__init__(context)
        self.config = config if config else {}
        self.functions: List[str] = self.config.get("functions", [])
        self.member_store = GroupMemberStore()
        self.member_store = GroupMemberStore()
        
    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    @filter.command("功能")
    async def func(self, event: AstrMessageEvent):
        """这是一个 function 指令"""  # 这是 function 功能，可以查看能使用哪些功能
        if self.functions:
            # 将每个功能用换行符连接，在一个消息框内显示
            functions_list = "\n".join(self.functions)
            client = event.bot
            yield event.plain_result(f"可用功能:\n{functions_list}")
        else:
            yield event.plain_result("暂无可使用的功能")

    @filter.command("随机抽人")
    async def random_person(self, event: AstrMessageEvent):
        """这是一个随机抽人 指令"""  # 这是 function 功能，可以随机抽一个人
        try:
            group_id = str(event.get_group_id())
        except:
            yield event.plain_result(f"获取群号出错!")
            event.stop_event()
            return

        # 检查缓存是否有效
        if self.member_store.is_cache_valid(group_id):
            ret = self.member_store.get_group_members(group_id)
            if not ret:
                # 缓存标记有效但数据为空，重新获取
                need_fetch = True
            else:
                # yield event.plain_result("使用缓存数据")
                need_fetch = False
        else:
            need_fetch = True

        # 需要重新获取群成员列表
        if need_fetch:
            if event.get_platform_name() == "aiocqhttp":
                assert isinstance(event, AiocqhttpMessageEvent)
                client = event.bot  # 得到 client
                payloads = {
                    "group_id": int(group_id),
                    "no_cache": True
                }
                ret = await client.api.call_action('get_group_member_list', **payloads)  # 调用 协议端  API
                
                # 保存到文件
                self.member_store.save_group_members(group_id, ret)
                #yield event.plain_result("已更新群成员信息")

        length = len(ret)
        num = random.randint(0, length - 1)
        theone = ret[num]
        user_id = theone.get('user_id')
        nick_name = theone.get('nickname')
        avatar_url = f"https://q4.qlogo.cn/headimg_dl?dst_uin={user_id}&spec=640"
        chain = [
            Comp.At(qq=event.get_sender_id()),  # At 消息发送者
            Comp.Plain("这是你抽到的群友"),
            Comp.Image.fromURL(avatar_url),  # 从 URL 发送图片
            Comp.Plain(nick_name)
        ]
        yield event.chain_result(chain)

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""