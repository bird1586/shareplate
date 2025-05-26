import streamlit as st
import os
from datetime import datetime

# 定義檔案儲存的路徑
# 在 Streamlit Cloud 上，'/app/your_repo_name/uploaded_files' 是一個可寫的路徑
# 建議使用相對於腳本的路徑，並確保該目錄存在
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- Helper Functions ---
def save_uploaded_file_locally(uploaded_file):
    """將上傳的檔案儲存到本地並返回其路徑"""
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

    # 檢查檔案是否已存在，避免覆蓋
    if os.path.exists(file_path):
        st.warning(f"檔案 '{uploaded_file.name}' 已存在，將會覆蓋舊檔案。")

    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"檔案儲存失敗: {e}")
        return None

def delete_local_file(file_path):
    """從本地刪除檔案"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success(f"檔案已從本地刪除: {os.path.basename(file_path)}")
        else:
            st.warning(f"嘗試刪除檔案但未找到: {os.path.basename(file_path)}")
    except Exception as e:
        st.error(f"刪除檔案失敗: {e}")

# --- Streamlit UI ---
st.title("簡易檔案上傳與下載平台")

st.header("上傳檔案")
uploaded_file = st.file_uploader("選擇一個檔案上傳", type=None) # type=None 允許所有檔案類型

if uploaded_file is not None:
    st.info("檔案上傳中...")
    file_path = save_uploaded_file_locally(uploaded_file)
    if file_path:
        st.success(f"檔案 **`{uploaded_file.name}`** 已成功上傳！")
        st.warning("請注意：此服務是基於本地儲存。**當應用程式重啟時（例如，使用者訪問、Streamlit Cloud自動重啟），您上傳的檔案將會丟失。**")


st.header("下載檔案")
download_filename = st.text_input("請輸入要下載的檔案名稱 (含副檔名)")

if st.button("下載並刪除檔案"):
    if download_filename:
        file_path_to_download = os.path.join(UPLOAD_DIR, download_filename)

        if os.path.exists(file_path_to_download):
            with open(file_path_to_download, "rb") as f:
                file_content = f.read()

            st.download_button(
                label=f"點擊下載 '{download_filename}'",
                data=file_content,
                file_name=download_filename,
                mime="application/octet-stream", # 根據實際檔案類型調整
                key="download_button_key"
            )
            st.success("檔案準備下載。")
            # 檔案下載按鈕生成後，立即嘗試刪除檔案
            delete_local_file(file_path_to_download)
            st.info("檔案下載連結已生成，下載完成後檔案將被刪除。")
        else:
            st.error(f"找不到檔案 **`{download_filename}`**，請檢查檔案名稱是否正確。")
    else:
        st.warning("請輸入檔案名稱。")

---

# 檔案列表 (僅供參考)

st.subheader("伺服器上現有檔案列表 (應用程式重啟後會清空)")
files_in_dir = os.listdir(UPLOAD_DIR)
if files_in_dir:
    for filename in files_in_dir:
        st.write(f"- `{filename}`")
else:
    st.info("目前沒有任何檔案在伺服器上。")
