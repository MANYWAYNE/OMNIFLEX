from .nodes.OmniflexProSampler import OmniflexProSampler, OmniflexProSamplerAdvanced, OmniflexProSamplerDPM
from .nodes.OmniflexAspectArchitect import OmniflexAspectArchitect
from .nodes.OmniflexScaleEqualizer import OmniflexScaleEqualizer
from .nodes.OmniflexHighResDetailer import OmniflexHighResDetailer
from .nodes.OmniflexTokenCounter import OmniflexTokenCounter

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