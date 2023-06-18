import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
import platform
from PIL import ImageFont, ImageDraw, Image
import time
import re
import tempfile
from matplotlib import pyplot as plt
# import cv2

import requests
import uuid
import time
import json

from tensorflow.keras.models import load_model

## OCR 인식 함수 ##
def extract_text(file):
  api_url = 'https://8cbdvua55p.apigw.ntruss.com/custom/v1/22878/18b029032c74f9dc3223fcfe629227edf8e8880be05ecf50148ea52dae003f79/general'
  secret_key = 'R1hjd3JEam9pT3ZRTmRNRkxPTG9MVWhqanpxQmRoeHk='

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
  files = [
    ('file',open(file,'rb'))
  ]
  headers = {
    'X-OCR-SECRET': secret_key
  }

  response = requests.request("POST", api_url, headers=headers, data = payload, files = files)
  hangul_pattern = re.compile('[가-힣]+')

  # 정규표현식 패턴에 매칭되는 모든 한글 단어를 추출하여 리스트에 저장
  hangul_words = hangul_pattern.findall(response.text)
  
  word_choice = ['다회용기','개인컵','다회용컵','컵할인']

  count = 0
  used = []
  for word in hangul_words:
      for target_word in word_choice:
          if target_word in word:
            count += 1
            used.append(target_word)
  sentence = ', '.join(used)
  point = 10 * count
  st.markdown("""
            <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                {}을(를) 이용하셨군요! {}포인트가 지급되었습니다!
            </div>
            """.format(sentence,point), unsafe_allow_html=True)
  
  

## 쓰레기 인식 함수 ##
def classification(image):
  model_path = 'model_2'

  model = load_model(model_path)
  
  # 예측
  f = image
  image_w = 64
  image_h = 64

  pixels = image_h * image_w * 3
  labels = ['캔','플라스틱','확인불가','유리']

  # labels = list(data_dict.keys())
  # data_dict = {'캔':can,'플라스틱':plastic,'확인불가':polluted,'유리':glass}
  img = Image.open(f)
  img = img.convert("RGB")
  img = img.resize((image_w, image_h))
  data = np.asarray(img)

  prediction = model.predict(np.expand_dims(data, axis=0))
  predicted_class_index = np.argmax(prediction)
  predicted_label = labels[predicted_class_index]
  price_dict = {'캔':30, '플라스틱': 20, '유리': 20}
  if predicted_label == '확인불가':
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                    확인이 불가합니다. 올바르게 배출해주세요. 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
  else:
    st.markdown("""
            <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                {}을(를) 배출하셨습니다. {}포인트가 지급되었습니다!
            </div>
            """.format(predicted_label,price_dict[predicted_label]), unsafe_allow_html=True)

  
  
if 'point' not in st.session_state:
  st.session_state['point'] = 0
  
### 앱 화면 ###  

## 메인 페이지 ##
st.title('에코리지')
st.header("Ecollege")


col1, col2 = st.columns([1, 1])
with col1:
    #st.image(img1, use_column_width=True)
    option1 = st.selectbox(
      '실천하기',
    ('서비스를 선택해주세요','영수증 인식하러 가기', '재활용품 분리배출 하러 가기'))
with col2:
    #st.image(img2, use_column_width=True)
    option2 = st.selectbox(
      '포인트 사용하기',
    ('메뉴를 선택해주세요','사용 가능한 지점 보러가기', '자전거 타러가기'))


## 영수증 인식 페이지 ##
if option1 == '영수증 인식하러 가기':
  st.subheader("🌱영수증 인식")
  st.markdown("""
        <div style="background-color: #dbead5; color: #000000; padding: 10px;">
        종이 영수증 대신 전자 영수증을 발급하면 환경 보호에 더 도움이 돼요!
        </div>
        """.format(st.session_state['point']), unsafe_allow_html=True)
  st.write("")
  receipt_type = st.selectbox(
        '영수증 종류를 선택해주세요.',
        ('전자영수증', '실물영수증'))
  
  if receipt_type == '전자영수증':
    upload_file = st.file_uploader('전자영수증을 업로드해주세요', type=['jpg', 'png', 'jpeg'])
  else:
    upload_file = st.file_uploader('실물영수증을 촬영해주세요 ', type=['jpg', 'png', 'jpeg'])
    
  if upload_file is not None:
    # 이미지 열기
    img = Image.open(upload_file)
    img = img.resize((256,512))
    st.image(img)
    # OCR
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload_file.name)[1]) as temp_file:
      img.save(temp_file.name,)
      extract_text(temp_file.name)

## 재활용품 배출 페이지 ##  
if option1 == '재활용품 분리배출 하러 가기':
  st.subheader("🌳재활용품 분리배출")
  if st.button("반납 방법 알아보기"):
    img = Image.open('안내 사진/음료 투입.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                    음료는 아래에 있는 음료 투입구에 버려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/페트병 분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                    페트병은 라벨을 제거하고 최대한 압축하여 배출구 위에 올려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/캔분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                    캔은 찌그러뜨려서 올려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/유리분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;">
                    유리병은 라벨과 뚜껑의 재질이 다를 경우 분리해서 배출해주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
  
  st.write("")
  upload_file = st.file_uploader('쓰레기를 투입구 위에 올려주세요',type=['jpg', 'png', 'jpeg'])
  text_placeholder = st.empty()
  if upload_file is not None:
    text_placeholder.text('이미지 인식을 시작합니다')
    # 이미지 출력
    img = Image.open(upload_file)
    img = img.resize((256,256))
    st.image(img)
    # 로딩 화면
    #with st.spinner('Wait for it...'):
      #time.sleep(3)
    # 이미지 인식
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload_file.name)[1]) as temp_file:
      img.save(temp_file.name,)
      classification(temp_file.name)
    text_placeholder.empty()
