"""Entry point: read config.yaml, denoise every image in the input dir."""

import sys
from pathlib import Path

import cv2

from config_loader import load_config
from bilateral import BilateralDenoiser
from non_local_means import NonLocalMeansDenoiser
from dark_frame import DarkFrameSubtractor


def app_dir() -> Path:
    """
    Directory the app should treat as 'home' for relative paths
    (config.yaml, ./images/...). Works both as a plain script and as
    a PyInstaller-built exe, regardless of the shell's cwd at launch.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def get_denoiser(cfg):
    if cfg.method == "bilateral":
        b = cfg.bilateral
        return BilateralDenoiser(b.diameter, b.sigma_color, b.sigma_space)
    elif cfg.method == "non_local_means":
        n = cfg.non_local_means
        return NonLocalMeansDenoiser(n.h, n.template_window_size, n.search_window_size)
    else:
        raise ValueError(f"Unknown method: {cfg.method}")


def find_images(input_dir: str, extensions: list[str]) -> list[Path]:
    input_path = Path(input_dir)
    return sorted(
        p for p in input_path.iterdir()
        if p.is_file() and p.suffix.lower() in extensions
    )


def main():
    default_config = app_dir() / "config.yaml"
    config_path = sys.argv[1] if len(sys.argv) > 1 else str(default_config)
    cfg = load_config(config_path)

    config_dir = Path(config_path).resolve().parent

    def resolve(p: str) -> Path:
        """Relative paths in config.yaml are resolved against the config file's folder."""
        path = Path(p)
        return path if path.is_absolute() else (config_dir / path)

    denoiser = get_denoiser(cfg)

    dark_subtractor = None
    if cfg.dark_frame.enabled:
        dark_subtractor = DarkFrameSubtractor(cfg.dark_frame.path)
        print(f"Dark frame subtraction: ENABLED ({cfg.dark_frame.path})")

    output_dir = resolve(cfg.output.directory) / cfg.method
    output_dir.mkdir(parents=True, exist_ok=True)

    input_dir = resolve(cfg.input.directory)
    images = find_images(str(input_dir), cfg.input.extensions)
    if not images:
        print(f"No images found in '{input_dir}' with extensions {cfg.input.extensions}")
        return

    print(f"Found {len(images)} image(s). Using method: {cfg.method}")
    print(f"Output directory: {output_dir}")

    success, failed = 0, 0
    for img_path in images:
        try:
            image = cv2.imread(str(img_path))
            if image is None:
                raise ValueError("cv2.imread returned None (unreadable/corrupt file)")

            if dark_subtractor is not None:
                image = dark_subtractor.subtract(image)

            result = denoiser.denoise(image)

            out_name = f"{img_path.stem}{cfg.output.suffix}{img_path.suffix}"
            out_path = output_dir / out_name
            cv2.imwrite(str(out_path), result)

            print(f"  OK: {img_path.name} -> {out_path.name}")
            success += 1
        except Exception as e:
            print(f"  FAILED: {img_path.name} ({e})")
            failed += 1

    print(f"\nDone. {success} succeeded, {failed} failed.")


if __name__ == "__main__":
    main()