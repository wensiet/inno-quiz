import requests
from requests.exceptions import RequestException

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="InnoQuiz",
    page_icon="📝",
    layout="wide",
)

# API Configuration
API_URL = "http://api:8000/api/v1"

# Initialize core session state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "current_quiz" not in st.session_state:
    st.session_state.current_quiz = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False


# Session state helper functions
def navigate_to(page, **kwargs):
    """Navigate to a specific page and update session state."""
    # Update page in session state
    st.session_state.page = page

    # Update other session state values
    for key, value in kwargs.items():
        if key in st.session_state:
            st.session_state[key] = value

    # Special handlers for specific pages
    if page == "take_quiz" and "quiz_id" in kwargs:
        st.session_state.current_quiz = kwargs["quiz_id"]
        st.session_state.quiz_answers = {}
        st.session_state.quiz_result = None

    # Force a rerun
    st.rerun()


def clear_state_except_core():
    """Clear temporary session state items."""
    core_state = [
        "page",
        "token",
        "user",
        "current_quiz",
        "quiz_answers",
        "quiz_result",
        "is_logged_in",
    ]
    for key in list(st.session_state.keys()):
        if key not in core_state:
            del st.session_state[key]


# API functions
def api_post(endpoint, token=None, json_data=None, form_data=None, params=None):
    """Make a POST request to the API."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if json_data:
            response = requests.post(
                f"{API_URL}/{endpoint}",
                headers=headers,
                json=json_data,
                params=params,
            )
        else:
            response = requests.post(
                f"{API_URL}/{endpoint}",
                headers=headers,
                data=form_data,
                params=params,
            )
        return response
    except RequestException as e:
        st.error(f"Connection error: {e!s}")
        return None


def api_get(endpoint, token=None, params=None):
    """Make a GET request to the API."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(
            f"{API_URL}/{endpoint}",
            headers=headers,
            params=params,
        )
        return response
    except RequestException as e:
        st.error(f"Connection error: {e!s}")
        return None


