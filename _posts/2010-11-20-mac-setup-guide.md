---
layout: post
title: Mac Setup Guide
---
## Preface
Simple guide for myself to remember, but others may find it useful.

## MobileMe
Syncs all preferences

## Install Xcode
Install Xcode from the OS X installation disc (or this little [gem] []) or if you have a Apple Developer account, you can download the installer from the [website] [].

[gem]: http://www.engadget.com/2010/10/20/new-macbook-airs-come-with-software-reinstall-usb-drive/
[website]: http://developer.apple.com/technologies/xcode.html

## Homebrew
The **new** standard for OS X package managers is [Homebrew] []. Don't argue, just use it.

[Homebew]: https://github.com/mxcl/homebrew

```bash
$ sudo mkdir /usr/local
$ sudo chown `whoami` /usr/local
$ ruby -e $(curl -fsSL https://gist.github.com/raw/323731/install_homebrew.rb)
```

The last line will install homebrew to ``/usr/local`` by default. The final step is preferential:

```bash
$ echo 'export PATH=/usr/local/bin:$PATH' >> ~/.bash_login
```

## System Libraries
Python is already installed by default on OS X (specifically Python 2.6.1 on 10.6). The version homebrew installs is Python 2.7 which I prefer.

```bash
$ brew install wget python git postgresql memcached nginx
```

If you chose to install Python, it is a good idea to add the following to your ``PATH`` as well:

```bash
$ echo 'export PATH=/usr/local/Cellar/python/2.7/bin:$PATH' >> ~/.bash_login
```

## System Python Libraries
I prefer using [pip] [] for my Python library management because it is easy and it works well with [virtualenv] [].

[pip]: http://pypi.python.org/pypi/pip
[virtualenv]: http://pypi.python.org/pypi/virtualenv

```bash
$ wget http://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c11.tar.gz
$ tar zxf setuptools-0.6c11.tar.gz && cd setuptools-0.6c11
$ python setup.py install
$ wget http://pypi.python.org/packages/source/p/pip/pip-0.8.1.tar.gz
$ tar zxf pip-0.8.1.tar.gz && cd pip-0.8.1
$ python setup.py install
```

These are generally multi-use libraries that won't generally conflict with the virtual environments I create for development (via virtualenv).

```bash
$ pip install virtualenv psycopg2 python-memcached markdown
```

## Applications

- [MacVim](http://code.google.com/p/macvim/)
- [Alfred App](http://www.alfredapp.com/)