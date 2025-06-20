from setuptools import find_packages, setup

setup(
    name="dexcom_dagster",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "dagster",
        "dagster-dbt",
        "dbt-duckdb<1.10",
    ],
    extras_require={
        "dev": ["dagster-webserver"],
        "cloud": ["dagster-cloud"],
    },
)
