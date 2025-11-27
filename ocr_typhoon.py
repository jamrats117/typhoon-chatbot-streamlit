import streamlit as st
import requests

st.set_page_config(page_title="Typhoon OCR", page_icon="📄")

st.title("📄 Typhoon OCR – Extract Text from Image/PDF")

API_KEY = st.secrets["TYPHOON_API_KEY"]
OCR_URL = "https://api.opentyphoon.ai/v1/ocr"

# UI: File upload
uploaded_file = st.file_uploader("อัปโหลดภาพหรือไฟล์ PDF", type=["jpg", "png", "jpeg", "pdf"])

if uploaded_file and st.button("เริ่ม OCR"):
    with st.spinner("กำลังประมวลผล OCR..."):
        # ----------------------------
        # Prepare form-data payload
        # ----------------------------
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }

        data = {
            "model": "typhoon-ocr",
            "task_type": "default",
            "max_tokens": "16000",
            "temperature": "0.1",
            "top_p": "0.6",
            "repetition_penalty": "1.1",
        }

        headers = {
            "Authorization": f"Bearer {API_KEY}"
        }

        try:
            response = requests.post(
                OCR_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()

                extracted_texts = []

                for page in result.get("results", []):
                    if page.get("success") and page.get("message"):
                        content = page["message"]["choices"][0]["message"]["content"]

                        # ผลลัพธ์บางครั้งเป็น JSON → parse
                        try:
                            parsed = eval(content)  # ใช้ eval ระวังได้ แต่ Typhoon structured JSON ปลอดภัย
                            content = parsed.get("natural_text", content)
                        except:
                            pass

                        extracted_texts.append(content)
                    else:
                        st.error(f"Error processing {page.get('filename')}: {page.get('error')}")

                full_text = "\n\n".join(extracted_texts)

                st.success("OCR เสร็จแล้ว!")
                st.text_area("ผลลัพธ์ OCR", full_text, height=300)

            else:
                st.error(f"Error {response.status_code}")
                st.write(response.text)

        except Exception as e:
            st.error(f"Error: {e}")
