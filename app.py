import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CORES CONEXA ---
LARANJA = "#ff7f50"
VINHO = "#800020"
BEGE = "#ece6e0"

st.set_page_config(page_title="Conexa - Avaliação DISC", layout="centered")

# --- ESTILO ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {BEGE}; }}
    h1 {{ color: {VINHO}; text-align: center; font-weight: bold; }}
    .stButton>button {{ background-color: {LARANJA}; color: white; border-radius: 10px; width: 100%; font-weight: bold; padding: 15px; border: none; }}
    .stButton>button:hover {{ background-color: {VINHO}; }}
    div[data-testid="stBlock"] {{ background-color: white; padding: 25px; border-radius: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# --- VERIFICAÇÃO TÉCNICA (SECRETS) ---
if "EMAIL_USER" not in st.secrets:
    st.error("❌ Erro de Configuração: Os 'Secrets' não foram preenchidos no painel do Streamlit.")
    st.stop()

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.markdown(f"<h1>CONEXA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color:#800020;'>Portal de Avaliação</p>", unsafe_allow_html=True)
    senha = st.text_input("Senha de acesso:", type="password")
    if st.button("ACESSAR"):
        if senha == "disc":
            st.session_state.logado = True
            st.rerun()
        else: st.error("Senha incorreta.")
    st.stop()

# --- CABEÇALHO ---
st.markdown(f"<h1 style='color:{LARANJA};'>CONEXA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>Transformação e Desenvolvimento</p>", unsafe_allow_html=True)

with st.expander("📖 Clique aqui para ler as instruções"):
    st.write("""
    Identifique como você se comporta e reage a situações. 
    Lembre-se: **não existe resposta certa ou errada**. 
    Atribua notas de 1 a 4 por linha:
    - **4:** Mais descreve você.
    - **1:** Menos descreve você.
    - **Atenção:** Não repita números na mesma linha.
    """)

# --- CAMPOS DE DADOS ---
with st.container():
    nome = st.text_input("Nome Completo")
    whats = st.text_input("WhatsApp (com DDD)")
    empresa = st.text_input("Empresa/Cargo")

# --- PERGUNTAS ---
mapa_letras = ["D", "I", "S", "C"]

grupo1 = [
    ["Direta e Decidida", "Comunicativa e Influente", "Calma e Acolhedora", "Analítica e Observadora"],
    ["Focada em Resultados", "Focada em Pessoas", "Focada em Apoiar o Time", "Focada em Processos/Regras"],
    ["Gosta de Desafios", "Gosta de Novidades", "Gosta de Harmonia", "Gosta de Lógica e Fatos"],
    ["Em conflito: Enfrenta", "Em conflito: Persuade", "Em conflito: Cede", "Em conflito: Analisa"]
]

grupo2 = [
    ["Independente e Firme", "Sociável e Interativa", "Estável e Paciente", "Precisa e Correta"],
    ["Pessoa Intensa", "Pessoa Entusiasta", "Pessoa Acolhedora", "Pessoa Cuidadosa"],
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
            st.warning("⚠️ Não repita números nesta linha.")
        res[f"L{i}"] = notas
    return res

res1 = render_bloco("🏢 Bloco 1: Estilo de Trabalho", grupo1, "b1")
res2 = render_bloco("🌟 Bloco 2: Percepção Social", grupo2, "b2")

# --- ENVIO ---
if st.button("ENVIAR AVALIAÇÃO"):
    if not nome or not whats:
        st.error("Preencha Nome e WhatsApp.")
    else:
        # Calcular
        pontos = {"D": 0, "I": 0, "S": 0, "C": 0}
        for bloco in [res1, res2]:
            for linha in bloco.values():
                for idx, nota in enumerate(linha):
                    pontos[mapa_letras[idx]] += nota
        
        # E-mail
        try:
            # Lendo segredos
            u = st.secrets["EMAIL_USER"]
            p = st.secrets["EMAIL_PASSWORD"]
            d = st.secrets["CONSULTANT_EMAIL"]
            
            # Criando e-mail
            msg = MIMEMultipart()
            msg['From'] = u
            msg['To'] = d
            msg['Subject'] = f"AVALIAÇÃO DISC CONEXA: {nome}"
            
            texto_corpo = f"""
            NOVO TESTE CONEXA
            -----------------
            Nome: {nome}
            WhatsApp: {whats}
            Empresa: {empresa}
            
            PONTUAÇÃO:
            Dominância (D): {pontos['D']}
            Influência (I): {pontos['I']}
            Estabilidade (S): {pontos['S']}
            Conformidade (C): {pontos['C']}
            """
            msg.attach(MIMEText(texto_corpo, 'plain'))
            
            # Enviando
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(u, p)
                server.send_message(msg)
            
            st.balloons()
            st.success(f"✅ Sucesso, {nome}! Seus dados foram enviados para a Conexa.")
            st.info("Em breve entraremos em contato com você.")
        except Exception as e:
            st.error("Houve um erro no envio para o servidor de e-mail.")
            st.warning(f"Detalhe do erro: {e}")
