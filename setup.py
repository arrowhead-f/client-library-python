import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name='test_arrowhead_client_library',
        version='0.0.2',
        author='Jacob Nilsson',
        author_email='jacob.nilsson@ltu.se',
        description='Arrowhead system and service client library',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/ajoino/python-arrowhead',
        packages=setuptools.find_packages(),
        install_requires=[
            'Flask>=1.0.2',
            'requests>=2.21'
        ],
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Operating System :: POSIX :: Linux',
            'License :: OSI Approved :: Eclipse Public License 2.0 (EPL-2.0)',
        ],
        python_requires='>=3.7'
)
