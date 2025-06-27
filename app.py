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
    page_icon="📄",
    layout="wide",
)

# --- Constante para o arquivo de histórico ---
COMPLETED_FILE = "completed_checklists.json"

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
        }
        
        /* Cor do Botão de Concluir */
        .stButton>button.button-complete {
            background-color: #28a745; /* Verde */
        }
        .stButton>button.button-complete:hover {
             background-color: #218838;
        }


        /* Estilo dos botões de download */
        .stDownloadButton>button {
            background-color: #5a6268;
        }
        .stDownloadButton>button:hover {
            background-color: #4a4f54;
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

# --- Funções de Persistência ---
def load_completed_tickets():
    """Carrega os chamados concluídos do arquivo JSON."""
    if not os.path.exists(COMPLETED_FILE):
        return {}
    with open(COMPLETED_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_completed_ticket(ticket_id, data):
    """Salva um único chamado concluído no arquivo JSON."""
    all_completed = load_completed_tickets()
    all_completed[ticket_id] = data
    with open(COMPLETED_FILE, 'w') as f:
        json.dump(all_completed, f, indent=4)


# --- Funções de Geração de Relatório ---

def get_report_data(ticket_data):
    """Coleta os dados do dicionário do chamado e retorna uma lista de strings formatadas."""
    agencia = ticket_data.get('agencia', '')
    cidade_uf = ticket_data.get('cidade_uf', '')
    endereco = ticket_data.get('endereco', '')
    num_racks = ticket_data.get('num_racks', 1)
    
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

def display_analyst_checklist(ticket_id, data_source, is_disabled=False):
    """Renderiza o checklist do analista, lendo/escrevendo de uma fonte de dados específica."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("CHECKLIST DE VERIFICAÇÃO NO LOCAL")
    
    def get_key(base_key):
        return f"{base_key}_{ticket_id}"

    st.markdown("##### - FOTO GERAL DA SALA ONLINE")
    st.checkbox("Tirar duas fotos pegando os dois cantos da sala.", key=get_key("analyst_chk_1"), value=data_source.get(get_key("analyst_chk_1"), False), disabled=is_disabled)

    st.markdown("##### - FOTOS DAS TOMADAS/RÉGUAS DO RACK")
    st.checkbox("Quantas tomadas estão livres.", key=get_key("analyst_chk_2"), value=data_source.get(get_key("analyst_chk_2"), False), disabled=is_disabled)
    st.checkbox("Verificar se há possibilidade de adicionar mais tomadas, se necessário.", key=get_key("analyst_chk_3"), value=data_source.get(get_key("analyst_chk_3"), False), disabled=is_disabled)

    st.markdown("##### - FOTO DO RACK")
    st.checkbox("Foto completa do rack (da base até o topo).", key=get_key("analyst_chk_4"), value=data_source.get(get_key("analyst_chk_4"), False), disabled=is_disabled)
    st.checkbox("Quantos U’s estão livres.", key=get_key("analyst_chk_5"), value=data_source.get(get_key("analyst_chk_5"), False), disabled=is_disabled)
    st.checkbox("Quantos U’s no total (tamanho do rack).", key=get_key("analyst_chk_6"), value=data_source.get(get_key("analyst_chk_6"), False), disabled=is_disabled)
    st.checkbox("Verificar se os cabos e equipamentos estão identificados.", key=get_key("analyst_chk_7"), value=data_source.get(get_key("analyst_chk_7"), False), disabled=is_disabled)

    st.markdown("##### - VERIFICAR QUANTOS APs JÁ EXISTEM")
    st.checkbox("Tirar fotos amplas mostrando onde os APs estão instalados.", key=get_key("analyst_chk_8"), value=data_source.get(get_key("analyst_chk_8"), False), disabled=is_disabled)

    st.markdown("##### - VERIFICAR INSTALAÇÃO DE NOVO AP")
    st.checkbox("Verificar se já existe infraestrutura no local.", key=get_key("analyst_chk_9"), value=data_source.get(get_key("analyst_chk_9"), False), disabled=is_disabled)
    st.checkbox(">>> Caso NÃO exista, alinhar com o gerente o ponto de instalação.", key=get_key("analyst_chk_10"), value=data_source.get(get_key("analyst_chk_10"), False), disabled=is_disabled)
    st.checkbox("Medir a altura do teto.", key=get_key("analyst_chk_11"), value=data_source.get(get_key("analyst_chk_11"), False), disabled=is_disabled)
    st.checkbox("Verificar a distância até a sala online (caso não tenha infraestrutura).", key=get_key("analyst_chk_12"), value=data_source.get(get_key("analyst_chk_12"), False), disabled=is_disabled)
    st.markdown('</div>', unsafe_allow_html=True)


def display_checklist(ticket_id, data_source, is_disabled=False):
    """Renderiza os campos do formulário para um determinado chamado."""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Informações Gerais da Agência")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Agência", key=f'agencia_{ticket_id}', value=data_source.get('agencia', ''), disabled=is_disabled)
        st.text_input("Endereço", key=f'endereco_{ticket_id}', value=data_source.get('endereco', ''), disabled=is_disabled)
    with col2:
        st.text_input("Cidade/UF", key=f'cidade_uf_{ticket_id}', value=data_source.get('cidade_uf', ''), disabled=is_disabled)
        st.number_input("Quantidade de Racks na agência", min_value=1, step=1, key=f'num_racks_{ticket_id}', value=data_source.get('num_racks', 1), disabled=is_disabled)
    st.markdown('</div>', unsafe_allow_html=True)
    
    num_racks = data_source.get(f'num_racks', 1) if is_disabled else st.session_state.get(f'num_racks_{ticket_id}', 1)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Detalhes dos Racks")
    for i in range(1, num_racks + 1):
        st.markdown(f"**Rack {i}**")
        c1, c2 = st.columns(2)
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
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Access Point (AP)")
    st.text_input("Verificar a quantidade de APs", key=f'ap_quantidade_{ticket_id}', value=data_source.get('ap_quantidade', ''), disabled=is_disabled)
    st.text_input("Identificar o setor onde será instalado*", help="Setor onde o novo AP ficará", key=f'ap_setor_{ticket_id}', value=data_source.get('ap_setor', ''), disabled=is_disabled)
    st.text_input("Verificar as condições da Instalação (se possui infra ou não)", help="Ex: Possui infra, não possui, precisa de canaleta, etc.", key=f'ap_condicoes_{ticket_id}', value=data_source.get('ap_condicoes', ''), disabled=is_disabled)
    st.text_input("** Altura que será instalado / distância do rack até o ponto de instalação", help="Ex: Teto 2.8m / 15m de distância do rack", key=f'ap_distancia_{ticket_id}', value=data_source.get('ap_distancia', ''), disabled=is_disabled)
    st.markdown('</div>', unsafe_allow_html=True)
    
    display_analyst_checklist(ticket_id, data_source, is_disabled)
    
    st.markdown("---")
    
    # --- Seção de Ações (Concluir ou Exportar) ---
    if not is_disabled:
        st.markdown("""<style>.button-complete {background-color: #28a745 !important;}</style>""", unsafe_allow_html=True)
        if st.button("Concluir e Arquivar Chamado", key=f"complete_{ticket_id}", type="primary"):
            # Coleta todos os dados do formulário para o chamado atual
            current_ticket_data = {key.replace(f"_{ticket_id}", ""): value for key, value in st.session_state.items() if key.endswith(f"_{ticket_id}")}
            save_completed_ticket(ticket_id, current_ticket_data)
            del st.session_state.tickets[ticket_id]
            st.success(f"Chamado {ticket_id} arquivado com sucesso!")
            st.rerun()

    st.subheader("Exportar Relatório")
    file_name_prefix = f"Checklist_{ticket_id.upper()}_{datetime.datetime.now().strftime('%Y%m%d')}"
    
    final_ticket_data = data_source if is_disabled else {key.replace(f"_{ticket_id}", ""): value for key, value in st.session_state.items() if key.endswith(f"_{ticket_id}")}
    
    txt_data = "\n".join([line.replace("TITLE:", "").replace("SUBTITLE:", "").strip() for line in get_report_data(final_ticket_data)])
    pdf_data = create_pdf_report(final_ticket_data)
    docx_data = create_docx_report(final_ticket_data)

    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        st.download_button(label="Baixar .TXT", data=txt_data, file_name=f"{file_name_prefix}.txt", mime="text/plain")
    with d_col2:
        st.download_button(label="Baixar .PDF", data=pdf_data, file_name=f"{file_name_prefix}.pdf", mime="application/pdf")
    with d_col3:
        st.download_button(label="Baixar .DOCX", data=docx_data, file_name=f"{file_name_prefix}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- Início da Interface ---
load_css()

# Inicializa o estado da sessão para chamados ativos
if 'tickets' not in st.session_state:
    st.session_state.tickets = {}

with st.sidebar:
    st.header("Gestor de Chamados")
    
    mode = st.radio("Modo de Operação", ["Preenchimento", "Revisão"], key="mode")
    
    if st.session_state.mode == "Preenchimento":
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
    
    elif st.session_state.mode == "Revisão":
        completed_tickets = load_completed_tickets()
        if not completed_tickets:
            st.info("Nenhum chamado concluído para revisar.")
        else:
            ticket_to_review = st.selectbox("Selecione um chamado para revisar", options=list(completed_tickets.keys()))
            st.session_state.review_ticket_id = ticket_to_review
            st.session_state.review_ticket_data = completed_tickets[ticket_to_review]


# --- Área Principal ---
st.title("Ferramenta de Checklist para Atividades de Campo")

if st.session_state.mode == "Preenchimento":
    if not st.session_state.tickets:
        st.info("Adicione um chamado na barra lateral para começar o preenchimento.")
    else:
        active_tickets = list(st.session_state.tickets.keys())
        tabs = st.tabs([f"Chamado: {tid.upper()}" for tid in active_tickets])
        for i, tab in enumerate(tabs):
            with tab:
                current_ticket_id = active_tickets[i]
                # Para preenchimento, a fonte de dados é o próprio st.session_state
                display_checklist(current_ticket_id, st.session_state, is_disabled=False)

elif st.session_state.mode == "Revisão":
    if 'review_ticket_id' in st.session_state and st.session_state.review_ticket_id:
        st.header(f"Revisando Chamado Concluído: {st.session_state.review_ticket_id.upper()}")
        # Para revisão, a fonte de dados é o dicionário do chamado concluído
        display_checklist(st.session_state.review_ticket_id, st.session_state.review_ticket_data, is_disabled=True)
    else:
        st.info("Selecione um chamado na barra lateral para iniciar a revisão.")
