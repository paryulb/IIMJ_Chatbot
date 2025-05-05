import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import os

# file intro
chatbot_original = 'Chatbot_MIS_fuzz.xlsx'
unanswered_questions = 'unanswered.xlsx'

# loading files
if os.path.exists(chatbot_original):
    chatbot = pd.read_excel(chatbot_original)
else:
    chatbot = pd.DataFrame(columns=["Category", "Question", "Answer"])
    chatbot.to_excel(chatbot_original, index=False)

if os.path.exists(unanswered_questions):
    una_que = pd.read_excel(unanswered_questions)
else:
    una_que = pd.DataFrame(columns=["Category", "Question"])
    una_que.to_excel(unanswered_questions, index=False)

# visual of my page
st.set_page_config(page_title="IIMJ MITRA", layout="wide")
st.markdown("<h1 style='text-align: center; color: #0E4D92;'>IIM'J Mitra</h1>", unsafe_allow_html=True)
st.image("logo.png", width=120)

tab1, tab2 = st.tabs(["🤖 Chatbot", "🛠️ Admin Panel"])


# ======= Chatbot Coding ========
with tab1:
    st.markdown("### Ask your Query")
    categories = chatbot["Category"].dropna().unique()   #deopna will give dropdown menu
    selected_cat = st.selectbox("Select a category", categories)

    question = st.text_input("Type your question here")

    if st.button("Get Answer"):
        if question.strip() == "":
            st.warning("Please Enter Question First")
        else:
            matching = chatbot[chatbot["Category"] == selected_cat]
            scores = matching["Question"].apply(lambda q: fuzz.ratio(str(q).lower(), question.lower()))  #fuzzy logic chapter 13
            if scores.max() >= 60:
                best_idx = scores.idxmax()
                answer = chatbot.loc[best_idx, "Answer"]
                st.success(f"**Answer:** {answer}")
            else:
                st.warning("Sorry, we'll get back to you soon. :)")

                already_logged = (
                    (una_que["Question"].astype(str).str.lower() == question.lower()) &
                    (una_que["Category"] == selected_cat)
                ).any()

                if not already_logged:
                    new_entry = pd.DataFrame({"Category": [selected_cat], "Question": [question]})
                    una_que = pd.concat([una_que, new_entry], ignore_index=True)

                    try:
                        una_que.to_excel(unanswered_questions, index=False)
                        st.info("Sheet updated successfully.")
                    except Exception as e:
                        st.error(f"Error saving to unanswered.xlsx: {e}")
       

# ======= ADMIN PANEL ========

with tab2:
    st.markdown("### 🔐 Admin Access")
    password = st.text_input("Enter Your Password", type="password")

    if password == "Paryul@1006":
        st.success("✅ Manage unanswered questions below.")

        una_que = pd.read_excel(unanswered_questions)
        chatbot = pd.read_excel(chatbot_original)
        unanswered_categories = una_que["Category"].dropna().unique()

        if len(unanswered_categories) == 0:
            st.info("All questions have been answered.")
        else:
            admin_cat = st.selectbox("Select Category", unanswered_categories)
            cat_questions = una_que[una_que["Category"] == admin_cat]["Question"].drop_duplicates()

            if not cat_questions.empty:
                admin_q = st.selectbox("Select question to answer", cat_questions)
                admin_ans = st.text_area("Enter your answer here")

                if st.button("Submit Answer"):
                    if admin_ans.strip() == "":
                        st.error("Cannot be empty field.")
                    else:
                        new_faq = pd.DataFrame({
                            "Category": [admin_cat],  
                            "Question": [admin_q],
                            "Answer": [admin_ans]
                        })

                        # Updating my original xl
                        chatbot = pd.concat([chatbot, new_faq], ignore_index=True)
                        chatbot.to_excel(chatbot_original, index=False)
                        chatbot = pd.read_excel(chatbot_original)

                        # Remove from unanswered
                        una_que = una_que[
                            ~((una_que["Category"] == admin_cat) & (una_que["Question"] == admin_q))
                        ]
                        una_que.to_excel(unanswered_questions, index=False)

                        st.success("✅ Answer added and removed from unanswered list.")
            else:
                st.info("No questions left")
                
        st.subheader("📄 Current Unanswered Questions")
        una_que = pd.read_excel(unanswered_questions)
        st.dataframe(una_que)

        st.subheader("📘 Current FAQ (You can edit")
        chatbot = pd.read_excel(chatbot_original)
        edited_faq = st.data_editor(chatbot, num_rows="dynamic", use_container_width=True)

        if st.button("Save Changes"):
            edited_faq.to_excel(chatbot_original, index=False)
            st.success("FAQ updated and saved permanently")
            try:
                chatbot = pd.read_excel(chatbot_original)
                st.dataframe(chatbot)
            except Exception as e:
                st.error(f"Error: {e}")
                
        

        with open(unanswered_questions, "rb") as f:
            st.download_button("📥 Download Unanswered Questions", f, file_name="unanswered.xlsx")

        with open(chatbot_original, "rb") as f:
            st.download_button("📥 Download FAQ", f, file_name="faq.xlsx")

    else:
        st.error("Incorrect password. Try again.")
                       



# =========Footer (always appearing) & credits============
st.markdown("<hr><center>Developed with ❤️ by Paryul (ipm24083@iimj.ac.in), IIM Jammu</center>", unsafe_allow_html=True)
st.markdown("<center>Some answers are taken from the official IIM Jammu Handbook.</center>", unsafe_allow_html=True)
