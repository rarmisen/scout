#!/usr/bin/env python
# encoding: utf-8
"""
wipe_and_load.py

Script to clean the database and reload it with new data.

Created by Måns Magnusson on 2015-01-14.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.

"""


from __future__ import absolute_import, unicode_literals, print_function

import sys
import os

import click

import scout

from pprint import pprint as pp
from pymongo import MongoClient, Connection
from mongoengine import connect, DoesNotExist
from mongoengine.connection import _get_db

from scout.ext.backend import (load_mongo_db, ConfigParser)

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(scout.__file__), '..'))

@click.command()
@click.option('-vcf', '--vcf_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the vcf file that should be loaded."
)
@click.option('-ped', '--ped_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the corresponding ped file."
)
@click.option('-scout_config', '--scout_config_file',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the scout config file."
)
@click.option('-config', '--config_file',
                nargs=1,
                type=click.Path(exists=True),
                default=os.path.join(BASE_PATH, 'configs/config_test.ini'),
                help="Path to the config file for loading the variants. Default configs/config_test.ini"
)
@click.option('-m', '--madeline',
                nargs=1,
                type=click.Path(exists=True),
                help="Path to the madeline file with the pedigree."
)
@click.option('-type', '--family_type',
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']),
                default='cmms',
                nargs=1,
                help="Specify the file format of the ped (or ped like) file."
)
@click.option('-vt', '--variant_type',
                type=click.Choice(['clinical', 'research']),
                default='clinical',
                nargs=1,
                help="Specify the type of the variants that is being loaded."
)
@click.option('-i', '--institute',
                default='CMMS',
                nargs=1,
                help="Specify the institute that the file belongs to."
)
@click.option('-db', '--mongo-db',
                default='variantDatabase'
)
@click.option('-u', '--username',
                type=str
)
@click.option('-p', '--password',
                type=str
)
@click.option('-port', '--port',
                default=27017,
                help='Specify the port where to look for the mongo database.'
)
@click.option('-h', '--host',
                default='localhost',
                help='Specify the host where to look for the mongo database.'
)
@click.option('-v', '--verbose',
                is_flag=True,
                help='Increase output verbosity.'
)
def load_mongo(vcf_file, ped_file, scout_config_file, config_file, family_type, 
              mongo_db, username, variant_type, madeline, password, institute, 
              port, host, verbose):
  """
  Load the mongo database.
  
  Command line arguments will override what's in the config file.
  
  """
  # Check if vcf file exists and that it has the correct naming:
  scout_configs = {}
  
  if scout_config_file:
    scout_configs = ConfigParser(scout_config_file)
  
  if vcf_file:
    scout_configs['load_vcf'] = vcf_file
    scout_configs['igv_vcf'] = vcf_file
  
  if ped_file:
    scout_configs['ped'] = ped_file
  
  if madeline:
    scout_configs['madeline'] = madeline
  
  if institute:
    scout_configs['institutes'] = [institute]
    
  if not scout_configs.get('load_vcf', None):
    print("Please provide a vcf file.(Use flag '-vcf/--vcf_file')", file=sys.stderr)
    sys.exit(0)
  
  # Check that the ped file is provided:
  if not scout_configs.get('ped', None):
    print("Please provide a ped file.(Use flag '-ped/--ped_file')", file=sys.stderr)
    sys.exit(0)
  
  # Check that the config file is provided:
  if not config_file:
    print("Please provide a config file.(Use flag '-config/--config_file')", file=sys.stderr)
    sys.exit(0)
  
  
  my_vcf = load_mongo_db(
                          scout_configs, 
                          config_file, 
                          family_type,
                          mongo_db=mongo_db, 
                          username=username, 
                          password=password,
                          variant_type=variant_type, 
                          port=port, 
                          host=host, 
                          verbose=verbose
                        )


if __name__ == '__main__':
    load_mongo()
