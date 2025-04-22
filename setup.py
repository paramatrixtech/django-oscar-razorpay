#!/usr/bin/env python
from setuptools import setup, find_packages

from rzpay import VERSION


setup(
    name='django-oscar-razorpay',
    version=VERSION,
    url='https://github.com/sunu/django-oscar-razorpay',
    description=(
        "Integration with Razorpay payment gateway for django-oscar"),
    long_description=open('README.rst').read(),
    keywords="Payment, Razorpay, Oscar",
    license=open('LICENSE').read(),
    platforms=['linux'],
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    include_package_data=True,
    install_requires=[
        'requests==2.32.3',
        'razorpay==1.4.2',
    ],
    extras_require={
        'oscar': ["django-oscar==3.2.5"]
    },
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Other/Nonlisted Topic'],
)
