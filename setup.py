from setuptools import setup, find_packages

try:
    from pypandoc import convert_file
    read_md = lambda f:convert_file(f, 'rst')
except ImportError:
    print("Warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

DISTNAME = 'aof_research'
INSTALL_REQUIRES = (
    ['pandas>=0.19.2', 'numpy>=1.20.2', 'requests>=2.3.0', 'wrapt>=1.10.0', 'lxml>=4.3.0', 'pypandoc>=1.4', 'plotly>=4.2.1', 'bs4>=0.0.1']
)

VERSION = '0.0.1'
LICENSE = 'MIT'
DESCRIPTION = 'Stock market'
AUTHOR = "HiepDuongTrong"
EMAIL = "duonghiep59.it@gmail.com"
URL = "https://github.com/duonghiepit/aof-research"
DOWNLOAD_URL = "https://github.com/duonghiepit/aof-research"
LONG_DESCRIPTION = 'This project provide the financial information and useful visualization instrument about stock market to researcher. Particularly, there are many aspect of data relating to any stock being able to store and clone. The official version are built on both machine learning language Python and R.'

## Setting:
setup(name=DISTNAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author=AUTHOR,
      author_email=EMAIL,
      url=URL,
      license=LICENSE,
      # Package name are looked in python path
      packages=find_packages(exclude= ['contrib', 'docs','tests*']),
      classifiers=[
          'Development Status :: 0 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Trader/Investor/Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Cython',
          'Programming Language :: Python :: 3.12'
          'Topic :: Financial/Stock Market',
      ],
      keywords='data',
      install_requires = INSTALL_REQUIRES,
      zip_safe=False,
      )