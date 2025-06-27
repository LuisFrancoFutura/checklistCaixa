# --- INSTRUÇÕES DE INSTALAÇÃO ---
# Antes de rodar, instale as bibliotecas necessárias:
# pip install streamlit python-docx reportlab pandas plotly

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

        /* Oculta a barra lateral gerada pelo Streamlit na página principal */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        .stButton>button, .stDownloadButton>button {
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: 500;
            border: 1px solid transparent;
            color: white !important;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        [data-testid="stExpander"] {
            background-color: #ffffff;
            border: 1px solid #e6e6e6;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        [data-testid="stExpander"] summary {
            font-size: 1.1rem;
            font-weight: 500;
            color: #0d2a4b;
        }
        
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
        
        h1, h2, h3, h4, h5 {
            color: #0d2a4b;
        }

        @media (max-width: 768px) {
            [data-testid="stHorizontalBlock"] {
                flex-direction: column !important;
            }
            [data-testid="stHorizontalBlock"] > div {
                width: 100% !important;
                margin-bottom: 1rem;
            }
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# --- Funções de Persistência ---
def load_completed_tickets():
    if not os.path.exists(COMPLETED_FILE):
        return {}
    with open(COMPLETED_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

def save_completed_ticket(ticket_id, data):
    all_completed = load_completed_tickets()
    all_completed[ticket_id] = data
    with open(COMPLETED_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_completed, f, indent=4, ensure_ascii=False)


# --- Funções de Geração de Relatório ---
def get_report_data(ticket_data):
    agencia = ticket_data.get('agencia', '')
    cidade_uf = ticket_data.get('cidade_uf', '')
    endereco = ticket_data.get('endereco', '')
    num_racks = int(ticket_data.get('num_racks', 1))
    
    report_lines = ["TITLE: Check list Caixa Econômica", ""]
    report_lines.extend([f"Agência: {agencia}", f"Cidade/UF: {cidade_uf}", f"Endereço: {endereco}", f"Quantidade de Rack na agência: {num_racks}", ""])

    for i in range(1, num_racks + 1):
        report_lines.extend([f"SUBTITLE: Rack {i}:", f"Local instalado: {ticket_data.get(f'rack_local_{i}', '')}", f"Tamanho do Rack {i} – Número de Us: {ticket_data.get(f'rack_tamanho_{i}', '')}", f"Quantidade de Us disponíveis: {ticket_data.get(f'rack_us_disponiveis_{i}', '')}", f"Quantidade de réguas de energia: {ticket_data.get(f'rack_reguas_{i}', '')}", f"Quantidade de tomadas disponíveis: {ticket_data.get(f'rack_tomadas_disponiveis_{i}', '')}", f"Disponibilidade para ampliação de réguas de energia: {ticket_data.get(f'rack_ampliacao_reguas_{i}', 'Não')}", f"Rack está em bom estado: {ticket_data.get(f'rack_estado_{i}', 'Não')}", f"Rack está organizado: {ticket_data.get(f'rack_organizado_{i}', 'Não')}", f"Equipamentos e cabeamentos identificados: {ticket_data.get(f'rack_identificado_{i}', 'Não')}", ""])

    report_lines.extend(["SUBTITLE: Access Point (AP)", "", f"Verificar a quantidade de APs: {ticket_data.get('ap_quantidade', '')}", f"Identificar o setor onde será instalado*: {ticket_data.get('ap_setor', '')}", f"Verificar as condições da Instalação (se possui infra ou não): {ticket_data.get('ap_condicoes', '')}", f"** Altura que será instalado / distância do rack até o ponto de instalação: {ticket_data.get('ap_distancia', '')}"])
    
    return report_lines

def create_pdf_report(ticket_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Title', parent=styles['h1'], fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle(name='Subtitle', parent=styles['h2'], fontName='Helvetica-Bold', fontSize=12, alignment=TA_LEFT, spaceAfter=10)
    body_style = ParagraphStyle(name='Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=4)
    story = []
    for line in get_report_data(ticket_data):
        if line.startswith("TITLE:"): story.append(Paragraph(line.replace("TITLE:", "").strip(), title_style))
        elif line.startswith("SUBTITLE:"): story.append(Paragraph(line.replace("SUBTITLE:", "").strip(), subtitle_style))
        elif line.strip() == "": story.append(Spacer(1, 0.1*inch))
        else: story.append(Paragraph(line.replace("<br>", "&nbsp;<br/>&nbsp;"), body_style))
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx_report(ticket_data):
    document = Document()
    for line in get_report_data(ticket_data):
        if line.startswith("TITLE:"):
            p = document.add_paragraph(); p.add_run(line.replace("TITLE:", "").strip()).bold = True; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("SUBTITLE:"):
            p = document.add_paragraph(); p.add_run(line.replace("SUBTITLE:", "").strip()).bold = True
        else: document.add_paragraph(line)
    buffer = io.BytesIO(); document.save(buffer); buffer.seek(0)
    return buffer

# --- Funções de Exibição da UI ---
def display_checklist_form(ticket_id):
    """Renderiza os campos do formulário para um determinado chamado."""
    
    with st.expander("Informações Gerais da Agência", expanded=True):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.text_input("Agência", key=f'agencia_{ticket_id}')
            st.text_input("Endereço", key=f'endereco_{ticket_id}')
        with col2:
            st.text_input("Cidade/UF", key=f'cidade_uf_{ticket_id}')
            st.number_input("Quantidade de Racks na agência", min_value=1, step=1, key=f'num_racks_{ticket_id}')
    
    num_racks = int(st.session_state.get(f'num_racks_{ticket_id}', 1))

    with st.expander("Detalhes dos Racks"):
        for i in range(1, num_racks + 1):
            st.markdown(f"#### Rack {i}")
            c1, c2 = st.columns([1, 1])
            with c1:
                st.text_input(f"Local instalado", key=f'rack_local_{i}_{ticket_id}')
                st.text_input(f"Tamanho do Rack {i} – Número de Us", key=f'rack_tamanho_{i}_{ticket_id}')
                st.text_input(f"Quantidade de Us disponíveis", key=f'rack_us_disponiveis_{i}_{ticket_id}')
                st.text_input(f"Quantidade de réguas de energia", key=f'rack_reguas_{i}_{ticket_id}')
                st.text_input(f"Quantidade de tomadas disponíveis", key=f'rack_tomadas_disponiveis_{i}_{ticket_id}')
            with c2:
                radio_options = ("Sim", "Não")
                st.radio("Disponibilidade para ampliação de réguas de energia", radio_options, key=f'rack_ampliacao_reguas_{i}_{ticket_id}', horizontal=True)
                st.radio("Rack está em bom estado", radio_options, key=f'rack_estado_{i}_{ticket_id}', horizontal=True)
                st.radio("Rack está organizado", radio_options, key=f'rack_organizado_{i}_{ticket_id}', horizontal=True)
                st.radio("Equipamentos e cabeamentos identificados", radio_options, key=f'rack_identificado_{i}_{ticket_id}', horizontal=True)
            if i < num_racks: st.markdown("---")

    with st.expander("Access Point (AP)"):
        st.text_input("Verificar a quantidade de APs", key=f'ap_quantidade_{ticket_id}')
        st.text_input("Identificar o setor onde será instalado*", key=f'ap_setor_{ticket_id}')
        st.text_input("Verificar as condições da Instalação", key=f'ap_condicoes_{ticket_id}')
        st.text_input("** Altura que será instalado / distância do rack", key=f'ap_distancia_{ticket_id}')
    
    st.markdown("---")
    st.subheader("Ações")
    
    if st.button("✔️ Concluir e Arquivar Chamado", key=f"complete_{ticket_id}", type="primary"):
        current_ticket_data = {key.replace(f"_{ticket_id}", ""): value for key, value in st.session_state.items() if str(key).endswith(f"_{ticket_id}")}
        save_completed_ticket(ticket_id, current_ticket_data)
        st.session_state.active_ticket_id = None
        st.success(f"Chamado {ticket_id} arquivado com sucesso!")
        st.rerun()

    final_ticket_data = {key.replace(f"_{ticket_id}", ""): value for key, value in st.session_state.items() if str(key).endswith(f"_{ticket_id}")}
    
    st.markdown("Exportar Relatório:")
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1: st.download_button("Baixar .TXT", "\n".join(get_report_data(final_ticket_data)), f"Checklist_{ticket_id.upper()}.txt", "text/plain")
    with d_col2: st.download_button("Baixar .PDF", create_pdf_report(final_ticket_data), f"Checklist_{ticket_id.upper()}.pdf", "application/pdf")
    with d_col3: st.download_button("Baixar .DOCX", create_docx_report(final_ticket_data), f"Checklist_{ticket_id.upper()}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- Lógica Principal da Aplicação ---
load_css()

# Inicializa o estado da sessão
if 'active_ticket_id' not in st.session_state:
    st.session_state.active_ticket_id = None

st.title("Ferramenta de Checklist de Campo")

if st.session_state.active_ticket_id is None:
    st.header("Iniciar Novo Checklist")
    with st.form("new_ticket_form"):
        ticket_id_input = st.text_input("Insira o código do chamado:")
        submitted = st.form_submit_button("Iniciar Checklist")
        if submitted and ticket_id_input:
            formatted_id = ticket_id_input.strip().upper()
            if formatted_id.isdigit(): formatted_id = f"CLAR-{formatted_id}"
            elif not formatted_id.startswith("CLAR-"): formatted_id = f"CLAR-{formatted_id}"
            
            st.session_state.active_ticket_id = formatted_id
            for key in list(st.session_state.keys()):
                if key.endswith(f"_{formatted_id}"): del st.session_state[key]
            st.rerun()
else:
    ticket_id = st.session_state.active_ticket_id
    st.header(f"Preenchendo Chamado: {ticket_id}")
    if st.button("<< Iniciar outro chamado"):
        st.session_state.active_ticket_id = None
        st.rerun()
    display_checklist_form(ticket_id)
