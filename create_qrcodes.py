import qrcode
from pathlib import Path

BASE_URL = "https://kmatsumoto1992048-sakurafes-admin-customer-app-be57dd.streamlit.app/?ticket="

A_START = 1
A_END = 10
B_START = 1
B_END = 10

output_dir = Path("qrcodes")
output_dir.mkdir(exist_ok=True)
(output_dir / "A").mkdir(exist_ok=True)
(output_dir / "B").mkdir(exist_ok=True)

def make_qr(ticket_number: str):
    url = BASE_URL + ticket_number
    img = qrcode.make(url)
    ticket_type = ticket_number[0]
    img.save(output_dir / ticket_type / f"{ticket_number}.png")

for i in range(A_START, A_END + 1):
    make_qr(f"A{i:04d}")

for i in range(B_START, B_END + 1):
    make_qr(f"B{i:04d}")

print(f"A券：{A_END - A_START + 1}枚")
print(f"B券：{B_END - B_START + 1}枚")
print(f"保存先：{output_dir.resolve()}")
