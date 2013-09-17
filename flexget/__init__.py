#!/usr/bin/python

from __future__ import unicode_literals, division, absolute_import
import os
import sys
import logging
from flexget import logger
from flexget.options import core_parser, exec_parser
from flexget import plugin
from flexget.manager import Manager

__version__ = '{git}'

log = logging.getLogger('main')


def main():
    """Main entry point for Command Line Interface"""

    logger.initialize()

    plugin.load_plugins(exec_parser)

    options = core_parser.parse_args()

    try:
        manager = Manager(options)
    except IOError as e:
        # failed to load config, TODO: why should it be handled here? So sys.exit isn't called in webui?
        log.critical(e)
        logger.flush_logging_to_console()
        sys.exit(1)

    log_level = logging.getLevelName(options.loglevel.upper())
    log_file = os.path.expanduser(manager.options.logfile)
    # If an absolute path is not specified, use the config directory.
    if not os.path.isabs(log_file):
        log_file = os.path.join(manager.config_base, log_file)
    logger.start(log_file, log_level)

    if getattr(options, 'func', False):
        # TODO: Fix this hacky crap
        if isinstance(options.func, list):
            options.func = getattr(plugin.get_plugin_by_name(options.func[0]).instance, options.func[1])
        options.func(options)
    elif options.subcommand == 'exec':
        if options.profile:
            try:
                import cProfile as profile
            except ImportError:
                import profile
            profile.runctx('manager.execute()', globals(), locals(), os.path.join(manager.config_base, 'flexget.profile'))
        else:
            manager.execute()
    manager.shutdown()
