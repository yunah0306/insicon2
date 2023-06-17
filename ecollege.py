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
from io import BytesIO

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
  setence = ', '.join(used)
  point = 10 * count
  st.text(f"{setence}을(를) 이용하셨군요! {point}포인트가 지급되었습니다!")
  
  

## 쓰레기 인식 함수 ##
def classification(image):
  
  url = "https://drive.google.com/uc?id=1OUYxM6fI0Bf3C2L6V5ibg8_egOUHKbNo"
  model_path = keras.utils.get_file("classification_model", url, untar=False)
  model = keras.models.load_model(model_path)
  
  # 예측
  f = image
  image_w = 64
  image_h = 64

  pixels = image_h * image_w * 3

  x = []
  labels = ['캔', '플라스틱', '확인불가','유리']
  # labels = list(data_dict.keys())
  # data_dict = {'캔':can,'플라스틱':plastic,'확인불가':polluted,'유리':glass}
  img = Image.open(f)
  img = img.convert("RGB")
  img = img.resize((image_w, image_h))
  data = np.asarray(img)

  prediction = model.predict(np.expand_dims(data, axis=0))
  predicted_class_index = np.argmax(prediction)
  predicted_label = labels[predicted_class_index]
  st.write("Predicted label:", predicted_label)
  category = os.listdir('dataset')
  reverse_category =  sorted(category, reverse=True)
  st.write(category)
  st.write(reverse_category)
  st.write(labels)
  '''
  file_path = 'model_2'
  model = load_model(file_path)
  f = image
  category = os.listdir('dataset')
  category = sorted(category, reverse=True)

  image_w = 64
  image_h = 64

  pixels = image_h * image_w * 3

  x = []
  filenames = []

  img = Image.open(f)
  img = img.convert("RGB")
  img = img.resize((image_w, image_h))
  data = np.asarray(img)
  filenames.append(f)
  x.append(data)
  x = np.array(x)
  prediction_test = model.predict(x)

  file_index = 0
  result = []
  for i in prediction_test:
      label = i.argmax() # [0.000, 0.000, 0.000, ..., 0.000, 1.000, 0.000] 중 최대값 추출 즉,1값의 인덱스
      text_placeholder.empty()
      if category[label] == '확인불가':
        st.write(category)
        st.write(prediction_test)
        st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    확인이 불가합니다. 올바르게 배출해주세요. 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
      else:
        st.write(category)
        st.write(category[label])
        st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    {}을(를) 배출하셨습니다. 포인트가 지급되었습니다!
                </div>
                """.format(escape(category[label])), unsafe_allow_html=True)
   '''
  
if 'point' not in st.session_state:
  st.session_state['point'] = 0
  
### 앱 화면 ###  
st.title('에코리지')
st.header("Ecollege")

option = st.sidebar.selectbox(
      '메뉴',
    ('서비스를 선택해주세요','영수증 인식하러 가기', '재활용품 분리배출 하러 가기'))

if option == '영수증 인식하러 가기':
  st.subheader("🌱영수증 인식")
  st.markdown("""
        <div style="background-color: #f6f5d0; color: #000000; padding: 10px;">
        종이 영수증 대신 전자 영수증을 발급하면 환경 보호에 더 도움이 돼요!
        </div>
        """.format(st.session_state['point']), unsafe_allow_html=True)
  upload_file = st.file_uploader('사진을 업로드 해주세요', type=['jpg', 'png', 'jpeg'])
  if upload_file is not None:
    # 이미지 열기
    img = Image.open(upload_file)
    img = img.resize((256,512))
    st.image(img)
    # OCR
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload_file.name)[1]) as temp_file:
      img.save(temp_file.name,)
      extract_text(temp_file.name)

      
      
        
if option == '재활용품 분리배출 하러 가기':
  st.subheader("🌳재활용품 분리배출")
  if st.button("반납 방법 알아보기"):
    img = Image.open('안내 사진/음료 투입.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    음료는 아래에 있는 음료 투입구에 버려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/페트병 분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    페트병은 라벨을 제거하고 최대한 압축하여 배출구 위에 올려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/캔분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    캔은 찌그러뜨려서 올려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/유리분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #d0d1f6; color: #000000; padding: 10px;">
                    유리병은 라벨과 뚜껑의 재질이 다를 경우 분리해서 배출해주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
  
  st.write("")
  upload_file = st.file_uploader('쓰레기를 올려주세요',type=['jpg', 'png', 'jpeg'])
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
