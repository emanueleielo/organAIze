import os
from PIL import Image
from utils import load_clip_model

# Load CLIP model and processor
processor, model = load_clip_model()


def classify_images_with_tags(input_folder, output_folder, tags, log_text_widget, recursive, total_images, progress_callback):
    """
    Classifies images based on the provided tags and logs the results.

    Parameters:
        - input_folder (str): Path to the input folder containing images.
        - output_folder (str): Path to the output folder for classified images.
        - tags (list of str): List of tags to classify each image against.
        - log_text_widget (ScrolledText): The GUI widget to display log messages.
        - recursive (bool): Whether to search subdirectories recursively.
        - total_images (int): Total number of images to process.
        - progress_callback (function): Function to update the progress bar.
    """
    processed_images = 0  # Track processed images to update the progress

    if recursive:
        # Recursive search for images
        for root, _, files in os.walk(input_folder):
            for image_file in files:
                image_path = os.path.join(root, image_file)
                if image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    process_image(image_path, tags, log_text_widget, output_folder)
                    processed_images += 1
                    progress_callback(processed_images / total_images)  # Update progress
    else:
        # Non-recursive search
        for image_file in os.listdir(input_folder):
            image_path = os.path.join(input_folder, image_file)
            if image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                process_image(image_path, tags, log_text_widget, output_folder)
                processed_images += 1
                progress_callback(processed_images / total_images)  # Update progress

def process_image(image_path, tags, log_text_widget, output_folder):
    """
    Processes and classifies a single image, saving it in a folder corresponding
    to the predicted tag, and logging the results.

    Parameters:
        - image_path (str): The path to the image file.
        - tags (list of str): List of tags to classify the image against.
        - log_text_widget (ScrolledText): The GUI widget to display log messages.
        - output_folder (str): Path to the output folder where categorized images will be saved.
    """
    try:
        image = Image.open(image_path)
        inputs = processor(text=tags, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)

        # Get probabilities and convert to list for readability
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)[0].tolist()

        # Find the tag with the highest probability
        max_prob_idx = probs.index(max(probs))
        predicted_tag = tags[max_prob_idx]

        # Log each tag with its probability
        log_text_widget.insert("end", f"Image: {os.path.basename(image_path)}\n")
        for tag, prob in zip(tags, probs):
            log_text_widget.insert("end", f" - {tag}: {prob:.2%}\n")
        log_text_widget.see("end")  # Scroll to the end of log

        # Create the folder for the predicted tag if it doesn't exist
        tag_folder = os.path.join(output_folder, predicted_tag)
        os.makedirs(tag_folder, exist_ok=True)

        # Save the image in the predicted tag's folder
        image_copy_path = os.path.join(tag_folder, os.path.basename(image_path))
        image.save(image_copy_path)

    except Exception as e:
        print(e)
        log_text_widget.insert("end", f"Failed to process {os.path.basename(image_path)}: {e}\n")