# 📚 AI Book Writer with CrewAI & Ollama

Welcome to the AI Book Writer — an interactive, multi-agent book creation system powered by [CrewAI](https://github.com/joaomdmoura/crewAI), [Ollama](https://ollama.com), and [Streamlit](https://streamlit.io/). This project enables you to generate full-length books — including structured outlines and detailed chapters — using autonomous AI agents.

---

## 🌟 Features

- 🎯 Define a **book topic, goal, number of chapters, and chapter length**
- ✍️ Auto-generates **book outlines and full chapters**
- 📄 Combines everything into a single `.md` file
- 🖥️ User-friendly **Streamlit interface** to guide the whole process
- 🧠 Leverages **CrewAI multi-agent workflows** (OutlineCrew + WriteBookChapterCrew)
- 🔧 Easy to customize agents, tasks, and flow logic

---

## 📸 Screenshot

> You can add a `screenshot.png` here showing the Streamlit interface and output.

---

## 🚀 How It Works

This flow leverages multiple AI agents, each with a specific task in the book-writing process:

1. **📘 Generate Book Outline**  
   The `OutlineCrew` creates a chapter-by-chapter structure using the input topic and goal.

2. **✍️ Write Book Chapters**  
   The `WriteBookChapterCrew` is spun up for each chapter to write detailed content (based on your desired word count).

3. **📄 Join and Save**  
   All chapters are merged into a markdown file with your book's title as the filename.

---

## 🧪 Try It with the Streamlit App

### 🖥️ Run the App

```bash
# Activate your virtual environment
source crewai-venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

### ✍️ App Inputs

- **Book Title**
- **Book Topic**
- **Goal of the Book**
- **Number of Chapters**
- **Words per Chapter**

After submission, the system will:

✅ Generate a markdown book  
✅ Display each chapter interactively  
✅ Save the book to a file

---

## 🛠 Installation

### Prerequisites

- Python 3.10–3.13
- [CrewAI](https://pypi.org/project/crewai/)
- [Ollama](https://ollama.com/) (for running LLMs locally)

### Set Up

```bash
git clone https://github.com/your-username/ai-book-writer.git
cd ai-book-writer

# Create virtual environment
python -m venv crewai-venv
source crewai-venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Or install crewAI tools (if needed)
crewai install
```

---

## 🔐 Configuration

1. Create a `.env` file in the root folder:

```env
OPENAI_API_KEY=your_key_here
SERPER_API_KEY=your_key_here
```

2. Customize agents and tasks as needed:

- `src/.../config/agents.yaml` → Define agent roles and tools  
- `src/.../config/tasks.yaml` → Define their goals and flows

---

## 🧩 Flow Structure

| Component              | Description                                                  |
|------------------------|--------------------------------------------------------------|
| `OutlineCrew`          | Builds the book outline using your topic and goal            |
| `WriteBookChapterCrew`| Writes each chapter based on the generated outline           |
| `join_and_save_chapter`| Merges chapters and saves the result in markdown format      |

Flow logic is orchestrated in `main.py`, and crews are modular for easy customization.

---

## 🧠 Understanding the AI System

This app is a working example of a **modular multi-agent framework** using CrewAI. Each agent:

- Has defined tools and memory
- Operates independently
- Collaborates through the flow logic to complete the book

It demonstrates the **power of agentic design** in real-world applications.

---

## 📂 Project Structure

```
├── app.py                        # Streamlit UI
├── main/
│   ├── main.py                   # Flow logic (BookFlow, BookState)
│   └── types.py                  # Chapter and outline models
│
├── crews/
│   ├── outline_crew/             # Outline generation crew
│   └── chapter_crew/             # Chapter writing crew
│
├── config/
│   ├── agents.yaml               # Define agent roles
│   └── tasks.yaml                # Define task structure
│
├── requirements.txt
└── README.md
```

---

## 🛠 Customization Tips

- 🔧 Want longer or fewer chapters? Change the word and chapter inputs in the app.
- 🧠 Want smarter agents? Customize your `agents.yaml` and `tasks.yaml`.
- 📄 Want different output formats? Add PDF or EPUB support using libraries like `pdfkit` or `weasyprint`.

---

## 🆘 Support & Community

For help or suggestions:

- 📖 Visit [CrewAI Docs](https://docs.crewai.io/)
- 🧑‍💻 Post issues or feature requests in this repo
- 💬 Join the [CrewAI Discord](https://discord.gg/RvFtmYg8nC)

---

## 📜 License

MIT License. See `LICENSE` for more details.

---

Let's create wonders together with the power of agentic AI 🧠📚✨