def api_delete(endpoint, token=None):
    """Make a DELETE request to the API."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.delete(
            f"{API_URL}/{endpoint}",
            headers=headers,
        )
        return response
    except RequestException as e:
        st.error(f"Connection error: {e!s}")
        return None


# Auth functions
def login(username, password):
    """Authenticate user and get token."""
    response = api_post(
        "auth/token",
        form_data={"username": username, "password": password, "scope": "user"},
    )

    if response and response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        st.session_state.token = access_token
        st.session_state.is_logged_in = True
        st.session_state.user = get_current_user()
        return True
    if response:
        try:
            error = response.json().get("detail", "Authentication failed")
            st.error(f"Error: {error}")
        except Exception:
            st.error(f"Error: {response.status_code}")
    return False


def register(username, email, password):
    """Register a new user."""
    response = api_post(
        "auth/register",
        json_data={"username": username, "email": email, "password": password},
    )

    if response and response.status_code == 201:
        st.success("Registration successful! You can now login.")
        return True
    if response:
        try:
            error = response.json().get("detail", "Registration failed")
            st.error(f"Error: {error}")
        except Exception:
            st.error(f"Error: {response.status_code}")
    return False


def get_current_user():
    """Get current user info."""
    response = api_get("users/me", token=st.session_state.token)

    if response and response.status_code == 200:
        return response.json()
    return None


def logout():
    """Log out the current user."""
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.current_quiz = None
    st.session_state.is_logged_in = False
    navigate_to("login")


# Quiz functions
def get_quizzes(my_quizzes=False):
    """Get available quizzes."""
    response = api_get(
        "quizzes/",
        token=st.session_state.token,
        params={"my_quizzes": my_quizzes},
    )

    if response and response.status_code == 200:
        return response.json()
    return []


def get_quiz(quiz_id):
    """Get a specific quiz."""
    response = api_get(
        f"quizzes/{quiz_id}",
        token=st.session_state.token,
    )

    if response and response.status_code == 200:
        return response.json()
    return None


def create_quiz(title, description, questions):
    """Create a new quiz."""
    # Debug the questions data structure
    st.write(f"Debug: Received {len(questions)} questions to create quiz")
    # Try the simplest payload structure based on the working endpoint
    payload = {
        "title": title,
        "description": description or "",
        "is_public": True,
        "questions": [],
    }
    # Debug each question's contents
    for i, q in enumerate(questions):
        st.write(f"Question {i+1}:")
        st.write(f"  - Text: {q['text']}")
        st.write(f"  - Options: {q['options']}")
        st.write(f"  - Correct: {q['correct_answer']}")
        st.write(f"  - Points: {q['points']}")

        # Handle correct_answer being either a single value or a list
        correct_answer = q["correct_answer"]
        if isinstance(correct_answer, list) and len(correct_answer) > 0:
            # Take the first correct answer for now
            # In the future, we could modify the backend to support multiple correct answers
            correct_answer = correct_answer[0]

        payload["questions"].append(
            {
                "text": q["text"],
                "options": q["options"],
                "correct_answer": correct_answer,
                "points": int(q["points"]),
            }
        )

    # Log the exact request being sent
    st.write("Sending API request:")
    st.write(f"POST {API_URL}/quizzes/")
    st.write("Headers:", {"Authorization": f"Bearer {st.session_state.token}"})
    st.write("Payload:", payload)

    # Make the request
    response = api_post("quizzes/", token=st.session_state.token, json_data=payload)

    # Log the response
    if response:
        st.write(f"Response status: {response.status_code}")
        try:
            st.write("Response content:", response.json())
        except Exception:
            st.write("Response content (not JSON):", response.text[:500])

    if response and response.status_code == 201:
        st.success("Quiz created successfully!")
        return response.json()
    if response:
        try:
            # Better error handling for validation errors
            if response.status_code == 422:
                errors = response.json()
                # Extract and display validation errors
                error_details = []
                for error in errors.get("detail", []):
                    loc = " -> ".join(str(x) for x in error.get("loc", []))
                    msg = error.get("msg", "")
                    error_details.append(f"{loc}: {msg}")

                error_message = "Validation errors:\n" + "\n".join(error_details)
                st.error(error_message)
            else:
                error = response.json().get("detail", "Failed to create quiz")
                st.error(f"Error: {error}")
        except Exception as e:
            st.error(f"Error: {response.status_code} - {str(e)}")
    return None


def delete_quiz(quiz_id):
    """Delete a quiz."""
    response = api_delete(
        f"quizzes/{quiz_id}",
        token=st.session_state.token,
    )

    if response and response.status_code == 200:
        st.success("Quiz deleted successfully!")
        return True
    return False


def submit_quiz(quiz_id, answers):
    """Submit quiz answers."""
    response = api_post(
        f"quizzes/{quiz_id}/results",
        token=st.session_state.token,
        json_data={"answers": answers},
    )

    if response and response.status_code == 201:
        return response.json()
    if response:
        try:
            error = response.json().get("detail", "Failed to submit quiz")
            st.error(f"Error: {error}")
        except Exception:
            st.error(f"Error: {response.status_code}")
    return None


def get_trivia_categories():
    """Get trivia categories."""
    response = api_get("trivia/categories")

    if response and response.status_code == 200:
        categories = response.json()
        # Ensure all categories have proper ID types
        for cat in categories:
            if isinstance(cat.get("id"), str):
                try:
                    cat["id"] = int(cat["id"])
                except (ValueError, TypeError):
                    # Keep as string if can't convert
                    pass
        return categories
    return []


def create_trivia_quiz(
    title, description, amount, category=None, difficulty=None, question_type=None
):
    """Create a quiz with trivia questions."""
    # The backend endpoint expects the parameters as query parameters

    # Debug the trivia quiz request
    st.write(f"Debug: Creating trivia quiz with {amount} questions")

    # Ensure amount is an integer
    try:
        amount = int(amount)
    except (ValueError, TypeError):
        st.error("Amount must be a valid integer")
        return None

    # Build the query parameters
    query_params = {"title": title, "amount": amount}  # Explicitly as integer

    if description:
        query_params["description"] = description

    if category and category != 0:
        query_params["category"] = int(category)

    if difficulty and difficulty != "Any Difficulty":
        query_params["difficulty"] = difficulty.lower()

    if question_type and question_type != "Any Type":
        query_params["type"] = question_type.lower()

    # Log request details
    st.write("Sending trivia quiz request:")
    st.write(f"POST {API_URL}/trivia/create-quiz")
    st.write("Headers:", {"Authorization": f"Bearer {st.session_state.token}"})
    st.write("Query params:", query_params)

    # Make the request
    response = api_post(
        "trivia/create-quiz", token=st.session_state.token, params=query_params
    )

    # Log response details
    if response:
        st.write(f"Response status: {response.status_code}")
        try:
            st.write("Response content:", response.json())
        except Exception:
            st.write("Response content (not JSON):", response.text[:500])

    if response and response.status_code == 201:
        st.success("Quiz created successfully!")
        return response.json()
    if response:
        try:
            # Better error handling for validation errors
            if response.status_code == 422:
                errors = response.json()
                # Extract and display validation errors
                error_details = []
                if isinstance(errors.get("detail"), list):
                    for error in errors.get("detail", []):
                        loc = " -> ".join(str(x) for x in error.get("loc", []))
                        msg = error.get("msg", "")
                        error_details.append(f"{loc}: {msg}")
                else:
                    error_details.append(
                        str(errors.get("detail", "Unknown validation error"))
                    )

                error_message = "Validation errors:\n" + "\n".join(error_details)
                st.error(error_message)
            else:
                try:
                    error = response.json().get(
                        "detail", "Failed to create trivia quiz"
                    )
                except Exception:
                    error = response.text or f"Error {response.status_code}"
                st.error(f"Error: {error}")
        except Exception as e:
            st.error(f"Error: {response.status_code} - {str(e)}")
    return None


def get_leaderboard(quiz_id):
    """Get quiz leaderboard."""
    response = api_get(
        f"quizzes/{quiz_id}/results/leaderboard", token=st.session_state.token
    )

    if response and response.status_code == 200:
        return response.json()["entries"]
    return []


def get_user_results():
    """Get user's quiz results."""
    response = api_get(
        "quizzes/results/user",
        token=st.session_state.token,
    )

    if response and response.status_code == 200:
        return response.json()
    return []


