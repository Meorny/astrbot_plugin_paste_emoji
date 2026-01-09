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
        功能：将指定的表情贴到引用的消息上
        """
        
        # 1. 获取消息链和引用对象
        chain = event.get_messages()
        reply = next((seg for seg in chain if isinstance(seg, Reply)), None)

        if not reply:
            # 如果没有引用消息，提示用户
            yield event.plain_result("❌ 请先引用(回复)一条消息，然后再发送此指令。")
            return

        # 2. 解析用户想要贴的表情 ID
        target_emoji_id = None
        
        # 优先检测：用户是否发送了系统表情组件 (Face)
        # 例如：/贴表情 [某个黄豆表情]
        face_component = next((seg for seg in chain if isinstance(seg, Face)), None)
        if face_component:
            target_emoji_id = face_component.id

        # 次级检测：解析纯文本参数
        # 例如：/贴表情 123  或者  /贴表情 🐖
        if target_emoji_id is None:
            # 获取去除指令后的纯文本内容
            raw_text = event.message_str.replace("/贴表情", "").strip()
            
            if not raw_text:
                 yield event.plain_result("❓ 请在指令后跟上一个表情或表情ID。")
                 return

            if raw_text.isdigit():
                # 如果是纯数字，转为 int (OneBot 标准协议通常只支持 int 类型的 ID)
                target_emoji_id = int(raw_text)
            else:
                # 如果是 Unicode 字符 (如 🐖) 或其他文本
                # 注意：标准的 OneBot v11 协议 set_msg_emoji_like 通常只接受 int 类型的系统表情 ID
                # 这里尝试直接透传，取决于底层适配器(LLOneBot/Lagrange/Go-CQHTTP)是否支持
                target_emoji_id = raw_text

        # 3. 执行贴表情操作
        try:
            logger.info(f"尝试对消息 {reply.id} 贴表情: {target_emoji_id}")
            
            # 调用核心 API
            await event.bot.set_msg_emoji_like(
                message_id=reply.id,
                emoji_id=target_emoji_id,
                set=True
            )
            
            # 可选：操作成功后不回复任何内容，或者回一个简单的确认
            # yield event.plain_result("✅") 
            
        except Exception as e:
            logger.error(f"贴表情失败: {e}")
            yield event.plain_result(f"❌ 贴表情失败：适配器可能不支持该类型表情或ID。\n错误信息: {e}")
