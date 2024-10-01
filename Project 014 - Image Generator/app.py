import streamlit as st
from diffusers import StableDiffusionPipeline
import torch
from PIL import Image
import io

class ImageGenerator:
    def __init__(self, model_name):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("Device set to:", self.device)
        self.pipeline = self.load_model()

    def load_model(self):
        """
        Load the pre-trained Stable Diffusion model.
        """
        print(f"Loading model '{self.model_name}'...")
        # Load the Stable Diffusion model
        pipeline = StableDiffusionPipeline.from_pretrained(
            self.model_name, 
            torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32
        ).to(self.device)
        print("Model loaded successfully.")
        return pipeline

    def generate_image(self, prompt):
        """
        Generate an image based on the given prompt using the pre-trained model.
        """
        if prompt:
            # Generate the image when the user enters a prompt
            image = self.pipeline(prompt, num_inference_steps=30).images[0]
            return image
        return None

# Use a suitable model for deployment with the given hardware
model_name = "stabilityai/stable-diffusion-2-1"  # Optimized model for better performance on good hardware
image_generator = ImageGenerator(model_name)

# Streamlit interface
st.title("Stable Diffusion Image Generator")

# User input for text prompt
prompt = st.text_input("Enter a prompt to generate an image:")

if prompt:
    # Generate the image
    with st.spinner("Generating image..."):
        image = image_generator.generate_image(prompt)

    # Display the generated image
    if image:
        st.image(image, caption="Generated Image", use_column_width=True)
        # Option to download the image
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        st.download_button("Download Image", data=img_byte_arr.getvalue(), file_name="generated_image.png", mime="image/png")
    else:
        st.error("Failed to generate an image. Please try again with a different prompt.")
else:
    st.info("Please enter a prompt to generate an image.")
