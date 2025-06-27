# --- INSTRUÇÕES DE INSTALAÇÃO ---
# Antes de rodar, instale as bibliotecas necessárias para exportar em PDF e Word:
# pip install streamlit python-docx reportlab

import streamlit as st
import datetime
import io
import json
import os
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch

# --- Configuração da Página ---
st.set_page_config(
    page_title="Checklist Help Desk",
    page_icon="✨",
    layout="wide",
)

# --- Constante para o arquivo de histórico ---
COMPLETED_FILE = "completed_checklists.json"

# --- CSS para um Design Aprimorado e Responsivo ---
def load_css():
    """Carrega e injeta o CSS customizado para estilizar a aplicação."""
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

        body, .main {
            font-family: 'Roboto', sans-serif;
            background-color: #f7f9fc;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e6e6e6;
            padding: 15px;
        }
        
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
             color: #0d2a4b;
        }

        .stButton>button, .stDownloadButton>button {
            border-radius: 8px;
            padding: 12px 20px; /* Aumenta o padding para melhor toque */
            font-weight: 500;
            border: 1px solid transparent;
            color: white !important;
            transition: all 0.3s ease;
            width: 100%;
        }

        .stButton>button[kind="primary"] {
            background-color: #0068c9;
            border-color: #0068c9;
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #0058ad;
            border-color: #0058ad;
        }
        
         .stButton>button[kind="secondary"] {
            background-color: #0068c9;
            border-color: #0068c9;
            color: white !important;
        }
        .stButton>button[kind="secondary"]:hover {
            background-color: #0058ad;
            border-color: #0058ad;
        }

        .stDownloadButton>button {
            background-color: #5c6c7d;
            border-color: #5c6c7d;
        }
        .stDownloadButton>button:hover {
            background-color: #4a5766;
            border-color: #4a5766;
        }
        
        [data-testid="stExpander"] {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }
        [data-testid="stExpander"] summary {
            font-size: 1.1rem;
            font-weight: 500;
            color: #0d2a4b;
            padding: 12px 15px;
        }
        [data-testid="stExpander"] summary:hover {
            background-color: #f7f9fc;
        }
        .st-expander-content {
            padding: 15px;
        }
        
        /* Correção para visibilidade dos labels em todos os temas */
        [data-testid="stWidgetLabel"] label {
            color: #0d2a4b !important;
            font-weight: 500 !important;
        }

        [data-testid="stTextInput"] input, 
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            border-radius: 8px;
            border: 1px solid #d1d5db;
        }
        [data-testid="stTextInput"] input:focus, 
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {
            border-color: #0068c9;
            box-shadow: 0 0 0 2px rgba(0, 104, 201, 0.25);
        }

        [data-testid="stTabs"] button {
            border-radius: 8px 8px 0 0 !important;
        }
        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            border-bottom: 2px solid #e6e6e6;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            border-bottom: 2px solid #0068c9 !important;
            color: #0068c9;
        }
        
        h1 {
            color: #0d2a4b;
            font-size: 2.2rem;
        }
        h2, h3 {
             color: #0d2a4b;
        }

        /* --- Media Queries para Responsividade --- */
        @media (max-width: 768px) {
            /* Empilha colunas em telas menores */
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            
            [data-testid="stHorizontalBlock"] > div {
                width: 100% !important;
                margin-bottom: 1rem; /* Adiciona espaço entre itens empilhados */
            }

            .main .block-container {
                padding: 1rem;
            }

            h1 {
                font-size: 1.8rem;
            }
            
            .st-expander-content {
                padding: 10px;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Funções de Persistência ---
def load_completed_tickets():
    """Carrega os chamados concluídos do arquivo JSON."""
    if not os.path.exists(COMPLETED_FILE):
        return {}
    with open(COMPLETED_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_completed_ticket(ticket_id, data):
    """Salva um único chamado concluído no arquivo JSON."""
    all_completed = load_completed_tickets()
    all_completed[ticket_id] = data
    with open(COMPLETED_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_completed, f, indent=4, ensure_ascii=False)


# --- Funções de Geração de Relatório ---

def get_report_data(ticket_data):
    """Coleta os dados do dicionário do chamado e retorna uma lista de strings formatadas."""
    agencia = ticket_data.get('agencia', '')
    cidade_uf = ticket_data.get('cidade_uf', '')
    endereco = ticket_data.get('endereco', '')
    num_racks = int(ticket_data.get('num_racks', 1))
    
    report_lines = [
        "TITLE: Check list Caixa Econômica",
        "",
        f"Agência: {agencia}",
        f"Cidade/UF: {cidade_uf}",
        f"Endereço: {endereco}",
        f"Quantidade de Rack na agência: {num_racks}",
        "",
    ]

    for i in range(1, num_racks + 1):
        report_lines.append(f"SUBTITLE: Rack {i}:")
        report_lines.append(f"Local instalado: {ticket_data.get(f'rack_local_{i}', '')}")
        report_lines.append(f"Tamanho do Rack {i} – Número de Us: {ticket_data.get(f'rack_tamanho_{i}', '')}")
        report_lines.append(f"Quantidade de Us disponíveis: {ticket_data.get(f'rack_us_disponiveis_{i}', '')}")
        report_lines.append(f"Quantidade de réguas de energia: {ticket_data.get(f'rack_reguas_{i}', '')}")
        report_lines.append(f"Quantidade de tomadas disponíveis: {ticket_data.get(f'rack_tomadas_disponiveis_{i}', '')}")
        report_lines.append(f"Disponibilidade para ampliação de réguas de energia: {ticket_data.get(f'rack_ampliacao_reguas_{i}', 'Não')}")
        report_lines.append(f"Rack está em bom estado: {ticket_data.get(f'rack_estado_{i}', 'Não')}")
        report_lines.append(f"Rack está organizado: {ticket_data.get(f'rack_organizado_{i}', 'Não')}")
        report_lines.append(f"Equipamentos e cabeamentos identificados: {ticket_data.get(f'rack_identificado_{i}', 'Não')}")
        report_lines.append("")

    report_lines.append("SUBTITLE: Access Point (AP)")
    report_lines.append("")
    report_lines.append(f"Verificar a quantidade de APs: {ticket_data.get('ap_quantidade', '')}")
    report_lines.append(f"Identificar o setor onde será instalado*: {ticket_data.get('ap_setor', '')}")
    report_lines.append(f"Verificar as condições da Instalação (se possui infra ou não): {ticket_data.get('ap_condicoes', '')}")
    report_lines.append(f"** Altura que será instalado / distância do rack até o ponto de instalação: {ticket_data.get('ap_distancia', '')}")
    
    return report_lines

def create_pdf_report(ticket_data):
    """Gera um relatório em PDF a partir de um dicionário de dados."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['h1'], fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle(name='Subtitle', parent=styles['h2'], fontName='Helvetica-Bold', fontSize=12, alignment=TA_LEFT, spaceAfter=10)
    body_style = ParagraphStyle(name='Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=4)
    story = []
    report_lines = get_report_data(ticket_data)
    for line in report_lines:
        if line.startswith("TITLE:"):
            story.append(Paragraph(line.replace("TITLE:", "").strip(), title_style))
        elif line.startswith("SUBTITLE:"):
            story.append(Paragraph(line.replace("SUBTITLE:", "").strip(), subtitle_style))
        elif line.strip() == "":
            story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph(line.replace("<br>", "&nbsp;<br/>&nbsp;"), body_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx_report(ticket_data):
    """Gera um relatório em Word (.docx) a partir de um dicionário de dados."""
    document = Document()
    report_lines = get_report_data(ticket_data)
    for line in report_lines:
        if line.startswith("TITLE:"):
            p = document.add_paragraph()
            p.add_run(line.replace("TITLE:", "").strip()).bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("SUBTITLE:"):
            p = document.add_paragraph()
            p.add_run(line.replace("SUBTITLE:", "").strip()).bold = True
        else:
            document.add_paragraph(line)
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer

# --- Funções de Exibição da UI ---

def display_checklist(ticket_id, data_source, is_disabled=False):
    """Renderiza os campos do formulário para um determinado chamado usando expanders."""
    
    with st.expander("Informações Gerais da Agência", expanded=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.text_input("Agência", key=f'agencia_{ticket_id}', value=data_source.get('agencia', ''), disabled=is_disabled)
            st.text_input("Endereço", key=f'endereco_{ticket_id}', value=data_source.get('endereco', ''), disabled=is_disabled)
        with col2:
            st.text_input("Cidade/UF", key=f'cidade_uf_{ticket_id}', value=data_source.get('cidade_uf', ''), disabled=is_disabled)
            st.number_input("Quantidade de Racks na agência", min_value=1, step=1, key=f'num_racks_{ticket_id}', value=int(data_source.get('num_racks', 1)), disabled=is_disabled)
    
    num_racks = int(data_source.get(f'num_racks', 1) if is_disabled else st.session_state.get(f'num_racks_{ticket_id}', 1))

    with st.expander("Detalhes dos Racks"):
        for i in range(1, num_racks + 1):
            st.markdown(f"#### Rack {i}")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.text_input(f"Local instalado", key=f'rack_local_{i}_{ticket_id}', value=data_source.get(f'rack_local_{i}', ''), disabled=is_disabled)
                st.text_input(f"Tamanho do Rack {i} – Número de Us", key=f'rack_tamanho_{i}_{ticket_id}', value=data_source.get(f'rack_tamanho_{i}', ''), disabled=is_disabled)
                st.text_input(f"Quantidade de Us disponíveis", key=f'rack_us_disponiveis_{i}_{ticket_id}', value=data_source.get(f'rack_us_disponiveis_{i}', ''), disabled=is_disabled)
                st.text_input(f"Quantidade de réguas de energia", key=f'rack_reguas_{i}_{ticket_id}', value=data_source.get(f'rack_reguas_{i}', ''), disabled=is_disabled)
                st.text_input(f"Quantidade de tomadas disponíveis", key=f'rack_tomadas_disponiveis_{i}_{ticket_id}', value=data_source.get(f'rack_tomadas_disponiveis_{i}', ''), disabled=is_disabled)
            with c2:
                radio_options = ("Sim", "Não")
                st.radio("Disponibilidade para ampliação de réguas de energia", radio_options, key=f'rack_ampliacao_reguas_{i}_{ticket_id}', index=radio_options.index(data_source.get(f'rack_ampliacao_reguas_{i}', 'Não')), horizontal=True, disabled=is_disabled)
                st.radio("Rack está em bom estado", radio_options, key=f'rack_estado_{i}_{ticket_id}', index=radio_options.index(data_source.get(f'rack_estado_{i}', 'Não')), horizontal=True, disabled=is_disabled)
                st.radio("Rack está organizado", radio_options, key=f'rack_organizado_{i}_{ticket_id}', index=radio_options.index(data_source.get(f'rack_organizado_{i}', 'Não')), horizontal=True, disabled=is_disabled)
                st.radio("Equipamentos e cabeamentos identificados", radio_options, key=f'rack_identificado_{i}_{ticket_id}', index=radio_options.index(data_source.get(f'rack_identificado_{i}', 'Não')), horizontal=True, disabled=is_disabled)
            if i < num_racks:
                st.markdown("---")

    with st.expander("Access Point (AP)"):
        st.text_input("Verificar a quantidade de APs", key=f'ap_quantidade_{ticket_id}', value=data_source.get('ap_quantidade', ''), disabled=is_disabled)
        st.text_input("Identificar o setor onde será instalado*", help="Setor onde o novo AP ficará", key=f'ap_setor_{ticket_id}', value=data_source.get('ap_setor', ''), disabled=is_disabled)
        st.text_input("Verificar as condições da Instalação (se possui infra ou não)", help="Ex: Possui infra, não possui, precisa de canaleta, etc.", key=f'ap_condicoes_{ticket_id}', value=data_source.get('ap_condicoes', ''), disabled=is_disabled)
        st.text_input("** Altura que será instalado / distância do rack até o ponto de instalação", help="Ex: Teto 2.8m / 15m de distância do rack", key=f'ap_distancia_{ticket_id}', value=data_source.get('ap_distancia', ''), disabled=is_disabled)
    
    st.markdown("---")
    
    # --- Seção de Ações (Concluir ou Exportar) ---
    st.subheader("Ações")
    
    if not is_disabled:
        if st.button("✔️ Concluir e Arquivar Chamado", key=f"complete_{ticket_id}", help="Salva o estado atual do checklist e move para a área de revisão.", type="primary"):
            current_ticket_data = {key.replace(f"_{ticket_id}", ""): value for key, value in st.session_state.items() if str(key).endswith(f"_{ticket_id}")}
            save_completed_ticket(ticket_id, current_ticket_data)
            del st.session_state.tickets[ticket_id]
            st.success(f"Chamado {ticket_id} arquivado com sucesso!")
            st.rerun()

    
    final_ticket_data = data_source if is_disabled else {key.replace(f"_{ticket_id}", ""): value for key, value in st.session_state.items() if str(key).endswith(f"_{ticket_id}")}
    
    txt_data = "\n".join([line.replace("TITLE:", "").replace("SUBTITLE:", "").strip() for line in get_report_data(final_ticket_data)])
    pdf_data = create_pdf_report(final_ticket_data)
    docx_data = create_docx_report(final_ticket_data)

    st.markdown("Exportar Relatório:")
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        st.download_button(label="Baixar .TXT", data=txt_data, file_name=f"Checklist_{ticket_id.upper()}.txt", mime="text/plain")
    with d_col2:
        st.download_button(label="Baixar .PDF", data=pdf_data, file_name=f"Checklist_{ticket_id.upper()}.pdf", mime="application/pdf")
    with d_col3:
        st.download_button(label="Baixar .DOCX", data=docx_data, file_name=f"Checklist_{ticket_id.upper()}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- Início da Interface ---
load_css()

# Inicializa o estado da sessão para chamados ativos
if 'tickets' not in st.session_state:
    st.session_state.tickets = {}

with st.sidebar:
    st.header("Gestão de Checklists")
    
    mode = st.radio("Modo de Operação", ["Preenchimento", "Revisão"], key="mode", help="Escolha 'Preenchimento' para trabalhar em chamados ativos ou 'Revisão' para ver chamados concluídos.")
    
    st.markdown("---")

    if st.session_state.mode == "Preenchimento":
        st.subheader("Adicionar Novos Chamados")
        with st.form("new_ticket_form", clear_on_submit=True):
            new_tickets_input = st.text_area("Códigos dos Chamados (um por linha)", placeholder="CLAR-411\n12345\nCLAR-354").strip()
            submitted = st.form_submit_button("Adicionar Chamados")
            if submitted and new_tickets_input:
                ticket_ids = [tid.strip() for tid in new_tickets_input.split('\n') if tid.strip()]
                added_count = 0
                for ticket_id in ticket_ids:
                    # Formata o ID do chamado
                    formatted_id = ticket_id.upper()
                    if formatted_id.isdigit():
                        formatted_id = f"CLAR-{formatted_id}"
                    elif not formatted_id.startswith("CLAR-"):
                         formatted_id = f"CLAR-{formatted_id}"

                    if formatted_id not in st.session_state.tickets:
                        st.session_state.tickets[formatted_id] = {}
                        added_count += 1
                if added_count > 0:
                    st.success(f"{added_count} chamado(s) adicionado(s)!")
    
    elif st.session_state.mode == "Revisão":
        st.subheader("Revisar Concluídos")
        completed_tickets = load_completed_tickets()
        if not completed_tickets:
            st.info("Nenhum chamado concluído para revisar.")
        else:
            options = list(completed_tickets.keys())
            options.insert(0, "Selecione...")
            ticket_to_review = st.selectbox("Selecione um chamado:", options=options)
            
            if ticket_to_review != "Selecione...":
                st.session_state.review_ticket_id = ticket_to_review
                st.session_state.review_ticket_data = completed_tickets[ticket_to_review]
            else:
                 if 'review_ticket_id' in st.session_state:
                     del st.session_state['review_ticket_id']


# --- Área Principal ---
st.title("Ferramenta de Checklist de Campo")

if st.session_state.mode == "Preenchimento":
    if not st.session_state.tickets:
        st.info("Adicione um ou mais chamados na barra lateral para começar.")
    else:
        active_tickets = list(st.session_state.tickets.keys())
        tabs = st.tabs([f"Chamado: {tid.upper()}" for tid in active_tickets])
        for i, tab in enumerate(tabs):
            with tab:
                current_ticket_id = active_tickets[i]
                display_checklist(current_ticket_id, st.session_state, is_disabled=False)

elif st.session_state.mode == "Revisão":
    if 'review_ticket_id' in st.session_state and st.session_state.review_ticket_id:
        st.header(f"Revisando Chamado: {st.session_state.review_ticket_id.upper()}")
        display_checklist(st.session_state.review_ticket_id, st.session_state.review_ticket_data, is_disabled=True)
    else:
        st.info("Selecione um chamado concluído na barra lateral para iniciar a revisão.")
