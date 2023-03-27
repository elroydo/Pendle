import setuptools

setuptools.setup(
    name="pendle",
    version="0.23",
    description="Pendle: SRISSS",
    author="elroyD",
    packages=setuptools.find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "deepface",
        "sqlalchemy",
    ],
    python_requires='>=3.6',
)