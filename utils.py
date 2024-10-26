from transformers import CLIPProcessor, CLIPModel


def load_clip_model():
    """
    Loads the CLIP model and processor.

    Returns:
        - CLIPProcessor: Processor to preprocess text and images.
        - CLIPModel: Model for image-text similarity classification.
    """
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return processor, model
