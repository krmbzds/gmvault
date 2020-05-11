"""
    Gmvault: a tool to backup and restore your gmail account.
    Copyright (C) <2011-2012>  <guillaume Aubert (guillaume dot aubert at gmail do com)>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import subprocess
import configparser
from distutils.command.build import build
from setuptools import setup, Command
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.build_py import build_py
from jinja2 import Template

#class Credential(distutils.cmd.Command):
class Credential(Command):
    """Add in custom google client ID and secret"""

    description = "Insert user's own google client ID and secret"
    user_options = [
        ('google-credentials-file=', None, 'Credentials file'),
        ('google-client-id=', None, 'google-client-id'),
        ('google-secret=', None, 'google-secret')]

    def initialize_options(self):
        self.google_client_id = None
        self.google_secret = None
        self.google_credentials_file = None

    def finalize_options(self):
        if self.google_credentials_file:
            assert os.path.exists(self.google_credentials_file), ('Credentials file %s does not exist', self.google_credentials_file)
            if self.google_secret or self.google_client_id:
                print("Warning: specifying a credentials file overrides a client_id or secret specificied on the commandline")
            config = configparser.ConfigParser()
            config.read(self.google_credentials_file)
            self.google_client_id = config['DEFAULT']['client_id']
            self.google_secret = config['DEFAULT']['secret']
            assert len(self.google_client_id) > 0, ('Client_id missing from credentials file %s', self.google_credentials_file)
            assert len(self.google_secret) > 0, ('Secret missing from credentials file %s', self.google_credentials_file)
        elif self.google_client_id is None and self.google_secret is None:
            if os.path.exists("google_credentials.ini"):
                print("Warning: No credentials file or parameters specified, using default existing file %s" % "google_credentials.ini")
                self.google_credentials_file = "google_credentials.ini"
                config = configparser.ConfigParser()
                config.read(self.google_credentials_file)
                self.google_client_id = config['DEFAULT']['client_id']
                self.google_secret = config['DEFAULT']['secret']
                assert len(self.google_client_id) > 0, ('Client_id missing from credentials file %s', self.google_credentials_file)
                assert len(self.google_secret) > 0, ('Secret missing from credentials file %s', self.google_credentials_file)
            else:
                raise Exception("Error: No credentials file or parameters specified, and default 'google_credentials.ini' was not found")
        else:
            assert len(self.google_client_id) > 0, 'Client_id not specified'
            assert len(self.google_secret) > 0, 'Secret not specified or missing from credentials file'


    def run(self):
        """Add in the client ids to files"""

        jinjadict = {
            'google_client_id': self.google_client_id,
            'google_secret': self.google_secret
        }
        template_files = ['src/gmv/credential_utils.t.py', 'src/gmv/gmvault_const.t.py']
        if self.google_credentials_file is None:
            if os.path.exists("google_credentials.ini"):
                pass
            else:
                template_files.append("google_credentials.t.ini")
                print("Writing passed parameters to default credentials file %s" % "google.credentials.ini")
        for f in template_files:
            fhandler = open(f)
            template = Template(fhandler.read())
            fhandler.close()
            rendered = template.render(credentials = jinjadict)
            newfile= os.path.splitext(f)[0][0:-2] + os.path.splitext(f)[1]
            ofh = open (newfile, 'w')
            ofh.write(rendered)
            ofh.close()


# class BuildWrapper(build_py):
#     def run(self):
#         self.run_command('credential')
#         super.run(self)

class CommandMixin(object):
    user_options = [
        ('google-credentials-file=', None, 'Credentials file'),
        ('google-client-id=', None, 'google-client-id'),
        ('google-secret=', None, 'google-secret')]

    def initialize_options(self):
        super().initialize_options()
        self.google_client_id = None
        self.google_secret = None
        self.google_credentials_file = None

    def finalize_options(self):
        super().finalize_options()

    def run(self):
        super().run()

class InstallCommand(CommandMixin, install):
    user_options = getattr(install, 'user_options', []) + CommandMixin.user_options

class DevelopCommand(CommandMixin, develop):
    user_options = getattr(develop, 'user_options', []) + CommandMixin.user_options

class BuildPyCommand(CommandMixin, build_py):
    user_options = getattr(build_py, 'user_options', []) + CommandMixin.user_options
    def run(self):
        self.run_command("credential")
        super().run()

class BuildCommand(CommandMixin, build):
    user_options = getattr(build, 'user_options', []) + CommandMixin.user_options
    def run(self):
        self.run_command("credential")
        super().run()

#function to find the version in gmv_cmd

def find_version(path):
    with open(path, 'r') as f:
        for line in f:
            index = line.find('GMVAULT_VERSION = "')
            if index > -1:
                print(line[index+19:-2])
                res = line[index+19:-2]
                return res.strip()

    raise Exception("Cannot find GMVAULT_VERSION in %s\n" % path)

path = os.path.join(os.path.dirname(__file__), './src/gmv/gmvault_utils.py')
print("PATH = %s\n" % path)

version = find_version(os.path.join(os.path.dirname(__file__),
                                    './src/gmv/gmvault_utils.py'))

print("Gmvault version = %s\n" % version)
README = os.path.join(os.path.dirname(__file__), './README.md')
if os.path.exists(README):
    with open(README, 'r') as f:
        long_description = f.read() + 'nn'
else:
    long_description = 'Gmvault'


APP = ['gmvault']
DATA_FILES = []
OPTIONS = {'argv_emulation': True}


setup(name='gmvault',
      cmdclass={'credential': Credential,
                'build_py': BuildPyCommand,
                'build': BuildCommand,
                'install': InstallCommand,
                'develop': DevelopCommand},
      version=version,
      description=("Tool to backup and restore your Gmail emails at will. http://www.gmvault.org for more info"),
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Topic :: Communications :: Email",
        "Topic :: Communications :: Email :: Post-Office :: IMAP",
        ],
      keywords='gmail, email, backup, gmail backup, imap',
      author='Guillaume Aubert',
      author_email='guillaume.aubert@gmail.com',
      url='http://www.gmvault.org',
      license='AGPLv3',
      packages=['gmv','gmv.conf', 'gmv.conf.utils'],
      package_dir = {'gmv': './src/gmv'},
      scripts=['./etc/scripts/gmvault'],
      package_data={'': ['release-note.txt']},
      include_package_data=True,
      #install_requires=['argparse', 'Logbook==0.4.1', 'IMAPClient==0.9.2','gdata==2.0.17']
      #install_requires=['argparse', 'Logbook==0.10.1', 'IMAPClient==0.13', 'chardet==2.3.0'],
      install_requires=['argparse', 'Logbook>=0.10.1', 'IMAPClient>=0.13', 'chardet>=2.3.0'],
      app=APP,
      data_files=DATA_FILES,
      options={'py2app': OPTIONS},
      setup_requires = ['py2app']
      )
