# Omniflex Specialized AI Environment
[<img width="1280" height="720" alt="COVER_04" src="https://github.com/user-attachments/assets/3873069f-64a2-4c7d-9cb3-0400681bf55c" />](https://t.me/omniflexinfo)
A collection of specialized custom nodes for ComfyUI focused on enhanced adaptive sampling, intelligent latent architecture, model optimization, and prompt token analysis.

## Features

### 🌌 Omniflex Sampling
Advanced sampling nodes with adaptive procedural noise injection for enhanced texture, depth, and organic detail control. Primarily designed to excel in image restoration, upscaling, and img2img pipelines, while maintaining robust text2img generation.

* **Omniflex Pro Sampler**: Standard implementation featuring adaptive noise injection with luminance-aware processing for automated texture refinement.
* **Omniflex Pro Sampler (Advanced)**: Full parameter control environment for granular fine-tuning of multi-frequency noise behavior and timestep scaling.
* **Omniflex Pro Sampler DPM++**: Specialized integration with the modern DPM++ 2M SDE sampler, blending structural sampling with custom organic noise.

### 📐 Latent Architecture
* **Omniflex Aspect Architect**: Advanced latent tensor initialization environment. Features multiple preprocessing configuration modes (including zeros, uniform noise, gaussian noise, and direct VAE encoding) coupled with aspect-ratio optimized resolution presets.

### 🧠 Model Optimization
* **Omniflex Scale Equalizer**: Dynamically adjusts model sampling schedules and shift parameters based on generation dimensions, preventing quality degradation and artifacts when scaling across non-standard aspect ratios and extreme resolutions.

### 🔍 Latent Utilities & Upscaling
* **Omniflex High-Res Detailer**: Multi-stage latent upscaler utilizing non-destructive tensor scaling combined with procedural soft-light blend noise injection for maintaining structural integrity during high-resolution high-res fix workflows.

### ✍️ Text Analysis
* **Omniflex Token Counter**: Real-time prompt serialization and tokenization tracker. Supports immediate frontend updates for CLIP-L and T5XXL token boundaries, preventing prompt truncation during complex generation tasks.

---

## Technical Specifications & Parameters

### Omniflex Pro Sampler Configurations
* **base_noise_strength** (0.0 - 0.3): Base amplitude of the custom procedural noise injection.
* **shadow_boost** (1.0 - 2.0): Target amplification multiplier applied strictly to luminance-evaluated shadow zones.
* **highlight_boost** (1.0 - 2.0): Target amplification multiplier applied strictly to luminance-evaluated highlight zones.
* **frequency_mix** (0.0 - 1.0): Dynamic balance matrix between high-frequency fine micro-textures and low-frequency macro structural noise patterns.
* **adaptive_timestep** (Boolean): Automatically scales noise degradation thresholds matching the current inversion execution step.
* **noise_seed** (Int): Dedicated isolation seed for reproducible procedural noise structures.

### Omniflex Scale Equalizer Configurations
* **max_shift** (Default: 1.15): Upper threshold limit for model sampling shift calculation.
* **base_shift** (Default: 0.50): Baseline shift compensation index for latent canvas evaluation.

---

## Technical Details

### Procedural Noise Generation
The Omniflex environment utilizes a multi-octave trigonometric noise formulation instead of simple raw mathematical randomization. This delivers highly structural, organic pattern designs that mirror real-world grain and texture without altering core prompt prompt-adherence or destroying color balance.

[<img width="3440" height="924" alt="START" src="https://github.com/user-attachments/assets/79a549a3-788d-4a73-9f60-854ffd5ef570" />](https://t.me/omniflexinfo)

