from kdevops.docker import Docker, MinikubeDocker

docker = Docker()

docker.build('streamrec')


docker.run('streamrec', it=True, cmd='bash')
