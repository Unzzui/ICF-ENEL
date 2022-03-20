from csv import writer
from datetime import date
from operator import index
from turtle import color
from matplotlib.pyplot import text, title
from scipy.fftpack import ss_diff
import streamlit as st
import pandas as pd
import numpy as np
from re import S, sub
from PIL import Image
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import plotly_express as px


def i_med():
    st.title("Informe de medio ambiente en proceso de elaboración.")