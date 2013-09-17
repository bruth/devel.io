from fabric.api import *

env.hosts = ['thedevel.webfactional.com']

def deploy():
    with cd('~/sites/devel.io'):
        run('git pull')
        run('jekyll build')
