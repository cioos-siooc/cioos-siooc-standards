from setuptools import setup

setup(
    name="cioos-standards",
    version="0.1.0",
    description="Python Package use to handle different vocabulary information hosted"
                " on the different vobulary servers.",
    url="https://github.com/cioos-siooc/cioos-siooc-standards/ocean_standards",
    author="Jessy Barrette",
    author_email="jessy.barrette@hakai.org",
    license="MIT",
    packages=["ocean_standards"],
    include_package_data=True,
    install_requires=[
        "requests",
        "pandas",
        "xmltodict",
        "tqdm",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    zip_safe=True,
)
