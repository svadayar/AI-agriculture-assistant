"""
agri_assistant_app.py
Gradio UI for AI Agriculture Assistant 1.0

Steps:
1. User picks crop + plant part.
2. User uploads photo.
3. User types OR records voice question.
4. We analyze, wrap with safety, and return text + audio guidance.
"""

import os
import gradio as gr

from advisory_rules import apply_safety_and_escalation
from eye_of_the_agronomist import analyze_crop_issue
from voice_of_the_agronomist import agronomist_response_to_speech
from voice_of_the_farmer import transcribe_farmer_audio
from utils_audio import ensure_dir


OUTPUT_AUDIO_PATH = "output_audio/agri_reply.wav"
ensure_dir("output_audio")


def analyze_handler(
    crop_type,
    plant_part,
    farmer_text,
    farmer_audio,
    crop_image
):
    """
    This is called when the user clicks "Analyze Issue".
    Returns:
      (assistant_text, path_to_audio_file)
    """

    # Step 1. transcription if needed
    if (not farmer_text or farmer_text.strip() == "") and farmer_audio is not None:
        farmer_text = transcribe_farmer_audio(farmer_audio)

    if not farmer_text:
        farmer_text = "No description provided."

    # Step 2. vision + LLM reasoning (raw answer)
    raw_answer = analyze_crop_issue(
        image_path=crop_image,
        farmer_text=farmer_text,
        crop_type=crop_type,
        plant_part=plant_part,
    )

    # Step 3. safety + escalation wrapper
    safe_answer = apply_safety_and_escalation(raw_answer)

    # Step 4. synthesize 'voice of the agronomist'
    audio_output_path = OUTPUT_AUDIO_PATH
    agronomist_response_to_speech(safe_answer, audio_output_path)

    # Step 5. return to UI
    return safe_answer, audio_output_path


def build_interface():
    with gr.Blocks(title="AI Agriculture Assistant 1.0") as demo:
        gr.Markdown(
            "### 🌾 AI Agriculture Assistant 1.0\n"
            "Upload a crop photo and describe the problem.\n"
            "You will get spoken guidance. \n\n"
            "**Note:** This tool gives general crop guidance. "
            "Always confirm pesticide products and rates with a local agronomist."
        )

        with gr.Row():
            crop_type = gr.Dropdown(
                choices=["tomato", "corn", "cotton", "wheat", "rice", "other"],
                label="Crop",
                value="tomato"
            )
            plant_part = gr.Dropdown(
                choices=["leaf", "stem", "fruit", "soil", "insect/pest"],
                label="Plant Part in Photo",
                value="leaf"
            )

        crop_image = gr.Image(
            label="Upload Crop Image (leaf, pest, soil, etc.)",
            type="filepath"
        )

        farmer_text = gr.Textbox(
            label="Describe the problem (when it started, weather, etc.)",
            placeholder="Spots appeared after 3 days of rain. Leaves turning yellow on the bottom.",
            lines=3
        )

        farmer_audio = gr.Audio(
            label="Or speak your question",
            type="filepath",
            sources=["microphone"]
        )

        analyze_button = gr.Button("Analyze Issue")

        advice_output = gr.Textbox(
            label="Assistant Advice",
            lines=8
        )

        audio_output = gr.Audio(
            label="Spoken Guidance",
            type="filepath"
        )

        analyze_button.click(
            fn=analyze_handler,
            inputs=[crop_type, plant_part, farmer_text, farmer_audio, crop_image],
            outputs=[advice_output, audio_output]
        )

    return demo


if __name__ == "__main__":
    ui = build_interface()
    ui.launch()
