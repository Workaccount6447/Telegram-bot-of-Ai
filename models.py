import logging
logging.basicConfig(level=logging.INFO)
class Model:
    def __init__(self, model_id, name, description):
        self.model_id = model_id
        self.name = name
        self.description = description

# List of AI models
models = [
    Model("google/gemma-3-4b-it:free", "Google: Gemma 3 4B (free)", "Gemma 3 introduces multimodality, supporting vision-language input and text outputs."),
    Model("qwen/qwq-32b:free", "Qwen: QWQ 32B (free)", "A distilled version of the DeepSeek-R1 model, optimized for reasoning domains like mathematics, coding, and logic."),
    Model("rekaai/reka-flash-3:free", "RekaAI: Reka Flash 3 (free)", "Experimental release with limited multilingual understanding capabilities."),
    Model("google/gemma-3-12b-it:free", "Google: Gemma 3 12B (free)", "Part of the Gemma 3 family, offering improved math, reasoning, and chat capabilities."),
    Model("moonshotai/moonlight-16b-a3b-instruct:free", "MoonShotAI: MoonLight 16B A3B Instruct (free)", "Optimized for low-latency performance across common AI tasks."),
    Model("nousresearch/deephermes-3-llama-3-8b-preview:free", "NousResearch: DeepHermes 3 Llama 3 8B Preview (free)", "A preview model based on Llama 3, designed for high-quality dialogue use cases."),
    Model("qwen/qwq-32b-preview:free", "Qwen: QWQ 32B Preview (free)", "Preview version of Qwen's 32B parameter model."),
    Model("deepseek/deepseek-r1-zero:free", "DeepSeek: DeepSeek R1 Zero (free)", "Fully open-source model with strong performance in reasoning domains."),
    Model("deepseek/deepseek-chat:free", "DeepSeek: DeepSeek Chat (free)", "Open-source model optimized for chat applications."),
    Model("google/gemini-2.0-flash-thinking-exp:free", "Google: Gemini 2.0 Flash Thinking Experimental (free)", "Experimental version of Gemini Flash optimized for speed and efficiency."),
    Model("deepseek/deepseek-r1:free", "DeepSeek: DeepSeek R1 (free)", "Open-sourced model with fully open reasoning tokens."),
    Model("sophosympatheia/rogue-rose-103b-v0.2:free", "Sophosympatheia: Rogue Rose 103B v0.2 (free)", "A large language model with strong reasoning capabilities."),
    Model("google/gemini-2.0-flash-exp:free", "Google: Gemini 2.0 Flash Experimental (free)", "Experimental version of Gemini Flash with reduced latency."),
    Model("google/gemma-2-27b-it:free", "Google: Gemma 2 27B (free)", "Advanced open-source language model built using Google's research."),
    Model("google/gemini-exp-1206:free", "Google: Gemini Experimental 1206 (free)", "Experimental release (December 6, 2024) of Gemini."),
    Model("meta-llama/llama-3.3-70b-instruct:free", "Meta-Llama: Llama 3.3 70B Instruct (free)", "Meta's latest class of model optimized for high-quality dialogue."),
    Model("mistralai/mistral-small-24b-instruct-2501:free", "MistralAI: Mistral Small 24B Instruct 2501 (free)", "A 24B-parameter language model optimized for low-latency performance."),
    Model("deepseek/deepseek-r1-distill-qwen-32b:free", "DeepSeek: DeepSeek R1 Distill Qwen 32B (free)", "Distilled version of Qwen 2.5 32B, achieving state-of-the-art results."),
    Model("deepseek/deepseek-r1-distill-qwen-14b:free", "DeepSeek: DeepSeek R1 Distill Qwen 14B (free)", "Distilled version of Qwen 2.5 14B, outperforming OpenAI's o1-mini."),
    Model("deepseek/deepseek-r1-distill-llama-70b:free", "DeepSeek: DeepSeek R1 Distill Llama 70B (free)", "Distilled version of Llama 70B, optimized for reasoning tasks."),
    Model("google/gemini-2.0-flash-lite-preview-02-05:free", "Google: Gemini 2.0 Flash Lite Preview (free)", "Preview version of Gemini Flash Lite with faster time-to-first-token."),
    Model("qwen/qwen2.5-vl-72b-instruct:free", "Qwen: Qwen 2.5 VL 72B Instruct (free)", "Multimodal LLM from the Qwen Team with enhancements for vision-language tasks."),
    Model("qwen/qwen-2.5-coder-32b-instruct:free", "Qwen: Qwen 2.5 Coder 32B Instruct (free)", "Specialized for coding tasks, part of the Qwen 2.5 family."),
    Model("nvidia/llama-3.1-nemotron-70b-instruct:free", "NVIDIA: Llama 3.1 Nemotron 70B Instruct (free)", "Optimized for natural language tasks and multiturn text/code chat."),
    Model("google/gemma-2-9b-it:free", "Google: Gemma 2 9B (free)", "Open-source language model suitable for text generation tasks."),
    Model("meta-llama/llama-3.2-3b-instruct:free", "Meta-Llama: Llama 3.2 3B Instruct (free)", "Smaller variant of Meta's Llama 3 series, optimized for dialogue."),
    Model("meta-llama/llama-3.2-1b-instruct:free", "Meta-Llama: Llama 3.2 1B Instruct (free)", "Compact version of Llama 3, designed for lightweight use cases."),
    Model("meta-llama/llama-3.2-11b-vision-instruct:free", "Meta-Llama: Llama 3.2 11B Vision Instruct (free)", "Vision-enabled variant of Llama 3, supporting multimodal tasks."),
    Model("qwen/qwen-2.5-72b-instruct:free", "Qwen: Qwen 2.5 72B Instruct (free)", "Latest series of Qwen large language models with significant improvements."),
    Model("qwen/qwen-2-7b-instruct:free", "Qwen: Qwen 2 7B Instruct (free)", "Transformer-based model excelling in language understanding and coding."),
    Model("mistralai/mistral-nemo:free", "MistralAI: Mistral Nemo (free)", "Multimodal model supporting image and video inputs."),
    Model("mistralai/mistral-small-3.1-24b-instruct:free", "MistralAI: Mistral Small 3.1 24B Instruct (free)", "Mistral Small 3.1 24B Instruct is an upgraded variant of Mistral Small 3 (2501), featuring 24 billion parameters with advanced multimodal capabilities. It provides state-of-the-art performance in text-based reasoning and vision tasks, including image analysis, programming, mathematical reasoning."),
    Model("open-r1/olympiccoder-7b:free", "Open-R1: OlympicCoder 7B (free)", "OlympicCoder-7B is an open-source language model fine-tuned on the CodeForces-CoTs dataset, consisting of nearly 100,000 high-quality chain-of-thought examples from competitive programming contexts."),
]