import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import os

# --- File Setup ---
faq_file = 'Chatbot_MIS_fuzz.xlsx'
unanswered_file = 'unanswered.xlsx'

# --- Load or create Excel files ---
if os.path.exists(faq_file):
    faq_df = pd.read_excel(faq_file)
else:
    faq_df = pd.DataFrame(columns=["Category", "Question", "Answer"])
    faq_df.to_excel(faq_file, index=False)

if os.path.exists(unanswered_file):
    unanswered_df = pd.read_excel(unanswered_file)
else:
    unanswered_df = pd.DataFrame(columns=["Category", "Question"])
    unanswered_df.to_excel(unanswered_file, index=False)

# --- Page Setup ---
st.set_page_config(page_title="IIMJ MITRA", layout="wide")
st.markdown("<h1 style='text-align: center; color: #0E4D92;'>IIM Smart Chatbot</h1>", unsafe_allow_html=True)
st.image("logo.png", width=120)

tab1, tab2 = st.tabs(["🤖 Chatbot", "🛠️ Admin Panel"])

# ========================
# ======= CHATBOT ========
# ========================
with tab1:
    st.markdown("### Ask a Question")
    categories = faq_df["Category"].dropna().unique()
    selected_cat = st.selectbox("Select a category", categories)

    user_q = st.text_input("Type your question here")

    if st.button("Get Answer"):
        matched_faqs = faq_df[faq_df["Category"] == selected_cat]
        scores = matched_faqs["Question"].apply(lambda q: fuzz.ratio(str(q).lower(), user_q.lower()))

        if scores.max() >= 70:
            best_idx = scores.idxmax()
            answer = faq_df.loc[best_idx, "Answer"]
            st.success(f"**Answer:** {answer}")
        else:
            st.warning("Sorry, I don't know the answer yet. We'll get back to you soon.")
          if not ((unanswered_df["Question"].str.lower() == user_q.lower()) & (unanswered_df["Category"] == selected_cat)).any():
                new_entry = pd.DataFrame({"Category": [selected_cat], "Question": [user_q]})
                unanswered_df = pd.concat([unanswered_df, new_entry], ignore_index=True)
                try:
                    unanswered_df.to_excel(unanswered_file, index=False)
                    st.info("Unanswered question logged.")
                except Exception as e:
                    st.error(f"Error saving to unanswered.xlsx: {e}")


# ============================
# ======= ADMIN PANEL ========
# ============================
with tab2:
    st.markdown("### Admin Access")
    password = st.text_input("Enter Admin Password", type="password")

    if password == "Paryul@1006":  # You can change this
        st.success("Access granted. You can now manage unanswered questions.")

        admin_cat = st.selectbox("Select category", unanswered_df["Category"].dropna().unique())
        cat_questions = unanswered_df[unanswered_df["Category"] == admin_cat]["Question"].drop_duplicates()

        if not cat_questions.empty:
            admin_q = st.selectbox("Select question to answer", cat_questions)
            admin_ans = st.text_area("Enter your answer here")

            if st.button("Submit Answer"):
                new_faq = pd.DataFrame({
                    "Category": [admin_cat],
                    "Keyword": [""],
                    "Question": [admin_q],
                    "Answer": [admin_ans]
                })

                # Update FAQ and unanswered
                faq_df = pd.concat([faq_df, new_faq], ignore_index=True)
                faq_df.to_excel(faq_file, index=False)

                unanswered_df = unanswered_df[~((unanswered_df["Category"] == admin_cat) & (unanswered_df["Question"] == admin_q))]
                unanswered_df.to_excel(unanswered_file, index=False)

                st.success("✅ Answer added to FAQ and removed from unanswered list!")
        else:
            st.info("No unanswered questions in this category.")
    else:
        if password:
            st.error("Incorrect password. Try again.")

# =============================
# ========= FOOTER ============
# =============================
st.markdown("<hr><center>Developed with ❤️ by Paryul (ipm24083@iimj.ac.in), IIM Jammu</center>", unsafe_allow_html=True)
st.markdown("<center>Some answers are taken from the official IIM Jammu Handbook.</center>", unsafe_allow_html=True)
