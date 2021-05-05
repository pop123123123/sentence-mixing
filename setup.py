import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentence_mixing",
    version="1.3.1",
    author="Nicolas BUSSER, Louis MOUHAT",
    author_email="nicolas.busser67@gmail.com",
    description="Sentence mixing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pop123123123/sentence-mixing",
    packages=[
        "sentence_mixing",
        "sentence_mixing.logic",
        "sentence_mixing.model",
        "sentence_mixing.parameter_tuning",
        "sentence_mixing.video_creator",
    ],
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
    ],
    python_requires=">=3.6",
)
