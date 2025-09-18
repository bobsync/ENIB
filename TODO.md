# ✅ TODO

## 🚀 Features
- [X] Far guardare Audrey nella stessa direzione dell'utente fin dall'inizio
- [X] Aggiungere una parola di chiusura all’interazione, ad esempio “Goodbye”
- [X] Aggiungere build del progetto Unity per lanciarlo direttamente da GUI
- [X] Non far partire Audrey a parlare [ice] quando ho già iniziato a parlare
- [ ] personalizzazione prompt per farla parlare di meno
- [ ] turnaround per API qualtrics :<

## 🐞 Bugs
- [ ] Whisper impiega troppo tempo a caricarsi, quindi il messaggio iniziale non viene riprodotto (???)
- [X] Le frasi troncate rimangono in coda e vengono inviate dopo la risposta alla prima metà
- [X] I gazeshift sono troppo strani, vanno spostati gli oggetti da guardare in unity e deve guardare per meno tempo.
- [X] In decider tutti i timer devono partire solamente dopo che sono partiti tutti i moduli.
- [X] Audrey deve spostare lo sguardo solamente quando non sta parlando.
- [X] Se Audrey sta già parlando non deve ovviamente partire un icebreaker
- [X] Tempo di Inattività troppo basso per far partire Icebreaker, aspetterei almeno una 25/30ina di secondi

## 🧹 Code Cleanup / Refactor
- [ ] Automatizzare la creazione della whiteboard localmente invece di caricarla su GitHub
- [ ] Controllare se alcune librerie sono inutilizzate
- [ ] Eliminare codice e dipendenze ridondanti
- [ ] Warning messages tensorflow, mediapipe absl::InitializeLog

## 📈 Improvements
- [X] L’agente dovrebbe distogliere lo sguardo ogni tanto, per maggiore realismo
- [X] Rimuovere l'azione “welldone”
- [X] Aumentare la frequenza di “handup”, “handdown”, “me” in base alla lunghezza della frase
- [X] Se la risposta contiene più frasi, variare la postura una volta per frase, proporzionalmente
- [X] Icebreakers 3 versioni e deve richiedere la stessa domanda con parole diverse
- [X] Mettere solo GazeDetection e non deve fare domande se l'utente sta guardando in basso

## 📝 Notes
- [ ] EatingDetection / ActionRecognition da migliorare per riconoscere con più precisione le azioni
