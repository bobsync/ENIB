# 🎙️ Audrey – A Multimodal Conversational Agent

_Audrey is a Python-based embodied conversational agent (ECA) that enables rich real-time interaction through voice, gestures, and facial expressions._

<!-- ![Audrey Demo](docs/demo.gif) <!-- Replace with actual image or gif of the interface -->

---

## ✨ Key Features

- 🎤 **Real-Time Speech Recognition**  
  Powered by [FasterWhisper](https://github.com/guillaumekln/faster-whisper) for fast and accurate speech-to-text conversion.

- 🤖 **LLM-Powered Dialogue System**  
  Integrates with OpenAI, Groq, or local large language models to provide intelligent responses.

- 🙋‍♀️ **Gesture and Facial Expression Generation**  
  Uses BML (Behavior Markup Language) to animate gestures and facial expressions, adding realism to conversations.

- 🧩 **Modular GUI Launcher**  
  A customizable and user-friendly interface to manage all components easily.

- 🔌 **UDP-Based Modular Communication**  
  Lightweight UDP protocol ensures smooth communication between decoupled modules.

- 🔧 **Plug-and-Play Architecture**  
  Easily extend Audrey with your own modules thanks to its flexible plugin-based design.

---

## 📦 Installation

Clone the repository:
```bash
git clone https://github.com/bobsync/ENIB.git
cd audrey-ECA
```

---

## 🎮 Unity Project (Required)

A Unity project is required to run the 3D avatar interface. Download it from the link below:

- 🔗 [Download from Google Drive](https://drive.google.com/uc?export=download&id=19jHt5FK66PhmNEqUYv8_euIYvddV4THG)

Unzip the project and open it with **Unity 2021.3.9f1 LTS**.

---

## 📌 Prerequisites

To use `webrtcvad`, you need to install the [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

---

## ⚙️ Environment Setup (Windows – PowerShell)

Run the setup script to configure everything automatically:

### 1. Enable script execution:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 2. Run the setup script:
```powershell
.\setup.ps1
```
This script will:
- Create a virtual environment  
- Set necessary environment variables  
- Install all required Python packages  

### 3. Verify environment variables:
```powershell
.\check.ps1
```

### 4. Prepare NLTK for text processing:
```powershell
py -3.10 -m textblob.download_corpora
```

### 5. Download and convert the Whisper model (for speech recognition):
```powershell
py -3.10 speech/download_and_convert.py
```
This will:
- Download the Whisper `small.en` model from Hugging Face  
- Convert it to the CTranslate2 format for use with FasterWhisper  
- Optionally delete the original download after conversion

## Testers

Beatrice Schisano : schisano25@gmail.com
Giacomo Zezza : giacomozezza@live.it
Carmen Barbesco : barbescocarmen@gmail.com
Alessia Vastola :
Francesco Sorrentino :
Giorgia Ungaro : 