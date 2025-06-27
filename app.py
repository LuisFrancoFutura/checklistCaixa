# --- INSTRUÇÕES DE INSTALAÇÃO ---
# Antes de rodar, instale as bibliotecas necessárias para exportar em PDF e Word:
# pip install streamlit python-docx reportlab

import streamlit as st
import datetime
import io
from docx import Document
from docx.shared import Inches
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.units import inch

# --- Configuração da Página ---
st.set_page_config(
    page_title="Checklist Help Desk",
    page_icon="📄",
    layout="wide",
)

# --- CSS para um Design Aprimorado ---
def load_css():
    """Carrega e injeta o CSS customizado para estilizar a aplicação."""
    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f0f2f6;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e6e6e6;
            padding: 15px;
        }
        
        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
             color: #004d99;
        }

        .stButton>button, .stDownloadButton>button {
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            border: none;
            color: white !important;
            transition: all 0.3s ease;
            width: 100%;
        }

        /* Cor do botão de Adicionar Chamado */
        .stButton>button {
            background-color: #0066cc;
        }
        .stButton>button:hover {
            background-color: #0052a3;
            transform: scale(1.02);
        }

        /* Estilo dos botões de download */
        .stDownloadButton>button {
            background-color: #5a6268;
        }
        .stDownloadButton>button:hover {
            background-color: #4a4f54;
            transform: scale(1.02);
        }

        .card {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            border: 1px solid #e6e6e6;
        }

        .card h3 {
            margin-top: 0;
            color: #004d99;
            border-bottom: 2px solid #e6e6e6;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        [data-testid="stTextInput"] input, 
        [data-testid="stNumberInput"] input {
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 10px;
        }
        [data-testid="stTextInput"] input:focus, 
        [data-testid="stNumberInput"] input:focus {
            border-color: #0066cc;
            box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.25);
        }

        [data-testid="stTabs"] button {
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 20px;
            color: #555;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            background-color: #ffffff;
            color: #0066cc;
            border-bottom: 2px solid #0066cc !important;
        }
        
        h1 {
            color: #004d99;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --- Funções de Geração de Relatório ---

def get_report_data(ticket_id):
    """Coleta os dados do formulário e retorna uma lista de strings formatadas."""
    agencia = st.session_state.get(f'agencia_{ticket_id}', '')
    cidade_uf = st.session_state.get(f'cidade_uf_{ticket_id}', '')
    endereco = st.session_state.get(f'endereco_{ticket_id}', '')
    num_racks = st.session_state.get(f'num_racks_{ticket_id}', 1)
    
    report_lines = [
        "===============================================",
        "           Check list Caixa Econômica",
        "===============================================",
        f"Chamado: {ticket_id.upper()}\n",
        "--- INFORMAÇÕES GERAIS DA AGÊNCIA ---",
        f"Agência: {agencia}",
        f"Cidade/UF: {cidade_uf}",
        f"Endereço: {endereco}",
        f"Quantidade de Racks na agência: {num_racks}\n",
    ]

    for i in range(1, num_racks + 1):
        report_lines.append(f"--- DETALHES DO RACK {i} ---")
        report_lines.append(f"Local instalado: {st.session_state.get(f'rack_local_{i}_{ticket_id}', '')}")
        report_lines.append(f"Tamanho do Rack (U's): {st.session_state.get(f'rack_tamanho_{i}_{ticket_id}', 0)}")
        report_lines.append(f"U's disponíveis: {st.session_state.get(f'rack_us_disponiveis_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Quantidade de réguas de energia: {st.session_state.get(f'rack_reguas_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Tomadas disponíveis: {st.session_state.get(f'rack_tomadas_disponiveis_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Disponibilidade para ampliação de réguas: {st.session_state.get(f'rack_ampliacao_reguas_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Rack está em bom estado: {st.session_state.get(f'rack_estado_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Rack está organizado: {st.session_state.get(f'rack_organizado_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Equipamentos e cabos identificados: {st.session_state.get(f'rack_identificado_{i}_{ticket_id}', 'Não')}\n")

    report_lines.append("--- INFORMAÇÕES SOBRE ACCESS POINT (AP) ---")
    report_lines.append(f"Quantidade de APs existentes: {st.session_state.get(f'ap_quantidade_{ticket_id}', 0)}")
    report_lines.append(f"Setor para instalação do novo AP: {st.session_state.get(f'ap_setor_{ticket_id}', '')}")
    report_lines.append(f"Condições da infraestrutura: {st.session_state.get(f'ap_condicoes_{ticket_id}', '')}")
    report_lines.append(f"Altura de instalação / Distância do rack: {st.session_state.get(f'ap_distancia_{ticket_id}', '')}\n")
    report_lines.append("===============================================")

    return report_lines

def create_pdf_report(ticket_id):
    """Gera um relatório em PDF em memória."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    
    # Estilo para o corpo do texto
    body_style = ParagraphStyle(name='Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14)
    # Estilo para títulos de seção
    header_style = ParagraphStyle(name='Header', parent=styles['h3'], fontName='Helvetica-Bold', fontSize=12, spaceAfter=6)

    story = []
    report_lines = get_report_data(ticket_id)

    # Adiciona as linhas ao PDF com formatação
    for line in report_lines:
        if line.startswith("---"):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph(line.replace("---", "").strip(), header_style))
        elif line.startswith("==="):
             story.append(Paragraph("________________________________________________", body_style))
        else:
            story.append(Paragraph(line, body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_docx_report(ticket_id):
    """Gera um relatório em Word (.docx) em memória."""
    document = Document()
    report_lines = get_report_data(ticket_id)

    # Adiciona as linhas ao documento Word
    for line in report_lines:
        if line.startswith("---"):
            document.add_heading(line.replace("---", "").strip(), level=2)
        elif line.startswith("===") or line.strip() == "":
            continue # Ignora separadores e linhas em branco para um docx mais limpo
        else:
            document.add_paragraph(line)
            
    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer

def display_checklist(ticket_id):
    """Renderiza os campos do formulário para um determinado chamado."""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Informações Gerais da Agência")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Agência", key=f'agencia_{ticket_id}')
        st.text_input("Endereço", key=f'endereco_{ticket_id}')
    with col2:
        st.text_input("Cidade/UF", key=f'cidade_uf_{ticket_id}')
        st.number_input("Quantidade de Racks na agência", min_value=1, step=1, key=f'num_racks_{ticket_id}')
    st.markdown('</div>', unsafe_allow_html=True)
    
    num_racks = st.session_state.get(f'num_racks_{ticket_id}', 1)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Detalhes dos Racks")
    for i in range(1, num_racks + 1):
        st.markdown(f"**Rack {i}**")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Local instalado", key=f'rack_local_{i}_{ticket_id}')
            st.number_input("Tamanho do Rack (Número de U's)", min_value=0, step=1, key=f'rack_tamanho_{i}_{ticket_id}')
            st.number_input("Quantidade de U's disponíveis", min_value=0, step=1, key=f'rack_us_disponiveis_{i}_{ticket_id}')
            st.number_input("Quantidade de réguas de energia", min_value=0, step=1, key=f'rack_reguas_{i}_{ticket_id}')
            st.number_input("Quantidade de tomadas disponíveis", min_value=0, step=1, key=f'rack_tomadas_disponiveis_{i}_{ticket_id}')
        with c2:
            st.radio("Disponibilidade para ampliação de réguas", ("Sim", "Não"), key=f'rack_ampliacao_reguas_{i}_{ticket_id}', horizontal=True)
            st.radio("Rack está em bom estado", ("Sim", "Não"), key=f'rack_estado_{i}_{ticket_id}', horizontal=True)
            st.radio("Rack está organizado", ("Sim", "Não"), key=f'rack_organizado_{i}_{ticket_id}', horizontal=True)
            st.radio("Equipamentos e cabos identificados", ("Sim", "Não"), key=f'rack_identificado_{i}_{ticket_id}', horizontal=True)
        if i < num_racks:
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Access Point (AP)")
    col1_ap, col2_ap = st.columns(2)
    with col1_ap:
        st.number_input("Verificar a quantidade de APs existentes", min_value=0, step=1, key=f'ap_quantidade_{ticket_id}')
        st.text_input("Identificar o setor onde será instalado*", help="Setor onde o novo AP ficará", key=f'ap_setor_{ticket_id}')
    with col2_ap:
        st.text_input("Verificar as condições da Instalação", help="Ex: Possui infra, não possui, precisa de canaleta, etc.", key=f'ap_condicoes_{ticket_id}')
        st.text_input("Altura / Distância do rack*", help="Ex: Teto 2.8m / 15m de distância do rack", key=f'ap_distancia_{ticket_id}')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Exportar Relatório")
    file_name_prefix = f"Checklist_{ticket_id.upper()}_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        st.download_button(
            label="Baixar .TXT",
            data="\n".join(get_report_data(ticket_id)),
            file_name=f"{file_name_prefix}.txt",
            mime="text/plain",
        )
    with d_col2:
        st.download_button(
            label="Baixar .PDF",
            data=create_pdf_report(ticket_id),
            file_name=f"{file_name_prefix}.pdf",
            mime="application/pdf",
        )
    with d_col3:
        st.download_button(
            label="Baixar .DOCX",
            data=create_docx_report(ticket_id),
            file_name=f"{file_name_prefix}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

# --- Início da Interface ---
load_css()

if 'tickets' not in st.session_state:
    st.session_state.tickets = {}

with st.sidebar:
    st.header("Gestor de Chamados")
    
    with st.form("new_ticket_form", clear_on_submit=True):
        new_ticket_id = st.text_input("Código do Chamado (ex: CLAR-123)", placeholder="CLAR-XXX").strip()
        submitted = st.form_submit_button("Adicionar Chamado")
        
        if submitted and new_ticket_id:
            if new_ticket_id not in st.session_state.tickets:
                st.session_state.tickets[new_ticket_id] = {}
                st.success(f"Chamado '{new_ticket_id}' adicionado!")
            else:
                st.warning(f"O chamado '{new_ticket_id}' já existe.")

    st.markdown("---")
    
    st.header("Checklist do Analista")
    st.info("Use esta lista para guiar o técnico em campo.")
    
    st.checkbox("FOTO GERAL DA SALA ONLINE (2 cantos)")
    st.checkbox("FOTOS DAS TOMADAS/RÉGUAS DO RACK")
    st.checkbox("FOTO COMPLETA DO RACK (base ao topo)")
    st.checkbox("VERIFICAR QUANTOS APs JÁ EXISTEM")
    with st.expander("Detalhes da Instalação de Novo AP"):
        st.checkbox("Verificar se já existe infraestrutura no local")
        st.checkbox("Alinhar ponto de instalação com o gerente (se necessário)")
        st.checkbox("Medir a altura do teto")
        st.checkbox("Verificar a distância até a sala online")

# --- Área Principal ---
st.title("Ferramenta de Checklist para Atividades de Campo")

if not st.session_state.tickets:
    st.info("Adicione um chamado na barra lateral para começar o preenchimento.")
else:
    ticket_ids = list(st.session_state.tickets.keys())
    tabs = st.tabs([f"Chamado: {tid.upper()}" for tid in ticket_ids])
    
    for i, tab in enumerate(tabs):
        with tab:
            current_ticket_id = ticket_ids[i]
            display_checklist(current_ticket_id)
