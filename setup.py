from setuptools import setup, find_packages


def run_setup():
    setup(
        name='sixnmt',
        version='0.0.1',
        packages=find_packages(),
        author=', '.join(["Joshua Klein"]),
        entry_points={
            'console_scripts': [
                "sixnmt = sixnmt.play:play"
            ],
        })


if __name__ == '__main__':
    run_setup()
