import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io

# Set the title for the Streamlit app
st.title("Photo Upload, Clipping, and Frame Adding App")

# Add a file uploader to the Streamlit app
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Open the uploaded image file
    original_image = Image.open(uploaded_file)

    # Resize the image for cropping preview (better for smaller screens)
    max_preview_width = 300
    aspect_ratio = original_image.height / original_image.width
    new_preview_height = int(max_preview_width * aspect_ratio)
    preview_image = original_image.resize(
        (max_preview_width, new_preview_height), Image.Resampling.LANCZOS
    )

    st.write("Adjust the crop box to a 1:1 aspect ratio and click 'Crop Image'.")
    
    # Display the cropper with the resized preview image
    cropped_preview = st_cropper(preview_image, aspect_ratio=(1, 1), return_type="box")

    if cropped_preview:
        # Map crop coordinates to the original high-resolution image
        crop_box = (
            int(cropped_preview["left"] * original_image.width / preview_image.width),
            int(cropped_preview["top"] * original_image.height / preview_image.height),
            int(cropped_preview["width"] * original_image.width / preview_image.width)
            + int(cropped_preview["left"] * original_image.width / preview_image.width),
            int(cropped_preview["height"] * original_image.height / preview_image.height)
            + int(cropped_preview["top"] * original_image.height / preview_image.height),
        )
        
        # Crop the original high-quality image using the mapped coordinates
        cropped_image = original_image.crop(crop_box)
        st.image(cropped_image, caption="Cropped Image", use_column_width=True)

        # Load the fixed frame file (frame.webp)
        frame = Image.open("frame.webp")

        # Ensure both images are in RGBA mode
        cropped_image = cropped_image.convert("RGBA")
        frame = frame.convert("RGBA")

        # Resize the frame to match the cropped image dimensions
        frame = frame.resize(cropped_image.size, Image.Resampling.LANCZOS)

        # Combine the cropped image and the frame
        combined_image = Image.alpha_composite(cropped_image, frame)

        # Display the combined image
        st.image(combined_image, caption="Cropped Image with Frame", use_column_width=True)

        # Add a download button for the combined image
        combined_image_io = io.BytesIO()
        combined_image.save(combined_image_io, format="PNG")
        combined_image_io.seek(0)  # Reset the stream position
        st.download_button(
            label="Download Image with Frame",
            data=combined_image_io,
            file_name="image_with_frame.png",
            mime="image/png",
        )
else:
    st.write("Please upload an image file to start.")
