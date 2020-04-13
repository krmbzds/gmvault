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
from setuptools import setup
import setuptools.command.build_py
import distutils.cmd
import distutils.log
import subprocess
import configparser
from jinja2 import Template

class AddClientID(distutils.cmd.Command):
    """Add in custom google client ID and secret"""

    description = "Insert user's own google client ID and secret"
    user_options = [
        ('google-credentials-file=', None, 'Credentials file'),
        ('google-client-id=', None, 'google-client-id'),
        ('google-secret=', None, 'google-secret')]

    def initialize_options(self):
        self.google_client_id = None
        self.google_secret = None
        self.google_credentials_file = "google_credentials.ini"

    def finalize_options(self):
        pass

    def run(self):
        """Add in the client ids to files"""

        if self.google_credentials_file:
            assert os.path.exists(self.google_credentials_file), ('Credentials file %s does not exist', self.google_credentials_file)
            config = configparser.ConfigParser()
            config.read(self.google_credentials_file)
            self.google_client_id = config['DEFAULT']['client_id']
            self.google_secret = config['DEFAULT']['secret']
            self.jinjadict = {
                'google_client_id': self.google_client_id,
                'google_secret': self.google_secret
            }
        for f in ['src/gmv/credential_utils.tpy', 'src/gmv/gmvault_const.tpy']:
            fhandler = open(f)
            template = Template(fhandler.read())
            fhandler.close()
            rendered = template.render(credentials = self.jinjadict)
            newfile= os.path.splitext(f)[0] + ".py"
            ofh = open (newfile, 'w')
            ofh.write(rendered)
            ofh.close()






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

class BuildWrapper(setuptools.command.build_py.build_py):
    def run(self):
        self.run_command('credential')
        setuptools.command.build_py.build_py.run(self)

setup(name='gmvault',
      cmdclass={'credential': AddClientID, 'build_py': BuildWrapper},
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
      install_requires=['argparse', 'Logbook==0.10.1', 'IMAPClient==0.13', 'chardet==2.3.0']
      )
