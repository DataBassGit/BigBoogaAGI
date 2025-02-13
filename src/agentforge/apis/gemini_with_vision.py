import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from agentforge.utils.logger import Logger
import base64
import numpy as np
from PIL import Image
from typing import Union, List, Any
from io import BytesIO
from .base_api import BaseModel
import requests

# Get API key from Env
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


class Gemini_With_Vision(BaseModel):
    """
    A class for interacting with Google's Generative AI models to generate text based on provided prompts and images.
    
    This class extends BaseModel to handle both text and vision inputs for Gemini models. It supports various image input
    formats and provides comprehensive error handling and validation.

    Args:
        model_name (str): The name of the Gemini model to use (e.g., "gemini-1.5-flash", "gemini-pro-vision")
        **kwargs: Additional keyword arguments passed to the base class

    Supported Image Formats:
        - JPEG/JPG
        - PNG
        - GIF
        - WEBP

    Image Input Types:
        - URL to image (str)
        - File path (str)
        - Base64 encoded string
        - Bytes object
        - PIL Image object
        - NumPy array

    Usage:
        ```python
        # Initialize the model
        model = Gemini_With_Vision("gemini-1.5-flash")

        # Text-only generation
        response = model.generate_response({
            "System": "You are a helpful assistant.",
            "User": "What is the capital of France?"
        })

        # Image from URL
        response = model.generate_response({
            "System": "Analyze this image.",
            "User": "What do you see?"
        }, image_parts="https://example.com/image.jpg")

        # Image from local file
        from PIL import Image
        image = Image.open("path/to/image.jpg")
        
        response = model.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image?"
        }, image_parts=image)

        # Multiple images
        response = model.generate_response({
            "System": "Compare these images.",
            "User": "What are the differences?"
        }, image_parts=[image1, image2])
        ```

    Notes:
        - Maximum image size: 20MB
        - For optimal performance, ensure images are in supported formats
        - When using multiple images, provide them as a list in image_parts
        - URLs must start with 'http://' or 'https://' and have a 10-second timeout
    """

    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        self._model = genai.GenerativeModel(model_name)

    @staticmethod
    def _prepare_prompt(model_prompt):
        return '\n\n'.join([model_prompt.get('system', ''), model_prompt.get('user', '')])

    def _process_image_input(self, image_input: Union[str, bytes, Image.Image, np.ndarray]) -> Any:
        """
        Process different types of image inputs into a format acceptable by Gemini.
        
        Parameters:
            image_input: Can be:
                - URL to image (str)
                - Path to image file (str)
                - Base64 encoded image string
                - Bytes object
                - PIL Image object
                - NumPy array
        
        Returns:
            Processed image in a format acceptable by Gemini
        """
        try:
            # Verify file type and size before processing
            def verify_image(img: Image.Image) -> bool:
                """Verify image format and size"""
                allowed_formats = {'JPEG', 'JPG', 'PNG', 'GIF', 'WEBP'}
                max_size = 20 * 1024 * 1024  # 20MB limit
                
                # Check format
                if img.format and img.format.upper() not in allowed_formats:
                    self.logger.log(f"Unsupported image format: {img.format}", 'warning')
                    return False
                
                # Check file size
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format=img.format or 'PNG')
                size = img_byte_arr.tell()
                if size > max_size:
                    self.logger.log(f"Image size ({size/1024/1024:.2f}MB) exceeds 20MB limit", 'warning')
                    return False
                
                return True

            self.logger.log(f"Processing image input of type: {type(image_input)}", 'info')

            if isinstance(image_input, str):
                # Check if it's a URL
                if image_input.startswith(('http://', 'https://')):
                    self.logger.log(f"Downloading image from URL: {image_input}", 'info')
                    response = requests.get(image_input, timeout=10)
                    response.raise_for_status()  # Raise exception for bad status codes
                    img = Image.open(BytesIO(response.content))
                # Check if it's a base64 string
                elif image_input.startswith(('data:image', 'base64:')):
                    self.logger.log("Processing base64 encoded image", 'info')
                    # Extract the base64 data
                    base64_data = image_input.split('base64,')[-1]
                    image_bytes = base64.b64decode(base64_data)
                    img = Image.open(BytesIO(image_bytes))
                else:
                    # Assume it's a file path
                    self.logger.log(f"Loading image from path: {image_input}", 'info')
                    img = Image.open(image_input)
            
            elif isinstance(image_input, bytes):
                self.logger.log("Processing bytes input", 'info')
                img = Image.open(BytesIO(image_input))
            
            elif isinstance(image_input, np.ndarray):
                self.logger.log("Processing NumPy array input", 'info')
                img = Image.fromarray(image_input)
            
            elif isinstance(image_input, Image.Image):
                self.logger.log("Processing PIL Image input", 'info')
                img = image_input
            
            else:
                error_msg = f"Unsupported image input type: {type(image_input)}"
                self.logger.log(error_msg, 'error')
                raise ValueError(error_msg)

            # Verify the processed image
            if not verify_image(img):
                error_msg = "Image verification failed"
                self.logger.log(error_msg, 'error')
                raise ValueError(error_msg)

            self.logger.log(f"Successfully processed image: {img.format} {img.size}", 'info')
            return img
                
        except Exception as e:
            error_msg = f"Error processing image input: {str(e)}"
            self.logger.log(error_msg, 'error')
            raise

    def _do_api_call(self, prompt, **filtered_params):
        # Combine text prompt with images if provided
        content = [prompt]
        image_parts = filtered_params.pop('images', None)
        
        if image_parts is not None:
            # Convert single image to list for uniform processing
            if not isinstance(image_parts, list):
                image_parts = [image_parts]
            
            # Process each image input
            processed_images = []
            for img in image_parts:
                try:
                    processed_img = self._process_image_input(img)
                    processed_images.append(processed_img)
                except Exception as e:
                    self.logger.log(f"Error processing image: {str(e)}", 'error')
                    continue
            
            content.extend(processed_images)

        response = self._model.generate_content(
            content,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=filtered_params.get("max_new_tokens", 2048),
                temperature=filtered_params.get("temperature", 0.7),
                top_p=filtered_params.get("top_p", 1),
                top_k=filtered_params.get("top_k", 1),
                candidate_count=max(filtered_params.get("candidate_count", 1), 1)
            )
        )
        return response

    def _process_response(self, raw_response):
        return raw_response.text

    def generate_response(self, model_prompt, image_parts=None, **params):
        """Wrapper method to maintain backward compatibility"""
        return self.generate(model_prompt, image_parts=image_parts, **params)


