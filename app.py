import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORES DA MARCA CONEXA ---
LARANJA = "#ff7f50"
VINHO = "#800020"
BEGE = "#ece6e0"

st.set_page_config(page_title="Conexa - Avaliação DISC", page_icon="📈", layout="centered")

# --- ESTILO VISUAL ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BEGE}; }}
    h1 {{ color: {VINHO}; font-family: 'Arial'; text-align: center; font-weight: bold; }}
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
st.markdown("<p style='text-align: center; font-size: 20px;'>Transformação e Desenvolvimento</p>", unsafe_allow_html=True)

st.markdown(f"""
<div class="instrucoes">
    <strong>Bem-vinda à sua jornada de autoconhecimento!</strong><br><br>
    Este teste identifica como você se comporta e reage a diferentes situações. 
    Lembre-se: <strong>não existe resposta certa ou errada</strong>. <br><br>
    O propósito é entender seu estilo único para <strong>potencializar seus resultados</strong>.
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
    whats = st.text_input("WhatsApp")
    empresa = st.text_input("Empresa/Cargo")

# --- PERGUNTAS SIMPLIFICADAS ---
# Mapeamento interno: D, I, S, C
mapa_letras = ["D", "I", "S", "C"]

grupo1 = [
    ["Direta e Decidida", "Comunicativa e Influente", "Calma e Acolhedora", "Analítica e Observadora"],
    ["Focada em Resultados", "Focada em Pessoas", "Focada em Apoiar o Time", "Focada em Processos/Regras"],
    ["Gosta de Desafios", "Gosta de Novidades", "Gosta de Harmonia", "Gosta de Lógica e Fatos"],
    ["Em conflito: Enfrenta", "Em conflito: Persuade", "Em conflito: Cede", "Em conflito: Analisa"]
]

grupo2 = [
    ["Independente", "Sociável/Interativa", "Paciente/Estável", "Precisa/Correta"],
    ["Intensa", "Entusiasta", "Apoio/Escuta", "Cuidadosa"],
    ["Assume Riscos", "Busca Reconhecimento", "Busca Segurança", "Busca Qualidade"],
    ["Decisões Rápidas", "Decisões Emocionais", "Decisões Pensadas", "Decisões Técnicas"]
]

def render_bloco(titulo, perguntas, chave):
    st.markdown(f"### {titulo}")
    res = {}
    for i, labels in enumerate(perguntas):
        st.write(f"**Linha {i+1}:**")
        cols = st.columns(4)
        notas = []
        for j, texto in enumerate(labels):
            n = cols[j].number_input(texto, 1, 4, 1, key=f"{chave}_{i}_{j}")
            notas.append(n)
        if len(set(notas)) < 4:
            st.warning("⚠️ Use 1, 2, 3 e 4 sem repetir.")
        res[f"L{i}"] = notas
    return res

res1 = render_bloco("🏢 Bloco 1: Estilo de Trabalho", grupo1, "b1")
res2 = render_bloco("🌟 Bloco 2: Percepção Pessoal", grupo2, "b2")

# --- ENVIO ---
if st.button("ENVIAR AVALIAÇÃO"):
    if not nome or not whats:
        st.error("Preencha seu nome e WhatsApp.")
    else:
        # Calcular
        pontos = {"D": 0, "I": 0, "S": 0, "C": 0}
        for bloco in [res1, res2]:
            for linha in bloco.values():
                for idx, nota in enumerate(linha):
                    pontos[mapa_letras[idx]] += nota
        
        # E-mail
        try:
            u = st.secrets["EMAIL_USER"]
            p = st.secrets["EMAIL_PASSWORD"]
            d = st.secrets["CONSULTANT_EMAIL"]
            
            msg = MIMEMultipart()
            msg['Subject'] = f"AVALIAÇÃO DISC CONEXA: {nome}"
            corpo = f"""
            TESTE REALIZADO - CONEXA
            ----------------------------
            Nome: {nome}
            WhatsApp: {whats}
            Empresa: {empresa}
            
            PONTUAÇÃO CALCULADA:
            Dominância (D): {pontos['D']}
            Influência (I): {pontos['I']}
            Estabilidade (S): {pontos['S']}
            Conformidade (C): {pontos['C']}
            ----------------------------
            """
            msg.attach(MIMEText(corpo, 'plain'))
            s = smtplib.SMTP('smtp.gmail.com', 587); s.starttls(); s.login(u, p); s.send_message(msg); s.quit()
            
            st.balloons()
            st.success("✅ Avaliação enviada com sucesso!")
            st.markdown(f"<div style='text-align:center; background:white; padding:20px; border-radius:15px; border:2px solid {LARANJA};'><h3>Obrigada por participar, {nome}!</h3><p>Seus dados foram enviados para a <b>Conexa</b> e em breve entraremos em contato.</p></div>", unsafe_allow_html=True)
        except:
            st.error("Erro no envio. Verifique a internet.")
