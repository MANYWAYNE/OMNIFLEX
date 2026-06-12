import torch
import comfy.model_management

class OmniflexAspectArchitect:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "resolution_preset": (["Custom", "1024x1024 (1:1 Square)", "832x1216 (2:3 Portrait)", "1216x832 (3:2 Landscape)", "720x1280 (9:16 Vertical)", "1280x720 (16:9 Wide)"], {"default": "1024x1024 (1:1 Square)"}),
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
            res_string = resolution_preset.split(" ")[0]
            w, h = map(int, res_string.split("x"))

        latent_w = w // 8
        latent_h = h // 8
        
        if init_mode == "vae_sample" and vae is not None and optional_image is not None:
            latent = vae.encode(optional_image[:,:,:,:3])
            return ({"samples": latent["samples"]}, w, h)
            
        elif init_mode == "gaussian_noise":
            samples = torch.randn([batch_size, 4, latent_h, latent_w], device=self.device)
        elif init_mode == "uniform_noise":
            samples = (torch.rand([batch_size, 4, latent_h, latent_w], device=self.device) * 2.0) - 1.0
        else:
            samples = torch.zeros([batch_size, 4, latent_h, latent_w], device=self.device)

        return ({"samples": samples}, w, h)