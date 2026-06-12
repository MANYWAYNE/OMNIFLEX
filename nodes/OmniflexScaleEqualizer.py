class OmniflexScaleEqualizer:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "model": ("MODEL",),
            "max_shift": ("FLOAT", {"default": 1.15, "min": 0.0, "max": 10.0, "step": 0.05}),
            "base_shift": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 10.0, "step": 0.05}),
            "width": ("INT", {"default": 1024, "min": 64, "max": 8192}),
            "height": ("INT", {"default": 1024, "min": 64, "max": 8192}),
        }}

    RETURN_TYPES = ("MODEL",)
    FUNCTION = "apply_normalization"
    CATEGORY = "Omniflex/Model Optimization"

    def apply_normalization(self, model, max_shift, base_shift, width, height):
        modified_model = model.clone()
        
        aspect_ratio = max(width, height) / min(width, height)
        resolution_factor = (width * height) / (1024 * 1024)
        
        calculated_shift = base_shift + (max_shift - base_shift) * (aspect_ratio * resolution_factor) ** 0.5
        calculated_shift = min(calculated_shift, max_shift)

        if hasattr(modified_model.model, "model_sampling"):
            modified_model.model.model_sampling.set_shift(calculated_shift)
            
        return (modified_model,)