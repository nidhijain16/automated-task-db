import streamlit as st
import openai
import pandas as pd
import json
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Automated Task DB", page_icon="🤖", layout="wide")

# Custom CSS for a professional look
st.markdown("""
    <style>
    .stTextArea textarea {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar for API Key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
    
    st.info("This tool uses AI to parse unstructured text into a structured database.")

st.title("🤖 Automated Task Database")
st.subheader("Turn messy thoughts into structured data.")

# Initialize Session State for Data
if 'task_data' not in st.session_state:
    st.session_state.task_data = pd.DataFrame(columns=["Task", "Category", "Priority", "Due Date", "Status"])

# Input Section
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 1. Input")
    user_input = st.text_area("Dump your tasks here:", height=150, 
        placeholder="E.g., I need to finish the quarterly report by Friday, and also buy milk tomorrow. The report is high priority.")
    
    if st.button("Process with AI", type="primary"):
        if not api_key:
            st.error("Please enter an API Key in the sidebar.")
        elif not user_input:
            st.warning("Please enter some text.")
        else:
            try:
                client = openai.OpenAI(api_key=api_key)
                
                # The Prompt Engineering part
                prompt = f"""
                Extract tasks from the following text and return them as a JSON list. 
                Each item should have: 'Task', 'Category' (Work, Personal, Health, Finance), 
                'Priority' (High, Medium, Low), 'Due Date' (YYYY-MM-DD or 'None'), and 'Status' (To Do).
                
                Text: {user_input}
                """
                
                with st.spinner("AI is thinking..."):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0
                    )
                    
                    # Parse output
                    content = response.choices[0].message.content
                    data = json.loads(content)
                    
                    # Update DataFrame
                    new_rows = pd.DataFrame(data)
                    st.session_state.task_data = pd.concat([st.session_state.task_data, new_rows], ignore_index=True)
                    st.success("Tasks extracted successfully!")

            except Exception as e:
                st.error(f"An error occurred: {e}")

with col2:
    st.markdown("### 2. Structured Database")
    if not st.session_state.task_data.empty:
        st.dataframe(st.session_state.task_data, use_container_width=True)
        
        # Download Button
        csv = st.session_state.task_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download as CSV",
            csv,
            "tasks.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No tasks processed yet. Enter text on the left to begin.")

# Clear Data Button
if not st.session_state.task_data.empty:
    if st.button("Clear Database"):
        st.session_state.task_data = pd.DataFrame(columns=["Task", "Category", "Priority", "Due Date", "Status"])
        st.experimental_rerun()
