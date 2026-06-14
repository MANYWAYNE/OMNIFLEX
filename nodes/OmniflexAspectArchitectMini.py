import torch
import comfy.model_management

MAX_RESOLUTION = 8192

class OmniflexAspectArchitectMini:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "resolution": ([
                    "--- Horizontal ---",
                    "576x416 (0.24MP) - 18:13",
                    "288x208 (0.06MP) - 18:13",
                    "144x112 (0.02MP) - 9:7",
                    "80x64 (0.01MP) - 5:4",
                    "--- Vertical ---",
                    "416x576 (0.24MP) - 13:18",
                    "208x288 (0.06MP) - 13:18",
                    "112x144 (0.02MP) - 7:9",
                    "64x80 (0.01MP) - 4:5"
                ], {"default": "416x576 (0.24MP) - 13:18"}),
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
        
        if "---" in resolution:
            resolution = "416x576 (0.24MP) - 13:18"
            
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
                return latent
            else:
                return self._generate_structured_noise(batch_size, latent_height, latent_width, noise_strength)
        except Exception:
            return self._generate_structured_noise(batch_size, latent_height, latent_width, noise_strength)
    
    def _generate_structured_noise(self, batch_size, latent_height, latent_width, noise_strength):
        latent = torch.randn([batch_size, 16, latent_height, latent_width], device=self.device) * noise_strength
        return latent