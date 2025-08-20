import streamlit as st
import PyPDF2
import docx2txt
import re
import time

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="ATS Resume Checker + AI Bot", page_icon="📄🤖", layout="wide")

# -------------------------------
# Custom CSS
# -------------------------------
st.markdown("""
<style>
body { 
    background: linear-gradient(120deg, #FFF176 25%, #FFD54F 50%, #FFB74D 75%);
    background-size: 400% 400%;
    animation: gradientBG 10s ease infinite;
}
@keyframes gradientBG {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}
.ai-button {
    background-color: #1abc9c;
    color: white;
    border-radius: 50%;
    font-size: 30px;
    width: 60px;
    height: 60px;
    text-align: center;
    line-height: 60px;
    cursor: pointer;
    position: fixed;
    bottom: 30px;
    left: 30px;
    z-index: 999;
}
.ai-box {
    background-color: #f0f0f0;
    border-radius: 12px;
    padding: 15px;
    position: fixed;
    bottom: 100px;
    left: 30px;
    width: 360px;
    max-height: 500px;
    overflow-y: auto;
    z-index: 998;
}
select { font-size: 16px; padding: 8px; width: 100%; border-radius: 6px; margin-top: 10px; }
option { padding: 8px; }
textarea { font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# Session state for AI
# -------------------------------
if "ai_clicked" not in st.session_state:
    st.session_state.ai_clicked = False
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

# -------------------------------
# Two-column layout
# -------------------------------
left_col, right_col = st.columns([2,1])

# -------------------------------
# Left Column: Resume + JD + Comparison
# -------------------------------
with left_col:
    st.header("📄 Resume & Job Description")
    
    # --- Single Resume Upload & ATS ---
    resume_file = st.file_uploader("Upload your Resume", type=["pdf","docx"])
    resume_text = ""
    if resume_file:
        file_type = resume_file.name.split(".")[-1]
        if file_type == "pdf":
            pdf_reader = PyPDF2.PdfReader(resume_file)
            for page in pdf_reader.pages:
                resume_text += page.extract_text()
        elif file_type == "docx":
            resume_text = docx2txt.process(resume_file)
        st.success("✅ Resume uploaded!")

        st.subheader("Resume Preview:")
        st.text_area("Resume Content", value=resume_text, height=300)

    jd_text = st.text_area("Paste Job Description here")  # Enter works normally

    if st.button("Calculate ATS Score"):
        if not resume_file:
            st.error("❌ Please upload a resume first!")
        elif not jd_text.strip():
            st.error("❌ Please paste the job description!")
        else:
            def extract_keywords(text):
                text = text.lower()
                text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
                stopwords = ["and","or","the","a","an","in","on","with","for","to","of"]
                return set([w for w in text.split() if w not in stopwords])
            
            resume_keywords = extract_keywords(resume_text)
            jd_keywords = extract_keywords(jd_text)
            matches = resume_keywords.intersection(jd_keywords)
            missing_keywords = jd_keywords - resume_keywords
            ats_score = int((len(matches)/len(jd_keywords))*100) if jd_keywords else 0
            priority_keywords = {"python","java","sql","aws"}
            weighted_score = min(ats_score + len(matches.intersection(priority_keywords))*2,100)

            st.subheader("🔹 ATS Score")
            st.write(f"Your resume matches **{ats_score}%** of JD keywords.")
            st.progress(ats_score)
            st.subheader("🔹 Matching Keywords")
            st.write(", ".join(matches) if matches else "No keywords matched.")
            st.subheader("🔹 Missing Keywords")
            st.write(", ".join(missing_keywords) if missing_keywords else "No missing keywords! 🎉")
            st.subheader("🔹 Weighted ATS Score")
            st.write(f"{weighted_score}% (priority skills considered)")

            report_text = f"ATS Score: {ats_score}%\nWeighted ATS Score: {weighted_score}%\nMatching: {', '.join(matches)}\nMissing: {', '.join(missing_keywords)}"
            st.download_button("📥 Download ATS Report", report_text, file_name="ATS_Report.txt")
    
    # --- Compare Two Resumes Feature ---
    st.subheader("📊 Compare Two Resumes for ATS")
    compare_resume_file1 = st.file_uploader("Upload First Resume to Compare", type=["pdf","docx"], key="comp1")
    compare_resume_file2 = st.file_uploader("Upload Second Resume to Compare", type=["pdf","docx"], key="comp2")
    compare_jd_text = st.text_area("Paste Job Description for Comparison", key="comp_jd")

    if st.button("Compare Resumes ATS Score", key="compare_btn"):
        if not compare_resume_file1 or not compare_resume_file2:
            st.error("❌ Please upload both resumes to compare!")
        elif not compare_jd_text.strip():
            st.error("❌ Please paste the job description!")
        else:
            def get_resume_text(file):
                text = ""
                file_type = file.name.split(".")[-1]
                if file_type == "pdf":
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text()
                elif file_type == "docx":
                    text = docx2txt.process(file)
                return text

            def extract_keywords(text):
                text = text.lower()
                text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
                stopwords = ["and","or","the","a","an","in","on","with","for","to","of"]
                return set([w for w in text.split() if w not in stopwords])

            resume1_text = get_resume_text(compare_resume_file1)
            resume2_text = get_resume_text(compare_resume_file2)
            jd_keywords = extract_keywords(compare_jd_text)

            resume1_keywords = extract_keywords(resume1_text)
            resume2_keywords = extract_keywords(resume2_text)

            matches1 = resume1_keywords.intersection(jd_keywords)
            matches2 = resume2_keywords.intersection(jd_keywords)

            ats1 = int((len(matches1)/len(jd_keywords))*100) if jd_keywords else 0
            ats2 = int((len(matches2)/len(jd_keywords))*100) if jd_keywords else 0

            st.write(f"**Resume 1 ATS Score:** {ats1}% | **Matching Keywords:** {', '.join(matches1)}")
            st.write(f"**Resume 2 ATS Score:** {ats2}% | **Matching Keywords:** {', '.join(matches2)}")

            if ats1 > ats2:
                st.success("✅ Resume 1 is a better match for the JD!")
            elif ats2 > ats1:
                st.success("✅ Resume 2 is a better match for the JD!")
            else:
                st.info("⚖️ Both resumes match equally with the JD.")

# -------------------------------
# Right Column: Offline AI Bot
# -------------------------------
with right_col:
    st.header("🤖 AI Chatbot")

    if st.button("🤖 AI Bot"):
        st.session_state.ai_clicked = True
        st.session_state.show_popup = True
        st.session_state.popup_time = time.time()

    if st.session_state.get("show_popup", False):
        if time.time() - st.session_state.get("popup_time",0) < 1:
            st.success("💬 How can I help you?")
        else:
            st.session_state.show_popup = False

    if st.session_state.ai_clicked:
        # 50 realistic resume Q&A
        offline_qa = {
            "How to improve my resume?": "Include relevant keywords, quantify achievements, and use clear headings.",
            "Common resume mistakes?": "Typos, unclear formatting, missing skills, irrelevant info.",
            "How to increase ATS score?": "Use JD keywords, avoid images/tables, standard fonts.",
            "Should I include projects?": "Yes, especially relevant projects.",
            "How to highlight skills?": "List skills separately and mention in experience.",
            "How to write summary?": "Concise summary highlighting skills and achievements.",
            "What font is best for resume?": "Use simple fonts like Arial, Calibri, or Helvetica.",
            "Resume length?": "Keep it 1-2 pages depending on experience.",
            "Include hobbies?": "Only if relevant to the job or shows soft skills.",
            "How to format dates?": "Use a consistent format like MM/YYYY.",
            "Include references?": "Optional, can write 'Available on request'.",
            "How to handle career gaps?": "Briefly explain positively in summary or experience.",
            "Use action verbs?": "Yes, start bullet points with strong action verbs.",
            "Include certifications?": "Yes, relevant ones only.",
            "How to show achievements?": "Quantify with numbers or results.",
            "ATS-friendly file type?": "PDF or DOCX without complex formatting.",
            "Include LinkedIn profile?": "Yes, always a good idea.",
            "Include personal details?": "Name, email, phone, city, LinkedIn optional.",
            "Should I include photo?": "No, unless required regionally.",
            "Use bullets or paragraphs?": "Bullets for clarity.",
            "Resume margins?": "1 inch recommended.",
            "How to handle multiple roles?": "List them separately under each company.",
            "Include freelance work?": "Yes, if relevant.",
            "Tailoring resume?": "Always match JD for each application.",
            "Use keywords?": "Yes, analyze JD carefully.",
            "How to handle internships?": "Include relevant internships with achievements.",
            "Education placement?": "After summary, before experience.",
            "Use numbering?": "No, bullets are better.",
            "Include GPA?": "Optional, only if impressive.",
            "Include awards?": "Yes, relevant ones only.",
            "Volunteer work?": "Include if relevant or shows skills.",
            "Professional summary?": "2-3 sentences summarizing expertise.",
            "Objective statement?": "Optional, keep concise.",
            "Include skills section?": "Yes, list technical & soft skills.",
            "Formatting consistency?": "Use same fonts, spacing, bullets.",
            "Highlight promotions?": "Yes, under experience.",
            "Include publications?": "Yes, if relevant to the field.",
            "Show leadership?": "Mention projects or team leads.",
            "Use keywords in summary?": "Yes, to improve ATS match.",
            "Action verbs examples?": "Led, Developed, Managed, Created, Optimized",
            "How to make resume readable?": "Clear sections, consistent font & spacing.",
            "Include programming languages?": "Yes, if relevant to JD.",
            "What to avoid?": "Images, tables, fancy formatting.",
            "Include GitHub?": "Yes, for developers.",
            "Highlight problem-solving?": "Mention specific projects or achievements.",
            "Use clear headings?": "Yes, for sections like Experience, Education, Skills.",
            "Customize resume per job?": "Yes, always tailor for each application.",
            "Use numbers for achievements?": "Yes, quantify results.",
            "Avoid long paragraphs?": "Keep bullet points concise.",
            "Include soft skills?": "Yes, only highlight relevant ones.",
            "How to describe experience?": "Action + Result format is best.",
            "Include languages?": "Yes, only if relevant to the job.",
            "ATS vs recruiter?": "Make it readable for both, simple formatting.",
            "How to handle multiple locations?": "List location next to company/job.",
            "ShouldKNOW AND COMAPS I include GPA?": "Include only if strong and relevant.", 
            "Include conferences?": "Optional, if relevant."
        }

        selected_question = st.selectbox(
            "Select a resume question:", 
            ["--Select--"] + list(offline_qa.keys())
        )
        if selected_question != "--Select--":
            st.markdown(f"**Answer:** {offline_qa[selected_question]}")
