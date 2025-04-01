
# 🤖 ThinkPlanSolve

*AI that Thinks, Plans, and Solves – End-to-End Agentic Automation*

ThinkPlanSolve is a modular multi-agent system powered by [CrewAI](https://github.com/joaomdmoura/crewAI), [LangChain](https://www.langchain.com/), and [Streamlit](https://streamlit.io/). It interprets user goals in natural language, then dynamically plans and executes task workflows using autonomous agents.

---

## 🧠 Two Architectures in One App

### 1. **Direct LLM Planner (Classic Mode)**

In this setup, the system:
- Takes a user-defined problem or goal via the UI
- Uses a **single LLM call** (OpenAI/Ollama) to:
  - Break down the problem
  - Define agents with roles/tools
  - Create a set of tasks
- Executes the multi-agent plan using CrewAI

> **Files involved**: `app.py`, `planner.py`, `crew.py`

---

### 2. **Agentic Planner (Recursive Mode)**

In this enhanced version, the app:
- Accepts a user goal
- Uses a **first multi-agent CrewAI system** to:
  - Understand the ask
  - Architect the solution itself
  - Define a **secondary set of agents and tasks**
- The resulting agent/task plan is then executed as a second CrewAI system

This creates a **nested agentic solution**, where agents build other agents to accomplish complex goals.

> **Files involved**: `app-v2.py`, `planner_crew.py`, `executer_crew.py`

---

## 🚀 Features

- 📝 **Natural Language Goal Parsing**
- 🤖 **Multi-layer Agent Planning**
- 🔁 **Recursive Agent-Orchestrated Architecture**
- 📁 **Reusable YAML Plans**
- 🧠 **Uses Ollama LLMs Locally**
- 💡 **Modular Code for Extension and Experimentation**

---

## 📂 Project Structure

```
.
├── app.py               # Streamlit UI using direct LLM planner
├── app-v2.py            # Streamlit UI using agentic planner
├── planner.py           # Uses LLM to generate crew plan (classic)
├── crew.py              # Executes the generated plan
├── planner_crew.py      # CrewAI-based multi-agent planner (recursive)
├── executer_crew.py     # Executes the nested agent plan
├── config/
│   ├── agents.yaml
│   ├── tasks.yaml
│   └── crew_plan.pkl
└── README.md
```

---

## 🧪 Usage

### 🧭 Run Classic Mode

```bash
streamlit run app.py
```

### 🧭 Run Agentic Recursive Mode

```bash
streamlit run app-v2.py
```

---

## 📌 Requirements

- Python 3.12+
- [Ollama](https://ollama.com/) running locally or OpenAI API key
- `CrewAI`, `LangChain`, `Streamlit`, `Unstructured`

```bash
pip install -r requirements.txt
```

---

## 💡 Example Goals

```text
Design an agent workflow to classify documents and summarize key topics.
```

```text
Plan a set of agents that can analyze a directory of PDFs and generate insights per file.
```

---

## 🛠️ Tools Available

| Tool Name             | Purpose                                      |
|----------------------|----------------------------------------------|
| Text Extraction Tool | Extracts readable text from documents        |
| Object Layout Tool   | Simulates spatial/visual element detection   |

You can extend the system with more `BaseTool` subclasses.

---

## 🛤 Roadmap Ideas

- 🧭 Adaptive planning: agents improve with memory
- ⏱ Parallel task execution
- 🎨 Better visualization of agent workflows
- 📄 Add drag-and-drop file upload in UI

---

## 📄 License

MIT License. Feel free to fork, modify, or enhance!

---

## 🙏 Acknowledgements

- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [LangChain](https://www.langchain.com/)
- [Ollama](https://ollama.com/)
- [Streamlit](https://streamlit.io/)
