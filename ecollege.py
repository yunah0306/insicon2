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
  
  word_choice = ['다회용기','개인컵','다회용컵','컵할인','텀블러']

  count = 0
  used = []
  for word in hangul_words:
      for target_word in word_choice:
          if target_word in word:
            count += 1
            used.append(target_word)
  sentence = ', '.join(used)
  return sentence, count

  
  

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
  return predicted_label
  

  
  
if 'point' not in st.session_state:
  st.session_state['point'] = 0
  
### 앱 화면 ###  

## 메인 페이지 ##
st.title('🍀에코리지')
if 'user_point' not in st.session_state:
  st.session_state['user_point'] = 0

## 마이페이지 ##
user_name = st.sidebar.text_input("이름을 입력하세요", key="user_name_input")
if user_name:
  st.sidebar.text(f'🌱{st.session_state.user_name_input}님, Ecollege에 오신걸 환영합니다!')
campus = st.sidebar.radio('재학중인 학교를 선택하세요', ['서강대학교', '연세대학교' ,'이화여자대학교', '홍익대학교'])

  
  

## 영수증 인식 페이지 ##
option1 = st.sidebar.selectbox(
  '🌳실천하기',
('메뉴를 선택해주세요','영수증 인식하러 가기', '재활용품 분리배출 하러 가기'))

if option1 == '영수증 인식하러 가기':
  #option2 = '메뉴를 선택해주세요'
  st.subheader("🧾영수증 인식")
  st.markdown("""
    <div style="background-color: #dbead5; color: #000000; padding: 10px; text-align: center;">
    종이영수증 대신 전자영수증을 발급하면 환경 보호에 더 도움이 돼요!<br>
    전자영수증: 100point<br>
    종이영수증: 80point<br>
    하루 적립 가능 최대 포인트는 300point입니다
    </div>
    """.format(st.session_state['point']), unsafe_allow_html=True)
  st.write("")
  receipt_type = st.selectbox(
        '영수증 종류를 선택해주세요.',
        ('전자영수증', '종이영수증'))
  
  if receipt_type == '전자영수증':
    upload_file = st.file_uploader('전자영수증을 업로드해주세요', type=['jpg', 'png', 'jpeg'])
    if upload_file is not None:
      # 이미지 열기
      img = Image.open(upload_file)
      img = img.resize((256,512))
      st.image(img)
      # OCR
      with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload_file.name)[1]) as temp_file:
        img.save(temp_file.name,)
        sentence, count = extract_text(temp_file.name)
        point = 100 * count
        st.markdown("""
              <div style="background-color: #dbead5; color: #000000; padding: 10px; text-align: center;">
                  {}을(를) 이용하셨군요! {}포인트가 지급되었습니다!
              </div>
              """.format(sentence,point), unsafe_allow_html=True)
        user_point += point

  else:
    upload_file = st.file_uploader('종이영수증을 촬영해주세요 ', type=['jpg', 'png', 'jpeg'])
    if upload_file is not None:
        # 이미지 열기
        img = Image.open(upload_file)
        img = img.resize((256,512))
        st.image(img)
        # OCR
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(upload_file.name)[1]) as temp_file:
          img.save(temp_file.name,)
          sentence, count = extract_text(temp_file.name)
          point = 80 * count
          st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px; text-align: center;">
                    {}을(를) 이용하셨군요! {}포인트가 지급되었습니다!
                </div>
                """.format(sentence,point), unsafe_allow_html=True)
          user_point += point


## 재활용품 배출 페이지 ##  
if option1 == '재활용품 분리배출 하러 가기':
  # option2 = '메뉴를 선택해주세요'
  st.subheader("♻️재활용품 분리배출")
  if st.button("반납 방법 알아보기"):
    img = Image.open('안내 사진/음료 투입.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;text-align: center;">
                    음료는 아래에 있는 음료 투입구에 버려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/페트병 분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;text-align: center;">
                    페트병은 라벨을 제거하고 최대한 압축하여 배출구 위에 올려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/캔분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;text-align: center;">
                    캔은 찌그러뜨려서 올려주세요 
                </div>
                """.format(st.session_state['point']), unsafe_allow_html=True) 
    st.write("")
    img = Image.open('안내 사진/유리분리수거.png')
    img = img.resize((256, 256))
    st.image(img)
    st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;text-align: center;">
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
      predicted_label = classification(temp_file.name)
      price_dict = {'캔':30, '플라스틱': 20, '유리': 20}
      if predicted_label == '확인불가':
        st.markdown("""
                    <div style="background-color: #dbead5; color: #000000; padding: 10px;text-align: center;">
                        확인이 불가합니다. 올바르게 배출해주세요. 
                    </div>
                    """.format(st.session_state['point']), unsafe_allow_html=True) 
      else:
        st.markdown("""
                <div style="background-color: #dbead5; color: #000000; padding: 10px;text-align: center;">
                    {}을(를) 배출하셨습니다. {}포인트가 지급되었습니다!
                </div>
                """.format(predicted_label,price_dict[predicted_label]), unsafe_allow_html=True)
        user_point += price_dict[predicted_label]
    text_placeholder.empty()
    
    
