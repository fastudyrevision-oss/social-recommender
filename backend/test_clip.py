import torch
import open_clip
from PIL import Image

def main():
    model, _, preprocess = open_clip.create_model_and_transforms(
        'ViT-B-32',
        pretrained='openai'
    )

    tokenizer = open_clip.get_tokenizer('ViT-B-32')

    # Dummy image (224x224)
    image = preprocess(Image.new("RGB", (224, 224))).unsqueeze(0)
    text = tokenizer(["a photo of a cat"])

    with torch.no_grad():
        image_features = model.encode_image(image)
        text_features = model.encode_text(text)

    print("Image embedding shape:", image_features.shape)
    print("Text embedding shape:", text_features.shape)

if __name__ == "__main__":
    main()
