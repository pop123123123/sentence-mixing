import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentence_mixing",
    version="0.0.1",
    author="nbusser lmouhat",
    author_email="nicolas.busser67@gmail.com",
    description="Sentence mixing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pop123123123/sentence-mixing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "textgrid",
        "youtube_dl",
        "num2words",
        "numpy",
        "scipy",
        "webvtt-py",
        "moviepy",
        "python-Levenshtein",
        "pocketsphinx",
    ],
    python_requires=">=3.6",
)
