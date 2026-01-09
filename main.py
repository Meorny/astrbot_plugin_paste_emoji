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
        支持：系统黄豆表情、emoji字符(🐉)、数字ID
        """
        
        # 1. 获取引用消息
        chain = event.get_messages()
        reply = next((seg for seg in chain if isinstance(seg, Reply)), None)

        if not reply:
            yield event.plain_result("❌ 请先引用(回复)一条消息。")
            return

        # 2. 解析目标表情
        target_emoji = None
        
        # 情况A：用户发送了系统黄豆表情 (Face组件)
        face_component = next((seg for seg in chain if isinstance(seg, Face)), None)
        if face_component:
            target_emoji = str(face_component.id) # 转为字符串以防万一

        # 情况B：用户发送了文本 (数字ID 或 Unicode表情)
        if target_emoji is None:
            raw_text = event.message_str.replace("/贴表情", "").strip()
            if not raw_text:
                 yield event.plain_result("❓ 请指定要贴的表情。")
                 return
            target_emoji = raw_text

        # 3. 执行操作
        # 注意：这里我们使用 call_api 直接调用，绕过 AstrBot 可能存在的 int 类型检查
        # NapCat 对 set_msg_emoji_like 的 emoji_id 字段定义为 string 类型，支持 unicode
        try:
            logger.info(f"贴表情: msg_id={reply.id}, emoji={target_emoji}")
            
            await event.bot.call_api(
                "set_msg_emoji_like",
                message_id=reply.id,
                emoji_id=target_emoji  # 直接传 "🐉" 或 "123"
            )
            
        except Exception as e:
            logger.error(f"贴表情失败: {e}")
            yield event.plain_result(f"❌ 贴表情失败: {e}")
