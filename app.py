import gradio as gr
from query import ask

def handle_query(question):
    """Handle a user query and return answer + sources"""
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

# ── GRADIO INTERFACE ──────────────────────────────────────────────────────────

with gr.Blocks(title="CSULB Unofficial Professor Guide") as demo:
    gr.Markdown("# 🎓 CSULB Unofficial Professor Guide")
    gr.Markdown("Ask questions about CS and Finance professors at CSULB based on real student reviews from Rate My Professors.")

    with gr.Row():
        inp = gr.Textbox(
            label="Your Question",
            placeholder="e.g. What do students say about Professor Nachawati's organization?",
            lines=2
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=10)
        sources = gr.Textbox(label="Retrieved From", lines=10)

    # Example questions
    gr.Examples(
        examples=[
            "What do students say about Professor Nachawati's organization?",
            "How are Professor Xiaoying Chen's exams?",
            "What is Professor Prombutr's class structure like?",
            "What do students say about Professor Sharifian's lectures and exams?",
            "Which CS professor is most recommended for first time students?"
        ],
        inputs=inp
    )

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

if __name__ == "__main__":
    demo.launch()