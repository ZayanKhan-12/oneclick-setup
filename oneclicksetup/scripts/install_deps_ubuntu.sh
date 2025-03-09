#!/usr/bin/env bash
set -e

echo "Installing system dependencies on Ubuntu..."

# 1) Update apt cache quietly
sudo apt-get update -qq

# 2) Install system-level dependencies
sudo apt-get install -y \
    build-essential \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    ssh \
    cmake \
    libssl-dev \
    libffi-dev \
    libhdf5-dev \
    libopencv-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    pkg-config \
    wget \
    curl

# 3) Ensure that the virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "❌ ERROR: Virtual environment is not activated! Run: source venv/bin/activate"
    exit 1
fi

# 4) Use the venv's pip
PIP_CMD="$(which pip)"

echo "Upgrading pip..."
$PIP_CMD install --upgrade pip --prefer-binary --quiet

echo "Installing Python packages via pip..."
# For Ubuntu, we use pinned versions for tensorflow==2.16.2 and compatible dependencies.
PACKAGES=(
    torch
    torchvision
    torchaudio
    tensorflow==2.16.2
    "keras>=3.0.0,<3.1.0"
    "ml-dtypes~=0.3.1"
    scikit-learn
    "detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cu118/torch2.0/index.html"
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
    onnxruntime-gpu
    tritonclient[all]
    pycryptodome
    pyjwt
)

$PIP_CMD install --prefer-binary --quiet "${PACKAGES[@]}" --no-warn-script-location

echo "✅ Done installing packages on Ubuntu."
