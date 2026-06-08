"""
Milestone 5: Gradio web interface for The Unofficial Guide (Furman dining).

This is a thin UI wrapper. All retrieval + grounded generation lives in
generate.py -- this file only calls ask() and displays the result, so there is
no duplicated pipeline logic.

Run it:
    python app.py
Then open:
    http://localhost:7860
"""

import gradio as gr

from generate import ask, get_engine


def handle_query(question: str):
    """Call the end-to-end ask() and split its result into the two textboxes."""
    question = (question or "").strip()
    if not question:
        return "Please type a question.", ""
    result = ask(question)                      # {"answer", "sources", "hits"}
    answer = result["answer"]                   # grounded, with inline [Source N] citations
    sources = "\n".join(f"• {s}" for s in result["sources"])  # metadata, not model-invented
    return answer, sources


with gr.Blocks(title="The Unofficial Guide — Furman Dining") as demo:
    gr.Markdown(
        "# The Unofficial Guide — Furman Dining\n"
        "Ask about Furman dining. Answers are grounded only in the retrieved "
        "sources; if the sources don't cover it, the assistant says so."
    )
    inp = gr.Textbox(label="Your question", placeholder="e.g. What do students say about wait times?")
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Sources (retrieved from)", lines=6)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    # Load the model/store/Groq client once before serving so the first query is
    # fast and a missing GROQ_API_KEY fails clearly at startup.
    get_engine()
    demo.launch()
