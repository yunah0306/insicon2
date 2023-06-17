import streamlit as st

st.markdown(
    """
    <style>
    .reportview-container {
        background: linear-gradient(rgba(102, 234, 0, 0.73), rgba(102, 234, 0, 0.03));
        background-size: cover;
    }
    @media (max-width: 600px) {
        .reportview-container .markdown-text-container {
            font-size: 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

points = 300

    st.title("Ecollege")
    
    # 카드 내역 이미지 불러오기
    image_path = "식비_카드_이미지.jpg"
    image_url = "https://github.com/green-sisters/streamlit/raw/main/src/resource/c1.png"

    st.markdown('##실천하기')

    # 열 분할
    col1, col2 = st.beta_columns(2)
    
    # 첫 번째 열에 이미지와 클릭 이벤트 추가
    with col1:
        image_url1 = "이미지1_URL"
        st.image(image_url, use_column_width=True)
        if st.button("이미지1"):
            # 이미지1 클릭 시 이동할 페이지로 이동하는 코드
            st.write("이미지1 클릭: 페이지1로 이동")
    
    # 두 번째 열에 이미지와 클릭 이벤트 추가
    with col2:
        image_url2 = "이미지2_URL"
        st.image(image_url, use_column_width=True)
        if st.button("이미지2"):
            # 이미지2 클릭 시 이동할 페이지로 이동하는 코드
            st.write("이미지2 클릭: 페이지2로 이동")
