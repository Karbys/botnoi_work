import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd
from Uploadfile.upload import *
from openai import OpenAI, AsyncOpenAI
from Models.model import SentimentItem, TRUEItem, ADS, SentimentTrue, OutputOptions, Item, system_prompt, system_prompt_2
from io import BytesIO
import asyncio
import openai
import random

msg= upload_file()
# โหลดค่าจาก .env
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# st.write(openai_api_key)

if not openai_api_key:
    st.error("API Key is missing. Please check your .env file.")
else:
    st.success("API Key loaded successfully!")


# if msg:
#     col1 = [row[0] for row in msg]  # ดึงค่า col1 เก็บเป็น list
#     col2 = [row[1] for row in msg]  # ดึงค่า col2 เก็บเป็น list
#     col3 = [row[2] for row in msg]


# เพิ่ม keywords สำหรับแต่ละประเภท
keywords_dict = {
    OutputOptions.True_You: ["ร้านเด็ด", "คะแนน", "แต้ม", "จัดแคมเปญ", "ทรูพอยท์"],
    OutputOptions.True_Corp: ["คอร์ปอเรชั่น", "บริษัททรู", "ซีอีโอทรู", "ทรูดีแทค", "ทรู ดิจิทัล กรุ๊ป", "จับมือ", "ทรู-ดีแทค", "ทรู ต้อนรับ", "เอส เอฟ จับมือ ทรูดีแทค", "บริษัทฯ", "ลูกค้าทรู ดีแทค", "True  + Dtac"],
    OutputOptions.True_iService: ["true iservice", "ทรู เซอร์วิส", "แจ้งยอดชำระ","True Service", "ไอเซอร์วิส"],
    OutputOptions.True_Visions_NOW: ["TrueVisions Now", "TrueVisions Now Max", "รวมความบันเทิงจากช่องชั้นนำของทรูวิชั่นส์", "ทรูวิชั่นส์ นาว"],
    OutputOptions.True_Visions: ["ทรูวิชั่น", " truevision", "ทรูส์วิชั่น", "TRUE Vision"],
    OutputOptions.True_ID: ["True id", "ทรูไอดี", "TrueID", "trueid"],
    OutputOptions.True_Online: ["เน็ตบ้าน", "true fiber", "ทรูไฟเบอร์", "ติดตั้งเน็ตบ้าน", "Fiber Stand alone", "โปรย้ายค่ายเน็ตบ้าน", "WiFiที่บ้าน", "Fiber", "แพ็กเกจเน็ตบ้านไฟเบอร์True", "กล่องเราท์เตอร์แดง",
                                "แพคเกจเน็ตบ้านทรู", "สนใจติดตั้งเน็ทบ้าน", "True wifi"],
    OutputOptions.True_5G: ["เน็ตโทรศัพท์", "เปิดเน็ตเบอร์โทร", "อินเตอร์เน็ตแบบเติมเงิน", "ทรูมูฟ", "ซิม", "โปรโมชั่น", "เครือข่ายดีแทค", "เปิดสัญญาณ", "เน็ตห่วย",
                            "แพคเกจ", "เน็ททรู", "eSIM", "เบอร์รายเดือน", "เน็ตดีแทค", "trueshop", "เครื่องเปล่า", "เล่นเน็ตไม่อั้น", "คลื่น", "โปรข้ามเวลา", "รายเดือนTruemove", "รายเดือนทรู",
                            "เน็ตทรูกับดีแทค", "โทรมาขายโปร", "ทรูแบบเติมเงิน", "ทรูช่วยยกเลิกเน็ต", "เก็บค่าบริการโรมมิ่ง", "เน็ตทรูรายเดือนคุ้มๆ", "สมัครโรมมิ่งทรู", "เบอร์ทรู", "เติมเงินเน็ต", "truemoveH"],
    OutputOptions.True_: ["ค่ายแดง", "สัญญาณ", "true", "ย้ายค่าย", "ทรู", "ช่องทรู", "กล่องทรู", "พนักงานทรู", "เน็ต", "เจ้าหน้าที่ทรู", "ติดต่อทรู", "1242", "เปิดสัญญาณทรู", "กลยุทธ์ของทรู", "สาขาทรู", "ทรูช็อป"],
}

