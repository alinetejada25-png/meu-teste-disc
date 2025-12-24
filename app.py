import streamlit as st
import smtplib
import pandas as pd
import plotly.express as px
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURAÇÕES ---
SENHA_ACESSO = "disc"

# Mapeamento DISC (Baseado na estrutura da sua imagem)
# D = Dominância, I = Influência, S = Estabilidade, C = Conformidade
mapa_disc = {
    "b1": {
        "L1": ["D", "I", "S", "C"], # Assertiva(D), Persuasiva(I), Paciente(S), Contemplativa(C)
        "L2": ["D", "I", "S", "C"], # Ser decisivo(D), Amizade social(I), Time(S), Ordem(C)
        "L3": ["I", "S", "C", "D"], # Variedade(I), Harmonia(S), Lógica(C), Menos Estrutura(D)
        "L4": ["D", "I", "S", "C"]  # Ditatorial(D), Sarcástico(I), Submisso(S), Arredio(C)
    },
    "b2": {
        "L1": ["D", "I", "S", "C"], # Independente, Interativo, Estável, Corretivo
        "L2": ["D", "I", "S", "C"], # Intenso, Não tradicional, Indeciso, Impessoal
        "L3": ["D", "I", "S", "C"], # Responsabilizado, Compromissos, Mudança, Decisão
        "L4": ["D", "I", "S", "C"]  # Histórico, Elogios, Contribuição, Qualidade
    }
}

st.set_page_config(page_title="Laudo DISC Pro", page_icon="📊", layout="centered")

# --- ESTILO ---
st.markdown("""
    <style>
    .main { background-color: #fffafb; }
    h1 { color: #8e44ad; text-align: center; }
    .stButton>button { background-color: #8e44ad; color: white; border-radius: 25px; width: 100%; }
    .resultado-card { background-color: #f8f9fa; padding: 20px; border-radius: 15px; border-left: 5px solid #8e44ad; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False
if not st.session_state.logado:
    st.title("🔒 Acesso ao Teste DISC")
    senha = st.text_input("Senha:", type="password")
    if st.button("Entrar"):
        if senha == SENHA_ACESSO:
            st.session_state.logado = True
            st.rerun()
        else: st.error("Senha incorreta.")
    st.stop()

# --- CÁLCULOS ---
def calcular_disc(respostas, bloco):
    totais = {"D": 0, "I": 0, "S": 0, "C": 0}
    for linha, valores in respostas.items():
        categorias = mapa_disc[bloco][linha]
        for i, valor in enumerate(valores):
            cat = categorias[i]
            totais[cat] += valor
    return totais

# --- FORMULÁRIO ---
st.title("🧩 Análise de Perfil Comportamental")
nome = st.text_input("Nome Completo")
whats = st.text_input("WhatsApp")

# Definição das palavras (Simplificado para o exemplo)
perguntas = [
    ["Assertiva", "Persuasiva", "Paciente", "Contemplativa"],
    ["Ser decisivo", "Amizade social", "Ser parte de um time", "Planejamento e ordem"],
    ["Variedade", "Menos estrutura", "Harmonia", "Lógica"],
    ["Ditatorial", "Sarcástico", "Submisso", "Arredio"]
]

def render_bloco(titulo, lista, chave):
    st.subheader(titulo)
    res = {}
    for i, row in enumerate(lista):
        st.write(f"Linha {i+1}:")
        cols = st.columns(4)
        v_linha = []
        for j, p in enumerate(row):
            v = cols[j].number_input(p, 1, 4, 1, key=f"{chave}_{i}_{j}")
            v_linha.append(v)
        res[f"L{i+1}"] = v_linha
    return res

resp_b1 = render_bloco("🏢 Bloco 1: Como você se vê", perguntas, "b1")
resp_b2 = render_bloco("🌟 Bloco 2: Como os outros te veem", perguntas, "b2")

if st.button("GERAR LAUDO E ENVIAR"):
    # 1. Calcular Resultados
    t1 = calcular_disc(resp_b1, "b1")
    t2 = calcular_disc(resp_b2, "b2")
    
    # Total Geral
    geral = {k: t1[k] + t2[k] for k in t1}
    df = pd.DataFrame(dict(r=list(geral.values()), theta=list(geral.keys())))

    # 2. Exibir Gráfico
    st.markdown("---")
    st.header("📊 Seu Resultado")
    fig = px.line_polar(df, r='r', theta='theta', line_close=True, range_r=[0,32])
    fig.update_traces(fill='toself', line_color='#8e44ad')
    st.plotly_chart(fig)

    # 3. Descrição Curta
    perfil_predominante = max(geral, key=geral.get)
    perfis = {
        "D": "Executor (Dominância): Focado em resultados, direto e decidido.",
        "I": "Comunicador (Influência): Otimista, persuasivo e sociável.",
        "S": "Planejador (Estabilidade): Paciente, bom ouvinte e confiável.",
        "C": "Analista (Conformidade): Preciso, detalhista e organizado."
    }
    st.success(f"**Perfil Predominante:** {perfis[perfil_predominante]}")

    # 4. Enviar E-mail com o Laudo
    try:
        user = st.secrets["EMAIL_USER"]
        passw = st.secrets["EMAIL_PASSWORD"]
        dest = st.secrets["CONSULTANT_EMAIL"]
        
        msg = MIMEMultipart()
        msg['Subject'] = f"LAUDO DISC: {nome}"
        corpo = f"""
        NOVO LAUDO GERADO
        Nome: {nome} | WhatsApp: {whats}
        
        PONTUAÇÃO TOTAL:
        Dominância (D): {geral['D']}
        Influência (I): {geral['I']}
        Estabilidade (S): {geral['S']}
        Conformidade (C): {geral['C']}
        
        Perfil sugerido: {perfil_predominante}
        """
        msg.attach(MIMEText(corpo, 'plain'))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(user, passw)
        s.send_message(msg)
        s.quit()
        st.info("O laudo detalhado foi enviado para a consultora.")
    except:
        st.error("Erro ao enviar e-mail, mas o resultado está na tela.")
