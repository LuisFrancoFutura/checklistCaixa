import streamlit as st
import datetime

# --- Configuração da Página ---
st.set_page_config(
    page_title="Checklist Help Desk",
    page_icon="📋",
    layout="wide",
)

# --- Funções Auxiliares ---

def get_report_string(ticket_id):
    """Gera uma string formatada com os dados do checklist para exportação."""
    data = st.session_state.tickets[ticket_id]
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Coleta de dados dos widgets usando as chaves de sessão
    # É importante buscar o valor atual da chave, caso o usuário tenha editado algo
    agencia = data.get(f'agencia_{ticket_id}', '')
    cidade_uf = data.get(f'cidade_uf_{ticket_id}', '')
    endereco = data.get(f'endereco_{ticket_id}', '')
    num_racks = data.get(f'num_racks_{ticket_id}', 1)
    
    report_lines = [
        "===============================================",
        f"  CHECKLIST DE ATIVIDADE - CHAMADO: {ticket_id.upper()}",
        "===============================================",
        f"Data de Geração: {now}\n",
        "--- INFORMAÇÕES GERAIS DA AGÊNCIA ---",
        f"Agência: {agencia}",
        f"Cidade/UF: {cidade_uf}",
        f"Endereço: {endereco}",
        f"Quantidade de Racks na agência: {num_racks}\n",
    ]

    # --- Seções dos Racks ---
    for i in range(1, num_racks + 1):
        report_lines.append(f"--- DETALHES DO RACK {i} ---")
        report_lines.append(f"Local instalado: {data.get(f'rack_local_{i}_{ticket_id}', '')}")
        report_lines.append(f"Tamanho do Rack (U's): {data.get(f'rack_tamanho_{i}_{ticket_id}', 0)}")
        report_lines.append(f"U's disponíveis: {data.get(f'rack_us_disponiveis_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Quantidade de réguas de energia: {data.get(f'rack_reguas_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Tomadas disponíveis: {data.get(f'rack_tomadas_disponiveis_{i}_{ticket_id}', 0)}")
        report_lines.append(f"Disponibilidade para ampliação de réguas: {data.get(f'rack_ampliacao_reguas_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Rack está em bom estado: {data.get(f'rack_estado_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Rack está organizado: {data.get(f'rack_organizado_{i}_{ticket_id}', 'Não')}")
        report_lines.append(f"Equipamentos e cabos identificados: {data.get(f'rack_identificado_{i}_{ticket_id}', 'Não')}\n")

    # --- Seção dos Access Points (AP) ---
    report_lines.append("--- INFORMAÇÕES SOBRE ACCESS POINT (AP) ---")
    report_lines.append(f"Quantidade de APs existentes: {data.get(f'ap_quantidade_{ticket_id}', 0)}")
    report_lines.append(f"Setor para instalação do novo AP: {data.get(f'ap_setor_{ticket_id}', '')}")
    report_lines.append(f"Condições da infraestrutura: {data.get(f'ap_condicoes_{ticket_id}', '')}")
    report_lines.append(f"Altura de instalação / Distância do rack: {data.get(f'ap_distancia_{ticket_id}', '')}\n")
    report_lines.append("===============================================")

    return "\n".join(report_lines)

def display_checklist(ticket_id):
    """Renderiza os campos do formulário para um determinado chamado."""
    
    data = st.session_state.tickets[ticket_id]

    with st.container(border=True):
        st.subheader("Informações Gerais da Agência")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Agência", key=f'agencia_{ticket_id}')
            st.text_input("Endereço", key=f'endereco_{ticket_id}')
        with col2:
            st.text_input("Cidade/UF", key=f'cidade_uf_{ticket_id}')
            st.number_input(
                "Quantidade de Racks na agência", 
                min_value=1, 
                step=1, 
                key=f'num_racks_{ticket_id}'
            )
    
    st.markdown("---")
    
    num_racks = st.session_state.get(f'num_racks_{ticket_id}', 1)
    
    # --- Seções dos Racks ---
    st.subheader("Detalhes dos Racks")
    for i in range(1, num_racks + 1):
        with st.container(border=True):
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

    st.markdown("---")

    # --- Seção de Access Points ---
    with st.container(border=True):
        st.subheader("Access Point (AP)")
        col1_ap, col2_ap = st.columns(2)
        with col1_ap:
            st.number_input("Verificar a quantidade de APs existentes", min_value=0, step=1, key=f'ap_quantidade_{ticket_id}')
            st.text_input("Identificar o setor onde será instalado*", help="Setor onde o novo AP ficará", key=f'ap_setor_{ticket_id}')
        with col2_ap:
            st.text_input("Verificar as condições da Instalação", help="Ex: Possui infra, não possui, precisa de canaleta, etc.", key=f'ap_condicoes_{ticket_id}')
            st.text_input("Altura / Distância do rack*", help="Ex: Teto 2.8m / 15m de distância do rack", key=f'ap_distancia_{ticket_id}')

    st.markdown("---")
    
    # --- Botão de Exportação ---
    report_data = get_report_string(ticket_id)
    file_name = f"Checklist_{ticket_id.upper()}_{datetime.datetime.now().strftime('%Y%m%d')}.txt"
    
    st.download_button(
        label="📥 Gerar e Baixar Relatório",
        data=report_data,
        file_name=file_name,
        mime="text/plain",
        use_container_width=True
    )

# --- Interface Principal ---

# Inicializa o estado da sessão para armazenar os chamados
if 'tickets' not in st.session_state:
    st.session_state.tickets = {}

# --- Barra Lateral (Sidebar) ---
with st.sidebar:
    st.header("Gestor de Chamados")
    
    with st.form("new_ticket_form", clear_on_submit=True):
        new_ticket_id = st.text_input("Código do Chamado (ex: CLAR-123)", placeholder="CLAR-XXX").strip()
        submitted = st.form_submit_button("➕ Adicionar Chamado")
        
        if submitted and new_ticket_id:
            if new_ticket_id not in st.session_state.tickets:
                st.session_state.tickets[new_ticket_id] = {}
                st.success(f"Chamado '{new_ticket_id}' adicionado!")
            else:
                st.warning(f"O chamado '{new_ticket_id}' já existe.")

    st.markdown("---")
    
    # --- Checklist do Analista ---
    st.header("✔️ Checklist do Analista")
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
st.title("📋 Ferramenta de Checklist para Atividades de Campo")
st.markdown("Adicione um chamado na barra lateral para começar o preenchimento.")

if not st.session_state.tickets:
    st.info("Nenhum chamado ativo. Adicione um novo chamado para iniciar.")
else:
    # Cria abas para cada chamado adicionado
    ticket_ids = list(st.session_state.tickets.keys())
    tabs = st.tabs(ticket_ids)
    
    for i, tab in enumerate(tabs):
        with tab:
            current_ticket_id = ticket_ids[i]
            st.header(f"Preenchendo Checklist para: {current_ticket_id.upper()}")
            display_checklist(current_ticket_id)

