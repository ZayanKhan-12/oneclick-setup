#!/usr/bin/env bash
set -e

echo "Installing system dependencies on macOS..."

# 1) Update Homebrew quietly. If update fails, log a warning and continue.
if ! command -v brew &>/dev/null; then
  echo "Homebrew not found. Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo "Homebrew found. Updating..."
  brew update --quiet || { echo "Warning: Brew update failed, continuing..."; }
fi

# 2) Install and link Python (using python@3.11 as an example)
if brew ls --versions python@3.11 &>/dev/null; then
  echo "python@3.11 is already installed. Linking it..."
  brew link python@3.11 || true
else
  echo "Installing python@3.11..."
  brew install python@3.11
  brew link python@3.11 || true
fi

# 3) Install other system-level dependencies quietly
brew install git cmake hdf5 opencv libomp --quiet

# 4) Ensure the virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ ERROR: Virtual environment is not activated! Run: source venv/bin/activate"
    exit 1
fi

# 5) Use the venv's pip
PIP_CMD="$(which pip)"

echo "Upgrading pip..."
$PIP_CMD install --upgrade pip --prefer-binary --quiet

echo "Installing Python packages via pip..."
# For macOS, we use pinned versions for tensorflow-macos and compatible dependencies.
PACKAGES=(
    torch
    torchvision
    torchaudio
    tensorflow-macos==2.12.0
    "keras==2.12.0"
    "ml-dtypes~=0.3.1"
    scikit-learn
    mmdet
    ultralytics
    opencv-python
    pillow
    albumentations
    imageio
    numpy
    scipy
    sympy
    statsmodels
    cvxpy
    pandas
    h5py
    lmdb
    pyarrow
    dask
    stable-baselines3
    gymnasium
    "ray[rllib]"
    fastapi
    flask
    onnx
    onnxruntime
    tritonclient[all]
    pycryptodome
    pyjwt
)

$PIP_CMD install --prefer-binary --quiet "${PACKAGES[@]}" --no-warn-script-location

echo "✅ Done installing packages on macOS."
