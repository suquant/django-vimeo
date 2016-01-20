from setuptools import setup, find_packages

import os

django_vimeo = __import__('django_vimeo')


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

README = read('README.rst')
CHANGES = read('CHANGES.rst')

setup(
    name='django-vimeo',
    packages=find_packages(),
    version=django_vimeo.get_version(),
    author='Georgy Kutsurua',
    author_email='g.kutsurua@gmail.com',
    url='https://github.com/suquant/django-vimeo',
    description=django_vimeo.__doc__.strip(),
    long_description='\n\n'.join([README, CHANGES]),
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
    ],
    keywords=['vimeo', 'video'],
    install_requires=[
        'PyVimeo >=0.3.2, <0.4',
        'Django >=1.5, <1.10',
        'xxhash >=0.4.3, <0.5',
    ],
    test_suite='nose.collector',
)
