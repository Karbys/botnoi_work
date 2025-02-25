import streamlit as st
import pandas as pd
from Uploadfile.upload import *
import openai
from Models.model import SentimentItem, TRUEItem, ADS, SentimentTrue, OutputOptions, Item
from io import BytesIO
import asyncio


# เรียกใช้งานฟังก์ชัน
msg= upload_file()

# if msg:
#     col1 = [row[0] for row in msg]  # ดึงค่า col1 เก็บเป็น list
#     col2 = [row[1] for row in msg]  # ดึงค่า col2 เก็บเป็น list
#     col3 = [row[2] for row in msg]

# กำหนด API Key ของคุณ
openai_api_key = st.text_input("Enter your OpenAI API Key:")  # ใส่ API Key ของคุณตรงนี้

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

    system_prompt = """

    PERSONA:
    You're Social Analysis from TRUE Company, a telecom company with multiple partners.

    TASKS:
    1. Classify the product of from user quotes.

    INPUT SOURCE:
    Many phases gathered from news tablets and Facebook pages.


    **Classify Section**
    You are an AI model that classifies user quotes into one or more True Corporation services.
    Follow these classification rules with high accuracy and efficiency:

    🔹 **Level 1: ตรวจสอบว่ามี "ทรู" หรือ "true" ในข้อความหรือไม่**
    - **ถ้ามี** → ดำเนินการจำแนกตามหมวดหมู่ด้านล่าง
    - **ถ้าไม่มี** → ให้ classify เป็น `"Nan"` ทันที

    🔹 **Level 2: ตรวจสอบประเภทผลิตภัณฑ์ (ถ้ามี "ทรู" หรือ "true")**
    1. **True You**: หากพบ **"ร้านเด็ด"**, **"คะแนน"**, **"แต้ม"**, **"จัดแคมเปญ"**.
    2. **True Corp**: หากพบ **"คอร์ปอเรชั่น"**, **"บริษัททรู"**, **"ซีอีโอทรู"**, **"ทรูดีแทค"**, **"ทรู ดิจิทัล กรุ๊ป"**, **"จับมือ"**, **"ทรู-ดีแทค"**,
    **"ทรู ต้อนรับ"**, **"เอส เอฟ จับมือ ทรูดีแทค"**, **"บริษัทฯ"**, **"ลูกค้าทรู ดีแทค"**, **"True  + Dtac"**.
    3. **True iService**: หากพบ **"true iservice"**, **"ทรู เซอร์วิส"**, **"แจ้งยอดชำระ"**, **"True Service"**, **"ไอเซอร์วิส"**.
    4. **True Visions NOW**: หากพบ **"TrueVisions Now"**, **"TrueVisions Now Max"**, **"รวมความบันเทิงจากช่องชั้นนำของทรูวิชั่นส์"**.
    5. **True Visions**: หากพบ **"ทรูวิชั่น"**, **"truevision"**, **"ทรูส์วิชั่น"**, **"TRUE Vision"**.
    6. **True ID**: หากพบ **"True id"**, **"ทรูไอดี"**, **"TrueID"**, **"trueid"**.
    7. **True Online**: หากพบ **"เน็ตบ้าน"**, **"true fiber"**, **"ทรูไฟเบอร์"**, **"ติดตั้งเน็ตบ้าน"**, **"Fiber Stand alone"**, **"โปรย้ายค่ายเน็ตบ้าน"**,
    **"WiFiที่บ้าน"**, **"Fiber"**, **"แพ็กเกจเน็ตบ้านไฟเบอร์True"**, **"กล่องเราท์เตอร์แดง"**, **"แพคเกจเน็ตบ้านทรู"**, **"สนใจติดตั้งเน็ทบ้าน"**, **"True wifi"**.
    8. **True 5G**: หากพบ **"เน็ตโทรศัพท์"**, **"เปิดเน็ตเบอร์โทร"**, **"อินเตอร์เน็ตแบบเติมเงิน"**, **"ทรูมูฟ"**, **"ซิม"**, **"โปรโมชั่น"**,
    **"เครือข่ายดีแทค"**, **"เปิดสัญญาณ"**, **"มือถือเก่ามาเเลกใหม่"**, **"เน็ตห่วย"**, **"แพคเกจ"**, **"ย้ายค่าย"**, **"เน็ททรู"**, **"eSIM"**,
    **"เบอร์รายเดือน"**, **"เน็ตดีแทค"**, **"trueshop"**, **"ทรูช็อป"**, **"เล่นเน็ตไม่อั้น"**, **"คลื่น"**, **"โปรข้ามเวลา"**, **"รายเดือนTruemove"**,
    **"รายเดือนทรู"**, **"เน็ตทรูกับดีแทค"**, **"โทรมาขายโปร"**, **"ทรูแบบเติมเงิน"**, **"ทรูช่วยยกเลิกเน็ต"**, **"เก็บค่าบริการโรมมิ่ง"**,
    **"เน็ตทรูรายเดือนคุ้มๆ"**, **"สมัครโรมมิ่งทรู"**, **"เบอร์ทรู"**.
    9. **TRUE (General Category)**: หากพบ **"ค่ายแดง"**, **"สัญญาณ"**, **"true"**, **"ย้ายค่าย"**, **"ทรู"**, **"ช่องทรู"**, **"กล่องทรู"**,
    **"พนักงานทรู"**, **"เน็ต"**, **"เจ้าหน้าที่ทรู"**, **"ติดต่อทรู"**, **"1242"**, **"เปิดสัญญาณทรู"**, **"กลยุทธ์ของทรู"**, **"สาขาทรู"**
    ➜ **รวมถึงกรณีที่พูดถึง "เน็ต" แต่ไม่ได้ระบุว่าเป็น "เน็ตบ้าน" หรือ "เน็ตโทรศัพท์"**
    ➜ **ให้ classify เป็น `"TRUE"`**

    🔹 **Special Case: "Nan"**
    - หาก **ไม่มีคำว่า "ทรู" หรือ "true"** → ให้ classify เป็น `"Nan"` ทันที เช่น **"สอบถามเรื่องเก่าแลกใหม่ครับ เงื่อนไข รายละเอียดเป็นอย่างไรครับ"**

    """

    system_prompt_2 = """
    PERSONA:
    You're Social Analysis from TRUE Company, a telecom company with multiple partners.

    TO DO: !!MUST ANSWER EVERY PHASE **CANNOT SKIP OR RETURN NONE FOR ANY PHASE**
    ALWAYS RETURN OUTPUT FOR EVERY PHASE, EVEN IF IT'S UNKNOWN.

    TASKS:
    1. Find the sentiment of these user quotes and return the output format for all {phase} phases one-by-one.

    INPUT SOURCE:
    Many phases about TRUE gathered from news tablets and TRUE Facebook pages.

    BASIC CRITERIA FOR SENTIMENT ANALYSIS:
    - If it's just a commercial ad or commercial phase (e.g., phases with # are likely to be ads), classify it as Neutral.
    - If the phase benefits, compliments, or shows interest in TRUE Company or TRUE Products, classify it as Positive.
    - Conversely, if the phase is bad for TRUE Company's reputation, classify it as Negative.
    - If the phase shows interest such as "สนใจ", classify it as Positive.

    !!IMPORTANT: RETURN OUTPUT FOR EVERY INPUT PHASE. DO NOT OMIT ANY ITEM!!
    """

    model = "gpt-4o-mini"

    # [ โค้ดจำแนกประเภทของ True ]

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
                completion = openai.beta.chat.completions.parse(
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

        completion = await openai.beta.chat.completions.parse(
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

    batch_size = 10
    ql = []
    for i in range(0, len(msg), batch_size):
        info = msg[i:i+batch_size]
        info = [f"{j+1}. {info[j]}" for j in range(len(info))]
        ql.append("\n".join(info))

    # เพิ่มปุ่มที่ให้ผู้ใช้กดเพื่อเริ่มการวิเคราะห์
    if st.button('Run Analysis'):
        # เรียกใช้ฟังก์ชัน function_llm เมื่อผู้ใช้กดปุ่ม
        task = [function_llm(ql[i]) for i in range(len(ql))]
        result = await asyncio.gather(*task)

        # วนลูปผ่านข้อมูลแต่ละ event และเก็บผลลัพธ์
        for event in result:
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

        min_length = len(msg)
        sentiment_exp = sentiment_exp[:min_length]
        sentiment_val = sentiment_val[:min_length]
        IS_TRUE_exp = IS_TRUE_exp[:min_length]
        IS_TRUE_val = IS_TRUE_val[:min_length]
        ADS_exp = ADS_exp[:min_length]
        ADS_val = ADS_val[:min_length]
        classify_val = classify_val[:min_length]

        arrays_length = [len(sentiment_exp), len(sentiment_val), len(IS_TRUE_exp), len(IS_TRUE_val), len(ADS_exp), len(ADS_val), len(classify_val)]

        # st.write(len(sentiment_exp))
        # st.write(len(sentiment_val))
        # st.write(len(len(IS_TRUE_exp))
        # st.write(len(len(IS_TRUE_val))
        # st.write(len(ADS_exp))
        # st.write(len(ADS_val))
        # st.write(len(classify_val))

        # ถ้าไม่ครบให้แสดงข้อความแจ้งเตือน
        if len(set(arrays_length)) != 1:
            st.warning("Warning: Some arrays have different lengths. Please run the process again to ensure data consistency.")

        gpt_4o_mini = pd.DataFrame({
            "Message": msg,
            "LLM_Reason": sentiment_exp,
            "LLM": sentiment_val,
            # "Answer": col2,
            # "Human_Answer": human_ans,
            "IS_TRUE_explain": IS_TRUE_exp,
            "IS_TRUE_value": IS_TRUE_val,
            "ADS_explain": ADS_exp,
            "ADS_value": ADS_val,
            "classify_value": classify_val,
            # "true_classify": col3,
            # "my_classify": my_classify
        })
        # gpt_4o_mini["Result"] = gpt_4o_mini["LLM"] == gpt_4o_mini["Answer"]
        # # gpt_4o_mini["ResultHuman"] = gpt_4o_mini["LLM"] == gpt_4o_mini["Human_Answer"]
        # # gpt_4o_mini["true_classify"] = gpt_4o_mini["true_classify"].replace("TRUE", "True")
        # gpt_4o_mini["ResultClassify"] = gpt_4o_mini.apply(
        #     lambda row: True if row["true_classify"] == "True" and row["classify_value"] == "TRUE"
        #     else set(str(row["true_classify"]).split(", ")).issubset(set(str(row["classify_value"]).split(", "))),
        #     axis=1
        # )
        # gpt_4o_mini["ResultClassify_2"] = gpt_4o_mini.apply(
        #     lambda row: True if row["my_classify"] == "True" and row["classify_value"] == "TRUE"
        #     else set(str(row["my_classify"]).split(", ")).issubset(set(str(row["classify_value"]).split(", "))),
        #     axis=1
        # )
        
        col1, col2 = st.columns([1, 2])  # ฝั่งซ้าย (กว้าง), ฝั่งขวา (แคบ)
        with col1:
            # ✅ **แสดงจำนวน sentiment ทั้งหมด (positive, negative, neutral)**
            st.write("### Sentiment Summary")
            # นับจำนวนประเภท sentiment ในคอลัมน์ "LLM"
            sentiment_counts = gpt_4o_mini["LLM"].value_counts()
            # result_true_count = gpt_4o_mini["Result"].sum()
            # result_classify_true_count = gpt_4o_mini["ResultClassify"].sum()

            # แสดงจำนวนทั้งหมดและแยกเป็นประเภท
            st.write(f"Total Sentiments: {sentiment_counts.sum()}")
            st.write(f"Positive: {sentiment_counts.get('Positive', 0)}")
            st.write(f"Negative: {sentiment_counts.get('Negative', 0)}")
            st.write(f"Neutral: {sentiment_counts.get('Neutral', 0)}")

            # แสดงผลใน Streamlit
            # st.write("### Sentiment count True")
            # st.write(f"Total 'Result' True Count: {result_true_count}")

            # ✅ **แสดงจำนวน classify_value ทั้งหมด**
            st.write("### Classify Summary")
            classify_counts = gpt_4o_mini["classify_value"].value_counts(dropna=False)  # นับรวมค่า NaN ด้วย

            # แสดงจำนวนรวมทั้งหมด
            st.write(f"Total Classifications: {classify_counts.sum()}")

            # แสดงจำนวนของแต่ละประเภท
            for classify, count in classify_counts.items():
                st.write(f"{classify}: {count}")

            # st.write("### Classify count True")
            # st.write(f"Total 'ResultClassify' True Count: {result_classify_true_count}")

        with col2:
            st.write("### 📊 Preview of Analysis Results")
            st.dataframe(gpt_4o_mini)  # หรือใช้ st.table(gpt_4o_mini) ถ้าอยากได้แบบเรียบง่าย

            # ✅ **สร้างไฟล์ Excel และให้ดาวน์โหลด**
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                gpt_4o_mini.to_excel(writer, index=False, sheet_name="Analysis Results")
            output.seek(0)

            st.download_button(
                label="📥 Download Excel file",
                data=output,
                file_name="analysis_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Please enter your OpenAI API Key to proceed.")

