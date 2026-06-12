import torch
import math
import comfy.samplers
import comfy.sample
  
class OmniflexProSampler:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "model": ("MODEL",),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                    "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0, "step":0.1, "round": 0.01}),
                    "sampler_name": (comfy.samplers.KSampler.SAMPLERS, ),
                    "scheduler": (comfy.samplers.KSampler.SCHEDULERS, ),
                    "positive": ("CONDITIONING", ),
                    "negative": ("CONDITIONING", ),
                    "latent_image": ("LATENT", ),
                    "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                    "base_noise_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 0.3, "step": 0.01}),
                    "shadow_boost": ("FLOAT", {"default": 1.3, "min": 1.0, "max": 2.0, "step": 0.05}),
                    "highlight_boost": ("FLOAT", {"default": 1.3, "min": 1.0, "max": 2.0, "step": 0.05}),
                    "frequency_mix": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 1.0, "step": 0.05}),
                    "adaptive_timestep": ("BOOLEAN", {"default": True}),
                    "noise_seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                }}

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "sample"
    CATEGORY = "Omniflex/Sampling"

    def generate_pro_noise(self, x, seed, timestep, steps, base_strength, shadow_boost, highlight_boost, freq_mix, adaptive):
        torch.manual_seed(seed)
        b, c, h, w = x.shape
        
        grid_y, grid_x = torch.meshgrid(torch.arange(h, device=x.device), torch.arange(w, device=x.device), indexing='ij')
        
        hf_noise = torch.sin(grid_x.float() * 1.5) * torch.cos(grid_y.float() * 1.5)
        lf_noise = torch.sin(grid_x.float() * 0.2) * torch.cos(grid_y.float() * 0.2)
        
        procedural_noise = (hf_noise * freq_mix) + (lf_noise * (1.0 - freq_mix))
        procedural_noise = procedural_noise.unsqueeze(0).unsqueeze(0).repeat(b, c, 1, 1)
        
        latent_mean = torch.mean(torch.abs(x), dim=1, keepdim=True)
        max_val = torch.max(latent_mean) if torch.max(latent_mean) > 0 else 1.0
        norm_latent = latent_mean / max_val
        
        shadow_mask = torch.clamp(1.0 - (norm_latent / 0.15), 0.0, 1.0)
        highlight_mask = torch.clamp((norm_latent - 0.85) / 0.15, 0.0, 1.0)
        
        step_modifier = 1.0
        if adaptive and steps > 0:
            step_modifier = max(0.0, 1.0 - (timestep / steps))
            
        total_strength = base_strength * step_modifier
        boosted_noise = procedural_noise * (1.0 + (shadow_mask * (shadow_boost - 1.0)) + (highlight_mask * (highlight_boost - 1.0)))
        
        return boosted_noise * total_strength

    def sample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise, 
               base_noise_strength, shadow_boost, highlight_boost, frequency_mix, adaptive_timestep, noise_seed):
        
        latent = latent_image.copy()
        x = latent["samples"]
        
        pro_noise = self.generate_pro_noise(x, noise_seed, 0, steps, base_noise_strength, shadow_boost, highlight_boost, frequency_mix, adaptive_timestep)
        latent["samples"] = x + pro_noise
        
        return comfy.sample.sample_common(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=denoise)


class OmniflexProSamplerAdvanced(OmniflexProSampler):
    @classmethod
    def INPUT_TYPES(s):
        return OmniflexProSampler.INPUT_TYPES()

    CATEGORY = "Omniflex/Sampling"
    
class OmniflexProSamplerDPM(OmniflexProSampler):
    @classmethod
    def INPUT_TYPES(s):
        types = OmniflexProSampler.INPUT_TYPES()
        types["required"].update({
            "eta": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "s_noise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
        })
        return types
    CATEGORY = "Omniflex/Sampling"