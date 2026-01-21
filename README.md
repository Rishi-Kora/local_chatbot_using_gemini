# Local Chatbot using Gemini 

A streamlined, local chatbot application powered by **Google's Gemini Pro** model. This project provides a user-friendly interface to interact with one of the most powerful Large Language Models (LLMs) available today, right from your local machine.

---

## Features
- **Powered by Gemini Pro:** High-quality text generation and reasoning.
- **Persistent Conversation:** Maintains chat history during the session for context-aware responses.
- **Local Deployment:** Easy-to-run local server using Streamlit.
- **Secure Configuration:** Uses environment variables to protect your API keys.
- **Minimalist UI:** Clean and responsive chat interface.

## Tech Stack
- **Language:** Python 3.9+
- **LLM API:** Google Generative AI (Gemini SDK)
- **Interface:** Streamlit
- **Environment Management:** `python-dotenv`

---

## Prerequisites

Before running the project, you will need:
1. **Python** (v3.9 or higher).
2. A **Google Gemini API Key**. 
   - Get your free key at [Google AI Studio](https://aistudio.google.com/).

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Rishi-Kora/local_chatbot_using_gemini.git
   cd local_chatbot_using_gemini
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Setup:** Create a file named `.env` in the root directory and add your API key:
   ```bash
   GOOGLE_API_KEY=your_actual_api_key_here
   ```
**Usage:**
To launch the chatbot run:
```bash
streamlit run app.py
```
**Project Structure:**
```bash
local_chatbot_using_gemini/
├── .env                # Private API keys
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
```
## License
This project is licensed under the **MIT License**. See [LICENSE](./LICENSE) for details.