sentiment_exp = []
sentiment_val = []
IS_TRUE_exp = []
IS_TRUE_val = []
ADS_exp = []
ADS_val = []

classify_val = []
classify_new = []

    
# หากกรอก API Key ให้ทำการตั้งค่า

if openai_api_key:
    openai.api_key = openai_api_key
    model = "gpt-4o-mini"

    client = AsyncOpenAI(api_key=openai.api_key)

    async def function_llm(qa_test):
        # แปลงข้อความเดี่ยวเป็นลิสต์
        qa_list = qa_test.strip().split("\n")
        qa_cleaned = [line.split(". ", 1)[1] for line in qa_list if ". " in line]
        classy_final = []  # ลิสต์สำหรับเก็บผลลัพธ์

        def classify_text(text):
            # คำที่บ่งบอกว่าเป็นของ True
            true_keywords = ["ทรู", "true", "ค่ายแดง", "dtac", "ดีแทค", "1242"]

            # ถ้าไม่มีคำที่เกี่ยวกับ True เลย → Nan
            if not any(word in text.lower() for word in true_keywords):
                return "Nan"

            # ถ้ามีคำที่เกี่ยวกับ True → ใช้ keywords_dict classify
            for category, keywords in keywords_dict.items():
                if any(keyword.lower() in text.lower() for keyword in keywords):
                    return category

            return "Nan"  # ถ้าไม่เข้าหมวดหมู่ไหนเลยให้เป็น Nan


        # ใช้ keywords_dict และเงื่อนไข "ทรู" ก่อน
        for qa in qa_cleaned:
            classified_output = classify_text(qa)

            if classified_output is None:  # ถ้า keyword หาไม่เจอ ให้ใช้ LLM
                completion = await client.beta.chat.completions.parse(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt.format(phase=len(qa.split("\n")))},
                        {"role": "user", "content": qa},
                    ],
                    response_format=Item,
                )
                classy = completion.choices[0].message.parsed

            else:
                classy = classified_output  # ใช้ค่าที่ได้จาก keyword classify

            classy_final.append(classy)

        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt_2.format(phase=len(qa_test.split("\n")))},
                {"role": "user", "content": qa_test},
            ],
            response_format=SentimentTrue,
        )
        sentiment = completion.choices[0].message.parsed

        output = {
            "Sentiment": sentiment,
            "Classify": classy_final
        }

        return output

    async def main():
        batch_size = 10
        ql = []
        for i in range(0, len(msg), batch_size):
            info = msg[i:i+batch_size]
            info = [f"{j+1}. {info[j]}" for j in range(len(info))]
            ql.append("\n".join(info))

        tasks = [function_llm(ql[i]) for i in range(len(ql))]
        result = await asyncio.gather(*tasks)
        
        return result

    if st.button("Run Analysis"):
        with st.spinner("Loading... Please wait"):
            final_result = asyncio.run(main())  # รอผลจาก main()

        # เตรียม list สำหรับเก็บข้อมูล
        sentiment_exp = []
        sentiment_val = []
        IS_TRUE_exp = []
        IS_TRUE_val = []
        ADS_exp = []
        ADS_val = []

        classify_val = []
        classify_new = []
        # วนลูปผ่านข้อมูลแต่ละ event
        for event in final_result:
            # ดึงข้อมูลจาก Sentiment
            sentiment_exp.extend([item.explanation for item in event['Sentiment'].Sentiment])
            sentiment_val.extend([item.output for item in event['Sentiment'].Sentiment])

            # ดึงข้อมูลจาก IS_TRUE
            IS_TRUE_exp.extend([item.explanation for item in event['Sentiment'].IS_TRUE])
            IS_TRUE_val.extend([item.output for item in event['Sentiment'].IS_TRUE])

            # ดึงข้อมูลจาก ADS
            ADS_exp.extend([item.explanation for item in event['Sentiment'].ADS])
            ADS_val.extend([item.ADS for item in event['Sentiment'].ADS])


            # ดึงข้อมูลจาก Classify (วนลูปในลิสต์)
            classify_val.extend([
                cls.output.value if isinstance(cls, Item) else
                cls.value if isinstance(cls, OutputOptions) else
                cls
                for cls in event['Classify']
            ])

            # classify_val.extend([cls.output.value for cls in event['Classify']])
            # classify_val.extend([cls.output if isinstance(cls, Item) else cls for cls in event['Classify']])

        # แสดงผลข้อมูลในแต่ละ list
        min_length = len(msg)
        sentiment_exp = sentiment_exp[:min_length]
        sentiment_val = sentiment_val[:min_length]
        # ans = ans[:min_length]
        # human_ans = human_ans[:min_length]
        IS_TRUE_exp = IS_TRUE_exp[:min_length]
        IS_TRUE_val = IS_TRUE_val[:min_length]
        ADS_exp = ADS_exp[:min_length]
        ADS_val = ADS_val[:min_length]
        classify_val = classify_val[:min_length]

        st.write(
            len(sentiment_exp), len(sentiment_val), len(IS_TRUE_exp), len(IS_TRUE_val),
            len(ADS_exp), len(ADS_val), len(classify_val)
        )


        if len(sentiment_exp) == len(sentiment_val) == len(IS_TRUE_exp) == len(IS_TRUE_val) == len(ADS_exp) == len(ADS_val) == len(classify_val):
            # ใช้ st.columns เพื่อแยกพื้นที่ออกเป็นสองคอลัมน์
            col1, col2 = st.columns(2)

            # ส่วนของคอลัมน์ซ้าย (col1)
            with col1:
                st.subheader("Sentiment Analysis Summary")
                
                # นับจำนวน Sentiment
                sentiment_counts = {
                    "Positive": sentiment_val.count("Positive"),
                    "Neutral": sentiment_val.count("Neutral"),
                    "Negative": sentiment_val.count("Negative")
                }

                # แสดงจำนวน Sentiment
                st.write(f"Positive: {sentiment_counts['Positive']}")
                st.write(f"Neutral: {sentiment_counts['Neutral']}")
                st.write(f"Negative: {sentiment_counts['Negative']}")
                total_sentiment = sum(sentiment_counts.values())
                st.write(f"**TOTAL SENTIMENT: {total_sentiment}**")

                # นับจำนวน classify ที่ไม่ใช่ NaN และแสดงจำนวน
                classify_counts = {
                    "Nan": classify_val.count("Nan"),
                    "True": classify_val.count("True"),
                    "True 5G": classify_val.count("True 5G"),
                    "True Visions": classify_val.count("True Visions"),
                    "True Visions NOW": classify_val.count("True Visions NOW"),
                    "True Online": classify_val.count("True Online"),
                    "True You": classify_val.count("True You"),
                    "True ID": classify_val.count("True ID"),
                    "True iService": classify_val.count("True iService"),
                    "True Corp": classify_val.count("True Corp")
                }
                total_classify = sum(classify_counts.values())
                # แสดงจำนวน Classify
                for key, value in classify_counts.items():
                    st.write(f"{key}: {value}")
                st.write(f"**TOTAL CLASSIFY: {total_classify}**")

            # ส่วนของคอลัมน์ขวา (col2)
            with col2:
                st.subheader("Preview:")
                gpt_4o_mini = pd.DataFrame({
                    "Message": msg,
                    "LLM_Reason": sentiment_exp,
                    "LLM": sentiment_val,
                    "IS_TRUE_explain": IS_TRUE_exp,
                    "IS_TRUE_value": IS_TRUE_val,
                    "ADS_explain": ADS_exp,
                    "ADS_value": ADS_val,
                    "classify_value": classify_val,
                })
                st.write(gpt_4o_mini.head())  # แสดง preview

                # สร้างไฟล์ Excel ให้ดาวน์โหลด
                output = BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    gpt_4o_mini.to_excel(writer, index=False, sheet_name="Results")
                output.seek(0)

                # ปุ่มดาวน์โหลด
                st.download_button(
                    label="Download as Excel",
                    data=output,
                    file_name="output_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.write("Data mismatch, re-running data extraction.")
            # คุณสามารถเพิ่มโค้ดที่นี่เพื่อรันข้อมูลใหม่หากไม่ตรงกัน
else:
    st.info("Please enter your OpenAI API Key to proceed.")

