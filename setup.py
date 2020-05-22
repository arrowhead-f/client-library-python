import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='arrowhead-client',
        version='0.1.1a1',
        author='Jacob Nilsson',
        author_email='jacob.nilsson@ltu.se',
        description='Arrowhead system and service client library',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/arrowhead-f/client-library-python',
        packages=setuptools.find_packages(exclude=['tests', 'examples']),
        licence='EPL-2.0',
        install_requires=[
            'Flask>=1.0.2',
            'requests>=2.21',
            'gevent>=20.5.0'
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Operating System :: POSIX :: Linux',
            'License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)',
        ],
        python_requires='>=3.7'
)
