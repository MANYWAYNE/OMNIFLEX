import torch
import comfy.model_management

class OmniflexAspectArchitect:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(s):
        resolutions = [
            "Custom",
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
            "1792x1024 (1.83MP) - 7:4",
            "1536x1536 (2.35MP) - 1:1",
            "1024x1792 (1.83MP) - 4:7",
            "1024x1856 (1.90MP) - 9:16",
            "896x2176 (1.95MP) - 9:20"
        ]
        
        return {"required": {
            "resolution_preset": (resolutions, {"default": "1728x1728 (2.99MP) - 1:1"}),
            "custom_width": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 64}),
            "custom_height": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 64}),
            "init_mode": (["zeros", "gaussian_noise", "uniform_noise", "vae_sample"], {"default": "zeros"}),
            "batch_size": ("INT", {"default": 1, "min": 1, "max": 64}),
        }, "optional": {
            "vae": ("VAE",),
            "optional_image": ("IMAGE",),
        }}

    RETURN_TYPES = ("LATENT", "INT", "INT")
    RETURN_NAMES = ("LATENT", "width", "height")
    FUNCTION = "execute"
    CATEGORY = "Omniflex/Latent"

    def execute(self, resolution_preset, custom_width, custom_height, init_mode, batch_size, vae=None, optional_image=None):
        if resolution_preset == "Custom":
            w, h = custom_width, custom_height
        else:
            res_part = resolution_preset.split(" ")[0]
            w, h = map(int, res_part.split("x"))

        latent_w = (w // 8)
        latent_h = (h // 8)
        
        if init_mode == "vae_sample" and vae is not None and optional_image is not None:
            image = optional_image.movedim(-1, 1)
            latent = vae.encode(image)
            return ({"samples": latent}, w, h)
            
        elif init_mode == "gaussian_noise":
            samples = torch.randn([batch_size, 4, latent_h, latent_w], device=self.device)
            return ({"samples": samples}, w, h)
            
        elif init_mode == "uniform_noise":
            samples = torch.rand([batch_size, 4, latent_h, latent_w], device=self.device) * 2.0 - 1.0
            return ({"samples": samples}, w, h)

        else:
            samples = torch.zeros([batch_size, 4, latent_h, latent_w], device=self.device)
            return ({"samples": samples}, w, h)