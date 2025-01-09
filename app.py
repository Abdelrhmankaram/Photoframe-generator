import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper
import io
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Set the title for the Streamlit app
st.title("Photo Upload, Clipping, and Frame Adding App")

# Add a file uploader to the Streamlit app
uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Open the uploaded image file in its original quality
    original_image = Image.open(uploaded_file).convert("RGBA")

    # Resize the image to fit within a defined size for the cropper (temporary)
    cropper_size = 500  # Maximum size (width or height) for the cropper
    temp_image = original_image.copy()
    temp_image.thumbnail((cropper_size, cropper_size), Image.Resampling.LANCZOS)

    # Display the cropper directly on the resized image
    st.write("Adjust the crop box to a 1:1 aspect ratio and click 'Generate Image with Frame'.")
    cropped_preview = st_cropper(
        temp_image,
        aspect_ratio=(1, 1),
        return_type="box",
        box_color="blue",
    )

    # Button to generate the cropped image with the frame
    if st.button("Generate Image with Frame"):
        if cropped_preview:
            # Calculate the scaling factor to revert the crop box to the original image size
            scale_factor_x = original_image.width / temp_image.width
            scale_factor_y = original_image.height / temp_image.height

            # Get the crop coordinates and apply scaling
            crop_box = (
                int(cropped_preview["left"] * scale_factor_x),
                int(cropped_preview["top"] * scale_factor_y),
                int((cropped_preview["left"] + cropped_preview["width"]) * scale_factor_x),
                int((cropped_preview["top"] + cropped_preview["height"]) * scale_factor_y),
            )

            # Crop the original high-quality image using the calculated coordinates
            cropped_image = original_image.crop(crop_box)

            # Load the fixed frame (ensure the frame exists in the directory)
            try:
                frame = Image.open("birthday-card.png").convert("RGBA")
            except FileNotFoundError:
                st.error("Frame file not found. Ensure 'frame.webp' is in the working directory.")
                st.stop()

            # Resize the cropped image to be smaller than the frame (e.g., 70% of the frame's size)
            resized_cropped_image = cropped_image.resize(
                (int(frame.width), int(frame.height)), Image.Resampling.LANCZOS
            )

            # Calculate position to center the cropped image on the frame
            offset = (
                (frame.width - resized_cropped_image.width) // 2,
                (frame.height - resized_cropped_image.height) // 2,
            )

            # Create a new image with a transparent background and paste the cropped image first
            combined_image = Image.new("RGBA", frame.size)
            combined_image.paste(resized_cropped_image, offset, resized_cropped_image)

            # Paste the frame on top of the cropped image
            combined_image.paste(frame, (0, 0), frame)

            # Display the combined image
            st.image(combined_image, caption="Cropped Image with Frame", use_container_width=True)

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
            st.warning("Please adjust the crop box before generating the image.")
else:
    st.write("Please upload an image file to start.")
