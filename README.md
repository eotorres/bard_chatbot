Script construido para execução do bard via streamlit.

O processo constiste em armazenar por nome de computador o histórico de consulta.
O streamlit tem a opção de consultar e a opção de histórico das conversas.


Para o script funcionar, precisa alterar os caminhos 
# Connect to SQLite database
conn = sqlite3.connect(r'D:\ProjetoDados\Desenvolvimentos\ChatBot\Bard\chat_history.db')
c = conn.cursor()

# Save the conversation history to CSV in a specific directory
    csv_directory = r'D:\ProjetoDados\Desenvolvimentos\ChatBot\Bard'
    csv_filename = 'chat_history.csv'
    csv_path = os.path.join(csv_directory, csv_filename)
    df.to_csv(csv_path, index=False)
    st.markdown(f"### [Download CSV]({csv_path})")

A alteração precisa ser no diretório de sua escolha.

Para utilizar o cookie do seu navegador é necessário alterar,

os.environ['_BARD_API_KEY'] = 'cgi95_I7_jZh_eWSffPddrEa7kyv0kI0y9BZ8Zur8IIN5Wxbkocxmwt-Vgmy6x29VoW0IA.'
token = 'cgi95_I7_jZh_eWSffPddrEa7kyv0kI0y9BZ8Zur8IIN5Wxbkocxmwt-Vgmy6x29VoW0IA.'

e passar as suas credenciais no ""__Secure-1PSID""

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





