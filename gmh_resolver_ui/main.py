## begin license ##
#
# Gemeenschappelijke Metadata Harvester (GMH) Resolver UI
# resolves nbn to locations
#
# Copyright (C) 2025 Koninklijke Bibliotheek (KB) https://www.kb.nl
# Copyright (C) 2025 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "GMH-Resolver-UI"
#
# "GMH-Resolver-UI" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "GMH-Resolver-UI" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "GMH-Resolver-UI"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import argparse
import asyncio
import pathlib

from swl import configure_logging, uvicorn_main

from gmh_resolver_ui.config import Config
from gmh_resolver_ui.server import create_app


def main_app():
    parser = argparse.ArgumentParser(
        prog="GMH Resolver", description="FrontEnd for GMH Resolver"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to, default %(default)s",
    )
    parser.add_argument(
        "--port", type=int, default="9000", help="Port to bind to, default %(default)s"
    )
    parser.add_argument(
        "--data-path",
        required=True,
        type=pathlib.Path,
        help="Path to data directory which will contain config directory and store data",
    )
    parser.add_argument(
        "--development",
        action="store_true",
        help="Run in development mode.",
        default=False,
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Log level, default %(default)s",
    )
    args = parser.parse_args()

    configure_logging(args.log_level)

    arg_vars = vars(args)

    config = Config(args.data_path, development=arg_vars.pop("development", False))

    asyncio.run(
        uvicorn_main(
            create_app=create_app,
            config=config,
            deproxy_ips=config.deproxy_ips,
            **arg_vars,
        )
    )
