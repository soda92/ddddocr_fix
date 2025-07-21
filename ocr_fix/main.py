import os
import sys


def get_venv_site_packages(project_root):
    """
    Attempts to find the site-packages directory within a .venv.
    """
    venv_path = os.path.join(project_root, ".venv")
    if not os.path.exists(venv_path):
        print(f"Error: Virtual environment not found at {venv_path}", file=sys.stderr)
        print("Please ensure your .venv is in the project root.", file=sys.stderr)
        sys.exit(1)

    # Common paths for site-packages in a venv
    # Linux/macOS: .venv/lib/pythonX.Y/site-packages
    # Windows: .venv/Lib/site-packages
    for root, dirs, files in os.walk(venv_path):
        if "site-packages" in dirs:
            return os.path.join(root, "site-packages")
    return None


def generate_pyinstaller_datas(project_root):
    site_packages_path = get_venv_site_packages(project_root)

    if not site_packages_path:
        print(
            "Error: Could not find 'site-packages' in your virtual environment.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Detected site-packages: {site_packages_path}\n")
    print("Add the following to the 'datas=[]' list in your .spec file:\n")

    datas_entries = []

    # --- ddddocr models ---
    ddddocr_dir = os.path.join(site_packages_path, "ddddocr")
    if os.path.exists(ddddocr_dir):
        # Common ddddocr model files
        ddddocr_models = ["common_old.onnx", "common.onnx"]
        for model in ddddocr_models:
            model_path = os.path.join(ddddocr_dir, model)
            if os.path.exists(model_path):
                # Destination in bundle is 'ddddocr' because the models are directly in the package root
                datas_entries.append((model_path, "ddddocr"))
            else:
                print(
                    f"Warning: ddddocr model not found: {model_path}", file=sys.stderr
                )
    else:
        print(
            f"Warning: ddddocr not found in site-packages: {ddddocr_dir}",
            file=sys.stderr,
        )

    # --- onnxruntime specific DLLs/shared libraries ---
    # This is for Windows, for Linux/macOS, the equivalent might be .so or .dylib
    # Onnxruntime often has a 'capi' directory with runtime components
    onnxruntime_capi_dir = os.path.join(site_packages_path, "onnxruntime", "capi")
    if os.path.exists(onnxruntime_capi_dir):
        # Look for the shared library. On Windows it's .dll, on Linux it's .so, macOS .dylib
        # We'll try to find common ones.
        for item in os.listdir(onnxruntime_capi_dir):
            if item.startswith("onnxruntime_providers_") and (
                item.endswith(".dll") or item.endswith(".so") or item.endswith(".dylib")
            ):
                datas_entries.append(
                    (
                        os.path.join(onnxruntime_capi_dir, item),
                        os.path.join("onnxruntime", "capi"),
                    )
                )
            elif item == "onnxruntime_pybind11_state.pyd" and sys.platform == "win32":
                datas_entries.append(
                    (
                        os.path.join(onnxruntime_capi_dir, item),
                        os.path.join("onnxruntime", "capi"),
                    )
                )
            elif (
                item.endswith(".so") and sys.platform != "win32"
            ):  # Generic .so for non-Windows
                datas_entries.append(
                    (
                        os.path.join(onnxruntime_capi_dir, item),
                        os.path.join("onnxruntime", "capi"),
                    )
                )
    else:
        print(
            f"Warning: onnxruntime\\capi not found in site-packages: {onnxruntime_capi_dir}",
            file=sys.stderr,
        )

    # Print the generated entries
    for source, dest in datas_entries:
        # Get relative path from project root for portability
        relative_source = os.path.relpath(source, project_root)
        # Use forward slashes for consistency in spec files
        print(
            f"    ('{relative_source.replace(os.sep, '/')}', '{dest.replace(os.sep, '/')}'),"
        )


def main():
    # Assuming the script is run from the project root
    project_root = os.getcwd()
    generate_pyinstaller_datas(project_root)


if __name__ == "__main__":
    main()
