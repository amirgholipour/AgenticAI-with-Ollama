# 🤖 ThinkPlanSolve
[Think, Plan, Solve: A Smarter Way to Tackle Problems with Multi-Agent Planning](https://medium.com/@saeedamirgholipour/building-a-recursive-multi-agent-system-with-crewai-and-ollama-898332dd8e12)

*AI that Thinks, Plans, and Solves – End-to-End Automation with LLMs and Agents*

ThinkPlanSolve is a dynamic AI task planner and executor powered by [CrewAI](https://github.com/joaomdmoura/crewAI), [LangChain](https://www.langchain.com/), and [Streamlit](https://streamlit.io/). It takes a user-defined problem or goal, uses an LLM to break it into agent roles and tasks, and executes them with a multi-agent CrewAI setup.

---

## 🚀 Features

- 📝 **Natural Language Task Planning**: Describe your goal in plain English.
- 🤖 **Dynamic Agent Creation**: Agents are generated with specific roles and tools.
- 🔄 **Task Chaining**: Tasks can depend on previous tasks.
- 🧰 **Tool Integration**: Includes tools for text extraction and layout analysis.
- 📁 **Reusable YAML Plan**: Agents and tasks are saved in `config/` for reuse.
- 💻 **ThinkPlanSolve UI**: Simple front-end to enter goals and run the workflow.

---

## 🛠️ Installation

```bash
git clone https://github.com/yourusername/ThinkPlanSolve.git
cd ThinkPlanSolve

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 📂 Project Structure

```
.
├── app.py               # Streamlit front-end
├── planner.py           # Uses LLM to generate crew plan
├── crew.py              # Executes the generated plan
├── config/
│   ├── agents.yaml      # Saved agents
│   ├── tasks.yaml       # Saved tasks
│   └── crew_plan.pkl    # Pickled CrewPlan
└── README.md
```

---

## 🧪 Usage

1. Start the Streamlit app:

```bash
streamlit run app.py
```

2. In the UI:
   - Enter a **goal** (e.g., “Analyze image layout and extract text”)
   - Provide the **path to a local image file**
   - Click “Generate Crew Plan and Execute Tasks”

3. View the result in the output panel!

---

## 🧠 How It Works

1. **User Input**: You define a goal and provide any necessary input data.
2. **Planner LLM** (`planner.py`): 
   - Sends your goal to an LLM (e.g., Ollama, OpenAI)
   - Creates a plan with agents and tasks
   - Exports to `agents.yaml`, `tasks.yaml`, and `crew_plan.pkl`
3. **Execution Engine** (`crew.py`):
   - Loads the YAML plan
   - Dynamically instantiates agents and assigns tools
   - Executes tasks sequentially using CrewAI
4. **ThinkPlanSolve UI**: Wraps the system in an interactive web app.

---

## 🛠️ Tools Available

| Tool                  | Purpose                                      |
|-----------------------|----------------------------------------------|
| Text Extraction Tool  | Extracts readable text from image files      |
| Object Location Tool  | Simulates layout analysis of UI elements     |

> You can easily extend tools by adding new `BaseTool` subclasses in `crew.py`.

---

## 🔄 Example Goal

```text
Analyze the provided image. First, extract all visible text content.
Second, describe the spatial layout and positions of key UI elements.
Finally, synthesize this information into a concise summary describing the board's structure and content.
```

---

## 📌 Requirements

- Python 3.12+
- Ollama server running locally or OpenAI API key
- Streamlit
- CrewAI
- LangChain
- Unstructured (for image parsing)

---

## 💡 Future Improvements

- Add support for parallel execution
- Integrate visual result display
- Use file upload instead of manual image paths
- Add error handling and progress indicators

---

## 📄 License

MIT License. Feel free to fork and extend the app.

---

## ✨ Acknowledgements

- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [LangChain](https://www.langchain.com/)
- [Ollama](https://ollama.com/)
- [Streamlit](https://streamlit.io/)
