import os
import traceback
from PIL import Image, PngImagePlugin
from io import BytesIO
import base64
import json
from typing import Any, Optional, Tuple
from nanoid import generate
from utils.http_client import HttpClient
from services.config_service import FILES_DIR


def generate_image_id() -> str:
    """Generate unique image ID"""
    return generate(size=10)  # 生成唯一图片ID


async def get_image_info_and_save(
    url: str,
    file_path_without_extension: str,
    is_b64: bool = False,  # 是否是base64编码
    metadata: Optional[dict[str, Any]] = None,
) -> Tuple[str, int, int, str]:
    """
    Download image from URL or decode base64, convert to PNG and save with metadata

    Args:
        url: Image URL or base64 string
        file_path_without_extension: File path without extension
        is_b64: Whether the url is a base64 string
        metadata: Optional metadata to be saved in PNG info

    Returns:
        tuple[str, int, int, str]: (mime_type, width, height, extension) - always PNG
    """
    try:
        if is_b64:
            image_data = base64.b64decode(url)  # 解码base64字符串
        else:
            # Fetch the image asynchronously
            async with HttpClient.create_aiohttp() as session:  # 创建异步HTTP客户端
                async with session.get(url) as response:  # 获取图片内容
                    # Read the image content as bytes
                    image_data = await response.read()  # 读取图片内容

        # Open image to get info
        image = Image.open(BytesIO(image_data))
        width, height = image.size  # 获取图片宽度和高度

        # Store original format for debugging
        original_format = image.format or 'Unknown'  # 获取图片格式
        print(f"Converting {original_format} image to PNG: {width}x{height}")

        # Handle different color modes properly for PNG conversion
        if image.mode == 'P':  # 调色板模式
            # Palette mode - convert to RGBA to preserve potential transparency
            if 'transparency' in image.info:  # 如果图片有透明度
                image = image.convert('RGBA')  # 转换为RGBA模式
            else:
                image = image.convert('RGB')  # 转换为RGB模式
        elif image.mode == 'LA':  # 灰度模式
            # Grayscale with alpha - convert to RGBA
            image = image.convert('RGBA')  # 转换为RGBA模式
        elif image.mode == 'L':
            # Grayscale - can stay as L or convert to RGB
            # PNG supports grayscale, so we can keep it
            pass
        elif image.mode == 'CMYK':
            # CMYK mode - convert to RGB
            image = image.convert('RGB')  # 转换为RGB模式
        elif image.mode in ('RGB', 'RGBA'):
            # Already compatible with PNG
            pass
        else:
            # For any other modes, convert to RGB as a safe fallback
            print(f"Warning: Unusual color mode {image.mode}, converting to RGB")
            image = image.convert('RGB')

        # Unified format: always PNG
        extension = 'png'
        mime_type = 'image/png'

        # Prepare PNG info for metadata
        pnginfo = PngImagePlugin.PngInfo()

        # Add original format info
        pnginfo.add_text("original_format", original_format)  # 添加原始格式信息

        if metadata:
            for key, value in metadata.items():
                try:
                    # Handle different value types
                    if isinstance(value, (dict, list)):
                        # Serialize complex types as JSON
                        text_value = json.dumps(value, ensure_ascii=False)
                    elif value is None:
                        text_value = "null"
                    else:
                        # Convert to string
                        text_value = str(value)

                    pnginfo.add_text(str(key), text_value)
                except Exception as e:
                    print(f"Warning: Failed to add metadata key '{key}': {e}")
                    traceback.print_stack()

        # Save as PNG with metadata
        file_path = (
            f"{file_path_without_extension}.{extension}"  # 最终图片保存的文件路径
        )

        # Save with optimizations and metadata
        if metadata or original_format != 'PNG':
            image.save(file_path, format='PNG', optimize=True, pnginfo=pnginfo)
        else:
            image.save(file_path, format='PNG', optimize=True)

        print(f"Successfully saved as PNG: {file_path}")
        return mime_type, width, height, extension

    except Exception as e:
        print(f"Error processing image: {e}")
        raise e


# Canvas-related utilities have been moved to tools/image_generation/image_canvas_utils.py


# Canvas element generation moved to tools/image_generation/image_canvas_utils.py


# Canvas saving functionality moved to tools/image_generation/image_canvas_utils.py


# Image generation orchestration moved to tools/image_generation/image_generation_core.py
# Notification functions moved to tools/image_generation/image_canvas_utils.py


async def process_input_image(input_image: str | None) -> str | None:
    """
    Process input image and convert to base64 format

    Args:
        input_image: Image file path

    Returns:
        Base64 encoded image with data URL, or None if no image
    """
    if not input_image:
        return None

    try:
        full_path = os.path.join(FILES_DIR, input_image)
        if not os.path.exists(full_path):
            print(f"Warning: Image file not found: {full_path}")
            return None

        image = Image.open(full_path)
        ext = os.path.splitext(input_image)[1].lower()
        mime_type_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
        }
        mime_type = mime_type_map.get(ext, 'image/jpeg')

        with BytesIO() as output:
            image.save(output, format=str(mime_type.split('/')[1]).upper())  # 保存图片
            compressed_data = output.getvalue()  # 获取压缩后的数据
            b64_data = base64.b64encode(compressed_data).decode(
                'utf-8'
            )  # 将压缩后的数据编码为base64

        data_url = f"data:{mime_type};base64,{b64_data}"  # 生成data URL
        return data_url  # 返回data URL

    except Exception as e:
        print(f"Error processing image {input_image}: {e}")
        return None
