import glob

from typing import Tuple

import magic
from pathlib import Path


def check_file(path_to_file) -> Tuple[Path, bool]:
    """Проверяет тип файла, и добавляет расширение если оно отсутствует."""
    mime_suffix = {"pdf", "tiff", "tif", "jpeg", "jpg", "png", "bmp"}

    file_path = Path(path_to_file)
    suffix = file_path.suffix
    if not suffix or suffix[1:] not in mime_suffix:
        file_mime = magic.from_file(file_path, mime=True)
        new_suffix = file_mime.split("/")[-1]
        if new_suffix not in mime_suffix:
            return file_path, False

        file_path.rename(Path(
            file_path.parent,
            f"{file_path.name}.{new_suffix}")
        )
        return file_path, True

    if suffix[1:] in mime_suffix:
        return file_path, True
    return file_path, False


# a1 = Path("pdf", "test.pdf")
# a2 = Path("pdf", "mime")
# a3 = Path("pdf", "tiff_file.t")
# a4 = Path("pdf", "png_file.p")
# a5 = Path("pdf", "jpeg.j")

# files_path = [a1, a2, a3, a4, a5]

path_to_files = Path("pdf")
print(path_to_files)
all_files = glob.iglob(str(Path(path_to_files, "*")))

for path in all_files:
    path = Path(path)
    print(path)
    if path.is_dir():
        continue
    p, b = check_file(path)
    print(p, b)
