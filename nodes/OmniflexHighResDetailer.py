import math
import comfy.utils
import torch
import numpy as np
from PIL import Image, ImageChops

class OmniflexHighResDetailer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "vae": ("VAE",),
                "target_resolution": (["4MP", "5MP", "6MP", "7MP"],),
                "upscale_method": (["nearest-exact", "bilinear", "area", "bicubic", "lanczos"],),
                "noise_scale": ("FLOAT", {"default": 0.40, "min": 0.00, "max": 1.00, "step": 0.01}),
                "blend_opacity": ("INT", {"default": 20, "min": 0, "max": 100}),
            },
            "optional": {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("LATENT",)
    FUNCTION = "scale_and_encode"
    CATEGORY = "Omniflex/Latent"

    def tensor_to_pil(self, tensor_image):
        tensor_image = tensor_image.squeeze(0)
        pil_image = Image.fromarray((tensor_image.cpu().numpy() * 255).astype(np.uint8))
        return pil_image

    def pil_to_tensor(self, pil_image):
        return torch.from_numpy(np.array(pil_image).astype(np.float32) / 255).unsqueeze(0)

    def generate_gaussian_noise(self, width, height, noise_scale=0.05):
        noise = np.random.normal(0.5, noise_scale * 0.5, (height, width, 3))
        noise = np.clip(noise, 0, 1)
        return Image.fromarray((noise * 255).astype(np.uint8))

    def soft_light_blend(self, base_image, noise_image, mask=None, opacity=15):
        base_image = base_image.convert('RGB')
        noise_image = noise_image.convert('RGB').resize(base_image.size)
        
        base = np.array(base_image, dtype=np.float32) / 255.0
        noise = np.array(noise_image, dtype=np.float32) / 255.0
        
        result = np.where(noise < 0.5,
                        2 * base * noise + base**2 * (1 - 2 * noise),
                        np.sqrt(base) * (2 * noise - 1) + (2 * base) * (1 - noise))
        
        result = result * (opacity / 100.0) + base * (1 - opacity / 100.0)
        
        result = (np.clip(result, 0, 1) * 255).astype(np.uint8)
        blended_image = Image.fromarray(result)
        
        if mask is not None:
            mask_pil = self.tensor_to_pil(mask).convert('L')
            mask_resized = mask_pil.resize(blended_image.size)
            mask_array = np.array(mask_resized, dtype=np.float32) / 255.0
            base_array = np.array(base_image)
            result_array = result * mask_array[..., None] + base_array * (1 - mask_array[..., None])
            blended_image = Image.fromarray(result_array.astype(np.uint8))
            
        return blended_image

    def scale_and_encode(self, image, vae, upscale_method, target_resolution, noise_scale=0.40, blend_opacity=20, mask=None):
        try:
            if image is None or vae is None:
                raise ValueError("Image and VAE must be provided")
                
            if noise_scale < 0 or noise_scale > 1:
                raise ValueError("Noise scale must be between 0 and 1")
                
            if blend_opacity < 0 or blend_opacity > 100:
                raise ValueError("Blend opacity must be between 0 and 100")
            
            _, original_height, original_width, _ = image.shape
            ratio = original_width / original_height
            
            target_areas = {
                "4MP": 4_000_000.0,
                "5MP": 5_000_000.0,
                "6MP": 6_000_000.0,
                "7MP": 7_000_000.0
            }
            target_area = target_areas[target_resolution]
            
            new_height = int(round(math.sqrt(target_area / ratio)))
            new_width = int(round(ratio * new_height))
            
            max_dimension = 8192
            if new_width > max_dimension or new_height > max_dimension:
                raise ValueError(f"Output dimensions ({new_width}x{new_height}) too large.")

            samples = image.movedim(-1, 1)
            scaled = comfy.utils.common_upscale(
                samples, 
                new_width, 
                new_height, 
                upscale_method, 
                "disabled"
            )
            scaled = scaled.movedim(1, -1)

            scaled_pil = self.tensor_to_pil(scaled)
            noise_image = self.generate_gaussian_noise(new_width, new_height, noise_scale)
            blended_image = self.soft_light_blend(scaled_pil, noise_image, mask, blend_opacity)
            blended_tensor = self.pil_to_tensor(blended_image)

            encoded = vae.encode(blended_tensor[:, :, :, :3])
            return ({"samples": encoded},)
            
        except Exception as e:
            print(f"Error in OmniflexHighResDetailer: {str(e)}")
            return ({"samples": vae.encode(image[:, :, :, :3])},)