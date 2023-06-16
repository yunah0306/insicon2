import streamlit as st
# st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        max-width: 70%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
from PIL import Image
import requests
import base64
import json
import uuid
import time
import re


#네이버 clova ocr api 불러오기
def ocr_naver(image_file, api_url, secret_key):
    request_json = {
        'images': [
            {
                'format': 'jpg',
                'name': 'demo'
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = {'message': json.dumps(request_json).encode('UTF-8')}
    files = [('file', ("filename.jpg", image_bytes))]
    headers = {'X-OCR-SECRET': secret_key}

    response = requests.request("POST", api_url, headers=headers, data = payload, files = files)
    if response.status_code == 200:
        result = response.json() 
        text = '\n'.join([item['inferText'] for item in result['images'][0]['fields']])
        return text
    else:
        return "Error : " + response.text
    
# 전자영수증에서 추출한 텍스트를 통해 다회용기 여부 판별, 다회용기일 경우 즉시 포인트 지급하는 
# 추출한 텍스트에서 '다회용기'인 것 추출        
def extract_item_name(text):
#     lines = text.split("' '")
#     for line in lines:
        if '컵 할인' in text:
            return '다회용기를 사용하셨네요!'
        elif '개인컵' in text:
            return '다회용기를 사용하셨네요!'
        elif '텀블러' in text:
            return '다회용기를 사용하셨네요!'
#         elif re.search('다회용기', text):
#             return '다회용기를 사용하셨네요!'
        #else:
            #return '일회용기를 사용하셨네요. 재활용이 가능한 물품은 투입함에 넣어주세요!'
        return None

api_url = 'https://qbt6a09jgb.apigw.ntruss.com/custom/v1/22868/ac35c97ba497dcff3abfab41716ba8999a7cc322edd363f9ce1876512a1dd152/general'
secret_key = 'dVdKZmpqSWpRUnh3c3d2Vmd1ZE1tVVhZbXd4cVdVVnU='

if 'point' not in st.session_state:
    st.session_state['point'] = 0
    
#1. 영수증 인식 페이지 구상

# Sidebar selection
option = st.sidebar.selectbox(
      '메뉴',
    ('','영수증 인식하러 가기', '재활용품 분리배출 하러 가기')
)
if option =='영수증 인식하러 가기':
    st.subheader("🌱영수증 인식")
    

if option == '영수증 인식하러 가기':
    option2 = st.selectbox(
        '1️⃣영수증의 종류를 선택해주세요.',
        ('', '전자영수증', '실물영수증')
    )
    st.markdown("""
        <div style="background-color: #f6f5d0; color: #000000; padding: 10px;">
        실물 영수증 사용 시 80 point  <br>
        전자 영수증 사용 시 100 point  <br>
        하루 적립 가능 최대 300 point. <br>
        </div>
        """.format(st.session_state['point']), unsafe_allow_html=True)    
    if option2 == '전자영수증':
        option3 = st.selectbox(
            '2️⃣영수증을 불러와주세요.',
            ('', '영수증 촬영', '사진 업로드')
        )
        
        if option3 == '사진 업로드':

            # Image uploader
            uploaded_file = st.file_uploader('',type=["jpg", "png"])

            if uploaded_file is not None:
                # Display uploaded image
                image = Image.open(uploaded_file)
                st.image(image, caption='', use_column_width=True)

                # Convert to bytes
                image_bytes = uploaded_file.getvalue()

                # OCR
                text = ocr_naver(image_bytes, api_url, secret_key)

                # 다회용기 check
                if extract_item_name(text):
                    st.session_state['point'] += 100
                    st.success('다회용기를 사용하셨네요! 100 point가 적립되었습니다.')
                    st.markdown("""
                <div style="background-color: #ffffff; color: #0a3711; padding: 10px; border: 2px solid #0a3711;">
                    녹색 자매님의 point는 {}.
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True)
                    if st.button('추가 적립하러 가기'):
                        st.experimental_rerun()


# 재활용품 기계 화면
if option == '재활용품 분리배출 하러 가기':
    st.subheader("🌳재활용품 분리배출 하러 가기")
    theme_option = st.radio(
        "폐기물 종류를 선택해주세요.",
        ('플라스틱', '종이','유리병','캔')
    )

    if theme_option == '플라스틱':
        gown_option = st.radio(
            "플라스틱 종류를 선택해주세요.",
            ('카페 플라스틱 컵', '무색 플라스틱 음료', '유색 플라스틱 음료')
        )

        if gown_option == '무색 플라스틱 음료':
            if st.button('반납 방법 알아보기'):
                st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    안의 액체를 모두 버린 후, 라벨을 제거하고 최대한 압축하여 배출구 위에 올려주세요..
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True)                
#                 st.write('액체를 비우고 반환해주세요.')
#                 st.write('안의 액체를 모두 버린 후, 라벨을 제거하고 최대한 압축하여 배출구 위에 올려주세요.')

            weight = st.number_input("음료의 무게를 측정합니다.", min_value=0.0)
            if weight > 100.0:
                st.markdown("""
                <div style="background-color: #f6d0d1; color: #000000; padding: 10px;">
                    액체를 비우고 반환해주세요.
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True)                
#                 st.write('액체를 비우고 반환해주세요.')
            elif weight > 0:
                st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px; ">
                    투입이 완료되었습니다. 이제 휴대폰 앱의 QR 코드를 인식해주세요.
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True)
#                 st.write('이제 휴대폰 앱의 QR 코드를 인식해주세요.')

                if st.button('QR 코드 인식 안하기'):
                    st.write('QR 코드 인식을 건너뜁니다.')
                else:
                       qr_code = st.file_uploader("", type=["png", "jpg", "jpeg"])
                       if qr_code is not None:
                          st.write('QR 코드가 인식되었습니다.')
                          st.session_state['point'] += 25
                          st.write('25 포인트가 적립되었습니다.')
