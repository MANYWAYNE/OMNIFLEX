from server import PromptServer

class OmniflexTokenCounter:
    MODEL_CONFIG = {
        'clip_l': {
            'key': 'l',
            'excluded_tokens': {49407, 49406},
            'max_tokens': 75,
            'display_max': '77'
        },
        't5xxl': {
            'key': 't5xxl',
            'excluded_tokens': {0, 1},
        }
    }

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        return {
            "required": {
                "clip": ("CLIP",),
                "text": ("STRING", {"multiline": True}),
                "model": (list(cls.MODEL_CONFIG.keys()),),
            },
            "hidden": {"unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("token_count", "text")
    FUNCTION = "count_tokens"
    CATEGORY = "Omniflex/Text"
    OUTPUT_NODE = True

    def _get_token_count(self, tokens: list, model_config: dict) -> str:
        if not tokens or len(tokens) == 0:
            return "0"
            
        batch_tokens = tokens[0]
        excluded_tokens = model_config['excluded_tokens']
        real_tokens = [(t[0], t[1]) for t in batch_tokens if t[0] not in excluded_tokens]
        return str(len(real_tokens))

    def count_tokens(self, clip, text: str, model: str, unique_id: str) -> tuple:
        model_config = self.MODEL_CONFIG.get(model)
        if not model_config:
            result_text = "0"
        else:
            tokens = clip.tokenize(text).get(model_config['key'])
            count = self._get_token_count(tokens, model_config)
            
            result_text = (model_config.get('display_max') 
                         if model == 'clip_l' and int(count) >= model_config['max_tokens'] 
                         else count)

        PromptServer.instance.send_sync("omniflex.token_counter.update", {
            "node": unique_id,
            "widget": "token_count",
            "text": result_text
        })

        return (result_text, text)

    @classmethod
    def IS_CHANGED(cls, clip, text: str, model: str, unique_id: str = None) -> int:
        return hash((text, model))