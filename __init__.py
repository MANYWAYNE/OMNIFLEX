from .soul_samplers import OmniflexProSampler, OmniflexProSamplerAdvanced, OmniflexProSamplerDPM
from .latent_size_picker import OmniflexAspectArchitect
from .model_sampling import OmniflexScaleEqualizer
from .highresfix_scaler import OmniflexHighResDetailer
from .token_counter import OmniflexTokenCounter

NODE_CLASS_MAPPINGS = {
    "OmniflexProSampler": OmniflexProSampler,
    "OmniflexProSamplerAdvanced": OmniflexProSamplerAdvanced,
    "OmniflexProSamplerDPM": OmniflexProSamplerDPM,
    "OmniflexAspectArchitect": OmniflexAspectArchitect,
    "OmniflexScaleEqualizer": OmniflexScaleEqualizer,
    "OmniflexHighResDetailer": OmniflexHighResDetailer,
    "OmniflexTokenCounter": OmniflexTokenCounter
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OmniflexProSampler": "🌌 Omniflex Pro Sampler",
    "OmniflexProSamplerAdvanced": "🌌 Omniflex Pro Sampler (Advanced)",
    "OmniflexProSamplerDPM": "🌌 Omniflex Pro Sampler DPM++",
    "OmniflexAspectArchitect": "📐 Omniflex Aspect Architect",
    "OmniflexScaleEqualizer": "🧠 Omniflex Scale Equalizer",
    "OmniflexHighResDetailer": "🔍 Omniflex High-Res Detailer",
    "OmniflexTokenCounter": "✍️ Omniflex Token Counter"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']