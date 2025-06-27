# --- INSTRUÇÕES DE INSTALAÇÃO ---
# Antes de rodar, instale as bibliotecas necessárias para exportar em PDF e Word:
# pip install streamlit python-docx reportlab

import streamlit as st
import datetime
import io
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
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            border-radius: 8px;
            border: 1px solid #ccc;
            padding: 10px;
        }
        [data-testid="stTextInput"] input:focus, 
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {
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
    """Coleta os dados do formulário e retorna uma lista de strings formatadas no layout solicitado."""
    agencia = st.session_state.get(f'agencia_{ticket_id}', '')
    cidade_uf = st.session_state.get(f'cidade_uf_{ticket_id}', '')
    endereco = st.session_state.get(f'endereco_{ticket_id}', '')
    num_racks = st.session_state.get(f'num_racks_{ticket_id}', 1)
    
    # Usa marcadores especiais (ex: TITLE:) para ajudar na formatação dos arquivos PDF e DOCX
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
        report_lines.append(f"Local instalado: {st.session_state.get(f'rack_local_{i}_{ticket_id}', '')}")
        report_lines.append(f"Tamanho do Rack {i} – Número de Us: {st.session_state.get(f'rack_tamanho_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Quantidade de Us disponíveis: {st.session_state.get(f'rack_us_disponiveis_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Quantidade de réguas de energia: {st.session_state.get(f'rack_reguas_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Quantidade de tomadas disponíveis: {st.session_state.get(f'rack_tomadas_disponiveis_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Disponibilidade para ampliação de réguas de energia: {st.session_state.get(f'rack_ampliacao_reguas_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Rack está em bom estado: {st.session_state.get(f'rack_estado_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Rack está organizado: {st.session_state.get(f'rack_organizado_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Equipamentos e cabeamentos identificados: {st.session_state.get(f'rack_identificado_{i}_{ticket_id}', 'Não')}")
        report_lines.append("")

    report_lines.append("SUBTITLE: Access Point (AP)")
    report_lines.append("")
    report_lines.append(f"Verificar a quantidade de APs: {st.session_state.get(f'ap_quantidade_{ticket_id}', 0)}")
    report_lines.append(f"Identificar o setor onde será instalado*: {st.session_state.get(f'ap_setor_{ticket_id}', '')}")
    report_lines.append(f"Verificar as condições da Instalação (se possui infra ou não): {st.session_state.get(f'ap_condicoes_{ticket_id}', '')}")
    report_lines.append(f"** Altura que será instalado / distância do rack até o ponto de instalação: {st.session_state.get(f'ap_distancia_{ticket_id}', '')}")
    
    return report_lines

def create_pdf_report(ticket_id):
    """Gera um relatório em PDF em memória com o novo layout."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    
    # Estilos customizados para o novo layout
    title_style = ParagraphStyle(name='Title', parent=styles['h1'], fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle(name='Subtitle', parent=styles['h2'], fontName='Helvetica-Bold', fontSize=12, alignment=TA_LEFT, spaceAfter=10)
    body_style = ParagraphStyle(name='Body', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, spaceAfter=4)

    story = []
    report_lines = get_report_data(ticket_id)

    # Adiciona as linhas ao PDF com formatação baseada nos marcadores
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

def create_docx_report(ticket_id):
    """Gera um relatório em Word (.docx) em memória com o novo layout."""
    document = Document()
    report_lines = get_report_data(ticket_id)

    # Adiciona as linhas ao documento Word com formatação baseada nos marcadores
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
            st.text_input(f"Local instalado", key=f'rack_local_{i}_{ticket_id}')
            st.number_input(f"Tamanho do Rack {i} – Número de Us", min_value=0, step=1, key=f'rack_tamanho_{i}_{ticket_id}')
            st.number_input(f"Quantidade de Us disponíveis", min_value=0, step=1, key=f'rack_us_disponiveis_{i}_{ticket_id}')
            st.number_input(f"Quantidade de réguas de energia", min_value=0, step=1, key=f'rack_reguas_{i}_{ticket_id}')
            st.number_input(f"Quantidade de tomadas disponíveis", min_value=0, step=1, key=f'rack_tomadas_disponiveis_{i}_{ticket_id}')
        with c2:
            st.radio("Disponibilidade para ampliação de réguas de energia", ("Sim", "Não"), key=f'rack_ampliacao_reguas_{i}_{ticket_id}', horizontal=True)
            st.radio("Rack está em bom estado", ("Sim", "Não"), key=f'rack_estado_{i}_{ticket_id}', horizontal=True)
            st.radio("Rack está organizado", ("Sim", "Não"), key=f'rack_organizado_{i}_{ticket_id}', horizontal=True)
            st.radio("Equipamentos e cabeamentos identificados", ("Sim", "Não"), key=f'rack_identificado_{i}_{ticket_id}', horizontal=True)
        if i < num_racks:
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Access Point (AP)")
    st.text_input("Verificar a quantidade de APs", key=f'ap_quantidade_{ticket_id}')
    st.text_input("Identificar o setor onde será instalado*", help="Setor onde o novo AP ficará", key=f'ap_setor_{ticket_id}')
    st.text_input("Verificar as condições da Instalação (se possui infra ou não)", help="Ex: Possui infra, não possui, precisa de canaleta, etc.", key=f'ap_condicoes_{ticket_id}')
    st.text_input("** Altura que será instalado / distância do rack até o ponto de instalação", help="Ex: Teto 2.8m / 15m de distância do rack", key=f'ap_distancia_{ticket_id}')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("Exportar Relatório")
    file_name_prefix = f"Checklist_{ticket_id.upper()}_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    # Prepara os dados do TXT removendo os marcadores de formatação
    txt_data = "\n".join([line.replace("TITLE:", "").replace("SUBTITLE:", "").strip() for line in get_report_data(ticket_id)])

    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        st.download_button(
            label="Baixar .TXT",
            data=txt_data,
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
        new_tickets_input = st.text_area("Códigos dos Chamados (um por linha)", placeholder="CLAR-411\nCLAR-379\nCLAR-354").strip()
        submitted = st.form_submit_button("Adicionar Chamados")
        
        if submitted and new_tickets_input:
            ticket_ids = [tid.strip() for tid in new_tickets_input.split('\n') if tid.strip()]
            added_count = 0
            for ticket_id in ticket_ids:
                if ticket_id not in st.session_state.tickets:
                    st.session_state.tickets[ticket_id] = {}
                    added_count += 1
            if added_count > 0:
                st.success(f"{added_count} chamado(s) adicionado(s)!")


    st.markdown("---")
    
    st.header("CHECKLIST DE VERIFICAÇÃO NO LOCAL")
    
    st.markdown("##### - FOTO GERAL DA SALA ONLINE")
    st.checkbox("Tirar duas fotos pegando os dois cantos da sala.", key="analyst_chk_1")

    st.markdown("##### - FOTOS DAS TOMADAS/RÉGUAS DO RACK")
    st.checkbox("Quantas tomadas estão livres.", key="analyst_chk_2")
    st.checkbox("Verificar se há possibilidade de adicionar mais tomadas, se necessário.", key="analyst_chk_3")

    st.markdown("##### - FOTO DO RACK")
    st.checkbox("Foto completa do rack (da base até o topo).", key="analyst_chk_4")
    st.checkbox("Quantos U’s estão livres.", key="analyst_chk_5")
    st.checkbox("Quantos U’s no total (tamanho do rack).", key="analyst_chk_6")
    st.checkbox("Verificar se os cabos e equipamentos estão identificados.", key="analyst_chk_7")

    st.markdown("##### - VERIFICAR QUANTOS APs JÁ EXISTEM")
    st.checkbox("Tirar fotos amplas mostrando onde os APs estão instalados.", key="analyst_chk_8")

    st.markdown("##### - VERIFICAR INSTALAÇÃO DE NOVO AP")
    st.checkbox("Verificar se já existe infraestrutura no local.", key="analyst_chk_9")
    st.checkbox(">>> Caso NÃO exista, alinhar com o gerente o ponto de instalação.", key="analyst_chk_10")
    st.checkbox("Medir a altura do teto.", key="analyst_chk_11")
    st.checkbox("Verificar a distância até a sala online (caso não tenha infraestrutura).", key="analyst_chk_12")


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
