# Process Mining Dashboard | BPI Challenge 2012

Questo progetto implementa una dashboard interattiva per l'analisi di processi finanziari (Process Mining) utilizzando il dataset **BPI Challenge 2012**.  
L'applicazione combina algoritmi tradizionali di process mining (PM4Py) con un modulo di intelligenza artificiale (Google Gemini) per fornire un AI Analyst in grado di ragionare sui dati.

---

## Struttura del Progetto

Descrizione dei file inclusi nella repository:

- **app.py**  
  Script principale dell'applicazione. Avvia la dashboard web basata su Streamlit e include:
  - preprocessing dei log
  - visualizzazioni interattive
  - integrazione con l’AI chatbot

- **benchmark_totale.py**  
  Script standalone per l’esecuzione offline dei benchmark.  
  Calcola le metriche di valutazione (Fitness, Precision, F1-Score) sull’intero dataset (100% dei casi) per:
  - Alpha Miner
  - Heuristic Miner
  - Inductive Miner

- **Documentation.docx**  
  Relazione tecnica completa del progetto con analisi metodologica, benchmark e conclusioni.

- **BPI Challenge 2012_1_all.zip**  
  Dataset originale in formato compresso.  
  IMPORTANTE: deve essere estratto prima dell’uso.

- **img1.png**  
  Asset grafico utilizzato nell’interfaccia della dashboard.

---

## Prerequisiti e Installazione

### 1. Python e Librerie

È necessario Python 3.9 o superiore.

Comando di installazione delle dipendenze:

pip install streamlit pm4py pandas google-genai

---

### 2. Graphviz (Fondamentale)

PM4Py richiede Graphviz per generare i grafici delle Reti di Petri.

Passaggi:

1. Scaricare Graphviz dal sito ufficiale:  
   https://graphviz.org/download/

2. Installare Graphviz sul sistema.

3. Aggiungere la cartella bin di Graphviz alle variabili d’ambiente (PATH).

Percorso tipico su Windows:

C:\Program Files\Graphviz\bin

Nota:  
Nel file app.py è presente un tentativo di aggiunta automatica di questo percorso.  
Se Graphviz è installato in una directory diversa, è necessario modificare il percorso nel codice oppure configurare manualmente il PATH di sistema.

---

## Come Eseguire il Progetto

### Passo 1: Estrazione del Dataset

1. Individuare il file BPI Challenge 2012_1_all.zip.
2. Estrarre tutto il contenuto nella cartella del progetto.
3. Ottenere il file BPI_Challenge_2012.xes (o nome simile).

---

### Passo 2: Avvio della Dashboard

Aprire il terminale nella cartella del progetto ed eseguire:

streamlit run app.py

Il browser si aprirà automaticamente.

Il file .xes può essere:
- caricato manualmente dalla sidebar
- rilevato automaticamente se presente nel percorso predefinito

---

### Passo 3: Esecuzione del Benchmark (Opzionale)

Per ricalcolare le metriche su tutto il dataset:

1. Aprire benchmark_totale.py
2. Modificare la variabile FILE_PATH con il percorso corretto del file .xes
3. Eseguire lo script:

python benchmark_totale.py

Verranno calcolati Fitness, Precision e F1-Score per tutti gli algoritmi.

---

## Funzionalità AI

Il progetto utilizza le API di Google Gemini per fornire spiegazioni qualitative sul processo (AI Reasoning).

Nel file app.py è presente una chiave API dimostrativa.  
In caso di errori di quota o scadenza, è possibile sostituire la variabile GEMINI_API_KEY con una chiave personale ottenibile da Google AI Studio.

---

## Autore

Roberto Rotunno  
Progetto per il corso di Metodi Formali / Process Mining