# UI Components
def render_header():
    """Render the app header."""
    col1, col2, col3 = st.columns([1, 3, 1])

    with col1:
        st.markdown("# 📝 InnoQuiz")

    with col2:
        if st.session_state.token:
            cols = st.columns(4)
            if cols[0].button("🏠 Home", key="hdr_home"):
                navigate_to("home")
            if cols[1].button("📋 My Quizzes", key="hdr_my_quizzes"):
                navigate_to("my_quizzes")
            if cols[2].button("✏️ Create Quiz", key="hdr_create"):
                navigate_to("create_quiz")
            if cols[3].button("📊 Results", key="hdr_results"):
                navigate_to("results")

    with col3:
        if st.session_state.token and st.session_state.user:
            st.markdown(f"👤 **{st.session_state.user['username']}**")
            if st.button("Logout", key="btn_logout"):
                logout()

    st.divider()


# Page rendering functions
def render_login_page():
    """Render the login page."""
    st.title("Login to InnoQuiz")

    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)
        submit = col1.form_submit_button("Login", use_container_width=True)
        register_btn = col2.form_submit_button("Register", use_container_width=True)

        if submit and username and password:
            if login(username, password):
                navigate_to("home")

        if register_btn:
            navigate_to("register")


def render_register_page():
    """Render the registration page."""
    st.title("Create an Account")

    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns(2)
        submit = col1.form_submit_button("Register", use_container_width=True)
        back_btn = col2.form_submit_button("Back to Login", use_container_width=True)

        if submit:
            if not username or not email or not password:
                st.error("All fields are required")
            elif password != confirm:
                st.error("Passwords do not match")
            elif register(username, email, password):
                navigate_to("login")

        if back_btn:
            navigate_to("login")


