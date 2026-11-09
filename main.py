
import streamlit as st
from groq import Groq
import re


# --------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🎯",
    layout="centered"
)

st.title("🎯 AI Interview Preparation Coach")

st.write(
    "Practice your interviews with AI and improve your answers."
)


# --------------------------------
# 2. SESSION STATE INITIALIZATION
# --------------------------------

if "interview_started" not in st.session_state:
    st.session_state.interview_started = False

if "interview_finished" not in st.session_state:
    st.session_state.interview_finished = False

if "question_number" not in st.session_state:
    st.session_state.question_number = 1

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

if "evaluated" not in st.session_state:
    st.session_state.evaluated = False

if "feedback" not in st.session_state:
    st.session_state.feedback = ""

if "interview_history" not in st.session_state:
    st.session_state.interview_history = []


# --------------------------------
# 3. API KEY INPUT
# --------------------------------

st.sidebar.header("API Configuration")

api_key = st.sidebar.text_input(
    "Enter your Groq API Key",
    type="password",
    placeholder="gsk_..."
)

st.sidebar.caption(
    "Your API key is used for this session."
)


# --------------------------------
# 4. INTERVIEW SETTINGS
# --------------------------------

st.sidebar.header("Interview Settings")

interview_type = st.sidebar.radio(
    "Choose Interview Type",
    ["Technical Interview", "HR Interview"]
)

job_role = st.sidebar.selectbox(
    "Choose Job Role",
    [
        "Python Developer",
        "Java Developer",
        "Software Engineer",
        "QA Engineer",
        "Data Analyst",
        "Machine Learning Engineer"
    ]
)

difficulty = st.sidebar.selectbox(
    "Choose Difficulty",
    ["Beginner", "Intermediate", "Advanced"]
)

number_of_questions = st.sidebar.slider(
    "Number of Questions",
    min_value=3,
    max_value=10,
    value=5
)


# --------------------------------
# 5. CREATE GROQ CLIENT
# --------------------------------

def create_client(key):

    client = Groq(
        api_key=key
    )

    return client


# --------------------------------
# 6. GENERATE INTERVIEW QUESTION
# --------------------------------

def generate_question(client, question_number):

    previous_questions = [
        item["question"]
        for item in st.session_state.interview_history
    ]

    prompt = f"""
    You are a professional interview coach.

    Conduct an interview for the following candidate:

    Interview Type: {interview_type}
    Job Role: {job_role}
    Difficulty: {difficulty}

    This is question number {question_number}.

    Previous questions:
    {previous_questions}

    Instructions:

    1. Ask one interview question only.
    2. Do not provide the answer.
    3. Do not repeat previous questions.
    4. Make the question suitable for the selected role.
    5. Keep the question clear and professional.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an experienced professional "
                    "interviewer."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.7,
        max_tokens=500
    )

    question = response.choices[0].message.content

    return question.strip()


# --------------------------------
# 7. EVALUATE USER ANSWER
# --------------------------------

def evaluate_answer(client, question, answer):

    if interview_type == "Technical Interview":

        evaluation_criteria = """
        Evaluate the answer based on:

        - Technical correctness
        - Conceptual understanding
        - Explanation clarity
        - Problem-solving approach
        """

    else:

        evaluation_criteria = """
        Evaluate the answer based on:

        - Relevance to the question
        - Communication clarity
        - Professionalism
        - Structure of the answer
        """

    prompt = f"""
    You are an experienced interview evaluator.

    Interview Type: {interview_type}
    Job Role: {job_role}
    Difficulty: {difficulty}

    Interview Question:
    {question}

    Candidate's Answer:
    {answer}

    Evaluation Criteria:
    {evaluation_criteria}

    Evaluate the candidate's answer.

    Follow this exact format:

    Score: X/10

    Strengths:
    Explain what the candidate did well.

    Areas for Improvement:
    Explain what the candidate should improve.

    Better Answer:
    Provide an example of a strong answer.

    Keep the feedback constructive and suitable for a fresher.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a fair, professional, "
                    "and helpful interview evaluator."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.4,
        max_tokens=1000
    )

    feedback = response.choices[0].message.content

    return feedback.strip()


# --------------------------------
# 8. EXTRACT SCORE FROM FEEDBACK
# --------------------------------

