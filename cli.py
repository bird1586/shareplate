import streamlit as st
import uuid
import os
from datetime import datetime

# 定義檔案儲存的路徑
# 在 Streamlit Cloud 上，'/app/your_repo_name/uploaded_files' 是一個可寫的路徑
# 建議使用相對於腳本的路徑，並確保該目錄存在
UPLOAD_DIR = "uploaded_files"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# 檔案代碼與本地檔案路徑的映射 (注意：這會在應用程式重啟時丟失)
if 'file_codes' not in st.session_state:
    st.session_state.file_codes = {}

# --- Helper Functions ---
def save_uploaded_file_locally(uploaded_file):
    """將上傳的檔案儲存到本地並返回其路徑"""
    # 創建一個唯一的檔案名稱，保留原始副檔名
    file_extension = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

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
            st.success(f"檔案已從本地刪除: {file_path}")
        else:
            st.warning(f"嘗試刪除檔案但未找到: {file_path}")
    except Exception as e:
        st.error(f"刪除檔案失敗: {e}")

# --- Streamlit UI ---
st.title("本地檔案上傳與下載平台")

st.header("上傳檔案")
uploaded_file = st.file_uploader("選擇一個檔案上傳", type=None) # type=None 允許所有檔案類型

if uploaded_file is not None:
    st.info("檔案上傳中...")
    file_path = save_uploaded_file_locally(uploaded_file)
    if file_path:
        file_code = str(uuid.uuid4())[:8] # 生成一個8位元的簡短代碼
        st.session_state.file_codes[file_code] = {
            "file_path": file_path,
            "original_filename": uploaded_file.name,
            "upload_time": datetime.now().isoformat()
        }
        st.success(f"檔案 '{uploaded_file.name}' 已成功上傳！")
        st.markdown(f"您的下載代碼是：**`{file_code}`**")
        st.warning("請注意：此服務是基於本地儲存。**當應用程式重啟時（例如，使用者訪問、Streamlit Cloud自動重啟），您上傳的檔案和代碼映射將會丟失。**")

st.header("下載檔案")
download_code = st.text_input("請輸入檔案下載代碼")

if st.button("下載檔案"):
    if download_code in st.session_state.file_codes:
        file_info = st.session_state.file_codes[download_code]
        file_path_to_download = file_info["file_path"]
        original_filename = file_info["original_filename"]

        if os.path.exists(file_path_to_download):
            with open(file_path_to_download, "rb") as f:
                file_content = f.read()

            st.download_button(
                label=f"點擊下載 '{original_filename}'",
                data=file_content,
                file_name=original_filename,
                mime="application/octet-stream", # 根據實際檔案類型調整
                key="download_button_key"
            )
            st.success("檔案準備下載。")
            # 檔案下載後，從本地刪除並從映射中移除
            delete_local_file(file_path_to_download)
            del st.session_state.file_codes[download_code]
            st.info("檔案下載連結已生成，下載完成後檔案將被刪除。")
        else:
            st.error("檔案不存在或已被刪除。")
            # 如果檔案不存在，也從 session_state 中移除該代碼
            if download_code in st.session_state.file_codes:
                del st.session_state.file_codes[download_code]
    else:
        st.error("無效的下載代碼，請重新檢查。")

# 簡單的目前上傳檔案列表 (僅用於示範st.session_state的內容)
st.subheader("目前上傳檔案列表 (僅供參考，應用程式重啟會清空)")
if st.session_state.file_codes:
    for code, info in st.session_state.file_codes.items():
        st.write(f"- 代碼: `{code}`, 原始檔名: `{info['original_filename']}`, 本地路徑: `{info['file_path']}`")
else:
    st.info("目前沒有可供下載的檔案。")