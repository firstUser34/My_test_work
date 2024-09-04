import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import zipfile

# Load the certificate template
template_path = "assets/c_iot-1.png"
template = Image.open(template_path)

# Streamlit app layout
st.title("Certificate Generator")

# Input fields for names
names_input = st.text_area("Enter names (one per line or comma-separated)").strip()
names = [name.strip() for name in names_input.replace(',', '\n').splitlines() if name.strip()]

# Input fields for custom font and size
font_file = st.file_uploader("Upload a font file (optional)", type=["ttf", "otf"])
font_size = st.number_input("Font size", min_value=10, max_value=200, value=145, step=1)  # Default font size set to 145

# Input fields for text position
horizontal_position = st.slider("Horizontal position (%)", min_value=0, max_value=100, value=43,
                                step=1)  # Default horizontal position set to 43%
vertical_position = st.slider("Vertical position (%)", min_value=0, max_value=100, value=50,
                              step=1)  # Default vertical position set to 50%


# Function to generate certificates
def generate_certificates(names, font_file, font_size, horizontal_position, vertical_position):
    certificates = []

    for name in names:
        if name:
            # Create a copy of the template
            certificate = template.copy()
            draw = ImageDraw.Draw(certificate)

            # Use default or custom font
            if font_file:
                font = ImageFont.truetype(font_file, font_size)
            else:
                font = ImageFont.truetype("arial.ttf", font_size)

            # Calculate text size and adjust position
            text_bbox = draw.textbbox((0, 0), name, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Calculate horizontal and vertical center positions
            width, height = certificate.size
            x_position = (width * horizontal_position / 100) - (text_width / 2)
            y_position = (height * vertical_position / 100) - (text_height / 2)

            # Draw the name on the template
            draw.text((x_position, y_position), name, font=font, fill="black")

            # Save the certificate to a bytes buffer
            buffer = io.BytesIO()
            certificate.save(buffer, format="PNG")

            # Append the certificate to the list
            certificates.append({
                'name': name,
                'certificate': buffer.getvalue()
            })

    return certificates


# Display certificates
if names:
    certificates = generate_certificates(names, font_file, font_size, horizontal_position, vertical_position)

    # Show the certificates and download options
    for cert in certificates:
        st.image(cert['certificate'], caption=f"Certificate for {cert['name']}")
        st.download_button(
            label=f"Download {cert['name']}'s Certificate",
            data=cert['certificate'],
            file_name=f"{cert['name']}_certificate.png",
            mime="image/png"
        )

    # Provide option to download all certificates as a zip file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for cert in certificates:
            zip_file.writestr(f"{cert['name']}_certificate.png", cert['certificate'])

    zip_buffer.seek(0)
    st.download_button(
        label="Download All Certificates as ZIP",
        data=zip_buffer,
        file_name="certificates.zip",
        mime="application/zip"
    )
else:
    st.error("Please enter at least one name.")
