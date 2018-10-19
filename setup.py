import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name='pypakr_pkg',
  version='0.0.1',
  author='Aleksandar Janicijevic',
  author_email='aleks@vogonsoft.com',
  description='Python containers',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/ajanicij/pypakr',
  packages=setuptools.find_packages(),
  classifiers=[
    'Programming Language :: Python :: 2.7',
    'License :: OSI Approved :: Apache 2.0',
    'Operating System :: Linux',
  ],
  scripts = [
    'scripts/pypakr'
  ],
)