## 사용 가능 지점 페이지 ##
option2 = st.sidebar.selectbox(
  '💰모은 포인트 사용하러 가기 GoGo',
('메뉴를 선택해주세요','사용 가능한 매장 보러가기', '자전거 타러가기'))

if option2 == '사용 가능한 매장 보러가기':
  option1 = '메뉴를 선택해주세요'
  if campus == '서강대학교':
    st.subheader(f"{campus}에서 사용 가능한 매장입니다")
    st.write("")
    img1 = Image.open('안내 사진/그라찌에.png')
    img2 = Image.open('안내 사진/공차.png')
    img3 = Image.open('안내 사진/본솔.png')
    img4 = Image.open('안내 사진/아이엔지.jpg')
    img5 = Image.open('안내 사진/커브.jpg')
    img6 = Image.open('안내 사진/컴포즈.png')
    img7 = Image.open('안내 사진/샐러디.png')
    img8 = Image.open('안내 사진/한솥.png')

    img1 = img1.resize((128,128))
    img2 = img2.resize((128,128))
    img3 = img3.resize((128,128))
    img4 = img4.resize((128,128))
    img5 = img5.resize((128,128))
    img6 = img6.resize((128,128))
    img7 = img7.resize((128,128))
    img8 = img8.resize((128,128))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(img1, caption='그라찌에')
        st.image(img4, caption='아이엔지')
        st.image(img7, caption='샐러디')
    with col2:
        st.image(img2, caption='공차')
        st.image(img5, caption='커피브레이크')
        st.image(img8, caption='한솥')
    with col3:
        st.image(img3, caption='본솔')
        st.image(img6, caption='컴포즈')
      
      
  if campus == '연세대학교':
    st.subheader(f"{campus}에서 사용 가능한 매장입니다")
    st.write("")
    img1 = Image.open('안내 사진/고를샘.png')
    img2 = Image.open('안내 사진/맛나샘.png')
    img3 = Image.open('안내 사진/부를샘.png')
    img4 = Image.open('안내 사진/하얀샘.png')

    img1 = img1.resize((128,128))
    img2 = img2.resize((128,128))
    img3 = img3.resize((128,128))
    img4 = img4.resize((128,128))

    col1, col2 = st.columns(2)
    with col1:
      st.image(img1, caption='고를샘')
      st.image(img2, caption='맛나샘')
    with col2:
      st.image(img3, caption='부를샘')
      st.image(img4, caption='하얀샘')
        
  if campus == '이화여자대학교':
    st.subheader(f"{campus}에서 사용 가능한 매장입니다")
    st.write("")
    img1 = Image.open('안내 사진/닥터로빈.png')
    img2 = Image.open('안내 사진/샐러디.png')
    img3 = Image.open('안내 사진/아이엔지.jpg')

    img1 = img1.resize((128,128))
    img2 = img2.resize((128,128))
    img3 = img3.resize((128,128))

    col1, col2, col3 = st.columns(3)
    with col1:
      st.image(img1, caption='닥터로빈')
    with col2:
      st.image(img2, caption='샐러디')
    with col3:
      st.image(img3, caption='아이엔지')
      
      
  if campus == '홍익대학교':
    st.subheader(f"{campus}에서 사용 가능한 매장입니다")
    st.write("")
    img1 = Image.open('안내 사진/그라찌에.png')
    img2 = Image.open('안내 사진/카페나무.png')
    img3 = Image.open('안내 사진/카페드림.png')

    img1 = img1.resize((128,128))
    img2 = img2.resize((128,128))
    img3 = img3.resize((128,128))

    col1, col2, col3 = st.columns(3)
    with col1:
      st.image(img1, caption='그라찌에')
    with col2:
      st.image(img2, caption='카페나무')
    with col3:
      st.image(img3, caption='카페드림')
    
    
    
    
if option2 == '자전거 타러가기':
  st.subheader("🚲아래에서 이용권을 구매해주세요")
  st.markdown("""
              <div style="background-color: #dbead5; color: #000000; padding: 20px 5px; font-size: 40px; text-align: center;">
                  30분 이용권: 500원
              </div>
              """.format(st.session_state['point']), unsafe_allow_html=True)
  st.write("")
  st.markdown("""
              <div style="background-color: #dbead5; color: #000000; padding: 20px 5px; font-size: 40px; text-align: center;">
                  1시간 이용권: 1000원
              </div>
              """.format(st.session_state['point']), unsafe_allow_html=True)
  st.write("")
  st.markdown("""
              <div style="background-color: #dbead5; color: #000000; padding: 20px 5px; font-size: 40px; text-align: center;">
                  2시간 이용권: 2000원
              </div>
              """.format(st.session_state['point']), unsafe_allow_html=True)
  
 
 

for i in range(8):
  st.sidebar.write("")
  
st.sidebar.subheader(f'현재 적립포인트는 {st.session_state["user_point"]}p입니다')
st.sidebar.markdown("""
    <div style="background-color: #dbead5; color: #000000; padding: 10px; text-align: center;">
    녹색자매님이 100p 적립했습니다!
    </div>
    """.format(st.session_state['point']), unsafe_allow_html=True)

