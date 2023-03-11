import setuptools

setuptools.setup(
    name="pendle",
    version="0.9.9",
    description="Pendle: SRISSS",
    author="elroy D",
    packages=setuptools.find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "pandas",
        "Pillow",
        "tensorflow",
        "mtcnn",
        "keras",
        "retina-face",
        "deepface",
        "Flask",
        "fire",
        "gdown",
        "tqdm"
    ],
    python_requires='>=3.6',
)