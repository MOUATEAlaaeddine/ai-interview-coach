import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval

# Setting up the Streamlit page configuration
st.set_page_config(page_title="Interview Chat", page_icon="💬")
st.title("Chatbot")

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "messages" not in st.session_state:
    st.session_state.messages = []


# Helper functions to update session state
def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

# Setup stage for collecting user details
if not st.session_state.setup_complete:
    st.subheader('Personal Information')

    # Initialize session state for personal information
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""

   
    # Get personal information input
    st.session_state["name"] = st.text_input(label="Name", value=st.session_state["name"], placeholder="Enter your name", max_chars=40)
    st.session_state["experience"] = st.text_area(label="Experience", value=st.session_state["experience"], placeholder="Describe your experience", max_chars=200)
    st.session_state["skills"] = st.text_area(label="Skills", value=st.session_state["skills"], placeholder="List your skills", max_chars=200)

    
    # Company and Position Section
    st.subheader('Company and Position')

    # Initialize session state for company and position information and setting default values 
    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"
    if "custom_position" not in st.session_state:
        st.session_state["custom_position"] = ""
    if "custom_company" not in st.session_state:
        st.session_state["custom_company"] = ""

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["Junior", "Mid-level", "Senior"],
            index=["Junior", "Mid-level", "Senior"].index(st.session_state["level"])
        )

    with col2:
        position_options = ["Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst", "Other (specify below)"]
        selected_position = st.selectbox(
            "Choose a position",
            position_options,
            index=position_options.index(st.session_state["position"]) if st.session_state["position"] in position_options else 0
        )
        
        if selected_position == "Other (specify below)":
            st.session_state["custom_position"] = st.text_input(
                "Specify position",
                value=st.session_state["custom_position"],
                placeholder="Enter custom position",
                max_chars=50
            )
            st.session_state["position"] = st.session_state["custom_position"] if st.session_state["custom_position"] else "Data Scientist"
        else:
            st.session_state["position"] = selected_position

    company_options = ["Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify", "Other (specify below)"]
    selected_company = st.selectbox(
        "Select a Company",
        company_options,
        index=company_options.index(st.session_state["company"]) if st.session_state["company"] in company_options else 0
    )
    
    if selected_company == "Other (specify below)":
        st.session_state["custom_company"] = st.text_input(
            "Specify company",
            value=st.session_state["custom_company"],
            placeholder="Enter custom company",
            max_chars=50
        )
        st.session_state["company"] = st.session_state["custom_company"] if st.session_state["custom_company"] else "Amazon"
    else:
        st.session_state["company"] = selected_company



    # Button to complete setup
    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")

# Interview phase
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
    """
    Start by introducing yourself
    """,
    icon="👋",
    )

    # Initialize OpenAI client
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Setting OpenAI model if not already initialized
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    # Initializing the system prompt for the chatbot
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role": "system",
            "content": (f"You are an HR executive that interviews an interviewee called {st.session_state['name']} "
                        f"with experience {st.session_state['experience']} and skills {st.session_state['skills']}. "
                        f"You should interview him for the position {st.session_state['level']} {st.session_state['position']} "
                        f"at the company {st.session_state['company']}")
        }]

    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Handle user input and OpenAI response
    # Put a max_chars limit
    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your response", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})

            # Increment the user message count
            st.session_state.user_message_count += 1

    # Check if the user message count reaches 5
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# Show "Get Feedback" 
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

# Show feedback screen
if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    # Initialize new OpenAI client instance for feedback
    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    # Generate feedback using the stored messages and write a system prompt for the feedback
    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""You are an expert HR interviewer evaluator specializing in {st.session_state['position']} roles at {st.session_state['level']} level.

Analyze the interview performance across these dimensions:
1. **Technical Knowledge** (0-10): Depth of skills and experience relevant to {st.session_state['position']}
2. **Communication** (0-10): Clarity, structure, and professionalism
3. **Cultural Fit** (0-10): Alignment with {st.session_state['company']} values and work style
4. **Problem-Solving** (0-10): Analytical thinking and approach to challenges
5. **Enthusiasm & Engagement** (0-10): Interest in role and company

Provide your evaluation in this format:

**Overall Score: X/10**

**Detailed Scores:**
- Technical Knowledge: X/10
- Communication: X/10
- Cultural Fit: X/10
- Problem-Solving: X/10
- Enthusiasm & Engagement: X/10

**Strengths:**
[2-3 specific strengths observed]

**Areas for Improvement:**
[2-3 actionable suggestions]

**Final Recommendation:**
[Brief statement on candidacy]

Be constructive, specific, and reference actual responses from the interview."""},
            {"role": "user", "content": f"Evaluate this interview for a {st.session_state['level']} {st.session_state['position']} position at {st.session_state['company']}:\n\n{conversation_history}"}
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    # Button to restart the interview
    if st.button("Restart Interview", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")