import streamlit as st
from PIL import Image
import requests
import json
import time
import uuid
# import cv2
import tempfile

# ...

#네이버 OCR API 설정
api_url = "https://qbt6a09jgb.apigw.ntruss.com/custom/v1/22868/ac35c97ba497dcff3abfab41716ba8999a7cc322edd363f9ce1876512a1dd152/general"
secret_key = 'dVdKZmpqSWpRUnh3c3d2Vmd1ZE1tVVhZbXd4cVdVVnU='

# ...

def main():
    st.title("Ecollege")
    #b.영수증 종류 선택
    option2 = st.selectbox(
        '영수증 종류를 선택해주세요.',
        ('전자영수증', '실물영수증')
    )
#c. 전자영수증일 경우 캡쳐한 파일을 업로드, 실물영수증일 경우 직접 촬영, 그 후 다회용기를 사용했을 경우 10포인트(예시) 적립
    if option2 == '전자영수증':
        st.write('영수증을 불러와주세요.')
        uploaded_file = st.file_uploader('', type=["jpg", "png"])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='', use_column_width=True)
            image_bytes = uploaded_file.getvalue()
            text = ocr_naver(image_bytes)
            if '개인 컵' in text:
                add_points(10) 
                st.write('10포인트가 적립되었습니다.')
    
    elif option2 == '실물영수증':
        st.write('사진 촬영하러 가기')
        
        # 이미지 촬영
        capture = cv2.VideoCapture(0)
        ret, frame = capture.read()
        if ret:
            image = Image.fromarray(frame)
            st.image(image, caption='', use_column_width=True)
            
            # 촬영된 이미지를 임시 파일로 저장
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.close()
            image.save(temp_file.name)
            
            # 저장된 이미지 파일을 업로드한 후 포인트 
            uploaded_file = st.file_uploader('', type=["jpg", "png"], accept_multiple_files=False)
            if uploaded_file is not None:
                uploaded_image = Image.open(uploaded_file)
                st.image(uploaded_image, caption='', use_column_width=True)
                image_bytes = uploaded_file.getvalue()
                text = ocr_naver(image_bytes)
                if '개인 컵' in text:
                    add_points(10) 
                    st.write('10포인트가 적립되었습니다.')
        
        capture.release()
        cv2.destroyAllWindows()
        
    st.container()
    st.markdown("""
        <div style="background-color: #f6f5d0; color: #000000; padding: 10px;">
            실물 영수증 사용 시 80 point  <br>
            전자 영수증 사용 시 100 point  <br>
            하루 적립 가능 최대 300 point. <br>
        </div>
    """, unsafe_allow_html=True)

#b-* 문자 인식 함수 정의
def ocr_naver(image_bytes):
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

    response = requests.request("POST", api_url, headers=headers, data=payload, files=files)
    if response.status_code == 200:
        result = response.json()
        text = '\n'.join([item['inferText'] for item in result['images'][0]['fields']])
        return text
    else:
        return "Error : " + response.text

def add_points(amount):
    pass

if __name__ == '__main__':
    main()
