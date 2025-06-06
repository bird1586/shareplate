import streamlit as st
import os
import mimetypes # 用於猜測檔案的MIME類型，讓下載更精確

# 定義內容暫存區的路徑
# 確保這個目錄存在
CONTENT_STORE_DIR = "temporary_holdings"
if not os.path.exists(CONTENT_STORE_DIR):
    os.makedirs(CONTENT_STORE_DIR)

# --- 內部程序 (非公開展示) ---
def receive_material_locally(input_file):
    """將傳入的資料儲存到暫存區並返回其路徑"""
    file_path = os.path.join(CONTENT_STORE_DIR, input_file.name)

    # 檢查檔案是否已存在，避免覆蓋（提供警告）
    if os.path.exists(file_path):
        st.warning(f"偵測到重複命名：'{input_file.name}' 已存在。將會覆寫現有內容。")

    try:
        with open(file_path, "wb") as f:
            f.write(input_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"資料接收處理失敗: {e}")
        return None

def clear_processed_material(file_path):
    """從暫存區移除已處理的資料"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success(f"已從暫存區清除：{os.path.basename(file_path)}")
        else:
            st.warning(f"嘗試清除資料但未找到：{os.path.basename(file_path)}")
    except Exception as e:
        st.error(f"資料清除作業失敗: {e}")

# --- 介面呈現 ---
st.title("測試介面")


st.header("測試材料")
input_material = st.file_uploader("請選擇要提交的材料", type=None, help="系統將接收您的選定內容以供後續處理。")

if input_material is not None:
    st.info("材料處理中...")
    material_path = receive_material_locally(input_material)
    if material_path:
        st.success(f"材料 **`{input_material.name}`** 已成功納入處理流程。")
        st.warning("提醒：本系統的暫存區內容會定期更新與清理，為確保資料時效性，請在必要時儘速完成處理。")


st.header("檢索材料")
target_material_name = st.text_input("", help="例如：document.pdf, image.png")

if st.button("檢索材料"):
    if target_material_name:
        material_path_to_retrieve = os.path.join(CONTENT_STORE_DIR, target_material_name)

        if os.path.exists(material_path_to_retrieve):
            with open(material_path_to_retrieve, "rb") as f:
                material_content = f.read()

            # 嘗試猜測MIME類型
            mime_type, _ = mimetypes.guess_type(material_path_to_retrieve)
            if mime_type is None:
                mime_type = "application/octet-stream" # 預設二進位流

            st.download_button(
                label=f"獲取 '{target_material_name}' 內容",
                data=material_content,
                file_name=target_material_name,
                mime=mime_type,
                key="retrieve_button_key"
            )
            st.success("材料已就緒，可進行獲取。")
            # 材料獲取按鈕生成後，立即嘗試清除
            clear_processed_material(material_path_to_retrieve)
            st.info("請注意：材料獲取完成後，系統將自動清除其在暫存區的副本。")
        else:
            st.error(f"暫存區中未找到名稱為 **`{target_material_name}`** 的材料。請檢查識別符號是否正確。")
    else:
        st.warning("請提供材料的完整識別符號以便檢索。")