def render_home_page():
    """Render the home page with available quizzes."""
    st.title("Available Quizzes")

    quizzes = get_quizzes()

    if not quizzes:
        st.info("No quizzes available. Create your first quiz!")
        if st.button("Create Quiz", key="home_create"):
            navigate_to("create_quiz")
    else:
        # Display quizzes in a grid
        cols = st.columns(3)
        for i, quiz in enumerate(quizzes):
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(quiz["title"])
                    st.write(quiz["description"] or "No description")
                    st.write(f"📝 {len(quiz['questions'])} questions")
                    st.write(f"👤 {quiz['author_username']}")

                    if st.button("Take Quiz", key=f"take_{quiz['id']}"):
                        navigate_to("take_quiz", quiz_id=quiz["id"])

                    # Only show delete if user is the author
                    if quiz.get("author_id") == st.session_state.user.get("id"):
                        if st.button("Delete Quiz", key=f"delete_{quiz['id']}"):
                            if delete_quiz(quiz["id"]):
                                st.rerun()


def render_my_quizzes_page():
    """Render my quizzes page."""
    st.title("My Quizzes")

    quizzes = get_quizzes(my_quizzes=True)

    if not quizzes:
        st.info("You haven't created any quizzes yet.")
        if st.button("Create a Quiz", key="my_create"):
            navigate_to("create_quiz")
    else:
        # Display quizzes in a grid
        cols = st.columns(3)
        for i, quiz in enumerate(quizzes):
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(quiz["title"])
                    st.write(quiz["description"] or "No description")
                    st.write(f"📝 {len(quiz['questions'])} questions")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Take", key=f"my_take_{quiz['id']}"):
                            navigate_to("take_quiz", quiz_id=quiz["id"])
                    with col2:
                        if st.button("Delete", key=f"my_del_{quiz['id']}"):
                            if delete_quiz(quiz["id"]):
                                st.rerun()


