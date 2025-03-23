# บอท Discord สำหรับ Exaroton

นี่คือบอท Discord ที่ใช้ในการจัดการเซิร์ฟเวอร์ Minecraft ผ่าน API ของ Exaroton บอทนี้สามารถเริ่ม หยุด รีสตาร์ทเซิร์ฟเวอร์ ตรวจสอบสถานะเซิร์ฟเวอร์ และอื่นๆ ได้

## คุณสมบัติ

- แสดงรายการเซิร์ฟเวอร์ทั้งหมดของ Exaroton
- ตรวจสอบสถานะของเซิร์ฟเวอร์
- เริ่ม หยุด และรีสตาร์ทเซิร์ฟเวอร์
- ตรวจสอบเครดิตที่เหลือในบัญชี Exaroton
- ส่งคำสั่งไปยังคอนโซลของเซิร์ฟเวอร์

## ข้อกำหนดเบื้องต้น

- Python 3.6 ขึ้นไป
- โทเค็นบอท Discord
- คีย์ API ของ Exaroton

## การติดตั้ง

1. โคลนโปรเจคนี้:
    ```sh
    git clone https://github.com/jakkapat-448/exaroton-discord-bot.git
    cd exaroton-discord-bot
    ```

2. ติดตั้งแพ็คเกจที่จำเป็น:
    ```sh
    pip install -r requirements.txt
    ```

3. สร้างไฟล์ `.env` ในไดเรกทอรีหลักและเพิ่มโทเค็นบอท Discord และคีย์ API ของ Exaroton:
    ```env
    BOT_TOKEN=your_discord_bot_token
    EXAROTON_API_KEY=your_exaroton_api_key
    ```

## การใช้งาน

1. รันบอท:
    ```sh
    python exarotonBot.py
    ```

2. เชิญบอทเข้าร่วมเซิร์ฟเวอร์ Discord ของคุณและใช้คำสั่งต่อไปนี้:
    - `!exaroton servers` - แสดงรายการเซิร์ฟเวอร์ทั้งหมด
    - `!exaroton status <server_id>` - แสดงสถานะของเซิร์ฟเวอร์
    - `!exaroton start <server_id>` - เริ่มเซิร์ฟเวอร์
    - `!exaroton stop <server_id>` - หยุดเซิร์ฟเวอร์
    - `!exaroton restart <server_id>` - รีสตาร์ทเซิร์ฟเวอร์
    - `!exaroton credits` - แสดงเครดิตที่เหลือในบัญชี Exaroton
    - `!exaroton cmd <server_id> <command>` - ส่งคำสั่งไปยังคอนโซลของเซิร์ฟเวอร์

## ใบอนุญาต

โปรเจคนี้ได้รับอนุญาตภายใต้ MIT License.
