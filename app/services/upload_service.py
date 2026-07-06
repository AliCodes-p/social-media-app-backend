import cloudinary.uploader
import app.core.cloudinary


def upload_image(file, folder: str = "posts"):
    result = cloudinary.uploader.upload(
        file.file,
        folder=folder,
    )

    return result["secure_url"]