def render_create_quiz_page():
    """Render create quiz page."""
    st.title("Create a Quiz")

    # Add a reset button at the top to completely clear the form state
    if st.button("Reset Form State", key="reset_quiz_form"):
        # Clear all form-related state
        for key in list(st.session_state.keys()):
            if (
                key.startswith("q_")
                or key.startswith("question_data_")
                or key == "num_questions"
                or key == "prev_num_questions"
            ):
                del st.session_state[key]
        st.success("Form state cleared! Refreshing page...")
        st.rerun()

    # Quiz title and description form
    tab1, tab2 = st.tabs(["Create Manual Quiz", "Create from Trivia API"])

    # Manual quiz creation
    with tab1:
        with st.form("quiz_info_form"):
            st.subheader("Quiz Information")
            title = st.text_input("Quiz Title", key="quiz_title_input")
            description = st.text_area("Description", key="quiz_description_input")

            # Add a submit button for this form
            info_submit = st.form_submit_button(
                "Save Quiz Info", use_container_width=True
            )

            if info_submit:
                # Save the title and description to session state with different keys
                st.session_state.saved_quiz_title = title
                st.session_state.saved_quiz_description = description
                st.success("✅ Quiz information saved!")
                st.rerun()

        # Add a form outside the tabs to control the number of questions
        with st.form(key="question_count_form"):
            st.write("### Set Number of Questions")
            if "num_questions" not in st.session_state:
                st.session_state.num_questions = 3

            num_questions = st.number_input(
                "Number of Questions",
                min_value=1,
                max_value=20,
                value=st.session_state.get("num_questions", 3),
                key="num_questions_input",
            )

            # Submit button must be inside the form
            update_button = st.form_submit_button("Update Question Count")
            if update_button:
                st.session_state.num_questions = num_questions
                st.success(f"Question count updated to {num_questions}")
                st.rerun()

        # First, let users set how many answers they want for each question (outside the form)
        st.write("### Set Answer Counts")
        st.write(
            "Set the number of answer options for each question before creating your quiz:"
        )

        actual_num_questions = int(st.session_state.num_questions)
        answer_counts_cols = st.columns(min(actual_num_questions, 4))
        for i in range(actual_num_questions):
            col_idx = i % min(actual_num_questions, 4)
            with answer_counts_cols[col_idx]:
                # Initialize default if not set
                if f"q{i}_num_answers" not in st.session_state:
                    st.session_state[f"q{i}_num_answers"] = 4

                # Each question gets its own answer count control
                st.write(f"Question {i+1}")
                answers_count = st.number_input(
                    "# of Answers",
                    min_value=2,
                    max_value=10,
                    value=st.session_state[f"q{i}_num_answers"],
                    key=f"q{i}_num_answers_control",
                )

                # When value changes, update session state and rerun
                if st.button("Set", key=f"set_answers_{i}"):
                    st.session_state[f"q{i}_num_answers"] = int(answers_count)
                    st.success(f"Question {i+1}: {answers_count} answers")
                    st.rerun()

        st.divider()

        # Create individual forms for each question
        st.write("### Create Questions")

        # Initialize empty list to collect all valid questions
        completed_questions = 0

        # Create each question in its own form
        for i in range(actual_num_questions):
            with st.container(border=True):
                # Color coding for complete/incomplete questions
                if f"question_data_{i}" in st.session_state:
                    st.subheader(f"Question {i + 1} 📝")
                else:
                    st.subheader(f"Question {i + 1} ⬜")

                # Create a separate form for each question
                with st.form(key=f"question_form_{i}"):
                    q_text = st.text_input("Question Text", key=f"q_text_{i}")

                    col1, col2 = st.columns([3, 1])
                    with col1:
                        q_points = st.number_input(
                            "Points",
                            min_value=1,
                            max_value=10,
                            value=1,
                            key=f"q_points_{i}",
                        )
                    with col2:
                        # Show the number of answers that will be used (read-only)
                        st.write(
                            f"**{st.session_state.get(f'q{i}_num_answers', 4)} answer options**"
                        )

                    # Container for answers
                    st.write("#### Answers")
                    options_list = []
                    correct_answers = []

                    # Use the stored answer count, or default to 4
                    question_num_answers = int(
                        st.session_state.get(f"q{i}_num_answers", 4)
                    )

                    # Process each answer option
                    for j in range(question_num_answers):
                        cols = st.columns([3, 1])
                        with cols[0]:
                            answer_key = f"q{i}_a{j}_text"
                            answer_text = st.text_input(
                                f"Answer {j+1}",
                                key=answer_key,
                                value=st.session_state.get(answer_key, ""),
                            )
                        with cols[1]:
                            correct_key = f"q{i}_a{j}_correct"
                            is_correct = st.checkbox(
                                "Correct",
                                key=correct_key,
                                value=st.session_state.get(correct_key, False),
                            )

                        # Only include non-empty answers
                        if answer_text and answer_text.strip():
                            answer = answer_text.strip()
                            options_list.append(answer)
                            if is_correct:
                                correct_answers.append(answer)

                    # Add a save button for this question
                    save_question = st.form_submit_button(
                        f"💾 Save Question {i+1}", use_container_width=True
                    )

                    # Process form submission for this question
                    if save_question:
                        # Validate question completeness
                        has_text = bool(q_text and q_text.strip())
                        has_enough_options = len(options_list) >= 2
                        has_correct_answer = len(correct_answers) > 0
                        is_complete = (
                            has_text and has_enough_options and has_correct_answer
                        )

                        if is_complete:
                            # Store the question data in a temporary dict
                            question_data = {
                                "text": q_text,
                                "options": options_list,
                                "correct_answer": correct_answers,  # Send all correct answers
                                "points": int(q_points),
                                "num_answers": question_num_answers,
                            }

                            # Store this question for later
                            st.session_state[f"question_data_{i}"] = question_data
                            st.success(f"✅ Question {i+1} saved successfully!")
                            st.rerun()
                        else:
                            error_messages = []
                            if not has_text:
                                error_messages.append("❌ Question text is required")
                            if not has_enough_options:
                                error_messages.append(
                                    f"⚠️ Add at least 2 answer options (you have {len(options_list)})"
                                )
                            if not has_correct_answer:
                                error_messages.append(
                                    "⚠️ Select at least one correct answer"
                                )

                            for message in error_messages:
                                st.error(message)

                # Show status outside the form
                if f"question_data_{i}" in st.session_state:
                    completed_questions += 1
                    st.success("✅ Question saved and ready for submission")
                else:
                    st.warning(
                        "⚠️ Question not yet saved - fill in and save this question"
                    )

        # Create a separate form for the quiz submission
        st.divider()

        # Summary of quiz creation status
        st.write(
            f"### Quiz Summary: {completed_questions}/{actual_num_questions} questions completed"
        )

        # Make sure the progress calculation is safe (avoid division by zero)
        if actual_num_questions > 0:
            progress = completed_questions / actual_num_questions
        else:
            progress = 0.0

        st.progress(progress)

        with st.form("submit_quiz_form"):
            # Show the saved quiz information
            if (
                "saved_quiz_title" in st.session_state
                and st.session_state.saved_quiz_title
            ):
                st.success(f"✅ Title: {st.session_state.saved_quiz_title}")
            else:
                st.error(
                    "❌ Quiz title is required - please save quiz information first"
                )

            if (
                "saved_quiz_description" in st.session_state
                and st.session_state.saved_quiz_description
            ):
                st.success(f"✅ Description: {st.session_state.saved_quiz_description}")

            # Give clear instructions for submission
            if completed_questions == 0:
                st.error(
                    "❌ You need to save at least one complete question before submitting"
                )
            else:
                st.success(
                    f"✅ You have {completed_questions} questions ready to submit"
                )

            # Create button with appropriate state - use actual question count
            quiz_title_missing = (
                "saved_quiz_title" not in st.session_state
                or not st.session_state.saved_quiz_title
            )
            button_disabled = quiz_title_missing or completed_questions == 0

            # Submit form button with clear instructions
            st.write("### Submit Your Quiz")
            st.write("Make sure to save each question before submitting your quiz!")
            submit_button = st.form_submit_button(
                "📤 Submit Quiz",
                type="primary",
                disabled=button_disabled,
                use_container_width=True,
            )

            if submit_button:
                if quiz_title_missing:
                    st.error(
                        "Quiz title is required - please save quiz information first"
                    )
                elif completed_questions == 0:
                    st.error("At least one valid question with answers is required")
                else:
                    # Collect all completed questions from session state
                    final_questions = []

                    # Debugging summary
                    st.write(
                        f"### Preparing to submit quiz with {completed_questions} complete questions"
                    )

                    # First pass: collect all completed questions
                    for i in range(actual_num_questions):
                        if f"question_data_{i}" in st.session_state:
                            question = st.session_state[f"question_data_{i}"]
                            st.write(
                                f"Adding complete question {i+1}: {question['text'][:30]}..."
                            )
                            final_questions.append(question)

                    # Debug: Show how many questions we're submitting
                    st.write(f"Submitting {len(final_questions)} completed questions")

                    # Get the title and description from session state
                    title = st.session_state.saved_quiz_title
                    description = st.session_state.saved_quiz_description or ""

                    # Create the quiz with the final questions list
                    if create_quiz(title, description, final_questions):
                        # Clear question-related session state to avoid stale data
                        for i in range(
                            actual_num_questions
                        ):  # Clear enough for the max possible questions
                            if f"question_data_{i}" in st.session_state:
                                del st.session_state[f"question_data_{i}"]
                            if f"partial_question_{i}" in st.session_state:
                                del st.session_state[f"partial_question_{i}"]

                        navigate_to("my_quizzes")

    # Trivia API quiz creation
    with tab2:
        with st.form("trivia_quiz_form"):
            st.subheader("Create a Quiz from Trivia Database")

            title = st.text_input("Quiz Title", key="trivia_title")
            description = st.text_area("Description", key="trivia_desc")

            # Get trivia categories and handle errors gracefully
            categories = get_trivia_categories()
            if not categories:
                st.warning("⚠️ Could not load trivia categories. Using default options.")
                category_options = {0: "Any Category"}
            else:
                # Convert all category IDs to integers to ensure proper typing
                category_options = {}
                for cat in categories:
                    try:
                        cat_id = int(cat["id"])
                        category_options[cat_id] = cat["name"]
                    except (ValueError, TypeError):
                        pass  # Skip categories with non-integer IDs
                category_options[0] = "Any Category"

            # Setup in columns for better appearance
            col1, col2 = st.columns(2)
            with col1:
                amount = st.slider(
                    "Number of Questions",
                    min_value=5,
                    max_value=50,
                    value=10,
                    key="trivia_amount",
                )
                # Debug the selected amount
                st.write(f"Selected {amount} questions")

                category = st.selectbox(
                    "Category",
                    options=list(category_options.keys()),
                    format_func=lambda x: category_options.get(x, "Any"),
                )

            with col2:
                difficulty = st.selectbox(
                    "Difficulty",
                    options=["Any Difficulty", "easy", "medium", "hard"],
                    format_func=lambda x: x.title() if x != "Any Difficulty" else x,
                )

                question_type = st.selectbox(
                    "Question Type",
                    options=["Any Type", "multiple", "boolean"],
                    format_func=lambda x: {
                        "Any Type": "Any Type",
                        "multiple": "Multiple Choice",
                        "boolean": "True/False",
                    }.get(x, x.title()),
                )

                st.markdown("---")
                st.markdown(
                    "Questions will be randomly generated from the selected category and difficulty."
                )

            # Submit button for the form
            submit_trivia = st.form_submit_button("Create Trivia Quiz", type="primary")

            if submit_trivia:
                if not title:
                    st.error("Quiz title is required")
                else:
                    with st.spinner("Generating questions from trivia database..."):
                        if create_trivia_quiz(
                            title,
                            description,
                            amount,
                            category,
                            difficulty,
                            question_type,
                        ):
                            st.success("Quiz created successfully!")
                            # Directly navigate to my quizzes
                            navigate_to("my_quizzes")


