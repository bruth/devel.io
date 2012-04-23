from fabric.api import *

env.hosts = ['thedevel.webfactional.com']

def deploy():
    with cd('~/sites/devel.io'):
        run('git pull')
        with prefix('rvm use 1.9.3'):
            run('jekyll')
