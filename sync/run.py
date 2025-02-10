#!/usr/bin/env python3

import argparse
import requests
import sys

from bs4 import BeautifulSoup


class MetamodulePlugins:
    def __init__(self, plugins_url: str, modules_url: str):
        self.plugins_url = plugins_url
        self.modules_url = modules_url

    def clean_modules(self, modules: list[str]) -> list[str]:
        if 'Bogaudio' in modules.keys():
            if 'Bogaudio-PolyCon16' in modules['Bogaudio']:
                for index, module in enumerate(modules['Bogaudio']):
                    if module == 'Bogaudio-PolyCon16':
                        modules['Bogaudio'][index] = 'Bogaudio-PolyCon'
        return modules

    def get_all_modules(self):
        modules = {}
        plugins = self.get_plugins()
        for plugin in plugins:
            plugin_slug = plugin.split('-/-')[0]
            modules[plugin_slug] = self.get_plugin_modules(plugin)
        return self.clean_modules(modules)

    def get_plugins(self):
        response = requests.get(self.plugins_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        plugins = [li.attrs['id'] for li in soup.find_all('li') if 'id' in li.attrs]
        return list(dict.fromkeys(plugins))

    def get_plugin_modules(self, plugin: str) -> list[str]:
        response = requests.get(self.modules_url, headers={'HX-Target': plugin})
        soup = BeautifulSoup(response.text, 'html.parser')
        modules = [a.attrs['href'].split('/')[-1] for a in soup.find_all('a') if 'href' in a.attrs]
        return list(dict.fromkeys(modules))


class VCVRackLibrary:
    def __init__(self, token_url: str, modules_url: str, email: str, password: str):
        self.token_url = token_url
        self.modules_url = modules_url
        self.email = email
        self.password = password

        self.token = self.get_token()

    def get_modules(self) -> dict[str, list[str]]:
        response = requests.get(self.modules_url,
            headers={'Cookie': f'token={self.token}'})
        if response.status_code == 200 and 'modules' in response.json():
            return response.json()['modules']
        return {}

    def get_token(self) -> str:
        response = requests.post(self.token_url,
            json={'email': self.email, 'password': self.password},
            headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            return response.json()['token']
        else:
            return None

    def add_module(self, plugin: str, module: str) -> bool:
        response = requests.post(self.modules_url,
            json={'token': self.token, 'pluginSlug': plugin, 'moduleSlug': module})
        return response.status_code == 200

    def sync(self, metamodule_modules: dict[str, list[str]]):
        vcv_modules = self.get_modules()
        # print('vcv_modules', vcv_modules)

        for plugin, modules in metamodule_modules.items():
            if plugin in vcv_modules.keys():
                for module in modules:
                    if module in vcv_modules[plugin]:
                        print(f'Module already in library (plugin: {plugin}, module: {module})')
                    else:
                        print(f'Adding module (plugin: {plugin}, module: {module})')
                        if self.add_module(plugin, module):
                            print(f'  Added module (plugin: {plugin}, module: {module})')
                        else:
                            print(f'  Failed to add module (plugin: {plugin}, module: {module})')
            else:
                print(f'Plugin not in library (plugin: {plugin})')
                for module in modules:
                    print(f'Adding module (plugin: {plugin}, module: {module})')
                    if self.add_module(plugin, module):
                        print(f'  Added module (plugin: {plugin}, module: {module})')
                    else:
                        print(f'  Failed to add module (plugin: {plugin}, module: {module})')

class Runner:
    def parse_args(self):
        parser = argparse.ArgumentParser(description="Metamodule to VCV Rack Library Sync")

        parser.add_argument('vcv_email', type=str, default=None,
            help='VCV Library email.')
        
        parser.add_argument('vcv_password', type=str, default=None,
            help='VCV Library password.')

        parser.add_argument('metamodule_plugins_url', type=str, default=None,
            help='Metamodule plugins URL.')

        parser.add_argument('metamodule_modules_url', type=str, default=None,
            help='Metamodule modules URL.')

        parser.add_argument('vcv_rack_libarary_token_url', type=str, default=None,
            help='VCV Rack Library login URL.')

        parser.add_argument('vcv_rack_library_modules_url', type=str, default=None,
            help='VCV Rack Library modules URL.')

        self.args = parser.parse_args()

    def run(self):
        self.parse_args()

        self.metamodule_plugins = MetamodulePlugins(
            self.args.metamodule_plugins_url,
            self.args.metamodule_modules_url)
        metamodule_modules = self.metamodule_plugins.get_all_modules()

        self.vcv_rack_library = VCVRackLibrary(
            self.args.vcv_rack_libarary_token_url,
            self.args.vcv_rack_library_modules_url,
            self.args.vcv_email, self.args.vcv_password)
        self.vcv_rack_library.sync(metamodule_modules)


if __name__ == '__main__':
    runner = Runner()
    runner.run()