def render_take_quiz_page():
    """Render take quiz page."""
    if not st.session_state.current_quiz:
        st.error("No quiz selected")
        if st.button("Back to Home"):
            navigate_to("home")
        return

    quiz = get_quiz(st.session_state.current_quiz)
    if not quiz:
        st.error("Quiz not found")
        if st.button("Back to Home", key="quiz_not_found"):
            navigate_to("home")
        return

    st.title(quiz["title"])
    if quiz["description"]:
        st.write(quiz["description"])

    # Show leaderboard in sidebar
    with st.sidebar:
        st.header("Leaderboard")
        leaderboard = get_leaderboard(quiz["id"])
        if leaderboard:
            for i, entry in enumerate(leaderboard[:10]):  # Show top 10
                st.write(f"**#{i + 1}: {entry['username']}**")
                st.write(
                    f"Score: {entry['score']}/{entry['max_score']} ({entry['percentage']:.1f}%)"
                )
        else:
            st.info("No results yet. Be the first!")

    # Show quiz result if already submitted
    if st.session_state.quiz_result:
        result = st.session_state.quiz_result
        score = result["score"]
        max_score = result["max_score"]
        percentage = (score / max_score * 100) if max_score > 0 else 0

        st.success(
            f"Quiz completed! You scored {score}/{max_score} ({percentage:.1f}%)"
        )

        # Show detailed results
        st.subheader("Your Results")
        for q in quiz["questions"]:
            q_id = str(q["id"])
            user_answer = st.session_state.quiz_answers.get(q_id, "Not answered")
            correct = user_answer == q["correct_answer"]

            with st.container(border=True):
                st.write(f"**Q: {q['text']}**")
                st.write(f"Your answer: {user_answer}")
                st.write(f"Correct answer: {q['correct_answer']}")

                if correct:
                    st.success(f"Correct! (+{q['points']} points)")
                else:
                    st.error("Incorrect")

        col1, col2 = st.columns(2)
        if col1.button("Back to Home", key="back_after_submit"):
            navigate_to("home")
        if col2.button("Try Again", key="retry_quiz"):
            # Reset quiz state
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None
            st.rerun()
    else:
        # Show quiz form
        with st.form(key=f"quiz_form_{quiz['id']}"):
            for i, question in enumerate(quiz["questions"]):
                st.write(f"### Question {i + 1}: {question['text']}")
                answer = st.radio(
                    "Select your answer:",
                    options=question["options"],
                    key=f"q_{question['id']}_{i}",
                )
                st.session_state.quiz_answers[str(question["id"])] = answer
                st.divider()

            submit = st.form_submit_button("Submit Answers")

            if submit:
                # Format answers for API
                answers = [
                    {"question_id": int(q_id), "answer": answer}
                    for q_id, answer in st.session_state.quiz_answers.items()
                ]

                result = submit_quiz(quiz["id"], answers)
                if result:
                    st.session_state.quiz_result = result
                    st.rerun()


