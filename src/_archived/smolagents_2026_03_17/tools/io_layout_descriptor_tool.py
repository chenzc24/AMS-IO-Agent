#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IO Layout Image Descriptor Tool
Uses OpenRouter API with Gemini 3 Pro to generate text descriptions from IO layout images.
"""

import os
import base64
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from smolagents import tool

# Load .env from repository root
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)


def _get_openrouter_config():
    """Get OpenRouter API configuration from environment variables.
    
    Uses multiple sources in priority order:
    1. IMAGE_API_* variables (from .env, consistent with image_vision_tool)
    2. MODEL configuration from .env (via MODELNAME_API_* pattern)
    3. OPENROUTER_* variables (backward compatibility)
    
    Returns:
        tuple: (base_url, api_key, model_id) or (None, None, None) if not found
        
    Environment variables (in order of preference):
    - IMAGE_API_BASE: Image API base URL (from .env, preferred)
    - IMAGE_API_KEY: Image API key (from .env, preferred)
    - IMAGE_MODEL: Image model ID (from .env, optional)
    - MODELNAME_API_BASE: Model API base URL (from .env MODEL config)
    - MODELNAME_API_KEY: Model API key (from .env MODEL config)
    - MODELNAME_MODEL_ID: Model ID (from .env MODEL config)
    - OPENROUTER_API_KEY: OpenRouter API key (fallback)
    - OPENROUTER_BASE_URL: OpenRouter base URL (fallback, optional, defaults to https://openrouter.ai/api/v1)
    """
    # Priority 1: IMAGE_API_* variables (from .env file, consistent with image_vision_tool)
    api_key = os.environ.get("IMAGE_API_KEY")
    base_url = os.environ.get("IMAGE_API_BASE")
    model_id = os.environ.get("IMAGE_MODEL")
    
    # Priority 2: Try to use MODEL configuration from .env
    # Look for any MODEL configuration that might be suitable
    if not api_key or not base_url:
        # Try to find a model config - check for common model prefixes
        # User can specify which model to use via IMAGE_MODEL_NAME env var
        model_name = os.environ.get("IMAGE_MODEL_NAME")  # e.g., "gemini", "openrouter", "qwen"
        
        if model_name:
            # Use specified model configuration
            prefix = model_name.upper().replace('-', '_')
            api_key = api_key or os.environ.get(f"{prefix}_API_KEY")
            base_url = base_url or os.environ.get(f"{prefix}_API_BASE")
            model_id = model_id or os.environ.get(f"{prefix}_MODEL_ID")
        else:
            # Auto-detect: try common model prefixes
            for prefix in ["GEMINI", "OPENROUTER", "QWEN", "CLAUDE", "GPT4O", "GPT4"]:
                if not api_key:
                    api_key = os.environ.get(f"{prefix}_API_KEY")
                if not base_url:
                    base_url = os.environ.get(f"{prefix}_API_BASE")
                if not model_id:
                    model_id = os.environ.get(f"{prefix}_MODEL_ID")
                if api_key and base_url:
                    break
    
    # Priority 3: Fallback to OPENROUTER_* variables for backward compatibility
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY")
    if not base_url:
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    if not api_key:
        return None, None, None
    
    # If base_url is still None after fallback, use default
    if not base_url:
        base_url = "https://openrouter.ai/api/v1"
    
    # Default model_id if not specified
    if not model_id:
        model_id = "google/gemini-3-pro-preview"  # Default model for this tool
    
    return base_url, api_key, model_id


def _encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def _get_image_mime_type(image_path: str) -> str:
    """Get MIME type for image file.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        MIME type string (e.g., 'image/png', 'image/jpeg')
    """
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    return mime_types.get(ext, 'image/png')


def _load_image_vision_instruction() -> str:
    """Load external image vision instruction markdown.

    Returns:
        Instruction text from image_vision_instruction.md, or empty string if unavailable.
    """
    try:
        instruction_path = Path(__file__).with_name("image_vision_instruction.md")
        if instruction_path.exists() and instruction_path.is_file():
            return instruction_path.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return ""


@tool
def describe_io_layout_image(image_path: str, detailed: bool = True) -> str:
    """
    Analyze IO Ring layout image and generate schematic configuration file using Gemini 3 Pro with reasoning.
    
    This tool acts as a Senior Analog IC Layout Engineer to:
    - Detect topology (Single-Ring or Double-Ring)
    - Extract signals in strict counter-clockwise order:
      * Left: Top-Corner → Bottom-Corner
      * Bottom: Left-Corner → Right-Corner  
      * Right: Bottom-Corner → Top-Corner (upwards)
      * Top: Right-Corner → Left-Corner (right-to-left)
    - Generate configuration in the required format for Cadence Virtuoso IO ring design
    
    The tool uses reasoning mode for accurate signal extraction and verification.
    
    Args:
        image_path: Path to the IO layout image file (PNG, JPEG, etc.)
        detailed: If True, uses reasoning mode with verification step. If False, single pass analysis.
        
    Returns:
        String in the format:
        Task: Generate IO ring schematic and layout design for Cadence Virtuoso.
        Design requirements: [pad count description]. [Single/Double] ring layout. Order: counterclockwise...
        SIGNAL CONFIGURATION
        Signal names: [signal list]
        Additionally, please insert inner ring pads: [inner ring logic if Double Ring]
        
        Pad count description format:
        - If all sides same: "[count] pads per side."
        - If different: "[count1] pads on left and right sides, [count2] pads on top and bottom sides."
        
    Example:
        describe_io_layout_image("output/generated/20251216_155455/io_ring_layout_visualization.png")
    """
    try:
        # Validate image path
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            return f"❌ Error: Image file not found: {image_path}"
        
        if not image_path_obj.is_file():
            return f"❌ Error: Path is not a file: {image_path}"
        
        # Get API configuration (supports IMAGE_API_*, MODEL config, or OPENROUTER_*)
        base_url, api_key, model_id = _get_openrouter_config()
        if not base_url or not api_key:
            return "❌ Error: API configuration not found. Please set one of:\n" \
                   "  - IMAGE_API_KEY and IMAGE_API_BASE (from .env)\n" \
                   "  - MODELNAME_API_KEY and MODELNAME_API_BASE (from .env MODEL config)\n" \
                   "  - OPENROUTER_API_KEY (fallback)\n" \
                   "You can also set IMAGE_MODEL_NAME to specify which MODEL config to use."
        
        # Initialize OpenAI client
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        
        # Encode image to base64
        try:
            image_base64 = _encode_image_to_base64(str(image_path_obj))
            mime_type = _get_image_mime_type(str(image_path_obj))
        except Exception as e:
            return f"❌ Error: Failed to encode image: {e}"
        
        # Prepare prompt for IO Ring analysis with specific format
        external_instruction = _load_image_vision_instruction()
        default_instruction = """Role: Senior Analog IC Layout Engineer.

    Task: Analyze the attached IO Ring image (which may be Single-Ring or Double-Ring) and generate a schematic configuration file.

    **Step 1: Topology Detection**

    - Examine the center area inside the boundary ring.

    - **Double Ring:** If there are colored pads/blocks floating *inside* the main boundary, treat as "Double Ring".

    - **Single Ring:** If the center is empty (white space/grid lines only), treat as "Single Ring".

    **Step 2: Signal Extraction Rules (Strict Counter-Clockwise)**

    You must extract signals in this specific physical order. Do not follow standard text reading direction for Right/Top sides.

    1. **Left Side:** Read from **Top-Corner** down to **Bottom-Corner**.

    2. **Bottom Side:** Read from **Left-Corner** across to **Right-Corner**.

    3. **Right Side:** Read from **Bottom-Corner** up to **Top-Corner**. (CRITICAL: Read upwards!)

    4. **Top Side:** Read from **Right-Corner** across to **Left-Corner**. (CRITICAL: Read right-to-left!)

    **Step 3: Output Generation**

    - Combine all signals from Step 2 into a single list under `Signal names`.

    - **If Double Ring:** Under "Additionally...", list the inner pads. Use the syntax: "insert an inner ring pad [Inner_Name] between [Outer_Pad_A] and [Outer_Pad_B]" based on visual alignment.

    - **If Single Ring:** Leave the "Additionally..." section empty or write "None".

    - **neglect the devices named "PFILLER*".

    **Output Template:**

    Please strictly follow this format:

    Task: Generate IO ring schematic and layout design for Cadence Virtuoso.

    Design requirements:
    [Insert pad count description]. [Single/Double] ring layout. Order: counterclockwise through left side, bottom side, right side, top side.

    **Pad count description format:**
    - If all sides have the same count: "[count] pads per side."
    - If sides have different counts: "[count1] pads on left and right sides, [count2] pads on top and bottom sides."
      Example: "10 pads on left and right sides, 6 pads on top and bottom sides."

    ======================================================================
    SIGNAL CONFIGURATION
    ======================================================================

    Signal names: [Insert the list of Outer Ring signals here, separated by spaces]

    Additionally, please insert inner ring pads:
    [Insert Inner Ring logic here if Double Ring, otherwise leave blank]"""

        prompt_text = external_instruction if external_instruction else default_instruction
        user_content = [
            {
                "type": "text",
            "text": prompt_text
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_base64}"
                }
            }
        ]
        
        # Single API call with reasoning enabled
        # The prompt already includes detailed instructions, and reasoning mode allows the model
        # to self-verify during the reasoning process
        try:
            # Use model_id from config, or default
            actual_model_id = model_id if model_id else "google/gemini-3-pro-preview"
            
            # Try with reasoning first, fallback to normal if it fails
            try:
                response = client.chat.completions.create(
                    model=actual_model_id,
                    messages=[
                        {
                            "role": "user",
                            "content": user_content
                        }
                    ],
                    extra_body={"reasoning": {"enabled": True}}
                )
            except Exception as reasoning_error:
                # If reasoning mode fails, try without it
                print(f"⚠️ Reasoning mode failed: {reasoning_error}, trying without reasoning...")
                response = client.chat.completions.create(
                    model=actual_model_id,
                    messages=[
                        {
                            "role": "user",
                            "content": user_content
                        }
                    ]
                )
            
            # Validate response structure
            if response is None:
                return "❌ Error: OpenRouter API returned None response"
            
            # Check for API errors first (before checking choices)
            if hasattr(response, 'error') and response.error is not None:
                error_info = response.error
                error_message = error_info.get('message', 'Unknown error') if isinstance(error_info, dict) else str(error_info)
                
                # Extract detailed error from metadata if available
                detailed_error = ""
                if isinstance(error_info, dict) and 'metadata' in error_info:
                    metadata = error_info['metadata']
                    if isinstance(metadata, dict) and 'raw' in metadata:
                        try:
                            import json
                            raw_error = json.loads(metadata['raw'])
                            if 'error' in raw_error:
                                detailed_error = raw_error['error'].get('message', '')
                        except:
                            detailed_error = metadata.get('raw', '')
                
                provider = error_info.get('provider_name', 'Unknown') if isinstance(error_info, dict) else 'Unknown'
                
                if detailed_error:
                    return f"❌ Error: {error_message}\n\nProvider: {provider}\nDetails: {detailed_error}\n\nNote: This may be due to API restrictions (e.g., geographic location, model availability, or API key permissions)."
                else:
                    return f"❌ Error: {error_message}\n\nProvider: {provider}\n\nNote: This may be due to API restrictions (e.g., geographic location, model availability, or API key permissions)."
            
            # Debug: Print response type and attributes
            if not hasattr(response, 'choices'):
                return f"❌ Error: Response has no 'choices' attribute. Response type: {type(response)}, Attributes: {dir(response)}"
            
            if response.choices is None:
                # Check if there's an error field we missed
                if hasattr(response, 'error'):
                    return f"❌ Error: API returned error. Response.choices is None. Error: {response.error}"
                return f"❌ Error: Response.choices is None. Response: {response}"
            
            if len(response.choices) == 0:
                return f"❌ Error: API response contains no choices. Response: {response}"
            
            choice = response.choices[0]
            if not hasattr(choice, 'message'):
                return f"❌ Error: Choice has no 'message' attribute. Choice: {choice}, Type: {type(choice)}"
            
            if choice.message is None:
                return f"❌ Error: Choice.message is None. Choice: {choice}"
            
            # Extract and return the assistant message
            assistant_message = choice.message
            
            if not hasattr(assistant_message, 'content'):
                return f"❌ Error: Message has no 'content' attribute. Message: {assistant_message}, Type: {type(assistant_message)}"
            
            if assistant_message.content is None:
                return f"❌ Error: Message.content is None. Message: {assistant_message}"
            
            return assistant_message.content
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"❌ Error: Failed to call OpenRouter API: {e}\n\nDetails:\n{error_details}"
            
    except Exception as e:
        return f"❌ Error: {e}"


@tool
def compare_io_layout_images(image_path1: str, image_path2: str) -> str:
    """
    Compare two IO layout images and describe the differences.
    
    Useful for comparing generated layouts with reference designs or checking
    if corrections were applied correctly.
    
    Args:
        image_path1: Path to the first IO layout image
        image_path2: Path to the second IO layout image
        
    Returns:
        String description of differences between the two layouts
        
    Example:
        compare_io_layout_images("output/generated/20251216_155455/io_ring_layout_visualization.png", 
                                 "output/generated/20251216_155242/io_ring_layout_visualization.png")
    """
    try:
        # Validate both image paths
        for img_path in [image_path1, image_path2]:
            img_path_obj = Path(img_path)
            if not img_path_obj.exists():
                return f"❌ Error: Image file not found: {img_path}"
            if not img_path_obj.is_file():
                return f"❌ Error: Path is not a file: {img_path}"
        
        # Get API configuration (supports IMAGE_API_*, MODEL config, or OPENROUTER_*)
        base_url, api_key, model_id = _get_openrouter_config()
        if not base_url or not api_key:
            return "❌ Error: API configuration not found. Please set one of:\n" \
                   "  - IMAGE_API_KEY and IMAGE_API_BASE (from .env)\n" \
                   "  - MODELNAME_API_KEY and MODELNAME_API_BASE (from .env MODEL config)\n" \
                   "  - OPENROUTER_API_KEY (fallback)\n" \
                   "You can also set IMAGE_MODEL_NAME to specify which MODEL config to use."
        
        # Initialize OpenAI client
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        
        # Encode both images
        try:
            image1_base64 = _encode_image_to_base64(image_path1)
            image1_mime = _get_image_mime_type(image_path1)
            image2_base64 = _encode_image_to_base64(image_path2)
            image2_mime = _get_image_mime_type(image_path2)
        except Exception as e:
            return f"❌ Error: Failed to encode images: {e}"
        
        # Prepare comparison prompt
        user_content = [
            {
                "type": "text",
                "text": """Compare these two IO ring layout images and describe the differences. Focus on:

1. **Structural Differences**: Changes in ring dimensions, pad count, placement order
2. **Pad Changes**: Added, removed, or repositioned pads
3. **Signal Changes**: Different signal names or assignments
4. **Device Type Changes**: Changes in pad device types (PDB3AC, PDDW16SDGZ, etc.)
5. **Corner Device Changes**: Differences in corner device placement or types
6. **Layout Quality**: Improvements or regressions in layout quality

Provide a clear, structured comparison."""
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image1_mime};base64,{image1_base64}"
                }
            },
            {
                "type": "text",
                "text": "Second image:"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image2_mime};base64,{image2_base64}"
                }
            }
        ]
        
        # Use model_id from config, or default
        actual_model_id = model_id if model_id else "google/gemini-3-pro-preview"
        
        # Call API with reasoning
        try:
            response = client.chat.completions.create(
                model=actual_model_id,
                messages=[
                    {
                        "role": "user",
                        "content": user_content
                    }
                ],
                extra_body={"reasoning": {"enabled": True}}
            )
            
            # Validate response structure
            if response is None:
                return "❌ Error: OpenRouter API returned None response"
            
            # Check for API errors first
            if hasattr(response, 'error') and response.error is not None:
                error_info = response.error
                error_message = error_info.get('message', 'Unknown error') if isinstance(error_info, dict) else str(error_info)
                
                # Extract detailed error from metadata if available
                detailed_error = ""
                if isinstance(error_info, dict) and 'metadata' in error_info:
                    metadata = error_info['metadata']
                    if isinstance(metadata, dict) and 'raw' in metadata:
                        try:
                            import json
                            raw_error = json.loads(metadata['raw'])
                            if 'error' in raw_error:
                                detailed_error = raw_error['error'].get('message', '')
                        except:
                            detailed_error = metadata.get('raw', '')
                
                provider = error_info.get('provider_name', 'Unknown') if isinstance(error_info, dict) else 'Unknown'
                
                if detailed_error:
                    return f"❌ Error: {error_message}\n\nProvider: {provider}\nDetails: {detailed_error}\n\nNote: This may be due to API restrictions (e.g., geographic location, model availability, or API key permissions)."
                else:
                    return f"❌ Error: {error_message}\n\nProvider: {provider}\n\nNote: This may be due to API restrictions (e.g., geographic location, model availability, or API key permissions)."
            
            if not hasattr(response, 'choices') or response.choices is None or len(response.choices) == 0:
                return f"❌ Error: Invalid API response structure. Response: {response}"
            
            if not hasattr(response.choices[0], 'message') or response.choices[0].message is None:
                return f"❌ Error: Invalid message structure in response"
            
            message = response.choices[0].message
            if not hasattr(message, 'content') or message.content is None:
                return f"❌ Error: Message has no content"
            
            return message.content
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"❌ Error: Failed to call OpenRouter API: {e}\n\nDetails:\n{error_details}"
            
    except Exception as e:
        return f"❌ Error: {e}"


__all__ = ['describe_io_layout_image', 'compare_io_layout_images']

