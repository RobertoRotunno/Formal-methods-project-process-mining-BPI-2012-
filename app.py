import streamlit as st
import pm4py
import pandas as pd
import os
import tempfile
import time
from google import genai 

# CONFIGURAZIONE PAGINA & CSS CUSTOM ---
st.set_page_config(
    page_title="BPI 2012 Analytics", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per l'interfaccia
st.markdown("""
<style>
    /* 1. Gestione Spazi Generali (Meno aggressiva di prima) */
    .block-container {
        padding-top: 3rem !important; /* Aumentato per leggere il titolo */
        padding-bottom: 1rem !important;
        padding-left: 3rem !important; /* Più aria ai lati */
        padding-right: 3rem !important;
    }
    
    .main { background-color: #f9f9f9; }
    
    /* 2. Titolo Dashboard */
    h3 {
        padding-top: 0px;
        margin-top: 0px !important;
    }

    /* 3. Card delle metriche (Stile pulito) */
    .stMetric {
        background-color: #ffffff;
        padding: 10px !important;
        border-radius: 8px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- SETUP BACKEND & AI ---
# Setup Graphviz
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# API KEY DI GEMINI
GEMINI_API_KEY = "AIzaSyCSAJiaVxvZT2nwPvqDETbv4XL7Dw53HDY"

def ask_gemini(query, context_data):
    """
    Interroga Google Gemini con il contesto del processo.
    """
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        Sei un esperto di Process Mining.
        Dati del processo: {context_data}
        Domanda utente: "{query}"
        
        Rispondi in Markdown, sii conciso e professionale.
        """
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt,
        )
        
        return response.text

    except Exception as e:
        # Fallback in caso di errore API o rete
        time.sleep(1) 
        return f"""
        ### ⚠️ Errore AI
        Non riesco a contattare Gemini.
        
        **Dettaglio Errore:** `{str(e)[:100]}...`
        """

# Importazioni PM4Py
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.objects.conversion.process_tree import converter as pt_converter

from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness
from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.filtering.log.variants import variants_filter

try:
    from pm4py.visualization.petri_net import visualizer as pn_visualizer
except ImportError:
    try:
        from pm4py.visualization.petrinet import visualizer as pn_visualizer
    except:
        pn_visualizer = None 

# --- CARICAMENTO DATI ---
@st.cache_data
def load_data_complete(path):
    """
    Carica l'intero dataset, pulisce le date e filtra solo i COMPLETE.
    Non applica ancora il campionamento (sampling) per permettere lo slider dinamico.
    """
    try:
        log = pm4py.read_xes(path)
        df = pm4py.convert_to_dataframe(log)
        
        # Preprocessing Base: Date
        if 'time:timestamp' in df.columns:
            df['time:timestamp'] = pd.to_datetime(df['time:timestamp'], utc=True)
        
        # Preprocessing Base: Tengo solo eventi COMPLETE per evitare grafici doppi
        if 'lifecycle:transition' in df.columns:
            df = df[df['lifecycle:transition'] == 'COMPLETE']
            
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento: {e}")
        return None

# --- SIDEBAR & LOGICA ---
with st.sidebar:
    st.image("img1.png", width=70)
    st.title("Control Panel")
    st.markdown("---")
    
    st.subheader("📂 1. Caricamento Dati")
    uploaded_file = st.file_uploader("Upload XES File", type=["xes", "xml"])
    
    default_path = r"C:\Users\robca\Desktop\progetto formal\BPI Challenge 2012_1_all\BPI_Challenge_2012.xes\BPI_Challenge_2012.xes"
    
    path_to_load = None
    if uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False); tfile.write(uploaded_file.read()); path_to_load = tfile.name
    elif os.path.exists(default_path):
        path_to_load = default_path
        st.caption("✅ File Default rilevato")
    
    st.markdown("---")
    st.subheader("⚙️ 2. Ottimizzazione")

# --- LOGICA PRINCIPALE ---
# Titolo compatto in una riga sola, allineato al centro o sinistra
st.markdown("""
    <h3 style='text-align: left; margin-bottom: 10px; color: #2c3e50;'>
        Process Mining Dashboard <span style='font-size: 0.6em; color: gray; font-weight: normal;'>| BPI Challenge 2012</span>
    </h3>
""", unsafe_allow_html=True)