def render_results_page():
    """Render user results page."""
    st.title("My Quiz Results")

    results = get_user_results()

    if not results:
        st.info("You haven't completed any quizzes yet.")
        if st.button("Find quizzes to take"):
            navigate_to("home")
    else:
        # Group results by quiz
        results_by_quiz = {}
        for result in results:
            quiz_id = result["quiz_id"]
            if quiz_id not in results_by_quiz:
                results_by_quiz[quiz_id] = []
            results_by_quiz[quiz_id].append(result)

        # Display results grouped by quiz
        for quiz_id, quiz_results in results_by_quiz.items():
            quiz_title = quiz_results[0]["quiz_title"] or f"Quiz #{quiz_id}"
            with st.expander(quiz_title, expanded=True):
                # Sort by most recent
                sorted_results = sorted(
                    quiz_results, key=lambda x: x["completed_at"], reverse=True
                )

                for i, result in enumerate(sorted_results):
                    score = result["score"]
                    max_score = result["max_score"]
                    percentage = (score / max_score * 100) if max_score > 0 else 0

                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Attempt {i + 1}**")
                            st.write(f"Date: {result['completed_at']}")
                            st.write(f"Score: {score}/{max_score} ({percentage:.1f}%)")

                        with col2:
                            if st.button("Take Again", key=f"again_{result['id']}"):
                                navigate_to("take_quiz", quiz_id=quiz_id)

                # Add a "take again" button at the bottom
                if st.button("Take This Quiz Again", key=f"quiz_again_{quiz_id}"):
                    navigate_to("take_quiz", quiz_id=quiz_id)


