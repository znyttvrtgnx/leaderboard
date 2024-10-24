import streamlit as st
import pandas as pd
from sklearn.metrics import roc_auc_score
import sqlite3


# ページのレイアウトを設定
st.set_page_config(
    page_title="リーダーボード",
    layout="wide", # wideにすると横長なレイアウトに
    initial_sidebar_state="expanded"
)

# タイトルの設定
st.title("リーダーボード")

with st.sidebar.form(key="form", clear_on_submit=True):
    name = st.text_input("ニックネームを入力してください(他の参加者にも表示されます)")
    uploaded_file = st.file_uploader("計算結果のCSVファイルをアップロードしてください", type='csv')
    submitted = st.form_submit_button("回答を送信")

if submitted:
    if uploaded_file is not None:
        # アップロードファイル読み込み
        uploaded_file.seek(0)
        df_res = pd.read_csv(uploaded_file)

        # 正解データを読み込み
        df_ref = pd.read_csv("正解_bin.csv")

        # AUC計算
        auc = roc_auc_score(df_ref["値"], df_res["値"])

        st.write(f"{name}: {auc}")

        # DBファイル読み込み
        conn = sqlite3.connect("lb.db")
        c = conn.cursor()

        # レコードを登録
        sql = f"""
            INSERT INTO leaderboard (name, auc) VALUES (
               :name 
            ,  :auc
            )
        """
        c.execute(sql, {"name": name, "auc": auc})
        conn.commit()

        # 現在の結果表示
        sql = f"""
            SELECT
                *
            FROM
                leaderboard
            ORDER BY
                auc DESC
        """

        df_lb = pd.read_sql(sql, conn)
        st.dataframe(df_lb)
        conn.close()
    else:
        st.alert("計算結果のファイルがアップロードされていません。") 
        st.stop()
