import streamlit as st
import auth_functions
import requests
from push_to_firestore import write_to_firestore, prev_ques
import json
import os
email = None
## -------------------------------------------------------------------------------------------------
## Not logged in -----------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
if 'user_info' not in st.session_state:
    st.title('Login/SignUp')
    col1,col2,col3 = st.columns([1,2,1])

    # Authentication form layout
    do_you_have_an_account = col2.selectbox(label='Do you have an account?',options=('Yes','No','I forgot my password'))
    auth_form = col2.form(key='Authentication form',clear_on_submit=False)
    email = auth_form.text_input(label='Email')
    password = auth_form.text_input(label='Password',type='password') if do_you_have_an_account in {'Yes','No'} else auth_form.empty()
    auth_notification = col2.empty()

    # Sign In
    if do_you_have_an_account == 'Yes' and auth_form.form_submit_button(label='Sign In',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Signing in'):
            auth_functions.sign_in(email,password)

    # Create Account
    elif do_you_have_an_account == 'No' and auth_form.form_submit_button(label='Create Account',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Creating account'):
            auth_functions.create_account(email,password)

    # Password Reset
    elif do_you_have_an_account == 'I forgot my password' and auth_form.form_submit_button(label='Send Password Reset Email',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Sending password reset link'):
            auth_functions.reset_password(email)

    # Authentication success and warning messages
    if 'auth_success' in st.session_state:
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success
    elif 'auth_warning' in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning

## -------------------------------------------------------------------------------------------------
## Logged in ---------------------------------------------------------------------------------------
## -------------------------------------------------------------------------------------------------
else:
    st.title("Semantic Question Similarity Analyzer")
    user_info = st.session_state['user_info']
    email = user_info['email']
    previous_questions = prev_ques(email)
    with st.sidebar:
            if previous_questions:
                st.header("Previous Questions")
                for question in previous_questions:
                    ques = question.to_dict()
                    #st.write(ques["Sentence_1"])
                    disp = "Question 1: {}\nQuestion 2: {}\nSimilarity:{}".format(ques["Sentence_1"],ques["Sentence_2"],ques["Similarity"])
                    st.text(disp)
            else:
                st.write("No previous questions found.")

    # Similarity Code Start---------
    # Define the API URL and query parameters
    url = "https://twinword-text-similarity-v1.p.rapidapi.com/similarity/"

    # Create empty textboxes for user input
    textbox1 = st.text_input("Enter First Question:")
    textbox2 = st.text_input("Enter Second Question:")

    # Create a button to trigger the API call
    button = st.button(label="Calculate Similarity",)

    # Check if the button is clicked
    if button:
        # Get the text from the textboxes
        text1 = textbox1
        text2 = textbox2

        # Construct the request payload
        payload = {"text1": text1, "text2": text2}

        # Set the API headers
        headers = json.load(open(os.path.join(os.path.dirname(__file__), 'secrets/RapidAPI.json'), 'r'))

        # Send the API request and get the response
        response = requests.post(url, data=payload, headers=headers)

        # Extract the similarity score from the response
        similarity_score = response.json()["similarity"]

        # Display the similarity score
        st.write("Similarity score:", similarity_score)

        # Pushing data to Firestore
        previous_questions = write_to_firestore(text1, text2, similarity_score, email)

    # Similarity Code End-----------

    # Sign out
    st.header('Sign out:')
    st.button(label='Sign Out',on_click=auth_functions.sign_out,type='primary')

    # Delete Account
    st.header('Delete account:')
    password = st.text_input(label='Confirm your password',type='password')
    st.button(label='Delete Account',on_click=auth_functions.delete_account,args=[password],type='primary')
