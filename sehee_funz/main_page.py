import streamlit as st
import pandas as pd

st.title('')
st.header('헤더헤더')
st.subheader('서브헤더')

my_site = st.text_input('텍스트인풋')
st.write(my_site)

if st.button(f'{my_site} 접속하기'):
    st.success(f'{my_site}접속 중...')