if path_to_load:
    # 1. Caricamento FULL (una volta sola)
    with st.spinner('🔄 Lettura e pulizia iniziale del dataset...'):
        df_full = load_data_complete(path_to_load)

    if df_full is not None:
        # 2. Configurazione Slider Dinamico
        all_case_ids = df_full['case:concept:name'].unique()
        total_cases_real = len(all_case_ids)
        
        with st.sidebar:
            # Slider dinamico che va da 1 a Totale Casi Reali
            max_cases = st.slider(
                "Max Casi (Sampling)", 
                min_value=1, 
                max_value=total_cases_real, 
                value=min(50, total_cases_real)
            )
            
            filter_perc = st.slider("Filtro Varianti (Semplificazione)", 0.1, 1.0, 1.0)
            st.info(f"Totale Casi nel file: **{total_cases_real}**")
            st.info("Status: **Ready**")

        # Applicazione Filtri
        with st.spinner('✂️ Applicazione filtri...'):
            # A. Sampling (Taglio i casi)
            selected_cases = all_case_ids[:max_cases]
            df_filtered = df_full[df_full['case:concept:name'].isin(selected_cases)]
            
            # Converto in log per applicare filtri avanzati PM4PY
            event_log = pm4py.convert_to_event_log(df_filtered)
            
            # B. Filtro Varianti (Rimuovo percorsi rari)
            if filter_perc < 1.0:
                # CORREZIONE QUI SOTTO: Uso la funzione specifica importata
                event_log = variants_filter.filter_log_variants_percentage(event_log, percentage=filter_perc)
                
                # Aggiorno il dataframe per allinearlo al log filtrato
                df_filtered = pm4py.convert_to_dataframe(event_log)

        # --- A. KPI ROW (SPOSTATA NELLA SIDEBAR) ---
        # Calcolo variabili
        n_cases = len(event_log)
        n_events = len(df_filtered) 
        try:
            n_variants = len(pm4py.get_variants_as_tuples(event_log))
        except:
            n_variants = 0
            
        if 'time:timestamp' in df_filtered.columns and not df_filtered.empty:
            duration = (df_filtered['time:timestamp'].max() - df_filtered['time:timestamp'].min()).days
        else:
            duration = 0

        # VISUALIZZAZIONE NELLA SIDEBAR
        with st.sidebar:
            st.markdown("---")
            st.subheader("📊 Metriche Chiave")
            
            # Usiamo colonne piccole nella sidebar
            sk1, sk2 = st.columns(2)
            sk1.metric("Casi", n_cases, delta=f"/{total_cases_real}")
            sk2.metric("Eventi", n_events)
            
            sk3, sk4 = st.columns(2)
            sk3.metric("Varianti", n_variants)
            sk4.metric("Durata", f"{duration} gg")
            
            st.markdown("---")

        # --- B. TABS ---
        tab1, tab2, tab3 = st.tabs(["📊 Statistiche", "🕸️ Process Discovery", "💬 Chat AI"])

        # --- TAB 1: DATA OVERVIEW ---
        with tab1:
            st.subheader("Analisi delle Frequenze")
            if not df_filtered.empty:
                col_chart, col_raw = st.columns([2, 1])
                with col_chart:
                    # FIX ALTAIR: Creiamo un DF pulito senza ':' nei nomi colonne
                    counts = df_filtered['concept:name'].value_counts().head(10)
                    chart_df = pd.DataFrame({
                        "Attivita": counts.index,
                        "Conteggio": counts.values
                    }).set_index("Attivita")
                    
                    st.bar_chart(chart_df, color="#3498db")
                    
                with col_raw:
                    st.write("Anteprima Dati:")
                    st.dataframe(df_filtered[['case:concept:name', 'concept:name', 'time:timestamp']].head(100), height=300)
            else:
                st.warning("Nessun dato rimasto dopo i filtri.")

        # --- TAB 2: PROCESS MINING ---
        with tab2:
            st.subheader("Process Discovery & Evaluation")
            
            c1, c2 = st.columns([1, 3])
            with c1:
                algo = st.radio(
                    "Algoritmo:", 
                    ["Heuristic Miner", "Inductive Miner", "Alpha Miner"],
                    help="Scegli l'algoritmo per estrarre il modello."
                )
                generate_btn = st.button("🚀 Genera e Valuta Modello")
            
            with c2:
                if generate_btn:
                    if len(event_log) > 0:
                        status_box = st.empty() # Box per messaggi di stato
                        
                        try:
                            # GENERAZIONE MODELLO
                            status_box.info(f"⚙️ 1/4: Esecuzione {algo}...")
                            
                            # Variabili per il modello
                            net, im, fm = None, None, None
                            
                            if algo == "Alpha Miner":
                                net, im, fm = alpha_miner.apply(event_log)
                            elif algo == "Heuristic Miner":
                                net, im, fm = heuristics_miner.apply(event_log)
                            elif algo == "Inductive Miner":
                                tree = inductive_miner.apply(event_log)
                                net, im, fm = pt_converter.apply(tree)
                            
                            # 2. VISUALIZZAZIONE
                            status_box.info("🖼️ 2/4: Generazione Grafico...")
                            if net and pn_visualizer:
                                gviz = pn_visualizer.apply(net, im, fm)
                                
                                # Layout grafico centrato
                                gc1, gc2, gc3 = st.columns([1, 10, 1]) 
                                with gc2:
                                    st.graphviz_chart(gviz, use_container_width=True)
                            else:
                                st.error("Errore: Il modello generato è vuoto.")
                            
                            # 3. CALCOLO METRICHE (LOGICA ADATTIVA)
                            # Se è Inductive Miner, usiamo pochissimi casi (10) perché è pesantissimo.
                            # Per gli altri algoritmi ne usiamo un po' di più (50) per stabilità.
                            
                            if algo == "Inductive Miner":
                                LIMIT_METRICS = 10  # Drastico, per evitare blocchi
                            else:
                                LIMIT_METRICS = 50  # Standard per Alpha/Heuristic
                            
                            # Importiamo classi necessarie
                            from pm4py.objects.log.obj import EventLog
                            import random

                            if len(event_log) > LIMIT_METRICS:
                                # Campionamento casuale semplice e robusto
                                sampled_traces = random.sample(event_log, LIMIT_METRICS)
                                
                                # Creiamo un nuovo "mini log"
                                log_for_metrics = EventLog(sampled_traces, attributes=event_log.attributes, extensions=event_log.extensions)
                                
                                msg_metrics = f"⚡ Metriche stimate su un sottoinsieme di casi."
                            else:
                                log_for_metrics = event_log
                                msg_metrics = f"Metriche calcolate su tutti i {len(event_log)} casi."

                            status_box.info(f"📊 3/4: Calcolo metriche ({msg_metrics})...")
                            
                            # Variabili default
                            log_fitness = 0.0
                            precision = 0.0
                            f_score = 0.0

                            # --- A. FITNESS ---
                            try:
                                fitness_res = replay_fitness.apply(log_for_metrics, net, im, fm)
                                log_fitness = fitness_res['log_fitness']
                            except:
                                log_fitness = 0.0

                            # --- B. PRECISION ---
                            try:
                                # Inductive Miner soffre molto qui, ma con 10 casi dovrebbe farcela subito
                                precision_res = precision_evaluator.apply(log_for_metrics, net, im, fm)
                                precision = precision_res
                            except Exception as e:
                                print(f"Precision error: {e}")
                                precision = 0.0 
                            
                            # --- C. F1-SCORE ---
                            if log_fitness > 0 and precision > 0:
                                f_score = 2 * (log_fitness * precision) / (log_fitness + precision)
                            
                            # 4. VISUALIZZAZIONE
                            st.markdown("### 📈 Metriche di Valutazione")
                            st.markdown("---") 
                            
                            cols = st.columns([1, 1, 1, 3]) 
                            with cols[0]:
                                st.markdown(f"**Fitness:** `{log_fitness:.2%}`")
                            with cols[1]:
                                val_prec = f"{precision:.2%}" if precision > 0 else "N/A"
                                st.markdown(f"**Precision:** `{val_prec}`")
                            with cols[2]:
                                f1_display = f"{f_score:.2%}" if f_score > 0 else "N/A"
                                st.markdown(f"**F1-Score:** `{f1_display}`")
                            
                            st.caption(msg_metrics)
                            status_box.success("✅ Analisi Completata")

                        except Exception as e:
                            status_box.error(f"Errore Critico: {e}")
                            st.error(f"Dettaglio: {e}")
                    else:
                        st.error("Il dataset è vuoto.")

        # --- TAB 3: AI CHATBOT ---
        with tab3:
            st.subheader("🧠 Consulente AI Interattivo")
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            chat_container = st.container(height=500, border=True)

            with chat_container:
                if not st.session_state.messages:
                    st.info("👋 Ciao! Analizzo il dataset filtrato attuale. Fammi una domanda!")
                
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if prompt := st.chat_input("Chiedi un'analisi..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Ragionamento..."):
                            # COSTRUZIONE CONTESTO MIGLIORATA
                            try:
                                top_activities = df_filtered['concept:name'].value_counts().head(5).to_dict()
                                # Passiamo n_events calcolato sui dati filtrati (totale reale)
                                context_str = (
                                    f"Totale Eventi nel log filtrato: {n_events}. "
                                    f"Casi: {n_cases}. "
                                    f"Varianti: {n_variants}. "
                                    f"Attività più frequenti: {top_activities}. "
                                    f"Algoritmo usato (se applicabile): {algo}."
                                )
                            except:
                                context_str = "Dati parziali o vuoti."

                            response_text = ask_gemini(prompt, context_str)
                            st.markdown(response_text)
                
                st.session_state.messages.append({"role": "assistant", "content": response_text})

    else:
        st.error("Impossibile leggere il file.")
else:
    st.info("👆 Carica il file XES dalla barra laterale per iniziare.")