# Main application
def main():
    # Clear the page to start fresh
    st.empty()

    # Check if token is valid when a user is logged in
    if st.session_state.is_logged_in and st.session_state.token:
        # If we have a token but no user data, try to get user info
        if not st.session_state.user:
            st.session_state.user = get_current_user()

            # If we can't get user info, token is probably invalid
            if not st.session_state.user:
                st.session_state.token = None
                st.session_state.is_logged_in = False
                st.warning("Your session has expired. Please login again.")
                st.session_state.page = "login"

        # If user is on login page but already logged in, redirect to home
        elif st.session_state.page == "login":
            navigate_to("home")

    # Only show header if logged in
    if st.session_state.is_logged_in and st.session_state.token:
        render_header()

    # Render the current page
    current_page = st.session_state.page

    if current_page == "login":
        render_login_page()
    elif current_page == "register":
        render_register_page()
    elif current_page == "home":
        if not st.session_state.is_logged_in:
            navigate_to("login")
        else:
            render_home_page()
    elif current_page == "my_quizzes":
        if not st.session_state.is_logged_in:
            navigate_to("login")
        else:
            render_my_quizzes_page()
    elif current_page == "create_quiz":
        if not st.session_state.is_logged_in:
            navigate_to("login")
        else:
            render_create_quiz_page()
    elif current_page == "take_quiz":
        if not st.session_state.is_logged_in:
            navigate_to("login")
        else:
            render_take_quiz_page()
    elif current_page == "results":
        if not st.session_state.is_logged_in:
            navigate_to("login")
        else:
            render_results_page()


if __name__ == "__main__":
    main()
