import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORES DA MARCA CONEXA ---
LARANJA = "#ff7f50"
VINHO = "#800020"
BEGE = "#ece6e0"

st.set_page_config(page_title="Conexa - Avaliação DISC", page_icon="📈", layout="centered")

# --- ESTILO VISUAL (CLEAN & PROFISSIONAL) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BEGE}; }}
    h1 {{ color: {VINHO}; font-family: 'Arial'; text-align: center; font-weight: bold; }}
    h3 {{ color: {VINHO}; font-family: 'Arial'; }}
    .stButton>button {{ 
        background-color: {LARANJA}; color: white; border-radius: 10px; 
        width: 100%; border: none; padding: 15px; font-weight: bold; font-size: 18px;
    }}
    .stButton>button:hover {{ background-color: {VINHO}; }}
    div[data-testid="stBlock"] {{
        background-color: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px;
    }}
    .instrucoes {{
        background-color: white; padding: 20px; border-left: 5px solid {LARANJA};
        border-radius: 10px; margin-bottom: 25px; font-size: 16px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.markdown(f"<h1>CONEXA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color:#800020;'>Portal de Avaliação</h3>", unsafe_allow_html=True)
    senha = st.text_input("Senha de acesso:", type="password")
    if st.button("ACESSAR"):
        if senha == "disc":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Senha incorreta.")
    st.stop()

# --- INTRODUÇÃO ---
st.markdown(f"<h1 style='color:{LARANJA};'>CONEXA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 20px; color:#800020; font-weight:bold;'>Transformação e Desenvolvimento</p>", unsafe_allow_html=True)

st.markdown(f"""
<div class="instrucoes">
    <strong>Bem-vinda à sua jornada de autoconhecimento!</strong><br><br>
    Este teste identifica como você se comporta e reage a diferentes situações. 
    Lembre-se: <strong>não existe resposta certa ou errada</strong>. <br><br>
    O propósito é entender seu estilo único para <strong>potencializar seus resultados</strong> e sua liderança.
    <br><br>
    <strong>Como responder:</strong><br>
    Em cada linha, atribua notas de 1 a 4:<br>
    • <b>4:</b> O que MAIS descreve você.<br>
    • <b>1:</b> O que MENOS descreve você.<br>
    ⚠️ <b>Atenção:</b> Não repita números na mesma linha.
</div>
""", unsafe_allow_html=True)

# --- DADOS ---
with st.container():
    st.markdown("### 📋 Seus Dados")
    nome = st.text_input("Nome Completo")
    whats = st.text_input("WhatsApp (com DDD)")
    empresa = st.text_input("Empresa ou Cargo")

# --- MAPEAMENTO DISC ---
# Ordem das colunas: Dominância (D), Influência (I), Estabilidade (S), Conformidade (C)
mapa_letras = ["D", "I", "S", "C"]

# PALAVRAS DO BLOCO 1 (COMO EU AJO)
grupo1 = [
    ["Direta e Decidida", "Comunicativa e Influente", "Calma e Acolhedora", "Analítica e Observadora"],
    ["Focada em Resultados", "Focada em Pessoas", "Focada em Apoiar o Time", "Focada em Processos e Regras"],
    ["Gosta de Desafios", "Gosta de Novidades", "Gosta de Harmonia", "Gosta de Lógica e Fatos"],
    ["Em conflito: Enfrenta", "Em conflito: Persuade", "Em conflito: Cede", "Em conflito: Analisa"]
]

# PALAVRAS DO BLOCO 2 (COMO AS PESSOAS ME VEEM)
grupo2 = [
    ["Independente e Firme", "Sociável e Interativa", "Estável e Paciente", "Precisa e Correta"],
    ["Pessoa Intensa", "Pessoa Entusiasta", "Pessoa Acolhedora", "Pessoa Cuidadosa"],
    ["Assume Riscos", "Busca Reconhecimento", "Busca Segurança", "Busca Qualidade"],
    ["Decisões Rápidas", "Decisões Emocionais", "Decisões Pensadas", "Decisões Técnicas"]
]

def render_bloco(titulo, perguntas, chave):
    st.markdown(f"<h3>{titulo}</h3>", unsafe_allow_html=True)
    res = {}
    for i, labels in enumerate(perguntas):
        st.write(f"**Grupo {i+1}:**")
        cols = st.columns(4)
        notas = []
        for j, texto in enumerate(labels):
            n = cols[j].number_input(texto, 1, 4, 1, key=f"{chave}_{i}_{j}")
            notas.append(n)
        if len(set(notas)) < 4:
            st.warning("⚠️ Atenção: Não repita números nesta linha. Use 1, 2, 3 e 4.")
        res[f"L{i}"] = notas
    return res

# Renderizar os dois blocos
res1 = render_bloco("🏢 Bloco 1: Como eu ajo (Estilo de Trabalho)", grupo1, "b1")
st.markdown("---")
res2 = render_bloco("🌟 Bloco 2: Como eu acho que as pessoas me veem", grupo2, "b2")

# --- PROCESSAMENTO E ENVIO ---
if st.button("FINALIZAR E ENVIAR AVALIAÇÃO"):
    if not nome or not whats:
        st.error("Por favor, preencha seu nome e WhatsApp antes de enviar.")
    else:
        # Calcular Pontuação Total
        pontos = {"D": 0, "I": 0, "S": 0, "C": 0}
        for bloco in [res1, res2]:
            for linha in bloco.values():
                for idx, nota in enumerate(linha):
                    pontos[mapa_letras[idx]] += nota
        
        # Envio de E-mail
        try:
            # Tenta ler os segredos
            u = st.secrets["EMAIL_USER"]
            p = st.secrets["EMAIL_PASSWORD"]
            d = st.secrets["CONSULTANT_EMAIL"]
            
            msg = MIMEMultipart()
            msg['Subject'] = f"AVALIAÇÃO DISC CONEXA: {nome}"
            corpo = f"TESTE CONEXA\nNome: {nome}\nWhatsApp: {whats}\nD:{pontos['D']} I:{pontos['I']} S:{pontos['S']} C:{pontos['C']}"
            msg.attach(MIMEText(corpo, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(u, p)
            server.send_message(msg)
            server.quit()
            
            st.balloons()
            st.success("✅ Avaliação enviada com sucesso!")
        except Exception as e:
            # ISSO VAI MOSTRAR O ERRO REAL NA TELA
            st.error(f"Ocorreu um erro técnico: {e}")
            st.info("Verifique se a senha de 16 letras no Secrets está correta e sem espaços.")
