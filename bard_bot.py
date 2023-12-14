import os
from io import BytesIO
import socket
import streamlit as st
import requests
from bardapi import Bard
from PIL import Image
import pandas as pd
import sqlite3
from datetime import datetime

# Setting page title and header
st.set_page_config(page_title="IA", 
                   page_icon=":robot_face:",
                   layout="wide")

# Obtém o nome da máquina
hostname = socket.gethostname()

# Configura a posição do nome da máquina no canto superior direito
st.write(
    f'<p style="position: absolute; top: 5px; right: 10px;">User: {hostname}</p>',
    unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Assistente de IA 🤖</h1>"
            """
           <style>
           [data-testid="stSidebar"][aria-expanded="true"]{
               min-width: 150px;
               max-width: 190px;
           }
           """, unsafe_allow_html=True)

# Connect to SQLite database
conn = sqlite3.connect(r'D:\ProjetoDados\Desenvolvimentos\ChatBot\Bard\chat_history.db')
c = conn.cursor()

# Create a table for chat history if it doesn't exist
c.execute('''
          CREATE TABLE IF NOT EXISTS chat_history (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              role TEXT,
              content TEXT,
              hostname TEXT,
              date TEXT
          )
          ''')
conn.commit()

# Inicializa o estado do chat
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Load existing conversation history from SQLite
c.execute('SELECT * FROM chat_history')
result = c.fetchall()
existing_messages = [{'role': row[1], 'content': row[2], 'hostname': row[3], 'date': row[4]} for row in result]

# Adiciona mensagens existentes ao estado do Streamlit
st.session_state["messages"].extend(existing_messages)

#_BARD_API_KEY e token , precisam ser o retorno do  __Secure-1PSID
os.environ['_BARD_API_KEY'] = ''
token = ''

# Tratativa para pagina Analytics
bard_api_key = token
os.environ["_BARD_API_KEY"] = bard_api_key

session = requests.Session()
session.headers = {
    "Host": "bard.google.com",
    "X-Same-Domain": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "https://bard.google.com",
    "Referer": "https://bard.google.com/",
}
session.cookies.set("__Secure-1PSID", os.getenv("_BARD_API_KEY"))
bard = Bard(token=token, session=session, timeout=30)

opcoes = ['Boas-vindas', 'Chat', 'Histórico']

pagina = st.sidebar.selectbox('Navegue pelo menu:', opcoes)

if pagina == 'Boas-vindas':
    st.header('Meu objetivo é auxiliar vocês em responder as perguntas feitas.')

if pagina == 'Chat':
    st.title('Chat com o Assistente de IA')
    
    # Elementos de interface do Streamlit
    use_image_question = st.checkbox("Fazer pergunta com base em uma imagem?")
    uploaded_image = None

    if use_image_question:
        uploaded_image = st.file_uploader("Faça upload de uma imagem (jpg, jpeg, png, webp)",
                                          type=["jpg", "jpeg", "png", "webp"])
    
    prompt = st.text_area('Faça uma pergunta:', 
                          value='',
                          height=160)

    if st.button("Enviar"):
        if use_image_question and uploaded_image is not None:
            # Converta a imagem para bytes
            image_bytes = uploaded_image.read()            
            # Faça a pergunta ao Bard sobre a imagem
            bard_answer = bard.ask_about_image(prompt, image_bytes)            
            # Exiba a imagem
            st.image(Image.open(BytesIO(image_bytes)),
                     caption="Imagem carregada",
                     use_column_width=True)
            
            # Exiba a pergunta e a resposta do Bard
            st.write("🙂 User:", prompt)
            st.write("🤖 Assistant:", bard_answer['content'])
            
            # Salve a pergunta e a resposta na sessão
            st.session_state["messages"].append({"role": "user", "content": prompt, "hostname": hostname, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            st.session_state["messages"].append({"role": "assistant", "content": bard_answer['content'], "hostname": hostname, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        elif not use_image_question:
            # Se o usuário não escolheu fazer uma pergunta com base em uma imagem
            st.write("🙂 User:", prompt)
            
            # Faz a pergunta ao Bard sem imagem
            bard_answer = bard.get_answer(prompt)
            
            # Exibe a resposta do Bard
            st.write("🤖 Assistant:", bard_answer['content'])
            
            # Salva a pergunta e a resposta na sessão
            st.session_state["messages"].append({"role": "user", "content": prompt, "hostname": hostname, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            st.session_state["messages"].append({"role": "assistant", "content": bard_answer['content'], "hostname": hostname, "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        else:
            st.warning("Faça o upload de uma imagem antes de enviar a pergunta, pois você escolheu fazer uma pergunta com base em uma imagem.")

if pagina == 'Histórico':
    st.title('Histórico da Conversa')

    # Save the conversation history to SQLite and CSV
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_messages = [(msg['role'], msg['content'], msg['hostname'], msg['date']) for msg in st.session_state["messages"]]
    c.executemany('INSERT INTO chat_history (role, content, hostname, date) VALUES (?, ?, ?, ?)', new_messages)
    conn.commit()

    # Fetch conversation history from SQLite
    c.execute('SELECT * FROM chat_history')
    result = c.fetchall()

    # Create a DataFrame from the SQLite result
    df = pd.DataFrame(result, columns=['id', 'role', 'content', 'hostname', 'date'])

    # Separate user and assistant messages
    user_messages = df[df['role'] == 'user'][['content', 'date']].rename(columns={'content': 'User', 'date': 'User_Date'})
    assistant_messages = df[df['role'] == 'assistant'][['content', 'hostname', 'date']].rename(columns={'content': 'Assistant', 'hostname': 'Hostname', 'date': 'Assistant_Date'})

    # Merge user and assistant messages on the date column
    merged_df = pd.merge(user_messages, assistant_messages, left_on='User_Date', right_on='Assistant_Date', how='outer')

    # Display the conversation history as an interactive table
    st.write(merged_df[['User', 'Assistant', 'Hostname', 'Assistant_Date']])

    # Save the conversation history to CSV in a specific directory
    csv_directory = r'D:\ProjetoDados\Desenvolvimentos\ChatBot\Bard'
    csv_filename = 'chat_history.csv'
    csv_path = os.path.join(csv_directory, csv_filename)
    df.to_csv(csv_path, index=False)
    st.markdown(f"### [Download CSV]({csv_path})")



