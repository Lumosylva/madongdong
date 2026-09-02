from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image

from app.core.config import settings
from app.models.media import MediaType
from app.services.media import (
    _delete_files,
    _get_image_derivative_paths,
    _guess_media_type,
    _validate_image_file,
)


class MediaSecurityTests(unittest.TestCase):
    def test_media_type_is_based_on_mime_type(self) -> None:
        self.assertEqual(_guess_media_type("image/png"), MediaType.IMAGE)
        self.assertEqual(_guess_media_type("video/mp4"), MediaType.VIDEO)
        self.assertEqual(_guess_media_type("application/octet-stream"), MediaType.OTHER)

    def test_image_validation_rejects_dimension_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = Path(temp_dir) / "wide.png"
            Image.new("RGB", (11, 2), "white").save(image_path)
            previous_limit = settings.upload_max_image_dimension
            settings.upload_max_image_dimension = 10
            try:
                with self.assertRaises(ValueError):
                    _validate_image_file(image_path, ".png")
            finally:
                settings.upload_max_image_dimension = previous_limit

    def test_image_derivatives_and_original_are_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            original = Path(temp_dir) / "image.png"
            derivatives = _get_image_derivative_paths(original)
            for path in [original, *derivatives]:
                path.write_bytes(b"test")

            _delete_files([original, *derivatives])

            self.assertFalse(original.exists())
            self.assertTrue(all(not path.exists() for path in derivatives))


if __name__ == "__main__":
    unittest.main()
