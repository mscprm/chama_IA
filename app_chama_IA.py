import streamlit as st
import pandas as pd
import datetime
import base64
import io
import os
import re
import urllib
import urllib.request
import html
import json
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
ARQUIVO_PERFIL_LOCAL = os.path.join(BASE_DIR, "perfil_operador_chama.json")

def carregar_perfil_disco():
    if os.path.exists(ARQUIVO_PERFIL_LOCAL):
        try:
            with open(ARQUIVO_PERFIL_LOCAL, "r", encoding="utf-8") as f:
                d = json.load(f)
                if isinstance(d, dict):
                    return d
        except Exception:
            pass
    return {"nome": "Paulo", "foto_b64": None, "ultima_pergunta": "", "ultima_resposta": ""}

def salvar_perfil_disco(nome=None, foto_b64=None, ultima_pergunta=None, ultima_resposta=None):
    dados = carregar_perfil_disco()
    if nome is not None and str(nome).strip():
        dados["nome"] = str(nome).strip()
    if foto_b64 is not None:
        dados["foto_b64"] = foto_b64
    if ultima_pergunta is not None:
        dados["ultima_pergunta"] = ultima_pergunta
    if ultima_resposta is not None:
        dados["ultima_resposta"] = ultima_resposta
    try:
        with open(ARQUIVO_PERFIL_LOCAL, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ----------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="Diário de Bordo C.H.A.M.A.",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# RECURSOS VISUAIS DE AVATARES (DECODIFICADOS DE FORMA NATIVA)
BIA_LOGO_B64 = "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"
BIA_LOGO = base64.b64decode(BIA_LOGO_B64)
IMG_JORGE = base64.b64decode("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")
IMG_CARLA = base64.b64decode("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")
IMG_RAFAEL = base64.b64decode("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")
IMG_MARTA = base64.b64decode("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")
IMG_LEO = base64.b64decode("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")
AVATAR_DEFAULT = base64.b64decode("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")

# Pré-computação de Base64 para centralização perfeita dos Avatares
B64_JORGE = base64.b64encode(IMG_JORGE).decode('utf-8')
B64_CARLA = base64.b64encode(IMG_CARLA).decode('utf-8')
B64_RAFAEL = base64.b64encode(IMG_RAFAEL).decode('utf-8')
B64_MARTA = base64.b64encode(IMG_MARTA).decode('utf-8')
B64_LEO = base64.b64encode(IMG_LEO).decode('utf-8')
B64_AVATAR_DEFAULT = base64.b64encode(AVATAR_DEFAULT).decode('utf-8')


# ESTILOS CSS CUSTOMIZADOS (PALETA OFICIAL DO MÉTODO)
st.markdown("""
<meta name="google" content="notranslate">
<style>
    /* Previne que o Google Translate / Edge Translate altere nós do React DOM */
    .stApp, .notranslate {
        translate: no !important;
    }

    .stApp {
        background-color: #FDFBF7;
    }
    .header-box {
        background-color: #1A3644;
        color: white;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.12);
        margin-bottom: 20px;
    }
    .header-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.5px;
        color: #FFFFFF;
        margin-top: 10px;
        margin-bottom: 4px;
    }
    .header-subtitle {
        font-size: 15px;
        color: #E2E8F0;
        font-weight: 500;
        margin-bottom: 4px;
    }
    .header-collab {
        font-size: 14px;
        font-weight: 700;
        color: #F4A261;
        letter-spacing: 0.8px;
    }
    .avatar-img-header {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 4px solid #F4A261;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.2);
    }
    .dicas-ouro-card {
        background-color: #FEF9E7;
        border-left: 6px solid #F4A261;
        padding: 16px 20px;
        border-radius: 12px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.04);
    }
    .chama-badge {
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .cuidometro-box {
        background-color: #11242E;
        color: #A8E6CF;
        padding: 16px;
        border-radius: 12px;
        font-weight: bold;
        text-align: center;
        font-size: 18px;
        border: 2px solid #2E8B57;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.15);
    }
    .avatar-center-box {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 8px;
    }
    .mentoria-bia-card {
        background-color: #FDFBF7;
        border: 1.5px solid #D0E1D9;
        border-radius: 14px;
        padding: 20px 24px;
        color: #1A3644;
        margin-top: 18px;
        margin-bottom: 20px;
        box-shadow: 0px 3px 8px rgba(0,0,0,0.03);
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# GERENCIAMENTO DE ESTADO (SESSION STATE)
# ----------------------------------------------------
if 'cuidometro' not in st.session_state:
    st.session_state['cuidometro'] = 25

if 'acordos_concluidos' not in st.session_state:
    st.session_state['acordos_concluidos'] = {}

if 'cliente_selecionado' not in st.session_state:
    st.session_state['cliente_selecionado'] = "Distribuidora Alfa Ltda."

if 'perfil_ativo' not in st.session_state:
    st.session_state['perfil_ativo'] = "Carla (A Apertada)"

if 'disparar_baloes' not in st.session_state:
    st.session_state['disparar_baloes'] = False

if 'historico_diario_bordo' not in st.session_state:
    st.session_state['historico_diario_bordo'] = []

if 'carteira_dinamica' not in st.session_state:
    st.session_state['carteira_dinamica'] = None

# Carrega perfil persistente do disco (cadastro único mantido permanentemente)
perfil_persistente = carregar_perfil_disco()

# Inicialização do nome: URL query_params ou disco local (padrão 'Paulo')
nome_salvo = st.query_params.get("operador", "").strip() or perfil_persistente.get("nome", "Paulo").strip() or "Paulo"

if 'nome_operador' not in st.session_state:
    st.session_state['nome_operador'] = nome_salvo

if 'input_nome_op' not in st.session_state:
    st.session_state['input_nome_op'] = st.session_state['nome_operador']

if 'foto_operador_bytes' not in st.session_state:
    foto_b64 = perfil_persistente.get("foto_b64")
    if foto_b64 and len(str(foto_b64)) > 50:
        try:
            st.session_state['foto_operador_bytes'] = base64.b64decode(foto_b64)
        except Exception:
            st.session_state['foto_operador_bytes'] = None
    else:
        st.session_state['foto_operador_bytes'] = None

if 'ultima_pergunta_bia' not in st.session_state:
    st.session_state['ultima_pergunta_bia'] = perfil_persistente.get("ultima_pergunta", "")

if 'ultima_resposta_bia' not in st.session_state:
    st.session_state['ultima_resposta_bia'] = perfil_persistente.get("ultima_resposta", "")

if 'modo_mentoria_bia' not in st.session_state:
    st.session_state['modo_mentoria_bia'] = "🎙️ Texto + Voz (Completo)"

if 'velocidade_fala_bia' not in st.session_state:
    st.session_state['velocidade_fala_bia'] = 1.0

if 'audio_counter' not in st.session_state:
    st.session_state['audio_counter'] = 0

if 'deve_tocar_audio' not in st.session_state:
    st.session_state['deve_tocar_audio'] = False

if st.session_state['disparar_baloes']:
    st.balloons()
    st.session_state['disparar_baloes'] = False

# ----------------------------------------------------
# BARRA LATERAL (IDENTIFICAÇÃO DO OPERADOR & LINHA DO TEMPO)
# ----------------------------------------------------
with st.sidebar:
    # 1. Identificação do Operador (Persistente no Disco)
    st.markdown('<div style="text-align:center; font-size: 14px; font-weight: bold; color: #1A3644; margin-bottom: 6px;">Identificação do Operador</div>', unsafe_allow_html=True)
    
    # Callbacks de atualização imediata e gravação permanente no disco
    def atualizar_nome_op():
        novo_n = st.session_state.get('input_nome_op', '').strip()
        if novo_n:
            st.session_state['nome_operador'] = novo_n
            st.query_params["operador"] = novo_n
            salvar_perfil_disco(nome=novo_n)

    def atualizar_foto_op():
        up = st.session_state.get('uploader_operador')
        if up is not None:
            conteudo = up.getvalue()
            if conteudo and len(conteudo) > 0:
                st.session_state['foto_operador_bytes'] = conteudo
                b64_salvar = base64.b64encode(conteudo).decode('utf-8')
                salvar_perfil_disco(nome=st.session_state['nome_operador'], foto_b64=b64_salvar)

    if st.session_state['foto_operador_bytes'] is not None:
        b64_foto_op = base64.b64encode(st.session_state['foto_operador_bytes']).decode('utf-8')
    else:
        b64_foto_op = B64_AVATAR_DEFAULT
    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><img src="data:image/png;base64,{b64_foto_op}" style="width: 90px; height: 90px; border-radius: 50%; box-shadow: 0px 3px 6px rgba(0,0,0,0.15);"></div>', unsafe_allow_html=True)

    st.text_input(
        "👤 Como gostaria de ser chamado neste treinamento?",
        value=st.session_state['nome_operador'],
        key="input_nome_op",
        on_change=atualizar_nome_op,
        placeholder="Seu nome ou apelido"
    )

    with st.expander("📷 Foto do Perfil (Opcional)", expanded=False):
        uploaded_img = st.file_uploader(
            "Carregue sua foto (.png, .jpg):",
            type=['png', 'jpg', 'jpeg'],
            key="uploader_operador",
            help="Sua foto fica salva permanentemente neste computador para o treinamento."
        )
        if uploaded_img is not None:
            conteudo = uploaded_img.getvalue()
            if conteudo and len(conteudo) > 0 and st.session_state.get('foto_operador_bytes') != conteudo:
                st.session_state['foto_operador_bytes'] = conteudo
                b64_salvar = base64.b64encode(conteudo).decode('utf-8')
                salvar_perfil_disco(nome=st.session_state['nome_operador'], foto_b64=b64_salvar)
                st.rerun()

        if st.session_state.get('foto_operador_bytes') is not None:
            if st.button("🗑️ Remover foto (usar avatar neutro)", use_container_width=True):
                st.session_state['foto_operador_bytes'] = None
                salvar_perfil_disco(nome=st.session_state['nome_operador'], foto_b64="")
                st.rerun()

    st.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

    # 2. Conexão Google Sheets (Fase 2)
    with st.expander("Carregar a Carteira de Clientes", expanded=False):
        st.caption("Conecte a planilha para carregar carteiras dinâmicas e registrar o Diário de Bordo em tempo real:")
        url_sheets = st.text_input("Link da Planilha Google (Compartilhada):", value="", placeholder="https://docs.google.com/spreadsheets/d/...")
        if url_sheets.strip():
            try:
                sheet_id = None
                if "/d/" in url_sheets:
                    sheet_id = url_sheets.split("/d/")[1].split("/")[0].split("?")[0].split("#")[0]
                elif "key=" in url_sheets:
                    sheet_id = url_sheets.split("key=")[1].split("&")[0]

                if not sheet_id:
                    st.warning("⚠️ Formato de link do Google Sheets não reconhecido.")
                else:
                    endpoints = [
                        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet=Carteira_Clientes",
                        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv",
                        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
                        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                    ]
                    df_carregado = None
                    for ep in endpoints:
                        try:
                            req = urllib.request.Request(ep, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req, timeout=8) as resp:
                                csv_data = resp.read().decode('utf-8', errors='ignore')
                                if "html" not in csv_data.lower()[:100] and len(csv_data.strip()) > 10:
                                    df_temp = pd.read_csv(io.StringIO(csv_data))
                                    if len(df_temp) > 0 and len(df_temp.columns) >= 2:
                                        df_carregado = df_temp
                                        break
                        except Exception:
                            continue

                    if df_carregado is not None:
                        cols_map = {}
                        for col in df_carregado.columns:
                            c_low = str(col).lower().strip()
                            if "cliente" in c_low or "nome" in c_low or "empresa" in c_low:
                                cols_map[col] = "Cliente"
                            elif "valor" in c_low or "divida" in c_low or "dívida" in c_low:
                                cols_map[col] = "Valor (R$)"
                            elif "atraso" in c_low or "dias" in c_low or "venc" in c_low:
                                cols_map[col] = "Atraso"
                            elif "perfil" in c_low or "persona" in c_low:
                                cols_map[col] = "Perfil"
                            elif "status" in c_low:
                                cols_map[col] = "Status_Padrao"

                        df_carregado = df_carregado.rename(columns=cols_map)

                        if "Cliente" in df_carregado.columns:
                            if "Valor (R$)" not in df_carregado.columns:
                                df_carregado["Valor (R$)"] = "R$ 0,00"
                            if "Atraso" not in df_carregado.columns:
                                df_carregado["Atraso"] = "Atraso pendente"
                            if "Perfil" not in df_carregado.columns:
                                df_carregado["Perfil"] = "Carla (A Apertada)"
                            if "Status_Padrao" not in df_carregado.columns:
                                df_carregado["Status_Padrao"] = "Aguardando Proposta"

                            st.session_state['carteira_dinamica'] = df_carregado.to_dict('records')
                            st.success("✅ Carteira sincronizada com o Google Sheets!")
                        else:
                            st.warning("⚠️ Planilha lida, mas coluna 'Cliente' não foi encontrada.")
                    else:
                        st.warning("⚠️ Operando em modo offline (Carteira local ativa). Certifique-se de que a planilha está pública para leitura.")
            except Exception:
                st.warning("⚠️ Operando em modo offline (Carteira local ativa).")
        else:
            st.info("ℹ️ Usando Carteira Padrão do Treinamento C.H.A.M.A.")

    # 3. Apresentação da Bia
    st.image(BIA_LOGO, width=90)
    st.markdown('<div style="font-size: 15px; font-weight: bold; color: #1A3644; margin-top: 6px; margin-bottom: 4px;">Olá sou a BIA!!! Analista do Financeiro, vou te ajudar no C.H.A.M.A.</div>', unsafe_allow_html=True)
    st.caption("Guia Pedagógico de Apoio ao Treinamento")

    fase_treino = st.radio(
        "Consulta de Etapas (Apoio ao Operador):",
        [
            "C · Conhecer (Prevenção & Análise)",
            "H · Humanizar (WhatsApp & Abordagem)",
            "A · Agir no Tempo Certo (Régua de Cobrança)",
            "M · Mediar (Negociação & Alçadas)",
            "A · Acompanhar (Ritual da Parcela & Redoma)"
        ],
        index=0
    )

    st.markdown("---")
    if "Conhecer" in fase_treino:
        st.info("""💡 **Dica de Ouro da Lilian:**\n*"Quando o pedido for alto e o cliente novo, converse com o vendedor antes de decidir. Ele sabe coisas que o birô não mostra!"* (págs. 10-12)""")
        st.warning("""⚠️ **Cuidado / Evite:**\nLiberar crédito no escuro sem consultar histórico ou cobrar sem conferir a baixa bancária no ERP (cobrança indevida destrói a confiança).""")
        st.success("""✨ **Na Prática:**\nOrganize a carteira pelo quadrante de prioridades e registre cada contato no CRM/ERP (se não está registrado, não aconteceu).""")
    elif "Humanizar" in fase_treino:
        st.info("""💡 **Dica de Ouro da Lilian:**\n*"Pausar é técnica! Se a conversa esquentar, diga: 'Entendo que o momento é difícil. Prefere que eu ligue amanhã às 10h para seguirmos com calma?'"* (págs. 14-17)""")
        st.warning("""⚠️ **Cuidado / Evite:**\nMensagens frias ou com tom de ameaça/ironia ("Última chance!"), uso de CAIXA ALTA (soa como grito) ou cobrança em horários invasivos.""")
        st.success("""✨ **Na Prática:**\nAnatomia em 5 partes: 1. Saudação com nome; 2. Quem fala; 3. O fato sem adjetivo; 4. Facilidade (PIX copia e cola); 5. Porta aberta.""")
    elif "Agir" in fase_treino:
        st.info("""💡 **Dica de Ouro da Lilian:**\n*"Deixe o sistema lembrar. Deixe as pessoas negociarem!"* (págs. 19-21)""")
        st.warning("""⚠️ **Cuidado / Evite:**\nViolar o Art. 42 do Código de Defesa do Consumidor — nunca expor, constranger ou ameaçar o cliente em momento algum.""")
        st.success("""✨ **Na Prática:**\nDo D-3 ao D+15, siga a cadência preventiva da régua (aviso útil no vencimento, lembrete amigável e ligação para valores expressivos).""")
    elif "Mediar" in fase_treino:
        st.info("""💡 **Dica de Ouro da Lilian:**\n*"Troque concessão por compromisso! Nunca conceda desconto sem exigir a garantia da entrada em até 24h."* (págs. 25-32)""")
        st.warning("""⚠️ **Cuidado / Evite:**\nConceder exceções fora da alçada "só desta vez" (o cliente acostuma e a próxima negociação já começa daquele patamar).""")
        st.success("""✨ **Na Prática:**\nPrimeiro o motivo real, depois a proposta. Use a Calculadora de Alçadas para manter a flexibilidade com limite claro de margem e caixa.""")
    else:
        st.info("""💡 **Dica de Ouro da Lilian:**\n*"O relacionamento não termina no pagamento. É aí que a fidelização começa!"* (págs. 34-39)""")
        st.warning("""⚠️ **Cuidado / Evite:**\nAbandonar o cliente após o aceite do acordo. Acordo sem acompanhamento vira promessa quebrada no mês seguinte.""")
        st.success("""✨ **Na Prática:**\nMova o cliente para a Redoma do Acordo Ativo (blindando-o de robôs de cobrança) e faça o contato preventivo no D-2 de cada parcela.""")

# ----------------------------------------------------
# CABEÇALHO PRINCIPAL (BIA CENTRALIZADA)
# ----------------------------------------------------
st.markdown("""
<div class="header-box">
    <div style="display: flex; justify-content: center; margin-bottom: 10px;">
        <img src="data:image/png;base64,""" + BIA_LOGO_B64 + """" class="avatar-img-header">
    </div>
    <div class="header-title">DIÁRIO DE BORDO DIGITAL · MÉTODO C.H.A.M.A.</div>
    <div class="header-subtitle">Autoria Intelectual: Lilian Lavorato (A Arte da Cobrança Humanizada)</div>
    <div class="header-collab">Collab MGP - Métodos, Gestão e Projetos</div>
</div>
""", unsafe_allow_html=True)


# ----------------------------------------------------
# GUIA PASSO A PASSO (INSTRUÇÕES DE USO DO DIÁRIO DE BORDO)
# ----------------------------------------------------
with st.expander("📖 Instruções de Uso: Passo a Passo do Diário de Bordo Digital C.H.A.M.A.", expanded=False):
    st.markdown("""
    ### 🎯 Como operar o Diário de Bordo no seu Treinamento e Rotina:
    
    1. **Identificação do Operador (Barra Lateral):**
       • Digite seu nome ou apelido e, se desejar, carregue sua foto de perfil. O seu nome será usado para assinar automaticamente todas as mensagens do WhatsApp e gravar o histórico de auditoria.
    
    2. **Carregar a Carteira de Clientes (Google Sheets ou Padrão):**
       • Para turmas e treinamentos, cole o link de compartilhamento da sua planilha Google. Se estiver offline ou sem planilha, a carteira padrão com 5 clientes estratégicos carrega na hora.
    
    3. **Painel de Empatia (Os 5 Perfis Comportamentais do Livro):**
       • Selecione o cliente em atendimento (Carla, Seu Jorge, Rafael, Dona Marta ou Léo). O sistema adapta a estratégia na hora com base na psicologia da inadimplência (págs. 7-8).
    
    4. **Trilha de Segurança Obrigatória Pré-Contato:**
       • Marque os 5 itens de checagem (Baixa no ERP, Artigo 42 do CDC, Titularidade, Tom Não-Violento e Histórico). O botão de acordo só libera com a trilha 100% verificada!
    
    5. **Calculadora Inteligente de Alçadas & WhatsApp:**
       • Simule valores de entrada e número de parcelas. Mantenha-se no **Farol Verde (Nível Analista)** para aprovação autônoma imediata. O texto do WhatsApp é gerado pronto para envio.
    
    6. **Confirmar Acordo & Mover para a Redoma:**
       • Ao fechar o compromisso, clique em *"🤝 Confirmar Acordo & Mover para Redoma"*. O cliente é blindado contra robôs de cobrança e o **Cuidômetro** sobe (+1 relação preservada no mês).
    
    7. **Mentoria Pedagógica com a Bia (IA & Voz):**
       • Na seção *"Pergunte para a Bia!"*, tire dúvidas sobre objeções, CDC ou consulte páginas específicas do livro (ex: *"O que tem na página 4?"* ou *"Caixa de ferramentas"*). Ouça a explicação em áudio suave e controle pela régua de tempo.
    
    8. **Auditoria & Exportação da Planilha:**
       • No rodapé, visualize em tempo real todas as negociações e mentorias realizadas e baixe o arquivo em CSV para acompanhamento do instrutor.
    """)

# ----------------------------------------------------
# RÉGUA C.H.A.M.A. & CUIDÔMETRO
# ----------------------------------------------------
col_regua, col_cuido = st.columns([3.5, 1.2])

with col_regua:
    st.subheader("Régua de Operação C.H.A.M.A.")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    cli_sel = st.session_state['cliente_selecionado']
    st_acordo = st.session_state['acordos_concluidos'].get(cli_sel, False)
    
    lbl_c = "✓ CONCLUÍDO" if st_acordo else "✓ OK"
    lbl_h = "✓ CONCLUÍDO" if st_acordo else "✓ OK"
    lbl_a1 = "✓ CONCLUÍDO" if st_acordo else "⏳ EM ANDAMENTO"
    lbl_m = "✓ CONCLUÍDO" if st_acordo else "PENDENTE"
    lbl_a2 = "✓ REDOMA ATIVA" if st_acordo else "PENDENTE"
    
    bg_m = "#A8E6CF" if st_acordo else "#D0E1D9"
    bg_a2 = "#A8E6CF" if st_acordo else "#D0E1D9"

    c1.markdown(f'<div class="chama-badge" style="background-color: #A8E6CF; color: #11242E;">C · Conhecer<br>{lbl_c}</div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="chama-badge" style="background-color: #FFD3B6; color: #11242E;">H · Humanizar<br>{lbl_h}</div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="chama-badge" style="background-color: #FFAAA5; color: #11242E;">A · Agir<br>{lbl_a1}</div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="chama-badge" style="background-color: {bg_m}; color: #11242E;">M · Mediar<br>{lbl_m}</div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="chama-badge" style="background-color: {bg_a2}; color: #11242E;">A · Acompanhar<br>{lbl_a2}</div>', unsafe_allow_html=True)

with col_cuido:
    val_cuido = st.session_state['cuidometro']
    st.markdown(f"""
    <div class="cuidometro-box">
        💚 CUIDÔMETRO<br>
        <span style="font-size: 26px;">{val_cuido}</span><br>
        <span style="font-size: 12px; font-weight: normal; color: #E2E8F0;">Relações Preservadas no Mês</span>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("❓ O que é o Cuidômetro?", expanded=False):
        st.markdown("""
        **Como Funciona o Cuidômetro (Método C.H.A.M.A. · Lilian Lavorato):**
        
        • **O Conceito Central:** *"Cobrar não é confrontar; é oferecer uma solução e cuidar de uma relação que vale a pena manter."*
        
        • **O que ele mede:** Em vez de focar apenas no valor financeiro recuperado friamente, ele mede o **número de clientes cuja relação comercial e confiança foram preservadas** após o atraso.
        
        • **Na Operação:**
          1. O operador realiza a checagem na **Trilha de Segurança** (Art. 42 CDC e baixa no ERP);
          2. Constrói uma proposta justa dentro do **Farol Verde (Nível Analista)**;
          3. Ao confirmar o acordo, o cliente é movido para a **Redoma do Acordo Ativo** (blindado de cobranças automáticas);
          4. O **Cuidômetro soma +1**, e o caso passa para o **Ritual da Parcela (D-2)** para acompanhamento e fidelização pós-pagamento.
        """)

# ----------------------------------------------------
# QUADRO DE DICAS DE OURO DA LILIAN (AUTORA DO MÉTODO)
# ----------------------------------------------------
st.markdown("""
<div class="dicas-ouro-card">
    <div style="font-size: 16px; font-weight: bold; color: #1A3644; margin-bottom: 6px;">
        💡 Dicas de Ouro da Lilian Lavorato (Apoio ao Operador em Treinamento)
    </div>
    <div style="font-size: 14px; color: #2C3E50; line-height: 1.5;">
        • <b>Cobrar é Cuidar:</b> <i>"Cobrar não é confrontar. É oferecer uma solução e cuidar de uma relação que vale a pena manter."</i><br>
        • <b>Regra da Negociação:</b> <i>"Troque concessão por compromisso! Nunca conceda desconto sem pedir a garantia da entrada em até 24h."</i><br>
        • <b>Pausar é Técnica:</b> <i>"Se a conversa esquentar, diga: 'Entendo que o momento é difícil. Prefere que eu te ligue amanhã às 10h para seguirmos com calma?'"</i>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ----------------------------------------------------
# PAINEL DE EMPATIA (AVATARES ILUSTRADOS - SEM EMOJIS NOS BOTÕES)
# ----------------------------------------------------
st.subheader("Painel de Empatia (Perfis Comportamentais do Livro)")
st.caption("Clique no perfil ou selecione na carteira abaixo para adaptar a estratégia:")

col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)

with col_a1:
    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><img src="data:image/png;base64,{B64_JORGE}" style="width: 80px; height: 80px; border-radius: 50%; box-shadow: 0px 3px 6px rgba(0,0,0,0.12);"></div>', unsafe_allow_html=True)
    if st.button("Seu Jorge", key="btn_jorge", use_container_width=True):
        st.session_state['perfil_ativo'] = "Seu Jorge (O Esquecido)"
        st.session_state['cliente_selecionado'] = "Mercearia do Jorge Ltda."

with col_a2:
    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><img src="data:image/png;base64,{B64_CARLA}" style="width: 80px; height: 80px; border-radius: 50%; box-shadow: 0px 3px 6px rgba(0,0,0,0.12);"></div>', unsafe_allow_html=True)
    if st.button("Carla", key="btn_carla", use_container_width=True):
        st.session_state['perfil_ativo'] = "Carla (A Apertada)"
        st.session_state['cliente_selecionado'] = "Distribuidora Alfa Ltda."

with col_a3:
    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><img src="data:image/png;base64,{B64_RAFAEL}" style="width: 80px; height: 80px; border-radius: 50%; box-shadow: 0px 3px 6px rgba(0,0,0,0.12);"></div>', unsafe_allow_html=True)
    if st.button("Rafael", key="btn_rafael", use_container_width=True):
        st.session_state['perfil_ativo'] = "Rafael (O Contestador)"
        st.session_state['cliente_selecionado'] = "Tech Logística S.A."

with col_a4:
    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><img src="data:image/png;base64,{B64_MARTA}" style="width: 80px; height: 80px; border-radius: 50%; box-shadow: 0px 3px 6px rgba(0,0,0,0.12);"></div>', unsafe_allow_html=True)
    if st.button("Dona Marta", key="btn_marta", use_container_width=True):
        st.session_state['perfil_ativo'] = "Dona Marta (A Sumida)"
        st.session_state['cliente_selecionado'] = "Marta Confecções EIRELI"

with col_a5:
    st.markdown(f'<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;"><img src="data:image/png;base64,{B64_LEO}" style="width: 80px; height: 80px; border-radius: 50%; box-shadow: 0px 3px 6px rgba(0,0,0,0.12);"></div>', unsafe_allow_html=True)
    if st.button("Léo", key="btn_leo", use_container_width=True):
        st.session_state['perfil_ativo'] = "Léo (O Promitente)"
        st.session_state['cliente_selecionado'] = "Léo Eventos & Produções"

# EXIBIÇÃO DO PERFIL ATIVO
perf = st.session_state['perfil_ativo']
if "Seu Jorge" in perf:
    st.info("**Perfil Ativo: Seu Jorge (O Esquecido)** — *Tem o dinheiro, mas perdeu o boleto na correria.* **Estratégia:** Lembrete amigável com código PIX copia e cola.")
elif "Carla" in perf:
    st.info("**Perfil Ativo: Carla (A Apertada)** — *Quer pagar, mas o caixa não fecha agora.* **Estratégia:** Escuta ativa e Calculadora de Alçadas para parcelamento.")
elif "Rafael" in perf:
    st.info("**Perfil Ativo: Rafael (O Contestador)** — *Acha que a cobrança está errada.* **Estratégia:** Conferência prévia de notas e comprovantes antes de insistir.")
elif "Dona Marta" in perf:
    st.info("**Perfil Ativo: Dona Marta (A Sumida)** — *Visualiza e não responde por vergonha.* **Estratégia:** Mensagem curta em opções numeradas simples (1, 2, 3).")
else:
    st.info("**Perfil Ativo: Léo (O Promitente)** — *Promete uma data e a data passa.* **Estratégia:** Registro por escrito e contato no exato dia do compromisso.")

st.markdown("<hr>", unsafe_allow_html=True)

# ----------------------------------------------------
# CARTEIRA DE CLIENTES SELECIONÁVEL & CONTROLE DE SESSÃO
# ----------------------------------------------------
st.subheader("Carteira de Atendimento Interativa")
st.write("Selecione o cliente na lista para carregar os dados e a persona correspondente:")

col_sel_cli, col_btn_reset = st.columns([3.2, 1.2])

clientes_base = [
    {"Cliente": "Distribuidora Alfa Ltda.", "Valor (R$)": "5.000,00", "Atraso": "18 dias", "Perfil": "Carla (A Apertada)", "Status_Padrao": "Aguardando Proposta"},
    {"Cliente": "Mercearia do Jorge Ltda.", "Valor (R$)": "1.200,00", "Atraso": "2 dias", "Perfil": "Seu Jorge (O Esquecido)", "Status_Padrao": "Enviar PIX"},
    {"Cliente": "Tech Logística S.A.", "Valor (R$)": "8.500,00", "Atraso": "12 dias", "Perfil": "Rafael (O Contestador)", "Status_Padrao": "Conferir NF"},
    {"Cliente": "Marta Confecções EIRELI", "Valor (R$)": "3.400,00", "Atraso": "25 dias", "Perfil": "Dona Marta (A Sumida)", "Status_Padrao": "Menu 1, 2, 3"},
    {"Cliente": "Léo Eventos & Produções", "Valor (R$)": "4.100,00", "Atraso": "7 dias", "Perfil": "Léo (O Promitente)", "Status_Padrao": "Confirmar Data"}
]

fonte_carteira = st.session_state['carteira_dinamica'] if st.session_state['carteira_dinamica'] else clientes_base
cli_nomes = [c["Cliente"] for c in fonte_carteira]
index_sel = cli_nomes.index(st.session_state['cliente_selecionado']) if st.session_state['cliente_selecionado'] in cli_nomes else 0

with col_sel_cli:
    cliente_escolhido = st.selectbox("Selecione o Cliente em Atendimento:", cli_nomes, index=index_sel)

with col_btn_reset:
    st.write("")
    st.write("")
    if st.button("🔄 Reiniciar Demonstração", use_container_width=True, help="Restaura o Cuidômetro para 25 e zera todos os acordos da simulação"):
        st.session_state['cuidometro'] = 25
        st.session_state['acordos_concluidos'] = {}
        st.session_state['cliente_selecionado'] = "Distribuidora Alfa Ltda."
        st.session_state['perfil_ativo'] = "Carla (A Apertada)"
        st.rerun()

if cliente_escolhido != st.session_state['cliente_selecionado']:
    st.session_state['cliente_selecionado'] = cliente_escolhido
    for c in fonte_carteira:
        if c["Cliente"] == cliente_escolhido:
            st.session_state['perfil_ativo'] = c.get("Perfil", "Carla (A Apertada)")
            st.rerun()

# Monta tabela com status dinâmico refletindo acordos concluídos
clientes_tabela = []
valor_divida_atual = "R$ 5.000,00"
for c in fonte_carteira:
    status_dinamico = "🛡️ Acordo Ativo (Redoma)" if st.session_state['acordos_concluidos'].get(c["Cliente"], False) else c.get("Status_Padrao", "Pendente")
    clientes_tabela.append({
        "Cliente": c["Cliente"],
        "Valor (R$)": c.get("Valor (R$)", "R$ 0,00"),
        "Atraso": c.get("Atraso", "-"),
        "Perfil": c.get("Perfil", "-"),
        "Status": status_dinamico
    })
    if c["Cliente"] == st.session_state['cliente_selecionado']:
        valor_divida_atual = str(c.get("Valor (R$)", "R$ 5.000,00"))

df_cli = pd.DataFrame(clientes_tabela)
st.dataframe(df_cli, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------------------------------
# TRILHA HORIZONTAL DO CHECKLIST DE SEGURANÇA (INTERATIVO)
# ----------------------------------------------------
st.subheader("Trilha de Segurança Obrigatória Pré-Contato (Checklist do Operador)")
st.caption("Marque cada item verificado para garantir a conformidade antes da abordagem:")

ck1, ck2, ck3, ck4, ck5 = st.columns(5)

cli_atual = st.session_state['cliente_selecionado']
val_ck1 = ck1.checkbox("1. Baixa no ERP?", value=True, key=f"ck1_{cli_atual}", help="Conferiu se o pagamento entrou nos últimos 30 min?")
val_ck2 = ck2.checkbox("2. Art. 42 CDC?", value=True, key=f"ck2_{cli_atual}", help="Garantir que não haverá exposição ou constrangimento.")
val_ck3 = ck3.checkbox("3. Confirmou Titular?", value=True, key=f"ck3_{cli_atual}", help="Só tratar de valores diretamente com o responsável.")
val_ck4 = ck4.checkbox("4. Tom Não-Violento?", value=False, key=f"ck4_{cli_atual}", help="Abordagem focada em solução e acolhimento.")
val_ck5 = ck5.checkbox("5. Leu Histórico?", value=False, key=f"ck5_{cli_atual}", help="Analisou negociações anteriores e promessas.")

tudo_ok = val_ck1 and val_ck2 and val_ck3 and val_ck4 and val_ck5
if tudo_ok:
    st.success("✅ **Trilha de Segurança 100% Verificada!** Operador liberado para efetuar o contato com total conformidade.")
else:
    st.warning("⚠️ **Trilha de Segurança Pendente:** Marque todos os itens acima para garantir o contato seguro.")

st.markdown("<hr>", unsafe_allow_html=True)

# ----------------------------------------------------
# CALCULADORA INTELIGENTE DE ALÇADAS & GAVETA DA BIA
# ----------------------------------------------------
def extrair_valor_float(v):
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace("R$", "").replace(".", "").replace(" ", "").replace(",", ".").strip()
    try:
        return float(s)
    except Exception:
        return 1000.0

col_calc, col_gaveta = st.columns([1, 1.1])

with col_calc:
    st.subheader("Calculadora Inteligente de Alçadas")
    st.write(f"**Simulação de Proposta para: {st.session_state['cliente_selecionado']}**")
    
    val_divida_num = extrair_valor_float(valor_divida_atual)
    ent = st.number_input("Valor da Entrada (R$):", value=1000.0, step=100.0)
    parc = st.slider("Número de Parcelas:", 1, 6, 4)
    desc = st.checkbox("Isenção de Juros/Multa (100%)", value=True)
    
    # Cálculo matemático exato do acordo (Item 1 dos 8 itens obrigatórios, pág. 34)
    saldo_restante = max(0.0, val_divida_num - ent)
    val_parcela = saldo_restante / parc if parc > 0 else 0.0
    rotulo_juros = "Isenção 100% de Juros/Multa" if desc else "Com Juros/Multa Contratual"
    
    # Card visual com detalhamento minucioso do acordo
    st.markdown(f"""
    <div style="background-color: #F8FAF9; border: 1.5px solid #D0E1D9; border-radius: 10px; padding: 12px 16px; margin-top: 10px; margin-bottom: 12px; font-size: 13px; color: #1A3644;">
        <div style="font-weight: bold; color: #2E8B57; margin-bottom: 6px;">📋 Resumo Matemático do Acordo (pág. 34):</div>
        • <b>Dívida Original:</b> R$ {val_divida_num:,.2f}<br>
        • <b>Entrada em até 24h:</b> R$ {ent:,.2f}<br>
        • <b>Saldo Restante a Parcelar:</b> R$ {saldo_restante:,.2f}<br>
        • <b>Plano de Parcelamento:</b> <b>{parc}x de R$ {val_parcela:,.2f}</b><br>
        • <b>Encargos:</b> <b>{'🟢 ' + rotulo_juros if desc else '🟡 ' + rotulo_juros}</b><br>
        <div style="font-size: 11px; color: #666; margin-top: 6px;">
            💡 <i>A Lilian ensina: Todo acordo deve prever entrada, valor exato de cada parcela e regra clara sobre juros (pág. 34 do livro).</i>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    alcada_aprovada = (parc <= 3 and ent >= 1000.0)
    if alcada_aprovada:
        st.success("🟢 **Farol Verde (Nível Analista):** Proposta aprovada automaticamente na sua alçada!")
    elif parc <= 5:
        st.warning("🟡 **Farol Amarelo (Nível Coordenação):** Exige validação do coordenador. *💡 A Bia lembra: Troque concessão por compromisso!*")
    else:
        st.error("🔴 **Farol Vermelho (Nível Diretoria):** Proposta acima da alçada padrão. Requer parecer do comitê.")

nome_op = st.session_state['nome_operador'].strip() if st.session_state['nome_operador'].strip() else "Analista"

with col_gaveta:
    st.subheader("Gaveta da Bia (Modelo WhatsApp)")
    
    # Orientação pedagógica da Bia para a persona ativa com o nome do operador
    if "Carla" in perf:
        st.info("💡 **Orientação da Bia para Carla (A Apertada):** Escuta ativa, validação da dificuldade e proposta viável com entrada garantida.")
        msg_txt = f"Olá Carla, tudo bem? Aqui é {nome_op}, do financeiro. Entendemos o momento da {cli_atual}. Conseguimos organizar uma entrada de R$ {ent:,.2f} e {parc} parcelas de R$ {val_parcela:,.2f} ({'sem juros nem multa' if desc else 'com encargos'}). Podemos formalizar para manter seu crédito protegido?"
    elif "Seu Jorge" in perf:
        st.info("💡 **Orientação da Bia para Seu Jorge (O Esquecido):** Lembrete leve e direto, com facilidade PIX sem nenhum tom de cobrança pesada.")
        if saldo_restante > 0:
            msg_txt = f"Oi, Seu Jorge, bom dia! Aqui é {nome_op}, do financeiro. Identifiquei o título de R$ {val_divida_num:,.2f} da {cli_atual}. Para facilitar na correria, organizamos uma entrada de R$ {ent:,.2f} via PIX e o saldo em {parc}x de R$ {val_parcela:,.2f} ({rotulo_juros}). Segue a chave PIX copia e cola para a entrada: [00020126...]. Se já quitou, só me avisar que dou baixa!"
        else:
            msg_txt = f"Oi, Seu Jorge, bom dia! Aqui é {nome_op}, do financeiro. Identifiquei o título de R$ {val_divida_num:,.2f} da {cli_atual}. Segue a chave PIX copia e cola para quitação à vista de R$ {ent:,.2f} ({rotulo_juros}): [00020126...]. Se já pagou, me envia o comprovante que dou baixa!"
    elif "Rafael" in perf:
        st.info("💡 **Orientação da Bia para Rafael (O Contestador):** Postura técnica e consultiva. Reenvie as NFs e comprovantes antes de debater valores.")
        msg_txt = f"Olá Rafael! Tudo bem? Aqui é {nome_op}, do financeiro. Conforme alinhado, estou reenviando a Nota Fiscal e o comprovante de entrega no valor de R$ {val_divida_num:,.2f} da {cli_atual}. Conseguimos formalizar com entrada de R$ {ent:,.2f} e {parc}x de R$ {val_parcela:,.2f} ({rotulo_juros}). Podemos confirmar a liquidação da entrada para hoje?"
    elif "Dona Marta" in perf:
        st.info("💡 **Orientação da Bia para Dona Marta (A Sumida):** Mensagem curta, acolhedora, com opções simples numeradas (1, 2, 3) para facilitar a resposta.")
        msg_txt = f"Olá Dona Marta! Aqui é {nome_op}, do financeiro. Para facilitar a regularização da {cli_atual} (R$ {val_divida_num:,.2f}), escolha uma opção: 1- PIX com desconto à vista | 2- Entrada de R$ {ent:,.2f} + {parc}x de R$ {val_parcela:,.2f} ({rotulo_juros}) | 3- Ligar para conversarmos."
    else:
        st.info("💡 **Orientação da Bia para Léo (O Promitente):** Formalização por escrito do compromisso agendado (Ritual da Parcela).")
        msg_txt = f"Olá Léo! Tudo bem? Passando para confirmar nosso compromisso agendado para hoje referente ao título de R$ {val_divida_num:,.2f} da {cli_atual}: entrada de R$ {ent:,.2f} + {parc}x de R$ {val_parcela:,.2f} ({rotulo_juros}). Segue a chave PIX para quitação da entrada."

    st.text_area("Texto Formatado Pronto para Envio:", value=msg_txt, height=110, key=f"msg_txt_{perf}_{cli_atual}_{nome_op}_{ent}_{parc}_{desc}")
    
    acordo_ja_feito = st.session_state['acordos_concluidos'].get(cli_atual, False)
    pode_confirmar = tudo_ok and alcada_aprovada and not acordo_ja_feito
    
    if acordo_ja_feito:
        st.success(f"🛡️ **Acordo Ativo:** O cliente **{cli_atual}** já está formalizado na Redoma de Proteção. Parabéns pelo relacionamento preservado!")
    elif not pode_confirmar:
        motivos = []
        if not tudo_ok:
            motivos.append("Marcar todos os 5 itens da Trilha de Segurança")
        if not alcada_aprovada:
            motivos.append("Simular proposta dentro do Farol Verde (Nível Analista)")
        msg_pend = "\n- ".join(motivos)
        st.info(f"🔒 **Aguardando Pré-Requisitos para o Acordo:**\n- {msg_pend}")

    if st.button("🤝 Confirmar Acordo & Mover para Redoma", disabled=not pode_confirmar, use_container_width=True):
        agora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        foto_status = "📷 Foto Carregada" if st.session_state['foto_operador_bytes'] is not None else "👤 Avatar Padrão"
        registro_acordo = {
            "Data/Hora": agora,
            "Operador": nome_op,
            "Cliente": cli_atual,
            "Valor Original": f"R$ {val_divida_num:,.2f}",
            "Encargos": rotulo_juros,
            "Entrada (R$)": f"R$ {ent:,.2f}",
            "Parcelamento": f"{parc}x de R$ {val_parcela:,.2f}",
            "Resumo do Acordo": f"Entrada R$ {ent:,.2f} + {parc}x de R$ {val_parcela:,.2f} ({rotulo_juros})",
            "Alçada": "🟢 Farol Verde (Nível Analista)",
            "Cuidômetro Acumulado": st.session_state['cuidometro'] + 1,
            "Status": "🛡️ Formalizado na Redoma Ativa"
        }
        st.session_state['historico_diario_bordo'].append(registro_acordo)
        st.session_state['cuidometro'] += 1
        st.session_state['acordos_concluidos'][cli_atual] = True
        st.session_state['disparar_baloes'] = True
        st.rerun()

# ----------------------------------------------------
# SEÇÃO: PERGUNTE PARA A BIA! (MENTORIA PEDAGÓGICA C.H.A.M.A.)
# ----------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)

col_bia_header, col_bia_img = st.columns([4.2, 0.8])
with col_bia_header:
    st.markdown("### 💬 Pergunte para a Bia!")
    st.markdown("""
    <div style="background-color: #F4F8F6; border-left: 4px solid #2E8B57; padding: 12px 16px; border-radius: 8px; font-size: 14px; color: #1A3644; margin-bottom: 12px;">
        💡 <b>Tire dúvidas sobre abordagem, objeções, CDC ou solicite orientações fundamentadas no livro <i>A Arte da Cobrança Humanizada</i> (Lilian Lavorato).</b>
    </div>
    """, unsafe_allow_html=True)
with col_bia_img:
    st.image(BIA_LOGO, width=70)

# Expansor de preferências de mentoria
with st.expander("⚙️ Preferências de Mentoria (Texto / Voz & Velocidade)", expanded=False):
    col_p1, col_p2 = st.columns([1.5, 1])
    with col_p1:
        st.session_state['modo_mentoria_bia'] = st.radio(
            "Como deseja interagir com a Bia?",
            ["🎙️ Texto + Voz (Completo)", "📝 Apenas Texto", "🔊 Apenas Voz"],
            index=0,
            horizontal=True
        )
    with col_p2:
        st.session_state['velocidade_fala_bia'] = st.slider(
            "⚡ Velocidade da Fala da Bia:",
            min_value=0.8,
            max_value=1.5,
            value=float(st.session_state['velocidade_fala_bia']),
            step=0.05,
            help="Velocidade da voz sintetizada. Padrão recomendado: 1.25x"
        )

# Dicionário de conhecimento pedagógico rigoroso do livro A Arte da Cobrança Humanizada (Lilian Lavorato)
def consultar_mentoria_bia(pergunta, cliente_nome, perfil_nome, divida_val):
    p_low = pergunta.lower().strip()
    
    # ---------------------------------------------------------
    # 1. ÍNDICE COMPLETO POR PÁGINAS DO LIVRO (Páginas 2 a 43)
    # ---------------------------------------------------------
    match_pag = re.search(r'\b(?:p[aá]gina|p[aá]g\.?)\s*(\d+)\b', p_low)
    if match_pag:
        num_pag = int(match_pag.group(1))
        paginas_livro = {
            2: "Aqui está o conteúdo integral da **Página 2** do livro *A Arte da Cobrança Humanizada* (Boas-Vindas):\n\n**Este livro é para quem precisa receber e quer continuar vendendo.**\n\nEmpreendedor, lojista, gestor financeiro, equipe de contas a receber ou prestador de serviço: se você já ficou sem saber o que dizer para um cliente em atraso, este material é para você.\n\nA inadimplência é um desafio comum. Mas a forma como lidamos com ela pode transformar um problema em uma oportunidade de fidelização. Aqui você vai do primeiro passo, a prevenção, até a negociação avançada, sempre com foco na comunicação e na quebra de objeções.\n\nAo final, você vai saber o que falar, quando falar, como agir em cada situação e como organizar um processo de cobrança que funcione mesmo quando a lista de atrasados é grande.\n\n💬 **Frase de Efeito da Lilian:**\n*'Cobrar não é confrontar. É oferecer uma solução e cuidar de uma relação que vale a pena manter.'*\n\n👤 **Quadro: Conheça a Bia**\nAnalista do financeiro e personagem pedagógica fictícia que vai aparecer nos exemplos, nas conversas e nos roteiros deste livro. Ela erra, aprende e aplica o método com você.\n\n📖 **Como Usar Este Livro:**\nLeia na ordem na primeira vez. Depois, use como consulta diária: os modelos e checklists estão no fim de cada parte e na Caixa de Ferramentas.",
            3: 'Aqui está o sumário estruturado da **Página 3** do livro *A Arte da Cobrança Humanizada*:\n\n**O QUE VEM A SEGUIR (Sumário da Obra):**\n\n• **Começo de conversa (págs. 2-8):** Boas-vindas (p. 2), Método C.H.A.M.A. (p. 4), Cobrar é cuidar (p. 5), Cobrar x pedir pagamento (p. 6), Psicologia da inadimplência (p. 7), 7 Erros a evitar (p. 8);\n• **C · Conhecer (págs. 10-12):** Gestão financeira e análise de crédito (p. 10), Registro e organização da carteira (p. 11), Como definir prioridades (p. 12);\n• **H · Humanizar (págs. 14-17):** Comunicação que conecta (p. 14), Anatomia do WhatsApp (p. 15), Horários e canais (p. 16), Roteiro de ligação (p. 17);\n• **A · Agir no tempo certo (págs. 19-23):** Régua de cobrança (p. 19), Mantendo adimplente (p. 20), Automação no ERP (p. 21), Modelos 01 a 06 (p. 22-23);\n• **M · Mediar (págs. 25-32):** Fluxograma de decisão (p. 25), Negociar sem destruir margem (p. 26), Alçadas e critérios (p. 27), Objeções 1 a 8 (p. 28-29), Silêncio e promessas (p. 30), Desculpas e resistência (p. 31), Casos delicados (p. 32);\n• **A · Acompanhar (págs. 34-39):** Estruturar acordos (p. 34), O ritual da parcela e modelos (p. 35), Escalonamento (p. 36), Cuidados legais e Art. 42 CDC (p. 37), 4 Indicadores (p. 38), Pós-cobrança (p. 39);\n• **Caixa de ferramentas (págs. 40-42):** Plano de ação de 7 dias (p. 40), Checklists de consulta rápida (p. 41), Fichas para imprimir (p. 42);\n• **Fechamento (pág. 43):** Conclusão e sobre a autora Lilian Lavorato.\n\n📌 **Convenções e Quadros Práticos do Livro:**\n• **NA PRÁTICA:** Como aplicar a ideia no dia a dia da operação;\n• **EVITE ISSO:** Atitudes que afastam o cliente ou criam riscos legais;\n• **EXPERIMENTE ASSIM:** Uma alternativa melhor, pronta para testar;\n• **DICA DA LILIAN:** Atalhos e segredos de quem vive o financeiro na pele;\n• **EXERCÍCIO RÁPIDO:** Espaço prático para aplicar no seu negócio;\n• **MODELO PRONTO:** Mensagens para copiar, preenchendo os campos entre colchetes.',
            4: "Aqui está o conteúdo integral da **Página 4** do livro *A Arte da Cobrança Humanizada* (Apresentação do Método C.H.A.M.A.):\n\n**O MÉTODO C.H.A.M.A.: um passo para cada momento da cobrança**\n\n*As cinco letras seguem a ordem do relacionamento com o cliente: antes da venda, na conversa, no vencimento, na negociação e depois do pagamento.*\n\n• **C · Conhecer:** *'Quem é esse cliente e quanto risco eu aceito?'*\n  Análise de crédito, políticas claras, registro dos contatos, organização da carteira e prioridades.\n\n• **H · Humanizar:** *'Como eu falo para ser ouvido?'*\n  Tom, WhatsApp com rosto, anatomia da mensagem, horários e roteiro de ligação.\n\n• **A · Agir no tempo certo:** *'Quando eu falo e o que digo em cada momento?'*\n  Régua de cobrança, prevenção, automação e modelos para cada etapa.\n\n• **M · Mediar:** *'O que está por trás do atraso e qual acordo é possível?'*\n  Escuta, objeções, silêncio, promessas, negociação, alçadas e casos delicados.\n\n• **A · Acompanhar:** *'Como o combinado vira pagamento e o cliente volta?'*\n  Acordos, escalonamento, cuidados legais, indicadores e reativação.\n\n💡 **Dica da Lilian (pág. 4):**\n*'Você não precisa aplicar tudo de uma vez. Se hoje sua dor é o cliente que some, comece por M · Mediar. Se é a desorganização, comece por C · Conhecer. O plano de 7 dias, no fim do livro, ajuda a montar o seu caminho.'*",
            5: "Aqui está o conteúdo integral da **Página 5** do livro (Introdução: Cobrar é Cuidar):\n\n**COBRAR É CUIDAR**\n\nNo universo dos negócios, a inadimplência é uma realidade que, se não for bem gerenciada, pode comprometer seriamente a saúde financeira de qualquer empresa.\n\nMas o processo de cobrança vai muito além de 'receber dinheiro'. É uma oportunidade de demonstrar profissionalismo, empatia e de manter um relacionamento saudável com seus clientes.\n\nA cobrança humanizada busca a solução, não o confronto. Ela transforma um momento delicado em uma experiência positiva para o cliente e para a empresa.\n\nMuitas vezes, a palavra 'cobrança' desperta sentimentos negativos, tanto em quem cobra quanto em quem é cobrado. Este livro existe para mudar essa percepção, com método e não só com boa vontade.\n\n👤 **Quadro: Quem Escreve**\n*'Olá! Sou Lilian, e minha paixão é mostrar que cobrar pode ser uma arte.'*\nSão mais de 15 anos dedicados ao setor financeiro, com foco em cobrança, análise de crédito, negociação e renegociação. Essa vivência mostrou as nuances do relacionamento com o cliente em momentos de dificuldade.\n\n💬 **Frase Marcante da Autora:**\n*'Vamos juntos construir um processo de cobrança eficiente, respeitoso e que funcione na vida real do financeiro.'*\n\n🎯 **Quadro: O Objetivo Deste Livro**\nO objetivo deste material é desmistificar a cobrança e transformá-la em uma ferramenta de relacionamento. Quero que você sinta confiança ao abordar seus clientes, sabendo que está oferecendo uma solução, e não apenas exigindo um pagamento.",
            6: "Aqui está o conteúdo integral da **Página 6** do livro (Cobrar x Pedir Pagamento):\n\n**COBRAR É DIFERENTE DE PEDIR PAGAMENTO**\n\nPedir pagamento é um ato isolado. Cobrar com método é um processo: tem começo, meio, fim e aprendizado.\n\n• **Só pedir pagamento:**\n  - Lembra do cliente só quando já atrasou;\n  - Manda a mesma mensagem para todos;\n  - Depende do humor do dia;\n  - Negocia no improviso;\n  - Não registra promessas;\n  - Termina quando o dinheiro entra (ou quando cansa).\n\n• **Cobrar com método (C.H.A.M.A.):**\n  - Começa antes do vencimento com aviso útil;\n  - Adapta ao perfil, ao valor e ao histórico;\n  - Segue uma régua clara e previsível;\n  - Negocia dentro de alçadas pré-definidas;\n  - Registra cada contato e próximo passo;\n  - Continua depois do pagamento para reativar o cliente.\n\n💬 **Frase de Efeito da Lilian:**\n*'Uma cobrança previsível é mais respeitosa: o cliente não é surpreendido, não se sente perseguido e sabe exatamente como resolver.'*\n\n🎯 **Exercício Rápido (pág. 6):**\nPense na última cobrança difícil que você fez. Ela se pareceu mais com a coluna da esquerda ou da direita? O que faltou?",
            7: "Aqui está o conteúdo integral da **Página 7** do livro (A Psicologia da Inadimplência):\n\n**POR QUE AS PESSOAS ATRASAM?**\n\nDois clientes devem o mesmo valor, com o mesmo atraso. Um paga depois de um lembrete; o outro some. A diferença não está na dívida: está no motivo.\n\n1. **Seu Jorge (O Esquecido):** Tem o dinheiro, mas o boleto se perdeu na correria. *O que funciona:* Lembrete simples com PIX ou boleto à mão, sem sermão;\n2. **Carla (A Apertada):** Quer pagar, mas o caixa não fecha agora. *O que funciona:* Escuta ativa e uma proposta que caiba no orçamento real;\n3. **Rafael (O Contestador):** Acha que a cobrança está errada (e às vezes está!). *O que funciona:* Conferir antes de insistir e responder rápido com documentos;\n4. **Dona Marta (A Sumida):** Visualiza e não responde por vergonha ou falta de saída. *O que funciona:* Mensagem curta, sem acusação e com saída fácil (menu 1, 2, 3);\n5. **Léo (O Promitente):** Promete uma data, a data passa e promete outra. *O que funciona:* Compromisso por escrito, data exata e contato no próprio dia.\n\nE existe ainda quem simplesmente prioriza as contas de quem cobra com mais constância. Para esse perfil, o antídoto é organização: régua clara e sem buracos.\n\n✨ **Na Prática (pág. 7):**\nPor trás de um 'não posso pagar' muitas vezes há uma dificuldade real ou um mal-entendido. Antes de escolher a mensagem, descubra o motivo. É ele que define a abordagem.\n\n⚠️ **Evite Isso (pág. 7):**\nRotular a pessoa para sempre. Um bom pagador pode virar 'apertado' num mês difícil. Identifique o motivo da vez, não o caráter do cliente!",
            8: "Aqui está o conteúdo integral da **Página 8** do livro (Erros que Afastam Clientes):\n\n**7 HÁBITOS QUE FAZEM O CLIENTE FUGIR DO SEU WHATSAPP**\n\nNenhum deles nasce de má intenção. Nascem da pressa, da falta de processo e do cansaço de cobrar todo dia.\n\n1. **Cobrar sem conferir se já foi pago:** Confira baixa, PIX, compensação e comprovantes antes de qualquer contato. Cobrança indevida custa confiança (e pode custar processo!);\n2. **Tom de ameaça ou ironia ('Última chance!'):** Firmeza com respeito. As consequências são informadas com clareza, nunca usadas para intimidar;\n3. **Mensagem genérica, sem valor nem vencimento:** Leve tudo o que o cliente precisa para pagar em um minuto: valor, referência, data e meio;\n4. **Insistir sem intervalo, em qualquer horário:** Siga a régua: cada contato tem um momento e um objetivo. Respeite os horários de descanso;\n5. **Falar da dívida com terceiros:** Trate apenas com o responsável. Funcionário, familiar ou grupo de WhatsApp não é canal de cobrança (violação do Art. 42 CDC);\n6. **Prometer o que não pode cumprir:** Ofereça só o que está dentro da política e da sua alçada. Uma promessa quebrada pela empresa destrói a negociação;\n7. **Sumir depois de fechar o acordo:** Acompanhe cada data combinada. Acordo sem acompanhamento é acordo esquecido.\n\n👤 **Quadro da Bia (pág. 8):**\n*'A Bia já cometeu o erro nº 1: cobrou um cliente que tinha pago por PIX no dia anterior. Desde então, conferir o recebimento no banco é o primeiro item inegociável do checklist dela!'*",
            10: "Conteúdo integral da **Página 10** do livro (C · Conhecer: Análise de Crédito e Prevenção):\n\n**A PREVENÇÃO É A MELHOR COBRANÇA**\n\nUma cobrança eficaz começa muito antes do atraso. A gestão financeira e a análise de crédito são a primeira linha da cobrança.\n\nLiberar crédito sem critérios claros é transferir para o futuro um problema que deveria ser resolvido agora. Estabeleça políticas transparentes:\n• Limites de crédito compatíveis com o porte do cliente;\n• Consulta preventiva a histórico e birôs;\n• Prazos de pagamento alinhados ao fluxo de caixa da empresa;\n• Cadastro completo e atualizado com o contato direto do responsável financeiro.\n\n💡 **Dica de Ouro da Lilian (pág. 10):**\n*'Quando o pedido é alto e o cliente é novo, converse com o gestor da loja ou com o vendedor antes de decidir. Quem atende o cliente sabe coisas que o birô não mostra: há quanto tempo ele compra, se paga em dia em outros lugares e se a empresa dele está crescendo!'*",
            11: 'Conteúdo integral da **Página 11** do livro (C · Conhecer: Registro e Organização da Carteira):\n\n**SE NÃO ESTÁ REGISTRADO, NÃO ACONTECEU**\n\nO monitoramento contínuo dos recebíveis é o coração da prevenção. E monitorar começa por registrar.\n\nMantenha uma rotina diária de conferência e atualização. Registre:\n• Todo contato realizado (data, hora, canal e com quem falou);\n• O motivo relatado para o atraso;\n• As opções oferecidas e a resposta do cliente;\n• O próximo passo com data e hora exatas.\n\n⚠️ **Alerta da Lilian (pág. 11):**\n*\'Escreva o próximo passo sempre com data. "Retornar" não é próximo passo. "Ligar dia 20 às 10h se o PIX não entrar" é!\'*',
            12: 'Conteúdo integral da **Página 12** do livro (C · Conhecer: A Matriz de Prioridades):\n\n**QUEM COBRAR PRIMEIRO QUANDO A LISTA É GRANDE?**\n\nTempo é o recurso mais escasso do financeiro. Priorizar é decidir onde cada contato rende mais:\n\n• **Prioridade 1 (Atenção Pessoal Hoje):** Valores altos e atrasos recentes. Ligação da pessoa mais experiente da equipe. Entender o motivo e propor solução dentro da alçada;\n• **Prioridade 2 (Negociação Estruturada):** Valores altos e atrasos antigos. Proposta formal, alçada superior envolvida e avaliação de escalonamento;\n• **Prioridade 3 (Deixe a Régua Trabalhar):** Valores menores e atrasos recentes. Lembretes automáticos e mensagens-modelo. Contato pessoal só se não houver resposta;\n• **Prioridade 4 (Campanha de Regularização):** Valores menores e atrasos antigos. Uma condição padrão para todos (ex: desconto em encargos à vista), divulgada de uma vez.\n\n📌 **Critérios Extras para Subir a Prioridade (pág. 12):**\nAlém de valor e tempo, suba a prioridade imediatamente quando:\n1. O cliente quebrou um acordo anterior;\n2. É um cliente estratégico para o comercial;\n3. Há prazo correndo para protesto ou negativação;\n4. O atraso é recente em um cliente que sempre pagou pontualmente.\n\n🎯 **Exercício Rápido (pág. 12):**\nListe os 8 maiores atrasos da sua carteira e marque o quadrante de cada um.',
            14: 'Conteúdo integral da **Página 14** do livro (H · Humanizar: Comunicação que Conecta):\n\n**PESSOAS FALAM COM PESSOAS**\n\nA forma como você se comunica é o diferencial no processo de cobrança. Transparência, acessibilidade e agilidade constroem confiança e facilitam a resolução.\n\nOs 4 princípios de uma comunicação que conecta:\n1. **Identifique-se:** Diga seu nome e o da sua empresa logo no início;\n2. **Seja específico:** Informe valor exato, referência da compra e vencimento, sem rodeios;\n3. **Ofereça o caminho:** Traga a solução pronta (chave PIX copia e cola ou boleto atualizado);\n4. **Feche com próximo passo:** Faça uma pergunta aberta que convide o cliente a responder e avançar.\n\n✨ **Na Prática (pág. 14):**\nO WhatsApp como aliado humanizado: Personalize o perfil da empresa com uma foto clara de quem cobra e o logo oficial. O cliente sabe exatamente com quem está falando, e isso muda por completo o tom da conversa!',
            15: "Conteúdo integral da **Página 15** do livro (H · Humanizar: Anatomia da Mensagem de WhatsApp):\n\n**A ANATOMIA DE UMA BOA MENSAGEM NO WHATSAPP**\n\nCinco partes, nesta ordem exata. O segredo é não pular nenhuma:\n1. **Saudação com o nome:** *'Oi, Seu Jorge, bom dia!'*\n2. **Quem fala:** *'Aqui é [Seu Nome], do financeiro da [Empresa].'*\n3. **O fato, sem adjetivo:** *'O boleto de R$ [valor], que venceu ontem, ainda não apareceu por aqui.'*\n4. **A facilidade:** *'Segue o PIX copia e cola: [código]'*\n5. **A porta aberta:** *'Se já pagou, me manda o comprovante que eu dou baixa.'*\n\n📌 **Regras de Ouro no WhatsApp (pág. 15):**\n• Frases curtas e objetivas (um assunto por mensagem);\n• Nada de CAIXA ALTA (soa como grito e afasta o cliente);\n• Áudio só se o cliente preferir (muita gente não pode ouvir no trabalho);\n• Sempre confirme e agradeça o recebimento quando o comprovante for enviado;\n• Nunca cobre em grupos nem por mensagem pública que terceiros possam ver.",
            16: 'Conteúdo integral da **Página 16** do livro (H · Humanizar: Horários e Canais):\n\n**HORÁRIOS NOBRES E CANAIS ADEQUADOS**\n\nTão importante quanto o que você diz é **quando** você diz:\n\n• **10h às 12h (Horário Nobre Matutino):** O cliente já entrou no ritmo do dia e ainda não saiu para o almoço;\n• **16h às 18h (Fechamento da Tarde):** Contato mais focado antes de encerrar o expediente comercial;\n\n⚠️ **Aviso Legal e Respeito ao Cliente (pág. 16):**\nRespeite estritamente os horários comerciais permitidos por lei (Art. 42 do CDC). Nunca cobre antes das 8h nem após as 18h, nem em fins de semana ou feriados. Cobrança invasiva gera rejeição e risco jurídico!',
            17: 'Conteúdo integral da **Página 17** do livro (H · Humanizar: Roteiro da Ligação de Cobrança):\n\n**ROTEIRO DA LIGAÇÃO DE COBRANÇA**\n\nA ligação é o canal mais humano e o mais desafiador. Com roteiro estruturado, ela fica mais curta, mais calma e mais produtiva:\n\n1. **Prepare-se antes de discar:** Tenha em mãos histórico, valor atualizado, comprovante de que não houve pagamento e as opções dentro da sua alçada;\n2. **Abra e confirme com quem fala:** Só fale da dívida com o responsável financeiro. Se for outra pessoa, deixe apenas recado de contato;\n3. **Apresente o fato com clareza:** Diga o valor, a compra e a data de vencimento sem acusação;\n4. **Pergunte e escute:** *\'Aconteceu alguma coisa?\'* Escute sem interromper o motivo real;\n5. **Proponha um caminho dentro da alçada:** Ofereça até duas alternativas viáveis;\n6. **Repita o combinado e registre:** Confirme valor, meio e data, e formalize por escrito logo após a ligação.\n\n⚠️ **Evite Isso (pág. 17):**\n• Ligar de um lugar barulhento;\n• Discutir sobre quem tem razão;\n• Expor a dívida a quem atendeu o telefone;\n• Encerrar a chamada sem uma data definida.\n\n💡 **Dica de Ouro da Lilian (pág. 17):**\n*\'Se a conversa esquentar, não reaja. Diga: "Entendo que o momento é difícil. Prefere que eu te ligue amanhã às 10h para a gente seguir com calma?" Pausar também é técnica!\'*',
            19: "Conteúdo integral da **Página 19** do livro (A · Agir no Tempo Certo: Régua de Cobrança):\n\n**A RÉGUA: CADA CONTATO TEM DIA E MOTIVO**\n\nA régua organiza a cobrança no tempo. Ela evita esquecimentos, evita excessos e faz a equipe inteira falar a mesma língua:\n\n• **D-5 a D-3 (Aviso Útil):** Agradece a compra e envia boleto/PIX. Não é cobrança, é serviço (WhatsApp/E-mail);\n• **D0 (Lembrete do Dia):** Mensagem curta e gentil no dia do vencimento (automático);\n• **D+1 (Lembrete Amigável):** Confirme a baixa bancária antes. Tom leve e acolhedor (WhatsApp);\n• **D+2 a D+15 (Primeiras Negociações):** Entender o motivo e oferecer caminhos. Ligue nos valores maiores (WhatsApp/Ligação);\n• **A partir de D+15 (Clareza sobre Consequências):** Informe encargos e providências possíveis com educação (Ligação/E-mail);\n• **D+30 a D+60 (Proposta Estruturada):** Proposta por escrito e aviso prévio antes de negativação ou cartório;\n• **Conforme a Política (Medidas Formais):** Protesto ou jurídico, sempre como último recurso da gestão.\n\n📌 **Regra de Ouro da Régua (pág. 19):**\n*'Antes de cada etapa: confirme que o valor realmente não foi recebido no banco. Esse cuidado vale para toda a régua, do D+1 ao jurídico!'*\n\n💡 **Dica da Lilian (pág. 19):**\n*'As etapas até D+15 seguem a experiência prática deste livro. Os prazos de D+30 em diante são exemplos: defina os seus na política de crédito e cobrança da sua empresa.'*",
            20: "Conteúdo da **Página 20** do livro (A · Agir: Mantendo o Cliente Adimplente):\n\n**É MAIS FÁCIL MANTER UM BOM PAGADOR DO QUE RECUPERAR UM DEVEDOR**\n\nTrate cada cliente conforme seu histórico:\n• **Cliente Pontual:** Só o aviso útil preventivo. Agradeça a pontualidade de vez em quando;\n• **Atrasa às Vezes:** Aviso útil + lembrete no D0 + contato amigável no D+1;\n• **Atrasa Sempre:** Contato pessoal antes do vencimento e avalie mudar a data de vencimento;\n• **Cliente Novo:** Acompanhe de perto as primeiras parcelas. É aí que o hábito se forma!\n\n💬 **Frase Marcante:** *'A pontualidade também se reconhece e se cultiva.'*",
            21: 'Conteúdo integral da **Página 21** do livro (A · Agir: Automação no ERP):\n\n**DEIXE O SISTEMA LEMBRAR. DEIXE AS PESSOAS NEGOCIAREM.**\n\nSe a sua empresa usa um ERP ou CRM, explore a régua automatizada:\n• O que o sistema faz: avisos prévios (D-3), lembrete de vencimento (D0) e segmentação por faixas;\n• O que as pessoas fazem: escuta ativa, negociação de alçadas, quebra de objeções e ligações ativas.\n\n📌 **Regra de Ouro da Conciliação (pág. 21):**\nPara evitar o erro grave de cobrar quem já pagou, a régua automatizada só deve disparar se o arquivo de retorno bancário tiver sido conciliado nos últimos 30 minutos!',
            22: "Conteúdo da **Página 22** do livro (Modelos Prontos 01 a 03):\n\n• **Modelo 01 (Aviso Útil - D-3 a D-5):** *'Olá, [Nome]! Tudo bem? Passando para te desejar uma ótima semana e já deixar aqui o boleto da NF [número], que vence no dia [data]...'*;\n• **Modelo 02 (Lembrete do Dia - D0):** *'Oi, [Nome]! Tudo bem? Hoje é o vencimento do título [número]. Segue o PIX copia e cola para facilitar...'*;\n• **Modelo 03 (Lembrete Amigável - D+1):** *'Olá, [Nome]! Aqui é [Seu Nome], do financeiro. O boleto que venceu ontem ainda não apareceu baixado. Se já pagou, me envia o comprovante; se precisar de 2ª via, segue aqui!'*",
            23: 'Conteúdo da **Página 23** do livro (Modelos Prontos 04 a 06):\n\n• **Modelo 04 (Primeiras Negociações - D+5 a D+10):** Proposta flexível com parcelamento;\n• **Modelo 05 (Silêncio / Menu 1, 2, 3):** Mensagem curta numerada para quem visualiza e não responde;\n• **Modelo 06 (Reincidência):** Abordagem para clientes frequentes, oferecendo ajuste na data de vencimento.',
            25: "Conteúdo integral da **Página 25** do livro (M · Mediar: Fluxograma de Decisão):\n\n**PRIMEIRO O MOTIVO, DEPOIS A PROPOSTA**\n\nQuando o cliente apresenta uma objeção, escute com atenção e empatia. O objetivo é entender o motivo real do atraso para oferecer a solução certa:\n\n1. O pagamento entrou no sistema? -> Se sim: Dê baixa, agradeça e encerre;\n2. Se não: O cliente respondeu? -> Se não: Mude de canal, use o menu 1, 2, 3 e formalize;\n3. Se respondeu: Descubra o motivo real (Esqueceu, Contestou, Alegou dificuldade ou Recusou);\n4. Em todos os caminhos: Registre o contato e defina o próximo passo com data e hora exatas!\n\n✨ **Na Prática (pág. 25):**\nA objeção não é um 'não'. É um convite para uma negociação mais aprofundada e a sua chance de mostrar perícia, empatia e proatividade. Evite reações emocionais: mantenha a calma e o foco na solução.",
            26: "Conteúdo integral da **Página 26** do livro (M · Mediar: Negociar sem Destruir Margem):\n\n**NEGOCIAR SEM DESTRUIR A MARGEM E O CAIXA**\n\nFlexibilidade gera valor para os dois lados, desde que tenha limite. Negociar bem é saber até onde ir antes de começar a conversa:\n\n• **1. Conheça seu piso antes de falar:** Saiba a menor entrada aceitável e o número máximo de parcelas;\n• **2. Troque concessão por compromisso:** Nunca conceda desconto de graça. Quer desconto nos juros? Exija entrada em até 24h;\n• **3. Negocie encargos antes do principal:** O valor principal só entra em renegociação em casos de dívidas antigas e perdas provisionadas.\n\n💡 **Dica de Ouro da Lilian (pág. 26):**\n*'Troque concessão por compromisso! Nunca conceda desconto sem exigir a garantia da entrada em até 24 horas!'*",
            27: "Conteúdo integral da **Página 27** do livro (M · Mediar: Alçadas e Critérios):\n\n**TABELA DE ALÇADAS DE NEGOCIAÇÃO (Faróis de Decisão)**\n\nQuem pode conceder o quê:\n\n🟢 **Farol Verde (Nível Analista):** Isenção de juros/multa mediante quitação à vista ou entrada mínima de R$ 1.000,00 com parcelamento em até 3x;\n🟡 **Farol Amarelo (Nível Coordenação):** Parcelamento de 4x a 5x ou desconto parcial em encargos moratórios;\n🔴 **Farol Vermelho (Nível Diretoria/Comitê):** Parcelamentos acima de 6x ou qualquer desconto no valor principal da dívida.\n\n⚠️ **Evite Isso (pág. 27):**\nConceder fora da alçada 'só desta vez'. O cliente acostuma, e a próxima negociação já começa daquele patamar!\n\n🎯 **Exercício Rápido (pág. 27):**\nQuais são hoje as três exceções que mais acontecem na sua equipe? Qual regra resolveria cada uma?",
            28: "Conteúdo integral da **Página 28** do livro (M · Mediar: Quebrando Objeções 1 a 4):\n\nCobrar não é pressionar: é negociar com classe, firmeza e solução:\n\n• **Objeção 01: 'Não posso pagar agora'**\n  - Resposta: *'Entendo perfeitamente, [Nome]. Nosso objetivo é manter a parceria saudável. Posso te apresentar uma alternativa de parcelamento que não comprometa seu caixa?'*\n  - *Intenção:* Mostrar que você é parceiro e focar em viabilidade financeira.\n\n• **Objeção 02: 'A fatura está errada'**\n  - Resposta: *'Vou revisar agora mesmo e te retorno com precisão. Nossa prioridade é manter uma relação justa e transparente com você.'*\n  - *Intenção:* Transparência + agilidade = confiança.\n\n• **Objeção 03: 'Esqueci, me manda de novo'**\n  - Resposta: *'Claro, acontece com todo mundo! Já estou te reenviando a chave PIX copia e cola para facilitar.'*\n  - *Intenção:* Facilitar sem julgar ou constranger.\n\n• **Objeção 04: 'Preciso de mais prazo'**\n  - Resposta: *'Vamos alinhar isso, sim. Você tem em mente um prazo viável? Posso te dar essa flexibilidade mediante confirmação por escrito da nova data.'*\n  - *Intenção:* Flexibilidade com responsabilidade e compromisso formal.",
            29: "Conteúdo integral da **Página 29** do livro (M · Mediar: Quebrando Objeções 5 a 8):\n\n• **Objeção 05: 'Não vou pagar agora, não tenho previsão'**\n  - Resposta: *'Entendo que o momento pode estar apertado. Mas manter essa pendência em aberto pode limitar seu crédito e condições especiais no futuro. Como podemos estruturar uma saída viável hoje?'*\n  - *Intenção:* Mostrar consequências com diplomacia e abrir porta para negociação.\n\n• **Objeção 06: 'Já paguei'**\n  - Resposta: *'Perfeito! Você pode me encaminhar o comprovante para eu dar baixa por aqui no sistema e manter tudo 100% regularizado?'*\n  - *Intenção:* Segurança documental com gentileza.\n\n• **Objeção 07: 'Não quero mais comprar com vocês'**\n  - Resposta: *'Respeitamos sua decisão, [Nome]. Mas antes de encerrar qualquer vínculo, queremos regularizar o que ficou pendente para garantir que não haja impactos futuros para o seu CNPJ.'*\n  - *Intenção:* Fechar com elegância, autoridade e evitar medidas judiciais.\n\n• **Objeção 08: Retomando um acordo quebrado**\n  - Resposta: *'Olá, [Nome]! Sou [Seu Nome], do financeiro. Temos ótimas condições para restabelecer nossa parceria e reativar seu cadastro. Que tal conversarmos sobre uma nova proposta?'*\n  - *Intenção:* Reengajar e dar saída digna ao cliente.",
            30: "Conteúdo integral da **Página 30** do livro (M · Mediar: Silêncio e Promessas):\n\n**SILÊNCIO E PROMESSAS NÃO CUMPRIDAS**\n\n• **Quando o cliente some:** O silêncio quase nunca é desprezo; é vergonha ou falta de opção imediata. Torne responder mais fácil do que ignorar:\n  - Troque o canal (quem ignora WhatsApp pode atender uma ligação amigável);\n  - Varie os horários;\n  - Simplifique a resposta com o menu numerado (1, 2, 3);\n  - Tire o peso emocional (evite frases como 'último aviso');\n  - Formalize por escrito antes de qualquer medida de escalonamento.\n\n• **Quando a promessa não se cumpre:** Promessa sem data, valor e meio é só intenção. Transforme intenção em compromisso formal por escrito!\n\n💬 **Frase de Encerramento Poderosa (pág. 30):**\n*'Estamos aqui para manter uma relação transparente e de confiança. Me diga o que é possível para você hoje, que eu vejo como podemos alinhar.'*",
            31: "Conteúdo da **Página 31** do livro (M · Mediar: Desculpas, Resistência e Dificuldade):\n\n• **Desculpas que se repetem:** Acolha uma vez com gentileza. Depois, traga a conversa para o concreto: *'Entendo. Para eu registrar no sistema: qual data exata você consegue?'*;\n• **Resistência e irritação:** Não reaja ao tom da pessoa. Valide o sentimento e volte ao fato: *'Entendo que isso é chato. Quero resolver com você, não contra você'*;\n• **Dificuldade financeira real:** Escute de verdade. Pergunte quanto cabe no caixa atual e monte uma proposta de fôlego com entrada.",
            32: 'Conteúdo da **Página 32** do livro (M · Mediar: Clientes Estratégicos e Casos Delicados):\n\nAlguns casos exigem cuidados especiais e alinhamento interno prévio:\n• Alinhe o discurso com a liderança comercial antes de ligar;\n• Suba a decisão para alçada superior se houver risco de perder um cliente-chave;\n• Separe a conversa de cobrança da conversa de vendas (preserve o vendedor como canal de negócios).',
            34: "Conteúdo integral da **Página 34** do livro (A · Acompanhar: Acordos Bem Estruturados):\n\n**ACORDO BOM É ACORDO CUMPRIDO**\n\nDepois de fechar a negociação, o trabalho muda de natureza: sai a negociação e entra o acompanhamento rigoroso:\n\n**Os 8 Itens Obrigatórios de Todo Acordo:**\n1. Valor original e encargos detalhados;\n2. Desconto concedido e quem aprovou na empresa;\n3. Valor final líquido negociado;\n4. Entrada: valor exato e data de liquidação (até 24h);\n5. Parcelas: quantidade, valores e datas exatas de vencimento;\n6. Meio de pagamento especificado (PIX ou boleto bancário);\n7. Regra explícita do que acontece se uma parcela atrasar (vencimento antecipado do saldo);\n8. Aceite formal do cliente por escrito (WhatsApp formal ou e-mail).\n\n💡 **Dica de Ouro da Lilian (pág. 34):**\n*'Coloque os acordos ativos em uma lista separada da carteira geral. Eles nunca devem receber as mensagens da régua comum de cobrança: o cliente que está pagando em dia e recebe cobrança automática se sente profundamente traído!'*\n\n⚠️ **Evite Isso (pág. 34):**\nFechar acordo por ligação e não mandar nada por escrito. Na dúvida, o registro protege você, a empresa e o cliente.",
            35: "Conteúdo integral da **Página 35** do livro (A · Acompanhar: O Ritual da Parcela):\n\n**O RITUAL DE CADA PARCELA**\n\n• **D-2 (Lembrete Preventivo Amigável - Modelo 11):** Envie uma mensagem leve com o código PIX ou boleto atualizado: *'Passando para lembrar que a parcela vence em [data]. Falta pouco!'*;\n• **D0 (Vencimento):** Conferência bancária discreta no sistema para verificar a entrada;\n• **D+1 (Imprevisto - Modelo 07):** Se o pagamento não caiu, faça contato imediato no mesmo tom respeitoso: *'Aconteceu algum imprevisto?'*;\n• **Última Parcela (Celebração e Reativação - Modelo 12):** Comunique a quitação completa e agradeça o compromisso mantido!",
            36: 'Conteúdo da **Página 36** do livro (A · Acompanhar: Escalonamento Formal):\n\nQuando as tentativas amigáveis se esgotam e o cliente se recusa a dialogar:\n• Notificação formal prévia com prazo claro antes de negativação ou protesto;\n• A clareza documental protege a empresa de contestações jurídicas;\n• Medidas legais são sempre o último recurso, adotadas com sobriedade e respeito.',
            37: 'Conteúdo integral da **Página 37** do livro (A · Acompanhar: Cuidados Legais e Art. 42 CDC):\n\n**RESPEITO TAMBÉM É REGRA (Conformidade Jurídica)**\n\nCobrar dentro da lei protege o cliente, a empresa e a reputação do seu negócio:\n\n• **Sem constrangimento nem ameaça (Artigo 42 do CDC):** Na cobrança de débitos, o consumidor não será exposto a ridículo, nem submetido a qualquer tipo de constrangimento ou ameaça;\n• **Cobrar o que já foi pago custa caro:** Cobrança indevida paga pode gerar devolução em dobro do valor;\n• **Sem prisão civil por dívida:** No Brasil, dívida comercial ou civil não leva à prisão (ameaçar com prisão é ilegal e abusivo);\n• **Proteção de Dados (LGPD):** Jamais compartilhe dados financeiros com terceiros, familiares ou vizinhos.\n\n📌 **Quadro: NUNCA x SEMPRE (pág. 37):**\n• **NUNCA:** Falar da dívida com terceiros; cobrar em grupos de WhatsApp; expor em redes sociais; usar tom de ameaça ou mentira;\n• **SEMPRE:** Falar apenas com o titular; informar valores e encargos com transparência; avisar antes de qualquer medida formal; guardar os registros de cada contato.',
            38: 'Conteúdo integral da **Página 38** do livro (A · Acompanhar: Indicadores Essenciais):\n\n**OS 4 INDICADORES ESSENCIAIS DA COBRANÇA**\n\nMeça o que importa para evoluir o processo com clareza:\n1. **Taxa de Inadimplência:** Percentual do faturamento total que não foi pago no vencimento;\n2. **Taxa de Recuperação:** Quanto do valor em atraso foi efetivamente recuperado no período;\n3. **Percentual de Acordos Cumpridos:** Mede a qualidade da negociação (acordo viável é acordo cumprido);\n4. **Índice de Reincidência:** Clientes que voltam a atrasar com frequência (indica necessidade de ajuste na política de crédito).\n\n🎯 **Exercício Rápido (pág. 38):**\nMeça o seu ponto de partida este mês. Compare sempre com o seu próprio histórico, mês a mês!',
            39: "Conteúdo integral da **Página 39** do livro (A · Acompanhar: Pós-Cobrança e Reativação):\n\n**DE EX-DEVEDOR A CLIENTE FIEL**\n\nTransformar quem já foi devedor em cliente leal é o maior testemunho de uma cobrança humanizada:\n\n• **Acompanhamento Pós-Quitação:** Avise o cliente da baixa definitiva e liberação cadastral;\n• **Reativação com o Comercial (Modelo 12):** Avise o vendedor responsável: *'A empresa [Nome] quitou o acordo com pontualidade e já está liberada para novas compras!'*;\n• **Comunicação de Boas-Vindas:** Envie uma mensagem leve: *'Parabéns pela quitação! É uma alegria ter você conosco. O [Vendedor] já está sabendo e vai adorar te atender de novo!'*\n\n💬 **Frase Marcante (pág. 39):**\n*'O relacionamento não termina no pagamento. É aí que a fidelização começa!'*",
            40: "Conteúdo integral da **Página 40** do livro (Caixa de Ferramentas: Plano de 7 Dias):\n\n**PLANO DE AÇÃO: O MÉTODO EM 7 DIAS**\n\nUma tarefa por dia, cerca de uma hora cada. No oitavo dia, você já cobra com processo:\n• **Dia 1 (Raio-X da Carteira - C):** Mapeie tudo o que está em aberto por faixa de atraso e valor;\n• **Dia 2 (Prioridades - C):** Classifique os maiores casos na Matriz de Prioridades (1 a 4);\n• **Dia 3 (Régua de Cobrança - A):** Defina etapas, prazos (D-3 a D+15) e canais da sua régua;\n• **Dia 4 (Modelos de Mensagem - H):** Adapte as mensagens ao seu tom de voz e salve como respostas rápidas;\n• **Dia 5 (Tabela de Alçadas - M):** Preencha os limites dos faróis verde, amarelo e vermelho com a gestão;\n• **Dia 6 (Registro - C):** Defina onde e como a equipe registra os contatos e os acordos;\n• **Dia 7 (Indicadores - A):** Meça o ponto de partida dos 4 KPIs e agende a reunião mensal de revisão.\n\n💡 **Dica de Ouro da Lilian (pág. 40):**\n*'Faça o plano com a equipe, não sozinho. Quem cobra todos os dias sabe onde estão os buracos da régua, e quem participa da construção segue o processo com orgulho!'*",
            41: "Conteúdo integral da **Página 41** do livro (Caixa de Ferramentas: Checklists Rápidos):\n\n**CHECKLISTS DE CONSULTA RÁPIDA**\n\nImprima, cole ao lado do monitor ou salve no celular:\n\n• **1. Antes de Cada Contato:** Conferi no banco se o pagamento não entrou? Sei o valor atualizado e a origem? Li o histórico anterior? Sei o que posso oferecer dentro da alçada? Estou dentro do horário comercial permitido?;\n• **2. Durante a Conversa:** Estou falando diretamente com o responsável? Me identifiquei no início? Perguntei e escutei o motivo real? Ofereci uma saída viável? Repeti o combinado com data e valor no final?;\n• **3. Antes de Fechar Acordo:** A proposta está dentro da minha alçada? A parcela cabe no orçamento real do cliente? Data, valor e meio de pagamento estão definidos? O cliente aceitou por escrito? O acordo saiu da régua comum de cobrança?;\n• **4. No Fim do Dia:** Registrei todos os contatos no sistema? Todo caso tem próximo passo com data? Conferi os pagamentos prometidos para hoje? Atualizei os acordos ativos? Separei os casos especiais para a gestão?\n\n👤 **As 4 Perguntas da Bia (pág. 41):**\n*'Antes de mandar qualquer mensagem, a Bia se pergunta: Eu conferi o banco? Eu me identifiquei? Eu facilitei o caminho? Eu deixei um próximo passo definido?'*",
            42: 'Conteúdo da **Página 42** do livro (Caixa de Ferramentas: Fichas para Imprimir):\n\n**FICHAS PRÁTICAS PARA O DIA A DIA**\n\n• **Ficha 1: Registro de Contato (As 5 Colunas Essenciais):**\n  - Data/Hora | Cliente | Motivo do Atraso | Combinado por Escrito | Próximo Passo com Data.\n\n• **Ficha 2: Estruturação de Acordo (Os 8 Itens Obrigatórios):**\n  - Formulário padrão para preenchimento de valor original, encargos, desconto aprovado, entrada em 24h, parcelas, meio PIX/boleto, regra de inadimplência e aceite formal do titular.',
            43: "Conteúdo da **Página 43** do livro (Fechamento e Sobre a Autora):\n\n**FECHAMENTO: A COBRANÇA COMO ARTE E PROCESSO**\n\nA cobrança, quando feita com estratégia e humanidade, é uma ferramenta poderosa para o crescimento sustentável da sua empresa.\n\nNão se trata apenas de recuperar valores, mas de preservar relacionamentos, fortalecer a imagem da sua marca e garantir a saúde financeira do seu negócio. Com o Método C.H.A.M.A., você tem um caminho para cada momento: conhecer, humanizar, agir no tempo certo, mediar e acompanhar.\n\n👤 **Sobre a Autora (Lilian Lavorato):**\nCom mais de 15 anos dedicados ao setor financeiro, com foco em cobrança, análise de crédito, negociação e renegociação, Lilian acredita que cobrar é cuidar e que todo processo de recuperação de valores pode ser também um processo de fortalecimento de relações.\n\n💬 **Mensagem Final da Obra:**\n*'Cada interação é uma chance de mostrar o valor da sua empresa e de construir um futuro financeiro mais sólido para todos. Vá em frente e faça a diferença!'*",
        }
        
        if num_pag in paginas_livro:
            return paginas_livro[num_pag]
        else:
            return (
                f"Olá, {nome_op}! O livro *A Arte da Cobrança Humanizada* da Lilian Lavorato possui 43 páginas organizadas do prefácio à Caixa de Ferramentas.\n\n"
                f"A página {num_pag} não possui um capítulo isolado registrado. Você pode consultar as páginas principais de 2 a 43 ou navegar pelos grandes temas do sumário na Página 3!"
            )

    # ---------------------------------------------------------
    # 2. TEMAS ESPECÍFICOS CONSAGRADOS DO MÉTODO
    # ---------------------------------------------------------
    # Caixa de Ferramentas
    if "ferramenta" in p_low or "caixa de ferramentas" in p_low or "plano de 7 dias" in p_low or "plano de ação" in p_low:
        return (
            f"Excelente pergunta, {nome_op}! Na **Caixa de Ferramentas** do livro *A Arte da Cobrança Humanizada* (págs. 40 a 42), "
            f"a Lilian Lavorato disponibiliza recursos práticos prontos para aplicação imediata na rotina financeira:\n\n"
            f"1. **Plano de Ação de 7 Dias (pág. 40):**\n"
            f"   • Um passo a passo estruturado (cerca de 1 hora por dia) para organizar o setor de cobrança em uma semana: "
            f"Raio-X da carteira, Matriz de Prioridades, Régua, Modelos, Alçadas, Registro e Indicadores;\n\n"
            f"2. **Checklists de Consulta Rápida (pág. 41):**\n"
            f"   • 4 roteiros de conferência: *Antes de cada contato*, *Durante a conversa*, *Antes de fechar acordo* e *No fim do dia*;\n\n"
            f"3. **Fichas Práticas para Imprimir (pág. 42):**\n"
            f"   • Ficha de Registro de Contato (com as 5 colunas essenciais) e Ficha de Estruturação de Acordo (com os 8 itens obrigatórios)."
        )

    # Acompanhamento Pós-Acordo (Páginas 34 a 39 do livro)
    elif "acompanhar" in p_low or "depois de fechado" in p_low or "acordo fechado" in p_low or "ritual da parcela" in p_low or "pós-acordo" in p_low or "fechou" in p_low:
        return (
            f"Excelente pergunta, {nome_op}! No livro *A Arte da Cobrança Humanizada* (págs. 34-39), a Lilian ensina que "
            f"**'o relacionamento não termina no pagamento. É aí que a fidelização começa'** e que **'acordo bom é acordo cumprido'**.\n\n"
            f"Depois de fechar a negociação, o trabalho muda de natureza: sai a negociação e entra o acompanhamento rigoroso. "
            f"Aqui estão as regras essenciais da Etapa **A · Acompanhar** do Método C.H.A.M.A.:\n\n"
            f"1. **Os 8 Itens Obrigatórios de Todo Acordo:**\n"
            f"   • Valor original com encargos e desconto concedido;\n"
            f"   • Valor final negociado, entrada e parcelas com datas exatas;\n"
            f"   • Meio de pagamento (PIX ou boleto);\n"
            f"   • Regra explícita do que acontece se atrasar;\n"
            f"   • **Aceite formal do cliente por escrito**.\n\n"
            f"2. **O Ritual de Cada Parcela:**\n"
            f"   • **D-2:** Lembrete amigável preventivo com link de PIX/boleto;\n"
            f"   • **D0:** Conferência bancária no sistema;\n"
            f"   • **D+1:** Contato sem acusação caso não compense (*'Aconteceu algum imprevisto?'*);\n"
            f"   • **Última Parcela:** Agradecimento e celebração pelo compromisso mantido!\n\n"
            f"3. **A Redoma do Acordo Ativo:** O cliente em dia **nunca** deve receber mensagens da régua de cobrança comum.\n\n"
            f"4. **Pós-Cobrança e Reativação:** Após a quitação, avise o vendedor comercial que a empresa {cliente_nome} está liberada para voltar a comprar!"
        )

    # Artigo 42 do CDC / Cuidados Legais
    elif "artigo 42" in p_low or "art. 42" in p_low or "cdc" in p_low or "lei" in p_low or "constrangimento" in p_low or "ameaça" in p_low:
        return (
            f"Atenção fundamental, {nome_op}! O **Artigo 42 do Código de Defesa do Consumidor** é uma das vigas mestras do livro da Lilian Lavorato (págs. 19-21 e 37).\n\n"
            f"Ele determina expressamente: *'Na cobrança de débitos, o consumidor inadimplente não será exposto a ridículo, nem será submetido a qualquer tipo de constrangimento ou ameaça.'*\n\n"
            f"**Na prática da Cobrança Humanizada:**\n"
            f"• **Nunca fale da dívida com terceiros:** Trate apenas diretamente com o responsável financeiro;\n"
            f"• **Respeite os horários de descanso:** Apenas das 8h às 18h em dias úteis;\n"
            f"• **Tom Não-Violento:** Não use CAIXA ALTA (soa como grito), nem termos como 'Último aviso' ou 'Medidas drásticas'."
        )

    # Trocar Concessão por Compromisso
    elif "concessão" in p_low or "compromisso" in p_low or "desconto" in p_low or "entrada" in p_low:
        return (
            f"A regra de ouro da negociação da Lilian (págs. 26 e 35): **'Troque concessão por compromisso!'**\n\n"
            f"Nunca conceda um benefício (como desconto de juros ou parcelamento mais longo) de graça. "
            f"Toda concessão exige uma contrapartida que proteja o caixa da empresa:\n\n"
            f"• **Quer desconto nos juros?** Exija o pagamento de uma entrada garantida nas próximas 24 horas;\n"
            f"• **Quer mais parcelas?** Peça uma entrada maior ou reduza o prazo da primeira parcela;\n"
            f"• **Negocie encargos antes do principal:** O principal só entra em dívidas antigas, já tratadas como perda."
        )

    # Pausar é Técnica
    elif "pausar" in p_low or "nervoso" in p_low or "esquentou" in p_low or "irritado" in p_low:
        return (
            f"Como a Lilian destaca na página 17: **'Pausar também é técnica!'**\n\n"
            f"Se a conversa esquentar ou o cliente elevar o tom, nunca reaja no mesmo nível. Diga com calma:\n\n"
            f"*'Entendo perfeitamente que o momento é difícil, {cliente_nome}. Prefere que eu te ligue amanhã às 10h para seguirmos com calma e encontrarmos uma boa saída juntas?'*\n\n"
            f"Isso desarma o confronto, preserva a sua autoridade e protege o relacionamento comercial."
        )

    # Cobrar é Cuidar / Filosofia
    elif "cobrar é cuidar" in p_low or "método chama" in p_low or "filosofia" in p_low or "o que é chama" in p_low:
        return (
            f"O coração da obra da Lilian Lavorato (págs. 4-6): **Cobrar não é confrontar; é oferecer uma solução e cuidar de uma relação que vale a pena manter!**\n\n"
            f"O acrônimo **C.H.A.M.A.** organiza o fluxo do relacionamento:\n"
            f"• **C · Conhecer:** Análise de crédito, políticas e registro da carteira;\n"
            f"• **H · Humanizar:** Tom acolhedor, WhatsApp com rosto e roteiro estruturado;\n"
            f"• **A · Agir no tempo certo:** Régua preventiva do D-3 ao D+15;\n"
            f"• **M · Mediar:** Escutar o motivo real antes de propor alçadas;\n"
            f"• **A · Acompanhar:** O Ritual da Parcela e a fidelização pós-acordo."
        )

    # Personas do livro
    elif "carla" in p_low or "apertada" in p_low:
        return (
            f"Para a **Carla (A Apertada)** (págs. 7 e 26): Ela quer pagar, mas o fluxo de caixa quebrou temporariamente.\n"
            f"• **Estratégia:** Escuta ativa e validação da dificuldade;\n"
            f"• **Ação:** Proposta estruturada com entrada viável e até 3x sem juros no Farol Verde;\n"
            f"• **Frase-chave:** *'Conseguimos organizar uma entrada e parcelas fixas para manter seu crédito protegido. Vamos formalizar?'*"
        )
    elif "jorge" in p_low or "esquecido" in p_low:
        return (
            f"Para o **Seu Jorge (O Esquecido)** (págs. 7 e 11): Ele tem o dinheiro, mas perdeu o boleto na correria.\n"
            f"• **Estratégia:** Facilitar sem julgar ou constranger;\n"
            f"• **Ação:** Lembrete amigável e direto com chave PIX copia e cola;\n"
            f"• **Frase-chave:** *'Oi, Seu Jorge! Segue a chave PIX para facilitar. Se já pagou, me manda o comprovante que dou baixa!'*"
        )
    elif "rafael" in p_low or "contestador" in p_low:
        return (
            f"Para o **Rafael (O Contestador)** (págs. 7 e 28): Ele desconfia da cobrança e acha que a nota está errada.\n"
            f"• **Estratégia:** Postura técnica, transparente e consultiva;\n"
            f"• **Ação:** Conferência prévia interna. Reenvie a Nota Fiscal e o comprovante de entrega antes de cobrar valores;\n"
            f"• **Frase-chave:** *'Vou revisar agora mesmo e te retorno com precisão. Nossa prioridade é manter uma relação justa e transparente.'*"
        )
    elif "marta" in p_low or "sumida" in p_low or "sumiu" in p_low:
        return (
            f"Para a **Dona Marta (A Sumida)** (págs. 7 e 30): Ela visualiza e não responde por vergonha ou falta de opção.\n"
            f"• **Estratégia:** Tirar o peso emocional e facilitar ao máximo a resposta;\n"
            f"• **Ação:** Mensagem curta numerada (Menu 1, 2, 3);\n"
            f"• **Frase-chave:** *'Para facilitar a regularização, escolha uma opção: 1- PIX com desconto | 2- Parcelar | 3- Ligar para conversarmos.'*"
        )
    elif "léo" in p_low or "leo" in p_low or "promitente" in p_low:
        return (
            f"Para o **Léo (O Promitente)** (págs. 7, 30 e 46): Ele promete uma data, a data passa e ele promete outra.\n"
            f"• **Estratégia:** Transformar intenção em compromisso formal por escrito;\n"
            f"• **Ação:** Contato no próprio dia do compromisso agendado com valor, data e meio;\n"
            f"• **Frase-chave:** *'Passando para confirmar nosso compromisso agendado para hoje referente ao título. Segue a chave PIX para quitação.'*"
        )

    # ---------------------------------------------------------
    # 3. RESPOSTA CALIBRADA PARA DÚVIDAS ABERTAS / PEDIDO DE DETALHAMENTO
    # ---------------------------------------------------------
    else:
        return (
            f"Olá, {nome_op}! Por favor, **me descreva melhor sua pergunta** para que eu consiga te orientar com máxima precisão pedagógica!\n\n"
            f"Posso te ajudar com qualquer tema, roteiro ou página do livro *A Arte da Cobrança Humanizada* da Lilian Lavorato. "
            f"Você pode me pedir diretamente pelo número da página (ex: *'O que diz a página 4?'*) ou escolher um dos grandes tópicos do sumário:\n\n"
            f"• **Começo de Conversa (págs. 2-8):** Boas-vindas (p. 2), Método C.H.A.M.A. (p. 4), Cobrar é Cuidar (p. 5), Cobrar x Pedir Pagamento (p. 6), Os 5 Perfis de Inadimplência (p. 7), 7 Hábitos a Evitar (p. 8);\n"
            f"• **C · Conhecer (págs. 10-12):** Gestão Financeira e Análise de Crédito (p. 10), Registro e Organização (p. 11), Matriz de Prioridades (p. 12);\n"
            f"• **H · Humanizar (págs. 14-17):** Comunicação que Conecta (p. 14), Anatomia do WhatsApp em 5 Partes (p. 15), Horários Nobres e Canais (p. 16), Roteiro da Ligação (p. 17);\n"
            f"• **A · Agir no Tempo Certo (págs. 19-23):** Régua de Cobrança D-5 a D+15 (p. 19), Automação no ERP (p. 21), Modelos Prontos 01 a 06 (p. 22-23);\n"
            f"• **M · Mediar (págs. 25-32):** Fluxograma de Decisão (p. 25), Troca de Concessão por Compromisso (p. 26), Tabela de Alçadas (p. 27), Quebra das 8 Objeções (p. 28-29), Silêncio e Casos Delicados (p. 30-32);\n"
            f"• **A · Acompanhar (págs. 34-39):** Os 8 Itens do Acordo (p. 34), Ritual da Parcela no D-2 (p. 35), Cuidados Legais e Art. 42 CDC (p. 37), 4 Indicadores Essenciais (p. 38), Pós-Cobrança (p. 39);\n"
            f"• **Caixa de Ferramentas (págs. 40-42):** Plano de Ação de 7 Dias (p. 40), Checklists de Consulta Rápida (p. 41), Fichas para Imprimir (p. 42)."
        )

# Chips de perguntas rápidas personalizadas por perfil
chips_por_perfil = {
    "Carla (A Apertada)": [
        "Como acompanhar o acordo depois de fechado?",
        "Como aplicar 'Trocar concessão por compromisso'?",
        "Como negociar a entrada sem confrontar a Carla?"
    ],
    "Seu Jorge (O Esquecido)": [
        "Como acompanhar o acordo depois de fechado?",
        "Como enviar o PIX de forma leve sem cobrança pesada?",
        "O que diz o Art. 42 do CDC sobre constrangimento?"
    ],
    "Rafael (O Contestador)": [
        "Como agir quando o cliente contesta a Nota Fiscal?",
        "Como aplicar a técnica de 'Pausar é técnica'?",
        "Como acompanhar o acordo depois de fechado?"
    ],
    "Dona Marta (A Sumida)": [
        "Como usar o Menu 1, 2, 3 para ela responder?",
        "O que a Lilian ensina quando o cliente some?",
        "Como acompanhar o acordo depois de fechado?"
    ],
    "Léo (O Promitente)": [
        "O que fazer quando o cliente quebra a promessa de data?",
        "Como aplicar o Ritual da Parcela no D-2?",
        "Como acompanhar o acordo depois de fechado?"
    ]
}

lista_perguntas_rapidas = chips_por_perfil.get(perf, [
    "Como acompanhar o acordo depois de fechado?",
    "O que diz o Art. 42 do CDC sobre cobrança?",
    "Como aplicar 'Trocar concessão por compromisso'?"
])

st.write("**Sugestões de Dúvidas Práticas para o Caso Atual:**")
col_b1, col_b2, col_b3 = st.columns(3)

pergunta_clicada = None
if col_b1.button(f"💡 {lista_perguntas_rapidas[0]}", key="btn_chip_0", use_container_width=True):
    pergunta_clicada = lista_perguntas_rapidas[0]
if col_b2.button(f"💡 {lista_perguntas_rapidas[1]}", key="btn_chip_1", use_container_width=True):
    pergunta_clicada = lista_perguntas_rapidas[1]
if col_b3.button(f"💡 {lista_perguntas_rapidas[2]}", key="btn_chip_2", use_container_width=True):
    pergunta_clicada = lista_perguntas_rapidas[2]

pergunta_digitada = st.text_input("Ou digite sua dúvida sobre o livro ou a negociação:", value="", key="input_pergunta_bia", placeholder="Ex: Como acompanhar o acordo depois de fechado?")

col_btn_env, col_esp = st.columns([1.5, 2.5])
with col_btn_env:
    btn_enviar = st.button("Enviar Pergunta para a Bia", key="btn_submeter_pergunta", use_container_width=True)

pergunta_final = None
if pergunta_clicada:
    pergunta_final = pergunta_clicada
elif pergunta_digitada.strip() and (btn_enviar or st.session_state.get('pergunta_anterior_digitada') != pergunta_digitada.strip()):
    pergunta_final = pergunta_digitada.strip()
    st.session_state['pergunta_anterior_digitada'] = pergunta_digitada.strip()

if pergunta_final:
    st.session_state['ultima_pergunta_bia'] = pergunta_final
    nova_resp = consultar_mentoria_bia(pergunta_final, cli_atual, perf, valor_divida_atual)
    st.session_state['ultima_resposta_bia'] = nova_resp
    st.session_state['audio_counter'] += 1
    # Ativa fala automática exclusivamente para quando uma pergunta foi enviada!
    st.session_state['deve_tocar_audio'] = True
    salvar_perfil_disco(nome=st.session_state['nome_operador'], ultima_pergunta=pergunta_final, ultima_resposta=nova_resp)
    
    # Registra no Diário de Bordo para rastreabilidade de mentoria
    agora_m = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    foto_status_m = "📷 Foto Carregada" if st.session_state['foto_operador_bytes'] is not None else "👤 Avatar Padrão"
    reg_mentoria = {
        "Data/Hora": agora_m,
        "Operador": nome_op,
        "Cliente": cli_atual,
        "Valor Original": f"R$ {val_divida_num:,.2f}",
        "Encargos": "-",
        "Entrada (R$)": "-",
        "Parcelamento": "-",
        "Resumo do Acordo": f"Dúvida: {pergunta_final[:50]}...",
        "Alçada": "💡 Mentoria com a Bia",
        "Cuidômetro Acumulado": st.session_state['cuidometro'],
        "Status": f"Consulta Pedagógica ({pergunta_final[:30]}...)"
    }
    st.session_state['historico_diario_bordo'].append(reg_mentoria)

# Exibe a resposta da Bia caso exista
if st.session_state['ultima_resposta_bia']:
    resp_formatada = st.session_state['ultima_resposta_bia']
    perg_feita = st.session_state['ultima_pergunta_bia']
    audio_id = st.session_state['audio_counter']
    
    # 1. Card de Resposta em Texto Íntegro (Sem conflito de DOM e com proteção notranslate)
    with st.container(border=True):
        st.caption(f"❓ Dúvida: \"{perg_feita}\"")
        st.markdown("### Orientação Pedagógica da Bia:")
        
        if st.session_state['modo_mentoria_bia'] in ["🎙️ Texto + Voz (Completo)", "📝 Apenas Texto"]:
            st.markdown(f'<div class="notranslate" translate="no">\n\n{resp_formatada}\n\n</div>', unsafe_allow_html=True)
    
    # 2. Player de Áudio Fonético com Leitura Integral por Frases (Sem corte de 15s do Chrome)
    if st.session_state['modo_mentoria_bia'] in ["🎙️ Texto + Voz (Completo)", "🔊 Apenas Voz"]:
        # Filtro fonético exclusivo para a síntese vocal (não altera o texto na tela!)
        texto_fonetico = resp_formatada
        texto_fonetico = re.sub(r'[💡⚠️✨📌🎯💬👤📖❓🔍•\*\#\_`]', '', texto_fonetico)
        texto_fonetico = re.sub(r'\bC\.?H\.?A\.?M\.?A\.?\b', 'Chama', texto_fonetico, flags=re.IGNORECASE)
        texto_fonetico = re.sub(r'\bCHAMA\b', 'Chama', texto_fonetico)
        texto_fonetico = re.sub(r'\bLilian\s+Lavorato\b', 'Líliam Lavorato', texto_fonetico, flags=re.IGNORECASE)
        texto_fonetico = re.sub(r'\bLilian\b', 'Líliam', texto_fonetico, flags=re.IGNORECASE)
        texto_fonetico = re.sub(r'\bPIX\b', 'Pícs', texto_fonetico)
        texto_fonetico = re.sub(r'\bArt\.?\s*42\b', 'Artigo quarenta e dois', texto_fonetico, flags=re.IGNORECASE)
        texto_fonetico = re.sub(r'R\$\s*([\d\.\,]+)', r'\1 reais', texto_fonetico)
        texto_fonetico = re.sub(r'\bCDC\b', 'C D C', texto_fonetico)
        texto_fonetico = re.sub(r'\bD-2\b', 'D menos dois', texto_fonetico)
        texto_fonetico = re.sub(r'\bD0\b', 'D zero', texto_fonetico)
        texto_fonetico = re.sub(r'\bD\+1\b', 'D mais um', texto_fonetico)
        texto_fonetico = re.sub(r'\s+', ' ', texto_fonetico).strip()
        
        # Divide o texto completo em frases naturais para contornar o limite de 15s do Chrome
        partes_frases = [p.strip() for p in re.split(r'[\r\n]+|(?<=[.!?])\s+', texto_fonetico) if p.strip()]
        if not partes_frases:
            partes_frases = [texto_fonetico]
        frases_json = json.dumps(partes_frases, ensure_ascii=False)
        total_frases = len(partes_frases)
        
        # Flag de reprodução automática: SOMENTE se uma pergunta nova acabou de ser enviada!
        auto_play_js = "true" if st.session_state.get('deve_tocar_audio', False) else "false"
        st.session_state['deve_tocar_audio'] = False
        
        audio_id = st.session_state['audio_counter']
        
        player_html = f"""
        <div class="notranslate" translate="no" style="background-color: #F8FAF9; border: 1.5px solid #D0E1D9; border-radius: 12px; padding: 14px 18px; margin-top: 10px; margin-bottom: 14px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; box-shadow: 0px 2px 6px rgba(0,0,0,0.03);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 13px; font-weight: bold; color: #1A3644;">
                    🎧 Áudio da Mentoria com a Bia (Voz Feminina C.H.A.M.A.)
                </span>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span style="font-size: 11px; color: #666; font-weight: 500;">Velocidade:</span>
                    <button type="button" onclick="alterarVelocidade(1.0)" id="btn_spd_10_{audio_id}" style="background:#2E8B57; color:#FFFFFF; border:none; border-radius:4px; padding:2px 7px; font-size:11px; font-weight:bold; cursor:pointer;">1.0x</button>
                    <button type="button" onclick="alterarVelocidade(1.25)" id="btn_spd_125_{audio_id}" style="background:#E2E8F0; color:#1A3644; border:none; border-radius:4px; padding:2px 7px; font-size:11px; font-weight:bold; cursor:pointer;">1.25x</button>
                    <button type="button" onclick="alterarVelocidade(1.50)" id="btn_spd_15_{audio_id}" style="background:#E2E8F0; color:#1A3644; border:none; border-radius:4px; padding:2px 7px; font-size:11px; font-weight:bold; cursor:pointer;">1.5x</button>
                </div>
            </div>
            
            <!-- Barra do Player: Play/Pause Circular + Régua de Tempo + Tempo Decorrido -->
            <div style="display: flex; align-items: center; gap: 12px;">
                <button type="button" id="btn_play_{audio_id}" onclick="togglePlayPause()" style="background-color: #2E8B57; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0px 2px 4px rgba(0,0,0,0.15);">
                    ▶️
                </button>
                
                <span id="time_current_{audio_id}" style="font-size: 12px; font-weight: 600; color: #1A3644; min-width: 32px;">0:00</span>
                
                <div style="flex-grow: 1; position: relative; display: flex; align-items: center;">
                    <input type="range" id="audio_regua_{audio_id}" min="0" max="100" value="0" step="1" 
                           oninput="onScrubInput(this.value)" 
                           onchange="onScrubChange(this.value)"
                           style="width: 100%; height: 6px; border-radius: 3px; cursor: pointer; accent-color: #2E8B57;">
                </div>
                
                <span id="time_total_{audio_id}" style="font-size: 12px; font-weight: 600; color: #666; min-width: 32px;">0:00</span>
                
                <button type="button" onclick="pararAudio()" style="background-color: #E2E8F0; color: #444; border: none; padding: 6px 12px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer;">
                    ⏹️ Parar
                </button>
            </div>
            
            <div style="margin-top: 6px; display: flex; justify-content: space-between; align-items: center;">
                <span id="status_voz_{audio_id}" style="font-size: 11px; color: #2E8B57; font-weight: 500;">Pronto para ouvir</span>
                <span id="progresso_frases_{audio_id}" style="font-size: 11px; color: #888;">Leitura integral ({total_frases} frases estruturadas)</span>
            </div>
        </div>

        <script>
            var frases_{audio_id} = {frases_json};
            var totalFrases_{audio_id} = frases_{audio_id}.length;
            var currentSpeed_{audio_id} = 1.0;
            var isPlaying_{audio_id} = false;
            var isSpeakingFrase_{audio_id} = false;
            var currentFraseIdx_{audio_id} = 0;
            var tickerTimer_{audio_id} = null;
            var elapsedSeconds_{audio_id} = 0;
            var autoPlay_{audio_id} = {auto_play_js};
            var timeoutVozes_{audio_id} = null;

            // Calcula total de caracteres para estimativa de tempo
            var totalChars_{audio_id} = 0;
            for (var i = 0; i < frases_{audio_id}.length; i++) {{
                totalChars_{audio_id} += frases_{audio_id}[i].length;
            }}
            var totalEstimatedSec_{audio_id} = Math.max(3, Math.round(totalChars_{audio_id} / 15));

            function formatarTempo(segundos) {{
                var m = Math.floor(segundos / 60);
                var s = Math.floor(segundos % 60);
                return m + ':' + (s < 10 ? '0' : '') + s;
            }}

            var elTot = document.getElementById('time_total_{audio_id}');
            if (elTot) elTot.innerText = formatarTempo(totalEstimatedSec_{audio_id});

            function atualizarBotoesVelocidade(vel) {{
                var b10 = document.getElementById('btn_spd_10_{audio_id}');
                var b125 = document.getElementById('btn_spd_125_{audio_id}');
                var b15 = document.getElementById('btn_spd_15_{audio_id}');
                if (b10) {{ b10.style.background = (vel === 1.0 ? '#2E8B57' : '#E2E8F0'); b10.style.color = (vel === 1.0 ? '#FFF' : '#1A3644'); }}
                if (b125) {{ b125.style.background = (vel === 1.25 ? '#2E8B57' : '#E2E8F0'); b125.style.color = (vel === 1.25 ? '#FFF' : '#1A3644'); }}
                if (b15) {{ b15.style.background = (vel === 1.50 ? '#2E8B57' : '#E2E8F0'); b15.style.color = (vel === 1.50 ? '#FFF' : '#1A3644'); }}
            }}

            function buscarVozFemininaSuave(ut) {{
                if (!window.speechSynthesis) return;
                var voices = window.speechSynthesis.getVoices();
                if (!voices || voices.length === 0) return;

                var prioridades = [
                    'francisca', 'leticia', 'google português do brasil', 'google portugues',
                    'luciana', 'maria', 'fernanda', 'vitória', 'vitoria', 'female', 'feminina'
                ];

                for (var p = 0; p < prioridades.length; p++) {{
                    for (var i = 0; i < voices.length; i++) {{
                        var vName = voices[i].name.toLowerCase();
                        var vLang = voices[i].lang.toLowerCase();
                        if ((vLang.indexOf('pt-br') !== -1 || vLang.indexOf('pt_br') !== -1 || vLang === 'pt') && vName.indexOf(prioridades[p]) !== -1) {{
                            ut.voice = voices[i];
                            return;
                        }}
                    }}
                }}

                for (var j = 0; j < voices.length; j++) {{
                    var l = voices[j].lang.toLowerCase();
                    if (l.indexOf('pt-br') !== -1 || l.indexOf('pt_br') !== -1) {{
                        ut.voice = voices[j];
                        return;
                    }}
                }}
            }}

            function iniciarTicker() {{
                pararTicker();
                tickerTimer_{audio_id} = setInterval(function() {{
                    if (isPlaying_{audio_id} && !window.speechSynthesis.paused) {{
                        elapsedSeconds_{audio_id} += 0.25;
                        var tEl = document.getElementById('time_current_{audio_id}');
                        if (tEl) tEl.innerText = formatarTempo(elapsedSeconds_{audio_id});
                    }}
                }}, 250);
            }}

            function pararTicker() {{
                if (tickerTimer_{audio_id}) {{
                    clearInterval(tickerTimer_{audio_id});
                    tickerTimer_{audio_id} = null;
                }}
            }}

            function falarFrase() {{
                if (!window.speechSynthesis) return;
                if (!isPlaying_{audio_id}) return;
                if (isSpeakingFrase_{audio_id}) return; // Trava estrita contra reentrância / repetição

                if (currentFraseIdx_{audio_id} >= totalFrases_{audio_id}) {{
                    finalizarAudio();
                    return;
                }}

                var textoFrase = frases_{audio_id}[currentFraseIdx_{audio_id}];
                if (!textoFrase || textoFrase.trim().length === 0) {{
                    currentFraseIdx_{audio_id}++;
                    falarFrase();
                    return;
                }}

                isSpeakingFrase_{audio_id} = true;
                var ut = new SpeechSynthesisUtterance(textoFrase);
                ut.lang = 'pt-BR';
                ut.rate = currentSpeed_{audio_id};
                ut.pitch = 1.15;
                buscarVozFemininaSuave(ut);

                ut.onstart = function() {{
                    isPlaying_{audio_id} = true;
                    isSpeakingFrase_{audio_id} = true;
                    var bPlay = document.getElementById('btn_play_{audio_id}');
                    if (bPlay) bPlay.innerHTML = '⏸️';
                    var sEl = document.getElementById('status_voz_{audio_id}');
                    if (sEl) sEl.innerText = '▶️ Reproduzindo...';
                    var pEl = document.getElementById('progresso_frases_{audio_id}');
                    if (pEl) pEl.innerText = 'Lendo frase ' + (currentFraseIdx_{audio_id} + 1) + ' de ' + totalFrases_{audio_id};
                    iniciarTicker();
                }};

                ut.onend = function() {{
                    isSpeakingFrase_{audio_id} = false;
                    currentFraseIdx_{audio_id}++;
                    var percent = Math.min(100, Math.round((currentFraseIdx_{audio_id} / totalFrases_{audio_id}) * 100));
                    var regua = document.getElementById('audio_regua_{audio_id}');
                    if (regua) regua.value = percent;

                    if (isPlaying_{audio_id} && currentFraseIdx_{audio_id} < totalFrases_{audio_id}) {{
                        // Delay limpo de 40ms entre frases para buffer de áudio
                        setTimeout(function() {{
                            if (isPlaying_{audio_id} && !isSpeakingFrase_{audio_id}) {{
                                falarFrase();
                            }}
                        }}, 40);
                    }} else if (currentFraseIdx_{audio_id} >= totalFrases_{audio_id}) {{
                        finalizarAudio();
                    }}
                }};

                ut.onerror = function() {{
                    isSpeakingFrase_{audio_id} = false;
                    currentFraseIdx_{audio_id}++;
                    if (isPlaying_{audio_id} && currentFraseIdx_{audio_id} < totalFrases_{audio_id}) {{
                        setTimeout(function() {{
                            if (isPlaying_{audio_id} && !isSpeakingFrase_{audio_id}) {{
                                falarFrase();
                            }}
                        }}, 40);
                    }} else {{
                        finalizarAudio();
                    }}
                }};

                window.speechSynthesis.speak(ut);
            }}

            function finalizarAudio() {{
                isPlaying_{audio_id} = false;
                isSpeakingFrase_{audio_id} = false;
                pararTicker();
                var bPlay = document.getElementById('btn_play_{audio_id}');
                if (bPlay) bPlay.innerHTML = '▶️';
                var sEl = document.getElementById('status_voz_{audio_id}');
                if (sEl) sEl.innerText = '✓ Concluído integralmente';
                var regua = document.getElementById('audio_regua_{audio_id}');
                if (regua) regua.value = 100;
                currentFraseIdx_{audio_id} = 0;
                var pEl = document.getElementById('progresso_frases_{audio_id}');
                if (pEl) pEl.innerText = 'Leitura 100% concluída (' + totalFrases_{audio_id} + ' frases)';
            }}

            function garantirVozesEComecar(indiceFrase) {{
                if (!window.speechSynthesis) return;
                
                // Limpeza completa de qualquer fala anterior
                window.speechSynthesis.cancel();
                isSpeakingFrase_{audio_id} = false;
                currentFraseIdx_{audio_id} = indiceFrase || 0;
                isPlaying_{audio_id} = true;

                if (timeoutVozes_{audio_id}) {{
                    clearTimeout(timeoutVozes_{audio_id});
                    timeoutVozes_{audio_id} = null;
                }}

                var v = window.speechSynthesis.getVoices();
                if (v && v.length > 0) {{
                    falarFrase();
                }} else {{
                    var executou = false;
                    var iniciarUnico = function() {{
                        if (executou) return;
                        executou = true;
                        window.speechSynthesis.onvoiceschanged = null;
                        if (timeoutVozes_{audio_id}) {{
                            clearTimeout(timeoutVozes_{audio_id});
                            timeoutVozes_{audio_id} = null;
                        }}
                        falarFrase();
                    }};

                    window.speechSynthesis.onvoiceschanged = iniciarUnico;
                    timeoutVozes_{audio_id} = setTimeout(iniciarUnico, 250);
                }}
            }}

            function togglePlayPause() {{
                if (!window.speechSynthesis) return;

                if (isPlaying_{audio_id} && !window.speechSynthesis.paused) {{
                    window.speechSynthesis.pause();
                    var bPlay = document.getElementById('btn_play_{audio_id}');
                    if (bPlay) bPlay.innerHTML = '▶️';
                    var sEl = document.getElementById('status_voz_{audio_id}');
                    if (sEl) sEl.innerText = '⏸️ Pausado';
                }} else if (window.speechSynthesis.paused) {{
                    window.speechSynthesis.resume();
                    var bPlay = document.getElementById('btn_play_{audio_id}');
                    if (bPlay) bPlay.innerHTML = '⏸️';
                    var sEl = document.getElementById('status_voz_{audio_id}');
                    if (sEl) sEl.innerText = '▶️ Reproduzindo...';
                }} else {{
                    garantirVozesEComecar(currentFraseIdx_{audio_id});
                }}
            }}

            function onScrubInput(val) {{
                var sEl = document.getElementById('status_voz_{audio_id}');
                if (sEl) sEl.innerText = 'Posição: ' + val + '%';
            }}

            function onScrubChange(val) {{
                var targetFrase = Math.floor((val / 100) * totalFrases_{audio_id});
                currentFraseIdx_{audio_id} = Math.min(totalFrases_{audio_id} - 1, Math.max(0, targetFrase));
                elapsedSeconds_{audio_id} = (val / 100) * totalEstimatedSec_{audio_id};
                var tEl = document.getElementById('time_current_{audio_id}');
                if (tEl) tEl.innerText = formatarTempo(elapsedSeconds_{audio_id});

                if (isPlaying_{audio_id}) {{
                    window.speechSynthesis.cancel();
                    isSpeakingFrase_{audio_id} = false;
                    falarFrase();
                }}
            }}

            function alterarVelocidade(novaVel) {{
                currentSpeed_{audio_id} = novaVel;
                atualizarBotoesVelocidade(novaVel);

                totalEstimatedSec_{audio_id} = Math.max(3, Math.round(totalChars_{audio_id} / (15 * currentSpeed_{audio_id})));
                var tTot = document.getElementById('time_total_{audio_id}');
                if (tTot) tTot.innerText = formatarTempo(totalEstimatedSec_{audio_id});

                if (isPlaying_{audio_id} && !window.speechSynthesis.paused) {{
                    window.speechSynthesis.cancel();
                    isSpeakingFrase_{audio_id} = false;
                    falarFrase();
                }}
            }}

            function pararAudio() {{
                if (window.speechSynthesis) {{
                    window.speechSynthesis.cancel();
                }}
                if (timeoutVozes_{audio_id}) {{
                    clearTimeout(timeoutVozes_{audio_id});
                    timeoutVozes_{audio_id} = null;
                }}
                isPlaying_{audio_id} = false;
                isSpeakingFrase_{audio_id} = false;
                pararTicker();
                currentFraseIdx_{audio_id} = 0;
                elapsedSeconds_{audio_id} = 0;
                var regua = document.getElementById('audio_regua_{audio_id}');
                if (regua) regua.value = 0;
                var bPlay = document.getElementById('btn_play_{audio_id}');
                if (bPlay) bPlay.innerHTML = '▶️';
                var sEl = document.getElementById('status_voz_{audio_id}');
                if (sEl) sEl.innerText = 'Pronto para ouvir';
                var tCur = document.getElementById('time_current_{audio_id}');
                if (tCur) tCur.innerText = '0:00';
                var pEl = document.getElementById('progresso_frases_{audio_id}');
                if (pEl) pEl.innerText = 'Leitura pausada (frase 1 de ' + totalFrases_{audio_id} + ')';
            }}

            // Keep-alive heartbeat para navegadores Chromium (Chrome / Edge)
            setInterval(function() {{
                if (window.speechSynthesis && window.speechSynthesis.speaking && !window.speechSynthesis.paused) {{
                    window.speechSynthesis.pause();
                    window.speechSynthesis.resume();
                }}
            }}, 8000);

            // Auto-play apenas se solicitado explicitamente por uma pergunta nova enviada
            if (autoPlay_{audio_id} === true) {{
                setTimeout(function() {{
                    garantirVozesEComecar(0);
                }}, 250);
            }}
        </script>
        """
        components.html(player_html, height=110)

# ----------------------------------------------------
# REGISTRO DO DIÁRIO DE BORDO (SAÍDA DE DADOS / AUDITORIA)
# ----------------------------------------------------
with st.expander("📋 Diário de Bordo dos Acordos Registrados (Histórico da Sessão / Auditoria)", expanded=False):
    st.write("Visualização em tempo real das relações preservadas que alimentam a planilha de treinamento e auditoria:")
    if st.session_state['historico_diario_bordo']:
        df_hist = pd.DataFrame(st.session_state['historico_diario_bordo'])
        st.dataframe(df_hist, use_container_width=True)
        csv_download = df_hist.to_csv(index=False, sep=";").encode('utf-8-sig')
        st.download_button(
            label="📥 Baixar Diário de Bordo em CSV (Planilha Excel)",
            data=csv_download,
            file_name=f"diario_de_bordo_chama_auditoria_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum acordo formalizado nesta sessão ainda. Conclua uma negociação para ver o registro automático aqui.")

st.markdown("<br><hr>", unsafe_allow_html=True)
st.caption("Apoio Pedagógico ao Treinamento A Arte da Cobrança Humanizada (Lilian Lavorato) · Collab MGP - Métodos, Gestão e Projetos")
