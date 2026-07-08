from pathlib import Path

import streamlit as st
from supabase import create_client

# Supabase接続
SUPABASE_URL = "https://axhpfaupxcdpjxokmtxl.supabase.co"
SUPABASE_KEY = "sb_publishable_aMFDA6pKPiWKW55zjtW-_A_tg8isXjj"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

JICHIKAI_LIST_PATH = Path(__file__).parent / "jichikai_list.txt"
JICHIKAI_LIST = [
    line.strip()
    for line in JICHIKAI_LIST_PATH.read_text(encoding="utf-8").splitlines()
    if line.strip()
]


def get_ticket_type_label(ticket_type: str) -> str:
    return "A券（会員）" if ticket_type == "A" else "B券（来場者）" if ticket_type == "B" else "不明な券種"


def is_valid_ticket_type(ticket_type: str) -> bool:
    return ticket_type in ("A", "B")

st.set_page_config(page_title="さくら祭り 抽選", page_icon="🌸", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Zen Maru Gothic', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #fff5f8 0%, #ffe4ee 50%, #ffd6e6 100%);
}

.sakura-header {
    text-align: center;
    padding: 1.75rem 1rem 1.25rem;
    margin-bottom: 1.25rem;
    background: linear-gradient(135deg, #ffb6c9 0%, #ff9ebb 100%);
    border-radius: 20px;
    box-shadow: 0 6px 20px rgba(232, 119, 154, 0.25);
}
.sakura-header h1 {
    color: #ffffff;
    font-size: 1.6rem;
    margin: 0;
    text-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
.sakura-header p {
    color: #fff0f4;
    margin: 0.35rem 0 0;
    font-size: 0.9rem;
}

div[data-testid="stVerticalBlock"][style*="border"] {
    background: #ffffff;
    border-radius: 18px !important;
    padding: 1rem !important;
    box-shadow: 0 4px 16px rgba(232, 119, 154, 0.15);
}

.stButton > button {
    background: linear-gradient(135deg, #ff8fab 0%, #e8779a 100%);
    color: white;
    border: none;
    border-radius: 999px;
    padding: 0.6rem 1.5rem;
    font-weight: 700;
    box-shadow: 0 4px 12px rgba(232, 119, 154, 0.35);
    transition: transform 0.15s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    color: white;
}

.ticket-number-display {
    text-align: center;
    margin: 0.5rem 0 1rem;
}
.ticket-number-display .label {
    font-size: 1rem;
    color: #a85a72;
    font-weight: 700;
}
.ticket-number-display .number {
    font-size: 3rem;
    font-weight: 700;
    color: #e8779a;
    letter-spacing: 0.05em;
    line-height: 1.2;
}
</style>

<div class="sakura-header">
    <h1>🌸 さくら祭り　抽選番号登録＆当選確認</h1>
</div>
""", unsafe_allow_html=True)

# URLパラメータから券番号を取得
params = st.query_params
ticket_number = params.get("ticket", [""])
if isinstance(ticket_number, list):
    ticket_number = ticket_number[0] if ticket_number else ""

ticket_type = ticket_number[0].upper() if ticket_number else ""

if not ticket_number:
    st.error("QRコードから正しくアクセスしてください。")
    st.stop()

if not is_valid_ticket_type(ticket_type):
    st.error("無効な券番号です。QRコードを確認してください。")
    st.stop()

# 登録済みかチェック
existing = supabase.table("registration").select("*").eq("ticket_number", ticket_number).execute()

# 発表状況を確認
draw_status = supabase.table("draw_status").select("*").eq("is_published", True).order("round").execute()

# -----------------------------
# 登録済みの場合 → 当選確認画面
# -----------------------------
if existing.data:
    record = existing.data[0]
    with st.container(border=True):
        st.markdown(f"""
        <div class="ticket-number-display">
            <div class="label">登録済み</div>
            <div class="number">{ticket_number}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 最新の結果を確認する", use_container_width=True):
            st.rerun()

        if not draw_status.data:
            st.info("⏳ まだ抽選結果が発表されていません。しばらくお待ちください。")
        else:
            st.header("🎯 当選確認")
            for draw in draw_status.data:
                round_num = draw["round"]
                st.subheader(f"第{round_num}回抽選")

                result = supabase.table("registration").select("prize_rank").eq("ticket_number", ticket_number).eq("draw_round", round_num).execute()

                if result.data and result.data[0]["prize_rank"]:
                    rank = result.data[0]["prize_rank"]
                    st.success(f"🎉 {rank}当選です！おめでとうございます！")
                else:
                    st.error("残念… はずれです。")

# -----------------------------
# 未登録の場合 → 登録画面
# -----------------------------
else:
    with st.container(border=True):
        st.header("📝 抽選登録")
        st.markdown(f"""
        <div class="ticket-number-display">
            <div class="label">券番号</div>
            <div class="number">{ticket_number}</div>
        </div>
        """, unsafe_allow_html=True)
        st.write(f"券種：**{get_ticket_type_label(ticket_type)}**")

        jichikai = None
        if ticket_type == "A":
            jichikai = st.selectbox("所属自治会を選択してください", JICHIKAI_LIST)

        if st.button("登録する", use_container_width=True):
            insert_result = supabase.table("registration").insert({
                "ticket_number": ticket_number,
                "ticket_type": ticket_type,
                "jichikai": jichikai,
            }).execute()

            if getattr(insert_result, "error", None):
                st.error("登録に失敗しました。もう一度お試しください。")
            else:
                st.success("✅ 登録が完了しました！抽選結果の発表をお待ちください。")
                st.balloons()
                st.rerun()