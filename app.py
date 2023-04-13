import streamlit as st
import pandas as pd
from transformers import (
    AutoModelForSequenceClassification,
    BertTokenizerFast,
)
import torch
import plotly.express as px
import os

def load_bert_model(model_version, model_dir, classes_num, device):
    tokenizer = BertTokenizerFast.from_pretrained(model_version, model_max_length=512)
    model = AutoModelForSequenceClassification.from_pretrained(
            model_dir, num_labels=classes_num
        ).to(device)
    model.eval()
    return tokenizer, model


classes_names = ['促銷','帳戶','其他','音樂','Myself','社群']  # 類別列表(依照CSV檔案的順序)

model_dir = os.path.join(os.getcwd(),"best_weight")


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
st.title("A Simple Streamlit Web App")

model_version = "bert-base-chinese"
tokenizer, model = load_bert_model(model_version, model_dir, len(classes_names), device)

with st.form("my_form"):
    text = st.text_area("Enter the text you want to inference!!", "", height=200)
    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        with torch.no_grad():
            text = tokenizer(text)
            text = torch.tensor(text["input_ids"]).unsqueeze(0).to(device)
            result = torch.nn.functional.softmax(model(text).logits)[0].tolist()
            result = [ item*100 for item in result]

        df = pd.DataFrame({"values":result, "class_name":classes_names})
        fig = px.pie(df, values='values', names='class_name', title='Prediction results')
        fig.update_traces(textposition='inside', textinfo='percent+label')

        st.plotly_chart(fig, use_container_width=True)