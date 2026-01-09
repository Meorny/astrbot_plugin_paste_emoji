import re
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
        
        # 优先级A：检测是否包含系统黄豆表情 (Face组件)
        face_component = next((seg for seg in chain if isinstance(seg, Face)), None)
        if face_component:
            target_emoji = str(face_component.id)
        
        # 优先级B：解析纯文本内容
        if target_emoji is None:
            # 获取纯文本
            plain_text = event.get_plain_text().strip()
            
            # 使用正则去除指令部分 (支持 /贴表情, 贴表情, 带有空格等情况)
            # 逻辑：匹配开头可选的斜杠 + 贴表情 + 可选的空格，替换为空
            cleaned_text = re.sub(r'^/??贴表情\s*', '', plain_text).strip()
            
            if not cleaned_text:
                 yield event.plain_result("❓ 请在指令后跟上一个表情(如: /贴表情 🔥)。")
                 return
            
            # 取出剩余文本的第一个“单词”作为表情（防止误读后面的长句）
            # 例如 "🔥 哈哈" -> "🔥"
            target_emoji = cleaned_text.split()[0]

        # 3. 执行操作
        try:
            logger.info(f"执行贴表情: msg_id={reply.id}, emoji={target_emoji}")
            
            # NapCat/LLOneBot 接口调用
            await event.bot.call_action(
                "set_msg_emoji_like",
                message_id=reply.id,
                emoji_id=target_emoji
            )
            
        except Exception as e:
            logger.error(f"贴表情异常: {e}")
            yield event.plain_result(f"❌ 失败: {e}")
