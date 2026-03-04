import chainlit as cl
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

# หาตำแหน่งไฟล์ .env (ถอยหลังกลับไป 2 ชั้นจากไฟล์นี้)
# ไฟล์นี้อยู่ที่: .../frontend/app.py
# .parent -> .../frontend
# .parent.parent -> .../ (Root Project ที่มี .env)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
# ------------------------------------------------

# Configuration
# ตอนนี้ os.getenv จะมองเห็นค่าใน .env แล้ว แม้จะรัน Local
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@cl.on_chat_start
async def on_chat_start():
    """เมื่อเริ่ม Chat Session ใหม่"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                await cl.Message(
                    content=f"👋 สวัสดีครับ! ยินดีต้อนรับสู่ **{data.get('app_name', 'OfficeMate AI')}**\n\n"
                            "ผมช่วยตอบคำถามเกี่ยวกับองค์กรได้ครับ เช่น:\n"
                            "- นโยบายการลาป่วยเป็นอย่างไร\n"
                            "- สวัสดิการพนักงานมีอะไรบ้าง\n"
                            "- ขั้นตอนการขอเบิกค่ารักษาพยาบาล\n"
                            "- เวลาทำงานปกติของบริษัทคือกี่โมง\n"
                            "- วิสัยทัศน์ของบริษัทคืออะไร?\n"
                            "- มีสินค้าอะไรบ้าง?\n"
                            "- วิธีการสั่งซื้อสินค้า?\n"
                            "- สินค้ามีรับประกันกี่ปี?\n"
                            "- ช่องทางการชำระเงินมีอะไรบ้าง?\n\n"
                            "ลองถามมาได้เลยครับ! 🚀"
                ).send()
    except Exception as e:
        await cl.Message(
            content=f"⚠️ ไม่สามารถเชื่อมต่อ Backend ได้\n"
                    f"กรุณาตรวจสอบว่า Backend Server ทำงานอยู่\n\n"
                    f"Error: {str(e)}"
        ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """เมื่อผู้ใช้ส่งข้อความ"""
    user_message = message.content
    
    # ตัวแปรสำหรับเก็บข้อมูล
    thinking_content = ""
    is_thinking = False
    thinking_done = False
    msg = None  # Message สำหรับ stream คำตอบ
    thinking_msg = None  # Message สำหรับแสดง loading
    
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{API_BASE_URL}/chat/stream",
                json={"question": user_message},
                timeout=60.0
            ) as response:
                
                if response.status_code != 200:
                    await cl.Message(content=f"❌ Error: Server returned {response.status_code}").send()
                    return

                async for chunk in response.aiter_text():
                    if not chunk:
                        continue

                    # กรณีเริ่มเจอ tag เปิด <think>
                    if "<think>" in chunk:
                        is_thinking = True
                        chunk = chunk.replace("<think>", "")
                        
                        # แสดง loading message
                        thinking_msg = cl.Message(content="🤔 กำลังคิด...")
                        await thinking_msg.send()
                    
                    # กรณีเจอ tag ปิด </think>
                    if "</think>" in chunk:
                        is_thinking = False
                        thinking_done = True
                        parts = chunk.split("</think>")
                        thinking_content += parts[0]
                        
                        # --- ลบ loading message ---
                        if thinking_msg:
                            await thinking_msg.remove()
                        
                        # --- Thinking จบแล้ว: แสดง Step ก่อน ---
                        if thinking_content.strip():
                            async with cl.Step(name="Used Thinking Process", type="tool", show_input=False) as step:
                                step.output = thinking_content.strip()
                        
                        # สร้าง Message สำหรับ stream คำตอบ
                        msg = cl.Message(content="")
                        await msg.send()
                        
                        # ส่งส่วนคำตอบแรก (ถ้ามี)
                        if len(parts) > 1 and parts[1].strip():
                            await msg.stream_token(parts[1])
                        continue

                    # --- เก็บหรือ stream ข้อมูลตาม state ---
                    if is_thinking:
                        # ยังอยู่ใน thinking mode -> เก็บไว้ก่อน
                        thinking_content += chunk
                    else:
                        # ไม่ได้อยู่ใน thinking mode -> stream คำตอบเลย
                        if msg is None:
                            # กรณีไม่มี thinking เลย
                            msg = cl.Message(content="")
                            await msg.send()
                        await msg.stream_token(chunk)
        
        # Update message เมื่อ stream เสร็จ
        if msg:
            await msg.update()
        
    except httpx.TimeoutException:
        await cl.Message(content="⏱️ Request Timeout - กรุณาลองใหม่").send()
    except httpx.ConnectError:
        await cl.Message(content=f"❌ ไม่สามารถเชื่อมต่อ Backend ได้").send()
    except Exception as e:
        await cl.Message(content=f"❌ เกิดข้อผิดพลาด: {str(e)}").send()