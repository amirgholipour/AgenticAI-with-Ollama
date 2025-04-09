# 🧠 Agentic AI with Ollama

A collection of experiments, projects, and tools that explore **Agentic AI systems** using **open-source models via [Ollama](https://ollama.com/)**.  
This repository documents the journey of building powerful, privacy-preserving AI workflows — all running locally.

---

## 🧪 Use Cases

### 1. 📸 ImageAnalyser  
A fully offline multi-agent system that interprets any image — including charts, dashboards, and screenshots — using local LLMs. It mimics how a human would extract text, detect layout, understand context, and summarize insights.  
🛠️ Built with: CrewAI, Streamlit, Langchain, Unstructured, Ollama.  
📂 Path: `ImageAnalyser/`  
🔗 [Read full documentation](ImageAnalyser/README.md)

### 2. 📸 Automatic Agents Builder

An agent that autonomously builds and customizes other agents based on user requirements, streamlining the development of AI workflows.  
🛠️ Built with: CrewAI, Ollama.  
📂 Path: `Automatic-Agents-Builder/`  
🔗 [Read full documentation](Automatic-Agents-Builder/README.md)

### 3. 📸 Kafka Video Summary

A system that consumes video data from Kafka topics, processes the content using local LLMs, and generates concise summaries for quick insights.  
🛠️ Built with: Kafka, Ollama.  
📂 Path: `Kafka_Video_Summary/`  
🔗 [Read full documentation](Kafka_Video_Summary/README.md)

### 4. 📝 LinkedIn Post Creator

An intelligent agentic system that automates the creation of professional LinkedIn posts based on a given topic, tone, and persona. It scrapes influencer content, researches web trends, and generates a structured, markdown-formatted post with a hook, implementation steps, and insights.
🛠️ Built with: crewAI, Ollama, Streamlit 
📂 Path: `Linkedin-Post-Creater/`  
🔗 [Read full documentation](Linkedin-Post-Creater/README.md)

### 5. 📝 Writing a book

This flow will guide you through the process of writing a book by leveraging multiple AI agents, each with specific roles.
🛠️ Built with: crewAI, Ollama, Streamlit 
📂 Path: `Write_a_Book_with_Flows/`  
🔗 [Read full documentation](Write_a_Book_with_Flows/README.md)
> *More use cases will be added as this repo evolves.*

---

## 🔧 Tech Stack

- **🧠 LLMs:** Open-source models via Ollama (e.g., Gemma, Granite, Phi)
- **🧩 Agent Framework:** [CrewAI](https://docs.crewai.com/)
- **🔎 Text & Layout Tools:** Langchain + Unstructured
- **🌐 Frontend:** Streamlit
- **🛡️ Privacy-first:** All logic runs locally — no external API calls
- **🛡️ Kafka:** An open-source real-time data handling platform that supports low-latency, high-volume tasks.

---

## 📌 Goals

- Demonstrate modular and scalable agent workflows with local models  
- Provide offline-friendly AI applications that respect data privacy  
- Showcase different use cases for agent-based reasoning (e.g., vision, reasoning, summarization)  
- Create reusable templates for future projects using YAML-driven configurations  

---

## 🚀 Get Started

To explore a use case:

```bash
cd ImageAnalyser
pip install -r requirements.txt
streamlit run app.py
