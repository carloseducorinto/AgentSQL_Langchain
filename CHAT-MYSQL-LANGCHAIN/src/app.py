from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from database import Database
import os


load_dotenv()
database = Database()




if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content='Hello! I am DerivaSQL, your SQL chatbot. How can I help you?'),
        
    ]

st.set_page_config(page_title='DerivaSQL', page_icon=':speech_baloon:')
st.title('DerivaSQL')


with st.sidebar:
    st.subheader('Settings')
    st.write('This is the DerivaSQL chat solution using MySQL. Connect to the database and start chatting.')
    
    st.text_input('Host', value='instancia-langchain-db.cr2e8io4erie.sa-east-1.rds.amazonaws.com', key='Host')
    st.text_input('Port', value='3306',key = 'Port')
    st.text_input('User', value='admin',key = 'User')
    st.text_input('Password', type='password', value='Admin1605', key ='Password')
    st.text_input('Database', value='langchain_db',key = 'Database')
    
    if st.button('Connect'):
        with st.spinner('Connecting to database ...'):
            #print('passei aqui')
            db = database.connect_to_database(
                st.session_state['Host'],
                st.session_state['User'],
                st.session_state['Password'],
                st.session_state['Port'],
                st.session_state['Database']
            )
            st.session_state.db = db
            print(f'st.session_state.db {st.session_state.db}')
            st.success('Connected to the database!')
    

for message in st.session_state.chat_history:
    #print('To Passando')
    if isinstance(message, AIMessage):
        with st.chat_message('AI'):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message('Human'):
            st.markdown(message.content)        
            
user_query = st.chat_input('Type your query...')

if user_query is not None and user_query.strip() != '':
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message('Human'):
        st.markdown(user_query)
        
    with st.chat_message('AI'):
        response = database.get_response(user_query, st.session_state.db, st.session_state.chat_history)
        #sql_chain = database.get_sql_chain(st.session_state.db)
        #response = sql_chain.invoke({
        #    "chat_history": st.session_state.chat_history,
        #    "question": user_query
        #}
        #)
        st.markdown(response) 
    
    st.session_state.chat_history.append(AIMessage(content=response))    