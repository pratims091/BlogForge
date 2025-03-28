# BlogForge

<p align="center">
  <img src="assets/logo.webp" alt="BlogForge Logo" width="200">
</p>

## AI-powered Content Alchemy

**Transform trending topics into golden blog posts with just a few keywords!**

### 🚀 Introduction

I wanted to write SEO-friendly blog posts for my portfolio website [pratim.me](https://pratim.me) about the latest technology trends, especially in AI and software engineering. However, keyword research, content research, and writing well-structured, SEO-friendly blog posts is a time-consuming process. As a lazy engineer, I decided to leverage an LLM to help automate this. And thus, **BlogForge** was created!

---

## 🌟 What It Does

1. **Keyword Research & Search**

   - Takes trending Google search keywords (up to 5 at a time).
   - Performs Google searches using [googlesearch-python](https://pypi.org/project/googlesearch-python/), focusing on blog posts related to these topics.

2. **Content Crawling**

   - Crawls the first **n** pages (configurable, currently set to 7) using [Jina AI's Public API](https://jina.ai/reader/).
   - Alternatively, uses [Crawl4AI's API](https://crawl4ai.com/) (configured via Docker Compose) for self-hosted crawling.

3. **Data Processing & Storage**

   - Chunks the crawled data.
   - Embeds them using **Google Gemini’s** embeddings.
   - Stores the processed data in a **local ChromaDB vector store**.

4. **AI-Generated Blog Writing**

   - Supports multiple LLM providers:
     - **Gemini** via Google AI
     - **LLaMA models** via Groq
     - **DeepSeek models** via DeepSeek AI
     - **Local models** via Ollama
   - Generates structured, SEO-optimized blog posts using your preferred LLM

5. **Interactive Refinement**

   - Provides a **Streamlit-based UI** ([Streamlit](https://streamlit.io/)) to allow users to refine the blog post interactively.
   - Allows users to chat with the AI to fine-tune content.

6. **Session Management & Persistence**

   - Uses **Supabase DB** for storing crawled website content and user chat history.

---

## 🔧 Running Locally

### **1️⃣ Prerequisites**

- Install **pipenv**:

  ```sh
  pip install pipenv
  ```

### **2️⃣ Setup**

```sh
pipenv shell
pipenv install
```

### **3️⃣ Environment Variables**

1. Copy the example environment file:

   ```sh
   cp example.env .env
   ```

2. Populate `.env` with required API keys and settings:
   - `GOOGLE_API_KEY` - Required for Google Search and Gemini models
   - `GROQ_API_KEY` - Required for Groq LLM models
   - `DEEP_SEEK_API_KEY` - Required for DeepSeek models
   - `JINA_API_KEY` - Required when using Jina for crawling
   - `SUPABASE_URL` and `SUPABASE_KEY` - Required for database functionality
   - `LLM_TO_USE` - Choose your LLM provider: "GEMINI", "GROQ", "DEEPSEEK", or "OLLAMA"
   - `LLM_MODEL` - Specify the model name for your chosen provider

### **4️⃣ Start the Application**

```sh
pipenv run start
```

### **5️⃣ (Optional) Use Crawl4AI**

- Set `CRAWLER_PROVIDER=CRAWL4AI` in `.env`.
- Generate a random secret and set it as `CRAWL4AI_API_TOKEN`.

---

## 📂 Directory Structure

```sh
├── Pipfile
├── Pipfile.lock
├── README.md
├── __init__.py
├── app.py
├── assets
│   └── logo.webp
├── config.py
├── crawler
│   ├── __init__.py
│   ├── crawler.py
│   └── processor.py
├── db
│   ├── __init__.py
│   ├── supabase.py
│   └── vector_store.py
├── docker-compose.yaml
├── main.py
├── rag
│   ├── __init__.py
│   ├── chains.py
│   ├── chat_history.py
│   ├── embeddings.py
│   ├── llm.py
│   └── prompts.py
├── tools
│   ├── __init__.py
│   ├── crawl4ai.py
│   ├── jina.py
│   └── search.py
└── utils
    ├── __init__.py
    ├── helpers.py
    └── logger.py
```

---

## 🚀 Future Improvements

- ✅ Enable **Classic LLM Chat**-like streaming.
- ✅ Improve **overall performance**.
- ✅ Enable **Docker deployment**.

---

## 🤝 Contribution Guidelines

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Create a pull request.

Please make sure your contributions adhere to best coding practices and include necessary documentation.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 🙌 Credits

Big thanks to:

- [**Jina AI**](https://jina.ai/reader/) for providing free API access.
- [**Google AI**](https://ai.google.dev/) for Gemini models and embeddings.
- [**Groq**](https://groq.com/) for high-performance LLaMA model inference.
- [**DeepSeek**](https://deepseek.ai/) for their powerful AI models.
- [**Ollama**](https://ollama.ai/) for local model support.
- [**Supabase**](https://supabase.io/) for database storage.
- [**ChromaDB**](https://www.trychroma.com/) for the vector store.
- [**Streamlit**](https://streamlit.io/) for the frontend framework.

Happy Blogging! 🚀
