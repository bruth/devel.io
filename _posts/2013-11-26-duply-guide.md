---
layout: post
title: "Duply Guide: Backup to S3"
date: 2013-11-26
---

This is very quick and terse guide to start backing up to S3 using Duply as I am posting this as a reminder for myself.

## Install [librsync](http://librsync.sourceforge.net/)

This should done using a package manager if available, but here are the steps for building from source:

```bash
wget "http://downloads.sourceforge.net/project/librsync/librsync/0.9.7/librsync-0.9.7.tar.gz"
tar zxf librsync-0.9.7.tar.gz
cd librsync-0.9.7/
./configure --enable-shared
make && make install
```

## Install [Boto](https://pypi.python.org/pypi/boto)

This is the underlying library that communicates with S3.

```bash
pip install boto
```

## Install [Duplicity](http://duplicity.nongnu.org/)

```bash
wget "wget http://code.launchpad.net/duplicity/0.6-series/0.6.22/+download/duplicity-0.6.22.tar.gz"
tar zxf duplicity-0.6.22.tar.gz
cd duplicity-0.6.22/
python setup.py install
```

_Note: The librsync headers and shared libraries must be found by this installer. This is only an issue if it was installed in an arbitrary location (e.g. your home directory). If needed, export the `LD_LIBRARY_PATH` and `INCLUDE_DIRS` environment variables in your .bashrc file, e.g `export LD_LIBRARY_PATH="$HOME/lib:$LD_LIBRARY_PATH"`._

## Install [Duply](http://duply.net/)

```bash
wget "http://downloads.sourceforge.net/project/ftplicity/duply%20%28simple%20duplicity%29/1.5.x/duply_1.5.11.tgz"
tar zxf duply_1.5.11.tgz
mkdir -p $HOME/bin
mv duply_1.5.11/duply $HOME/bin
```

This creates a bin directory in your home directory and moves the duply script into it. You can of course move it anywhere you want. However I am going to assume it is on your `PATH`.

## Create Duply Profile

```bash
duply myprofile create
```

Edit the new profile config `vim ~/.duply/myprofile/conf` and change `TARGET` (around line 69) to the match the following template:

```bash
TARGET='s3://<access_key_id>:<secret_access_key>@<region_host>/<bucket_name>/<path>
```

where:

- `access_key_id` - AMI access key
- `secret_access_key` - AMI secrete access key
- `region_host` - the [host to the S3 region](http://docs.aws.amazon.com/general/latest/gr/rande.html#s3_region), e.g. s3.amazonaws.com for US Eastern
- `bucket_name` - the name of the bucket to create/use
- `path` - the path in the bucket that will store the files

Change `SOURCE` (around line 76) to the directory or file to be backed up.

```bash
SOURCE=~
```

## Backup

```bash
duply myprofile backup
```

## References

- [Duplicity + S3](http://blog.phusion.nl/2013/11/11/duplicity-s3-easy-cheap-encrypted-automated-full-disk-backups-for-your-servers/)
