# documents/ai_summarizer.py

from transformers.pipelines import pipeline
import logging

# Load the HuggingFace summarization model once
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
except Exception as e:
    logging.error(f"Error loading summarizer model: {e}")
    summarizer = None

    
def generate_summary(text, max_len=130, min_len=30):
    """
    Generate a summary for the given text using HuggingFace Transformers.
    """
    if summarizer is None:
        return "Summarization model not available."

    if not text or len(text.strip()) == 0:
        return "Empty text provided."

    try:
        # Hugging Face models usually support max ~1024 tokens
        short_text = text.strip()
        if len(short_text) > 1500:
            short_text = short_text[:1500]  # truncate safely

        result = summarizer(short_text, max_length=max_len, min_length=min_len, do_sample=False)
        return result[0]['summary_text']
    except Exception as e:
        import logging
        logging.error(f"Summarization failed: {e}")
        return "Error generating summary."
