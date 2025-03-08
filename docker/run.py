#!/usr/bin/env python3

import os
import sys

import argparse
import subprocess
import textwrap


class Process(subprocess.Popen):
    def __init__(self, command: list[str], quiet: bool = False, *args, **kwargs):
        kwargs['args'] = command
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.PIPE
        kwargs['text'] = True

        super().__init__(*args, **kwargs)

        if not quiet:
            while self.poll() is None:
                stdout = self.stdout.read()
                if stdout:
                    sys.stdout.write(stdout)
                    sys.stdout.flush()

                stderr = self.stderr.read()
                if stderr:
                    sys.stderr.write(stderr)
                    sys.stderr.flush()

            stdout = self.stdout.read()
            while stdout:
                sys.stdout.write(stdout)
                sys.stdout.flush()
                stdout = self.stdout.read()

            stderr = self.stderr.read()
            while stderr:
                sys.stderr.write(stderr)
                sys.stderr.flush()
                stderr = self.stderr.read()


class DockerImage:
    def __init__(self, name: str, dockerfile_path: str, context_dir: str):
        self.name = name
        self.dockerfile_path = dockerfile_path
        self.context_dir = context_dir

    def build(self) -> (bool, Process):
        process = Process(command=[
            'docker', 'build',
            '-t', self.name,
            '-f', self.dockerfile_path,
            self.context_dir,
        ])

        return (process.returncode == 0, process)

    def exists(self) -> bool:
        process = Process(command=[
            'docker', 'image', 'inspect', self.name,
        ], quiet=True)

        return (process.returncode == 0)

    def run(self,
        container_name: str,
        vcv_email: str,
        vcv_password: str,
        metamodule_plugins_url: str,
        metamodule_modules_url: str,
        vcv_rack_libarary_token_url: str,
        vcv_rack_library_modules_url: str,
        verbose: bool
    ) -> (bool, Process):
        command = [
            'docker', 'run',
            '--rm',
            '--name', container_name,
            self.name,
            '--',
            vcv_email,
            vcv_password,
            metamodule_plugins_url,
            metamodule_modules_url,
            vcv_rack_libarary_token_url,
            vcv_rack_library_modules_url,
            str(verbose)
        ]

        process = Process(command=command)
        return (process.returncode == 0, process)

class Runner:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))

    def parse_args(self):
        parser = argparse.ArgumentParser(description="Metamodule to VCV Rack Library Sync")

        parser.add_argument('vcv_email', type=str, default=None,
            help='VCV Library email.')
        
        parser.add_argument('vcv_password', type=str, default=None,
            help='VCV Library password.')

        parser.add_argument('-b', '--build', action='store_true',
            help='Always build before running.')

        parser.add_argument('-i', '--image-name', type=str, action='store',
            default='metamodule_vcv_sync', help='Docker image name.')

        parser.add_argument('-c', '--container-name', type=str, action='store',
            default='metamodule_vcv_sync', help='Docker container name.')

        parser.add_argument('--metamodule_plugins_url', type=str, action='store',
            default='https://metamodule.info/plugins', help='Metamodule plugins URL.')

        parser.add_argument('--metamodule_modules_url', type=str, action='store',
            default='https://metamodule.info/hx/plugins/open_list',
            help='Metamodule modules URL.')

        parser.add_argument('--vcv_rack_libarary_token_url', type=str, action='store',
            default='https://api.vcvrack.com/token', help='VCV Rack Library login URL.')

        parser.add_argument('--vcv_rack_library_modules_url', type=str, action='store',
            default='https://api.vcvrack.com/modules', help='VCV Rack Library modules URL.')

        parser.add_argument('-v', '--verbose', action='store_true',
            help='Verbose output.')

        self.args = parser.parse_args()

    def run(self):
        self.parse_args()

        self.docker_image = DockerImage(name=self.args.image_name,
            dockerfile_path=os.path.join(self.script_dir, 'Dockerfile'),
            context_dir=os.path.join(self.script_dir, '..'))

        if self.args.build or not self.docker_image.exists():
            if self.args.verbose:
                print('Building docker image.')

            success, _ = self.docker_image.build()

            if self.args.verbose and success:
                print('Docker image built.')

            if not success:
                print('Docker build failed.')
                sys.exit(1)

        if self.args.verbose:
            print('Running container.')

        success, _ = self.docker_image.run(container_name=self.args.container_name,
            vcv_email=self.args.vcv_email, vcv_password=self.args.vcv_password,
            metamodule_plugins_url=self.args.metamodule_plugins_url,
            metamodule_modules_url=self.args.metamodule_modules_url,
            vcv_rack_libarary_token_url=self.args.vcv_rack_libarary_token_url,
            vcv_rack_library_modules_url=self.args.vcv_rack_library_modules_url,
            verbose=self.args.verbose)

        if not success:
            print('Docker run failed.')
            sys.exit(1)

if __name__ == "__main__":
    runner = Runner()
    runner.run()
