import torch
import comfy.model_management

MAX_RESOLUTION = 8192

class OmniflexAspectArchitect:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "resolution": ([
                    "2688x1088 (2.92MP) - 2.39:1",
                    "2304x1280 (2.95MP) - 16:9",
                    "2240x1280 (2.87MP) - 7:4",
                    "1984x1472 (2.92MP) - 4:3",
                    "1728x1728 (2.99MP) - 1:1",
                    "1472x1984 (2.92MP) - 3:4",
                    "1280x2240 (2.87MP) - 4:7",
                    "1280x2304 (2.95MP) - 9:16",
                    "2176x896 (1.95MP) - 2.39:1",
                    "1856x1024 (1.90MP) - 16:9",
                    "1792x1024 (1.84MP) - 7:4",
                    "1600x1216 (1.95MP) - 4:3",
                    "1408x1408 (1.98MP) - 1:1",
                    "1216x1600 (1.95MP) - 3:4",
                    "1024x1792 (1.84MP) - 4:7",
                    "1024x1856 (1.90MP) - 9:16",
                    "1536x640 (0.98MP) - 2.39:1",
                    "1344x768 (1.03MP) - 16:9",
                    "1280x768 (0.98MP) - 7:4",
                    "1152x832 (0.96MP) - 4:3",
                    "1024x1024 (1.05MP) - 1:1",
                    "832x1152 (0.96MP) - 3:4",
                    "768x1280 (0.98MP) - 4:7",
                    "768x1344 (1.03MP) - 9:16"
                ], {"default": "2304x1280 (2.95MP) - 16:9"}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
                "width_override": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "height_override": ("INT", {"default": 0, "min": 0, "max": MAX_RESOLUTION, "step": 8}),
                "initialization_mode": (["zeros", "vae_sample", "gaussian_noise", "uniform_noise"], {"default": "zeros"}),
                "noise_strength": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 2.0, "step": 0.01}),
            },
            "optional": {
                "vae": ("VAE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("LATENT", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "Omniflex/Latent"

    def execute(self, resolution, batch_size, initialization_mode, noise_strength,
                width_override=0, height_override=0, vae=None, seed=0):
        
        width_str, height_str = resolution.split(" ")[0].split("x")
        width = width_override if width_override > 0 else int(width_str)
        height = height_override if height_override > 0 else int(height_str)
        
        latent_height = height // 8
        latent_width = width // 8
        
        if seed != 0:
            torch.manual_seed(seed)
        
        if initialization_mode == "zeros":
            latent = torch.zeros([batch_size, 16, latent_height, latent_width], device=self.device)
            
        elif initialization_mode == "vae_sample":
            if vae is None:
                latent = torch.zeros([batch_size, 16, latent_height, latent_width], device=self.device)
            else:
                latent = self._sample_from_vae(vae, batch_size, latent_height, latent_width, noise_strength)
                
        elif initialization_mode == "gaussian_noise":
            latent = torch.randn([batch_size, 16, latent_height, latent_width], device=self.device) * noise_strength
            
        elif initialization_mode == "uniform_noise":
            latent = (torch.rand([batch_size, 16, latent_height, latent_width], device=self.device) - 0.5) * 2 * noise_strength
            
        else:
            latent = torch.zeros([batch_size, 16, latent_height, latent_width], device=self.device)

        return ({"samples": latent}, width, height)
    
    def _sample_from_vae(self, vae, batch_size, latent_height, latent_width, noise_strength):
        try:
            if hasattr(vae, 'sample') and callable(vae.sample):
                with torch.no_grad():
                    samples = vae.sample(batch_size, device=self.device)
                    if samples.shape[-2:] != (latent_height, latent_width):
                        samples = torch.nn.functional.interpolate(
                            samples, size=(latent_height, latent_width), mode='bilinear', align_corners=False
                        )
                    return samples
            elif hasattr(vae, 'first_stage_model') or hasattr(vae, 'encode'):
                latent = torch.randn([batch_size, 16, latent_height, latent_width], device=self.device) * (noise_strength * 0.5)
                if latent_height > 1 and latent_width > 1:
                    low_freq = torch.randn([batch_size, 16, max(1, latent_height//4), max(1, latent_width//4)], device=self.device)
                    low_freq = torch.nn.functional.interpolate(low_freq, size=(latent_height, latent_width), mode='bilinear', align_corners=False)
                    latent = latent + low_freq * (noise_strength * 0.3)
                return latent
            else:
                return self._generate_structured_noise(batch_size, latent_height, latent_width, noise_strength)
        except Exception:
            return self._generate_structured_noise(batch_size, latent_height, latent_width, noise_strength)
    
    def _generate_structured_noise(self, batch_size, latent_height, latent_width, noise_strength):
        latent = torch.randn([batch_size, 16, latent_height, latent_width], device=self.device) * noise_strength
        if latent_height > 4 and latent_width > 4:
            low_freq = torch.randn([batch_size, 16, max(1, latent_height//4), max(1, latent_width//4)], device=self.device)
            low_freq = torch.nn.functional.interpolate(
                low_freq, size=(latent_height, latent_width), mode='bilinear', align_corners=False
            )
            latent = latent + low_freq * (noise_strength * 0.5)
        return latent