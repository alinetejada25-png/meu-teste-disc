import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÕES DE ACESSO ---
SENHA_ACESSO = "disc"

# --- CONFIGURAÇÕES DE ESTILO (Visual para Empreendedoras) ---
st.set_page_config(page_title="Perfil DISC", page_icon="🧩", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    h1 { color: #8e44ad; font-family: 'Arial'; text-align: center; }
    .stButton>button { 
        background-color: #8e44ad; color: white; border-radius: 25px; 
        width: 100%; border: none; padding: 12px; font-weight: bold;
    }
    div[data-testid="stBlock"] {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔒 Acesso Restrito")
    senha = st.text_input("Digite a senha para iniciar:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_ACESSO:
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

# --- FUNÇÃO DE ENVIO DE E-MAIL ---
def enviar_email(nome, whats, empresa, b1, b2):
    try:
        usuario = st.secrets["EMAIL_USER"]
        senha_app = st.secrets["EMAIL_PASSWORD"]
        destinatario = st.secrets["CONSULTANT_EMAIL"]

        msg = MIMEMultipart()
        msg['From'] = usuario
        msg['To'] = destinatario
        msg['Subject'] = f"NOVO TESTE DISC: {nome}"

        corpo = f"""
        NOVO PERFIL COMPORTAMENTAL
        ---------------------------
        NOME: {nome}
        WHATSAPP: {whats}
        EMPRESA: {empresa}

        RESPOSTAS DO TESTE (VALORES DE 1 A 4):
        ---------------------------
        BLOCO 1: {b1}
        
        BLOCO 2: {b2}
        ---------------------------
        """
        msg.attach(MIMEText(corpo, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(usuario, senha_app)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        return False

# --- FORMULÁRIO ---
st.title("🧩 Teste de Perfil Comportamental DISC")
st.write("Responda com honestidade. Use 1 para o que MENOS se identifica e 4 para o que MAIS se identifica. Não repita números na mesma linha.")

with st.container():
    st.subheader("📝 Seus Dados")
    nome = st.text_input("Nome Completo")
    whats = st.text_input("WhatsApp")
    empresa = st.text_input("Empresa/Ocupação")

# Definição das perguntas conforme sua imagem
perguntas = [
    ["Assertiva", "Persuasiva", "Paciente", "Contemplativa"],
    ["Ser decisivo", "Amizade social", "Ser parte de um time", "Planejamento e ordem"],
    ["Variedade", "Menos estrutura", "Harmonia", "Lógica"],
    ["Ditatorial", "Sarcástico", "Submisso", "Arredio"]
]

def montar_bloco(titulo, lista, chave):
    st.subheader(titulo)
    respostas = {}
    for i, row in enumerate(lista):
        st.write(f"**Linha {i+1}:**")
        cols = st.columns(4)
        vals = []
        for j, item in enumerate(row):
            v = cols[j].number_input(item, 1, 4, 1, key=f"{chave}_{i}_{j}")
            vals.append(v)
        
        if len(set(vals)) < 4:
            st.warning(f"Atenção: Não repita números na Linha {i+1}")
        respostas[f"L{i+1}"] = vals
    return respostas

resp_b1 = montar_bloco("🏢 Bloco 1: Como você se vê", perguntas, "b1")
resp_b2 = montar_bloco("🌟 Bloco 2: Como os outros te veem", perguntas, "b2")

if st.button("FINALIZAR E ENVIAR"):
    if not nome or not whats:
        st.error("Preencha seu nome e WhatsApp.")
    else:
        sucesso = enviar_email(nome, whats, empresa, resp_b1, resp_b2)
        if sucesso:
            st.balloons()
            st.success("✅ Enviado! Sua consultora entrará em contato com o resultado em breve.")
        else:
            st.error("Erro ao enviar. Verifique as configurações de e-mail.")