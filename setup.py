from setuptools import setup

setup(
    name="plynk_api",
    version="1.0.0",
    description="Unofficial reverse engineered Plynk API.",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/matthew55/Plynk-API",
    author="Matthew",
    packages=["plynk_api"],
    install_requires=["curl_cffi", "pytz"],
)
