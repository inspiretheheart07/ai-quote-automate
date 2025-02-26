from PIL import Image, ImageDraw, ImageFont, ImageFilter

def wrap_text(draw, text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        text_width, _ = draw.textsize(test_line, font=font)
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line != "":
                lines.append(current_line.strip())
            current_line = word + " "
    if current_line != "":
        lines.append(current_line.strip())
    return lines

def text_on_background(text, background_image_path, font_path, output_image_path='output_image.png', line_height=15, shadow_offset=(5, 5)):
    image = Image.open(background_image_path)
    image = image.convert('RGB')
    image_width, image_height = image.size

    # Crop the image to the required region
    left = (image_width - 1080) // 2
    top = (image_height - 1920) // 2
    right = (image_width + 1080) // 2
    bottom = (image_height + 1920) // 2
    cropped_image = image.crop((left, top, right, bottom))

    draw = ImageDraw.Draw(cropped_image)
    padding_top = 140
    padding_bottom = 70
    padding_left = 10
    padding_right = 190
    available_width = cropped_image.width - padding_left - padding_right
    available_height = cropped_image.height - padding_top - padding_bottom

    font_size = 150
    font = ImageFont.truetype(font_path, font_size)

    # Wrap the text into lines based on available width
    lines = wrap_text(draw, text, font, available_width)

    # Dynamically adjust font size based on available height
    def fit_text_to_height(lines, font, font_size):
        while True:
            total_text_height = sum([draw.textsize(line, font=font)[1] for line in lines])
            total_text_height += (len(lines) - 1) * line_height
            if total_text_height <= available_height:
                break
            font_size -= 10  # Decrease font size if the text exceeds available space
            font = ImageFont.truetype(font_path, font_size)
            lines = wrap_text(draw, text, font, available_width)
        return lines, font

    # Adjust font size
    lines, font = fit_text_to_height(lines, font, font_size)
    
    # Calculate total text height after adjustment
    total_text_height = sum([draw.textsize(line, font=font)[1] for line in lines])
    total_text_height += (len(lines) - 1) * line_height

    # Calculate the starting position for the text to be vertically centered
    position_y = (cropped_image.height - total_text_height) // 2 - (padding_bottom - padding_top) // 2 + padding_top
    position_x = padding_left

    # Draw text with shadow
    for line in lines:
        text_width, text_height = draw.textsize(line, font=font)
        position_x = (cropped_image.width - text_width) // 2
        shadow_position = (position_x + shadow_offset[0], position_y + shadow_offset[1])
        draw.text(shadow_position, line, fill=(50, 50, 50), font=font)
        draw.text((position_x, position_y), line, fill=(255, 255, 255), font=font)
        position_y += text_height + line_height

    # Apply sharpening filter and save the output
    sharpened_image = cropped_image.filter(ImageFilter.SHARPEN)
    sharpened_image.save(output_image_path, 'PNG')
    return output_image_path
