# MetaModule to VCV Library Sync
This project keeps your VCV Library in sync with MetaModule plugins/modules.

It scrapes the MetaModule site for all plugins and modules.  Then it logs into VCV Library and loads the plugins/modules from your library.  Any MetaModule modules/plugins that are not in your VCV Library are added.

[!PLEASE BE KIND]
Please note that both 4MS and VCV are being kind enough to let us use their sites and APIs to do this.  I have been very careful to limit the load on their sites.  For example, on VCV Library, there is one call to login (getting a token) and another call to get the modules/plugins currently in your library.  If all of the MetaModule plugins/modules are already in your library, nothing else will happen.  If some plugins/modules are not in your library, they will be added individually.

If you encounter any issues, please don't run the script over and over.  It shouldn't cause much load on 4MS or VCV sites, but please be conscious to not keep trying if it's failing.  Instead, please run in [verbose mode](#verbose-mode) and create an issue with the output and I will do my best to help.

## Project Structure
Since the project uses some dependencies that can be a pain to install in some environments (and also because I love docker for its portability), the main script runs in a docker container.

There are two python scripts:
- [docker/run.py](docker/run.py) is the main script that does the work within the container.
- [run.py](run.py) builds and runs the docker container, which runs [docker/run.py](docker/run.py)

The only requirements for [run.py](run.py) should be Python 3 and docker.  Other requirements are installed for you inside the container.

## Running
Provide your VCV Library username and password as arguments to [run.py](run.py):
```
./run.py 'username@address.com' 'password'
```

[!NOTE]
In many shells, you could have issues with special characters, particularly for passwords.  Use single quotes around your password, as in the example above, and you should be okay.  Double quotes will usually cause problems and the VCV Library login will fail.

### Verbose mode
If you are having any issues, you can run in verbose mode to get more information about what is going on:
```
./run.py 'username@address.com' 'password' -v
```
OR
```
./run.py 'username@address.com' 'password' --verbose
```

## Development
The first time you run the [run.py](run.py), the container will be built.  If you make any changes to [docker/run.py](docker/run.py) or the container, you will need to force the container to be rebuilt.  Simply pass the `-b` or `--build` flag to build the image before running:
```
./run.py 'username@address.com' 'password' -b
```
OR
```
./run.py 'username@address.com' 'password' --build
```