if __name__ == "__main__":
    # Initialize the model
    gemini_vision = Gemini_With_Vision("gemini-1.5-flash")

    # Test 1: Text-only input
    print("\n=== Test 1: Text-only Input ===")
    text_response = gemini_vision.generate_response({
        "System": "You are a helpful assistant.",
        "User": "What is the capital of France?"
    }, agent_name="TestAgent")
    print("Response:", text_response)

    # Test 2: Direct URL input
    print("\n=== Test 2: URL Input ===")
    try:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques%2C_Paris_ao%C3%BBt_2014_%282%29.jpg/1200px-La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques%2C_Paris_ao%C3%BBt_2014_%282%29.jpg"
        url_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=image_url, agent_name="TestAgent")
        print("Response:", url_response)
    except Exception as e:
        print(f"Error during URL test: {str(e)}")

    # Test 3: PIL Image input
    print("\n=== Test 3: PIL Image Input ===")
    try:
        from PIL import Image
        import requests
        from io import BytesIO

        # Download and convert to PIL Image
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        vision_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=image, agent_name="TestAgent")
        print("Response:", vision_response)
    except Exception as e:
        print(f"Error during PIL image test: {str(e)}")

    # Test 4: Base64 image input
    print("\n=== Test 4: Base64 Input ===")
    try:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        base64_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=f"data:image/jpeg;base64,{img_str}", agent_name="TestAgent")
        print("Response:", base64_response)
    except Exception as e:
        print(f"Error during base64 image test: {str(e)}")

    # Test 5: NumPy array input
    print("\n=== Test 5: NumPy Array Input ===")
    try:
        import numpy as np
        np_image = np.array(image)
        numpy_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=np_image, agent_name="TestAgent")
        print("Response:", numpy_response)
    except Exception as e:
        print(f"Error during NumPy array test: {str(e)}")

    # Test 6: Format verification
    print("\n=== Test 6: Format Verification ===")
    try:
        temp_image = Image.new('RGB', (100, 100), color='red')
        buffered = BytesIO()
        temp_image.save(buffered, format="BMP")
        bmp_data = buffered.getvalue()
        
        bmp_response = gemini_vision.generate_response({
            "System": "You are a helpful assistant that can analyze images.",
            "User": "What do you see in this image? Please describe it in detail."
        }, image_parts=bmp_data, agent_name="TestAgent")
        print("Response:", bmp_response)
    except Exception as e:
        print(f"Expected error during BMP image test: {str(e)}")