def extract_score(feedback):

    match = re.search(
        r"Score:\s*(\d+)\s*/\s*10",
        feedback
    )

    if match:

        return int(match.group(1))

    return None


# --------------------------------
# 9. START INTERVIEW
# --------------------------------

if not st.session_state.interview_started:

    st.info(
        "Select your interview preferences "
        "from the sidebar and start practicing."
    )

    if st.button("Start Interview"):

        if not api_key.strip():

            st.warning(
                "Please enter your Groq API key first."
            )

        else:

            try:

                client = create_client(api_key)

                question = generate_question(
                    client,
                    1
                )

                st.session_state.interview_started = True

                st.session_state.interview_finished = False

                st.session_state.question_number = 1

                st.session_state.current_question = question

                st.session_state.interview_history = []

                st.session_state.evaluated = False

                st.session_state.feedback = ""

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to start interview: {error}"
                )


# --------------------------------
# 10. INTERVIEW IN PROGRESS
# --------------------------------

if (
    st.session_state.interview_started
    and not st.session_state.interview_finished
):

    st.divider()

    st.subheader(
        f"Question {st.session_state.question_number}"
    )

    st.markdown(
        st.session_state.current_question
    )

    answer = st.text_area(
        "Your Answer",
        placeholder="Type your answer here...",
        height=180,
        key=f"answer_{st.session_state.question_number}"
    )


    # Evaluate Answer Button

    if st.button(
        "Evaluate Answer",
        disabled=st.session_state.evaluated
    ):

        if not answer.strip():

            st.warning(
                "Please enter your answer first."
            )

        elif not api_key.strip():

            st.warning(
                "Please enter your Groq API key."
            )

        else:

            try:

                client = create_client(api_key)

                feedback = evaluate_answer(
                    client,
                    st.session_state.current_question,
                    answer
                )

                st.session_state.feedback = feedback

                st.session_state.evaluated = True

                score = extract_score(feedback)

                st.session_state.interview_history.append(
                    {
                        "question": (
                            st.session_state.current_question
                        ),
                        "answer": answer,
                        "feedback": feedback,
                        "score": score
                    }
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to evaluate answer: {error}"
                )


    # Display Feedback

    if st.session_state.evaluated:

        st.divider()

        st.subheader("AI Feedback")

        st.markdown(
            st.session_state.feedback
        )


        # Next Question Button

        if (
            st.session_state.question_number
            < number_of_questions
        ):

            if st.button("Next Question"):

                try:

                    client = create_client(api_key)

                    next_number = (
                        st.session_state.question_number + 1
                    )

                    question = generate_question(
                        client,
                        next_number
                    )

                    st.session_state.question_number = (
                        next_number
                    )

                    st.session_state.current_question = (
                        question
                    )

                    st.session_state.evaluated = False

                    st.session_state.feedback = ""

                    st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to generate question: {error}"
                    )


        # Finish Interview Button

        if st.button("Finish Interview"):

            st.session_state.interview_finished = True

            st.session_state.interview_started = False

            st.rerun()


# --------------------------------
# 11. FINAL INTERVIEW REPORT
# --------------------------------

if st.session_state.interview_finished:

    st.divider()

    st.header("🏆 Interview Summary")

    history = st.session_state.interview_history

    scores = [
        item["score"]
        for item in history
        if item["score"] is not None
    ]

    if scores:

        average_score = sum(scores) / len(scores)

        st.metric(
            "Average Score",
            f"{average_score:.1f}/10"
        )

    st.write(
        f"Questions Attempted: {len(history)}"
    )

    for index, item in enumerate(history, start=1):

        with st.expander(
            f"Question {index}"
        ):

            st.write(
                "**Question:**",
                item["question"]
            )

            st.write(
                "**Your Answer:**",
                item["answer"]
            )

            st.write(
                "**Feedback:**"
            )

            st.markdown(
                item["feedback"]
            )

    if st.button("Start New Interview"):

        st.session_state.interview_started = False

        st.session_state.interview_finished = False

        st.session_state.question_number = 1

        st.session_state.current_question = ""

        st.session_state.evaluated = False

        st.session_state.feedback = ""

        st.session_state.interview_history = []

        st.rerun()
