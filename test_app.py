"""
Minimal test app to verify Gradio is working.
"""

import gradio as gr

def greet(name):
    return f"Hello {name}!"

with gr.Blocks() as demo:
    name = gr.Textbox(label="Name")
    output = gr.Textbox(label="Output")
    greet_btn = gr.Button("Greet")
    greet_btn.click(fn=greet, inputs=name, outputs=output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=3000)
