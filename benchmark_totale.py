import pm4py
import pandas as pd
import time
from pm4py.objects.conversion.process_tree import converter as pt_converter

# --- CONFIGURAZIONE ---
FILE_PATH = r"C:\Users\robca\Desktop\progetto formal\BPI Challenge 2012_1_all\BPI_Challenge_2012.xes\BPI_Challenge_2012.xes"

def main():
    print("="*60)
    print("🏆 BENCHMARK TOTALE: ALPHA vs HEURISTIC vs INDUCTIVE")
    print("="*60)

    # 1. CARICAMENTO DATI (Una volta per tutte)
    print(f"📂 Caricamento dataset e pulizia...")
    try:
        log = pm4py.read_xes(FILE_PATH)
        df = pm4py.convert_to_dataframe(log)
        
        # Filtro COMPLETE
        if 'lifecycle:transition' in df.columns:
            df = df[df['lifecycle:transition'] == 'COMPLETE']
        
        event_log = pm4py.convert_to_event_log(df)
        print(f"✅ Dati pronti: {len(event_log)} casi totali.")
        
    except Exception as e:
        print(f"❌ Errore caricamento: {e}")
        return

    # Lista degli algoritmi da testare
    algorithms = ["Alpha Miner", "Heuristic Miner", "Inductive Miner"]
    
    # Dizionario per salvare i risultati finali
    final_results = []

    # 2. CICLO SUGLI ALGORITMI
    for algo in algorithms:
        print("\n" + "-"*60)
        print(f"🚀 ESECUZIONE: {algo.upper()}...")
        print("-" * 60)
        
        net, im, fm = None, None, None
        start_algo = time.time()
        
        try:
            # --- DISCOVERY ---
            print(f"   ⛏️  Generazione modello...", end=" ")
            if algo == "Alpha Miner":
                net, im, fm = pm4py.discover_petri_net_alpha(event_log)
            elif algo == "Heuristic Miner":
                net, im, fm = pm4py.discover_petri_net_heuristics(event_log)
            elif algo == "Inductive Miner":
                tree = pm4py.discover_process_tree_inductive(event_log)
                net, im, fm = pt_converter.apply(tree)
            print("Fatto.")

            # --- METRICHE ---
            print(f"   📊 Calcolo Fitness...", end=" ")
            # Fitness
            fit_res = pm4py.fitness_token_based_replay(event_log, net, im, fm)
            fitness = fit_res['log_fitness']
            print(f"Done ({fitness:.2%})")

            print(f"   ⏳ Calcolo Precision (Lento)...", end=" ")
            # Precision
            try:
                prec_res = pm4py.precision_token_based_replay(event_log, net, im, fm)
                precision = prec_res
                print(f"Done ({precision:.2%})")
            except Exception as e:
                print(f"Errore: {e}")
                precision = 0.0

            # F1 Score
            if fitness > 0 and precision > 0:
                f1 = 2 * (fitness * precision) / (fitness + precision)
            else:
                f1 = 0.0

            # Salviamo i dati
            elapsed = time.time() - start_algo
            final_results.append({
                "Algoritmo": algo,
                "Fitness": fitness,
                "Precision": precision,
                "F1-Score": f1,
                "Tempo (s)": round(elapsed, 2)
            })

        except Exception as e:
            print(f"\n❌ ERRORE CRITICO su {algo}: {e}")
            final_results.append({
                "Algoritmo": algo,
                "Fitness": 0, "Precision": 0, "F1-Score": 0, "Tempo (s)": 0
            })

    # 3. TABELLA RIASSUNTIVA FINALE
    print("\n\n")
    print("="*75)
    print(f"{'ALGORITMO':<20} | {'FITNESS':<10} | {'PRECISION':<10} | {'F1-SCORE':<10} | {'TEMPO'}")
    print("="*75)
    
    for res in final_results:
        print(f"{res['Algoritmo']:<20} | {res['Fitness']:.2%}     | {res['Precision']:.2%}     | {res['F1-Score']:.2%}     | {res['Tempo (s)']}s")
    
    print("="*75)
    print("✅ Report generato con successo. Copia questi valori nelle slide.")
    input("Premi INVIO per uscire...")

if __name__ == "__main__":
    main()