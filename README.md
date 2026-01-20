# Process Mining Dashboard | BPI Challenge 2012

Questo progetto implementa una dashboard interattiva per l'analisi di processi finanziari (Process Mining) utilizzando il dataset **BPI Challenge 2012**.  
L'applicazione combina algoritmi tradizionali di process mining (PM4Py) con un modulo di intelligenza artificiale (Google Gemini) per fornire un *AI Analyst* in grado di ragionare sui dati.

---

## Struttura del Progetto

Descrizione dei file inclusi nella repository:

- **app.py**  
  Script principale dell'applicazione. Avvia la dashboard web basata su **Streamlit** e include:
  - preprocessing dei log,
  - visualizzazioni interattive,
  - integrazione con l’AI chatbot.

- **benchmark_totale.py**  
  Script standalone per l’esecuzione offline dei benchmark.  
  Calcola le metriche di valutazione (**Fitness**, **Precision**, **F1-Score**) sull’intero dataset (100% dei casi) per i tre algoritmi:
  - Alpha Miner  
  - Heuristic Miner  
  - Inductive Miner  

- **Documentation.docx**  
  Relazione tecnica completa del progetto.  
  Contiene:
  - analisi metodologica,
  - benchmark dettagliati,
  - scelte architetturali,
  - conclusioni.

- **BPI Challenge 2012_1_all.zip**  
  Dataset originale in formato compresso.  
  **Importante:** deve essere estratto prima dell’uso.

- **img1.png**  
  Asset grafico utilizzato nell’interfaccia della dashboard (logo/icona).

---

## Prerequisiti e Installazione

### 1. Python e Librerie

Assicurati di avere **Python 3.9 o superiore** installato.  
Installa le dipendenze necessarie con:

```bash
pip install streamlit pm4py pandas google-genai
2. Graphviz (Fondamentale)
PM4Py richiede Graphviz per generare i grafici delle Reti di Petri.

Scarica Graphviz dal sito ufficiale:
https://graphviz.org/download/

Aggiungi la cartella bin di Graphviz alle variabili d’ambiente (PATH) del sistema.

Nota:
Nel file app.py è presente un tentativo di aggiunta automatica del percorso
C:\Program Files\Graphviz\bin.
Se Graphviz è installato in un percorso diverso, modifica quella riga o configura manualmente il PATH.

Come Eseguire il Progetto
Passo 1: Estrazione del Dataset
Il file .xes è contenuto nell’archivio .zip.

Individua BPI Challenge 2012_1_all.zip.

Estrai tutto il contenuto nella cartella del progetto.

Otterrai un file BPI_Challenge_2012.xes (o nome simile).

Passo 2: Avvio della Dashboard
Apri il terminale nella cartella del progetto ed esegui:

bash
Copia codice
streamlit run app.py
Il browser si aprirà automaticamente.

Caricamento del dataset:
Puoi trascinare il file .xes nella sidebar.
Se il file si trova nel percorso predefinito, la dashboard potrebbe rilevarlo automaticamente.

Passo 3: Esecuzione del Benchmark (Opzionale)
Per ricalcolare le metriche su tutto il dataset (operazione lenta ma accurata):

Apri benchmark_totale.py.

Modifica la variabile FILE_PATH con il percorso corretto del file .xes.

Esegui lo script:

bash
Copia codice
python benchmark_totale.py
Lo script calcolerà Fitness, Precision e F1-Score per:

Alpha Miner

Heuristic Miner

Inductive Miner

Funzionalità AI
Il progetto utilizza le API di Google Gemini per fornire spiegazioni qualitative sul processo (AI Reasoning).

Nel file app.py è presente una chiave API a scopo dimostrativo.

In caso di errori di quota o scadenza, sostituisci la variabile GEMINI_API_KEY con una tua chiave, ottenibile da Google AI Studio.

Autore
Roberto Rotunno
Progetto per il corso di Metodi Formali / Process Mining.

Copia codice
