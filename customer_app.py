import streamlit as st
from supabase import create_client

# Supabase接続
SUPABASE_URL = "https://axhpfaupxcdpjxokmtxl.supabase.co"
SUPABASE_KEY = "sb_publishable_aMFDA6pKPiWKW55zjtW-_A_tg8isXjj"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

JICHIKAI_LIST = [
    "〇〇自治会",
    "△△自治会",
    "□□自治会",
    "◇◇自治会",
    "★★自治会",
    "☆☆自治会",
]


def get_ticket_type_label(ticket_type: str) -> str:
    return "A券（会員）" if ticket_type == "A" else "B券（来場者）" if ticket_type == "B" else "不明な券種"


def is_valid_ticket_type(ticket_type: str) -> bool:
    return ticket_type in ("A", "B")

st.set_page_config(page_title="さくら祭り 抽選", layout="centered")
st.title("🌸 さくら祭り 2026 抽選登録・確認")

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
    st.success(f"登録済み：**{ticket_number}**")

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
    st.header("📝 抽選登録")
    st.write(f"券番号：**{ticket_number}**")
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