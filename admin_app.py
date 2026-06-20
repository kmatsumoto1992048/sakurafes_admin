
# 運営側 抽選管理アプリ（Streamlit）
# 1等・2等・3等の当選人数を毎回コントロール
# 当日の結果を today.json に保存
# 高齢者向け「代理入力モード」付き

import streamlit as st
import random
import json
from datetime import date
from pathlib import Path

st.set_page_config(page_title="運営側 抽選管理アプリ", layout="centered")
st.title("🎛 運営側 抽選管理アプリ")

DATA_FILE = Path("today.json")

# -----------------------------
# ユーティリティ
# -----------------------------
def format_num(n: int) -> str:
    """4桁ゼロ埋め表示"""
    return f"{n:04d}"

def load_today():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("history"), list):
                return data
            if isinstance(data, list):
                return {"history": data}
            if isinstance(data, dict):
                return {"history": [data]}
    return {"history": []}

def save_today(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# -----------------------------
# セクション1：当選人数の設定 & 抽選
# -----------------------------
st.header("① 当選人数の設定 と 抽選")

col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
with col1:
    n1 = st.number_input("1等の人数", min_value=0, max_value=10000, value=1, step=1)
with col2:
    n2 = st.number_input("2等の人数", min_value=0, max_value=10000, value=3, step=1)
with col3:
    n3 = st.number_input("3等の人数", min_value=0, max_value=10000, value=50, step=1)
with col4:
    draw_no = st.number_input("抽選回", min_value=1, max_value=100, value=1, step=1)

saved_data = load_today()
if "result" not in st.session_state:
    history = saved_data.get("history", [])
    st.session_state["result"] = history[-1] if history else None

if st.button("🎲 抽選を実行する", use_container_width=True):
    total_needed = n1 + n2
    if total_needed > 10000:
        st.error("1等＋2等の人数が 10,000 を超えています（4桁番号の総数を超過）。")
    else:
        # 1等：重複なし
        first = random.sample(range(10000), n1)

        # 2等：1等と重複なし
        remaining = list(set(range(10000)) - set(first))
        second = random.sample(remaining, n2)

        # 3等：重複OK
        third = [random.randint(0, 9999) for _ in range(n3)]

        result = {
            "draw_no": int(draw_no),
            "label": f"第{int(draw_no)}回",
            "date": str(date.today()),
            "first": first,
            "second": second,
            "third": third,
        }
        st.session_state["result"] = result
        st.success("抽選が完了しました。下に結果が表示されます。")

# -----------------------------
# セクション2：当日の結果表示 & 保存
# -----------------------------
st.header("② 当日の当選結果")

result = st.session_state.get("result")

if result:
    st.write(f"📅 抽選回：**{result.get('label', '未設定')}**  |  抽選日：**{result.get('date', '未設定')}**")

    first = result.get("first", [])
    second = result.get("second", [])
    third = result.get("third", [])

    st.subheader(f"1等（{len(first)}名）")
    if first:
        st.write(", ".join(format_num(n) for n in first))
    else:
        st.write("該当なし")

    st.subheader(f"2等（{len(second)}名）")
    if second:
        st.write(", ".join(format_num(n) for n in second))
    else:
        st.write("該当なし")

    st.subheader(f"3等（{len(third)}名）")
    if third:
        st.write(", ".join(format_num(n) for n in third))
    else:
        st.write("該当なし")

    if st.button("💾 当日の結果を保存（today.json）", use_container_width=True):
        saved_history = saved_data.get("history", [])
        saved_history = [item for item in saved_history if item.get("draw_no") != result.get("draw_no")]
        saved_history.append(result)
        saved_history.sort(key=lambda item: item.get("draw_no", 0))
        save_today({"history": saved_history})
        st.success("today.json に保存しました。お客様UIから参照されます。")

    if saved_data.get("history"):
        st.markdown("---")
        st.subheader("保存済みの抽選履歴")
        for item in saved_data.get("history", []):
            st.write(f"**{item.get('label', '第?回')} ({item.get('date', '未設定')})**")
            st.write(f"1等: {', '.join(format_num(n) for n in item.get('first', [])) or '該当なし'}")
            st.write(f"2等: {', '.join(format_num(n) for n in item.get('second', [])) or '該当なし'}")
            st.write(f"3等: {', '.join(format_num(n) for n in item.get('third', [])) or '該当なし'}")
            st.write("---")
else:
    st.info("まだ抽選結果がありません。「抽選を実行する」を押してください。")

# -----------------------------
# セクション3：代理入力モード（高齢者対応）
# -----------------------------
st.header("③ 代理入力モード（高齢者対応）")
st.caption("※ お客様の紙に印刷された番号を、運営側が代わりに入力して判定します。")

proxy_num = st.text_input("お客様の番号（4桁）を入力", max_chars=4)

if st.button("🔍 判定する", use_container_width=True):
    if not result:
        st.error("先に抽選を実行してください。")
    elif not proxy_num.isdigit() or len(proxy_num) != 4:
        st.error("4桁の数字で入力してください（例：0034）。")
    else:
        num_int = int(proxy_num)
        first = result.get("first", [])
        second = result.get("second", [])
        third = result.get("third", [])

        st.write(f"入力された番号：**{format_num(num_int)}**")

        if num_int in first:
            st.success("🎉 1等当選です！おめでとうございます")
        elif num_int in second:
            st.success("🎉 2等当選です！おめでとうございます")
        elif num_int in third:
            st.success("🎉 3等当選です！おめでとうございます")
        else:
            st.error("残念… はずれです。")
