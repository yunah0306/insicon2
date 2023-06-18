img1 = Image.open("안내 사진/영수증픽토그램.jpg")
img1 = img1.resize((256, 256))
img2 = Image.open("안내 사진/재활용픽토그램.png")
img2 = img2.resize((256, 256))

col1, col2 = st.columns([1, 1])
with col1:
    st.image(img1, use_column_width=True)
    checkbox1 = st.checkbox('영수증 인식하러 가기')
with col2:
    st.image(img2, use_column_width=True)
    checkbox2 = st.checkbox('재활용품 분리배출 하러 가기')
    
if checkbox1:
  checkbox2 = False
  st.write('영수증 인식하러 가볼까요?')
if checkbox2:
  checkbox1 = False
  st.write('재활용품 분리배출하러 가볼까요?')
