from astrbot.api.star import Context, Star
from astrbot.api.event import filter
from astrbot.api import logger
from astrbot.core.message.components import Reply, Face
from astrbot.core.platform.sources.aiocqhttp.aiocqhttp_message_event import AiocqhttpMessageEvent

class PasteEmojiPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("贴表情")
    async def paste_emoji(self, event: AiocqhttpMessageEvent):
        """
        指令：/贴表情 [表情/ID]
        """
        # 1. 获取引用消息
        chain = event.get_messages()
        reply = next((seg for seg in chain if isinstance(seg, Reply)), None)

        if not reply:
            yield event.plain_result("❌ 请先引用(回复)一条消息。")
            return

        # 2. 解析目标表情
        target_emoji = None
        
        # 情况A：用户发送了系统黄豆表情
        face_component = next((seg for seg in chain if isinstance(seg, Face)), None)
        if face_component:
            target_emoji = str(face_component.id)

        # 情况B：用户发送了文本 (数字ID 或 Unicode表情)
        if target_emoji is None:
            raw_text = event.message_str.replace("/贴表情", "").strip()
            if not raw_text:
                 yield event.plain_result("❓ 请指定要贴的表情。")
                 return
            target_emoji = raw_text

        # 3. 执行操作 (修复点)
        try:
            logger.info(f"贴表情: msg_id={reply.id}, emoji={target_emoji}")
            
            # 修复：使用 call_action，并直接传入关键字参数 (message_id=..., emoji_id=...)
            # 不要传字典，也不要用 call_api (部分版本实现有问题)
            await event.bot.call_action(
                "set_msg_emoji_like",
                message_id=reply.id,
                emoji_id=str(target_emoji)  # 确保是字符串，NapCat 支持 Unicode 字符
            )
            
        except Exception as e:
            logger.error(f"贴表情失败: {e}")
            yield event.plain_result(f"❌ 贴表情失败: {e}")
