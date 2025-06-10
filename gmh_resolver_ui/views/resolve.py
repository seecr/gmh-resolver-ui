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

from swl.responses import SuccessResponse
from swl.utils import render_template

from gmh_resolver_ui.check_url import check_url

import re

NBN_PATTERN = re.compile(
    "^[uU][rR][nN]:[nN][bB][nN]:[nN][lL](:([a-zA-Z]{2}))(:\\d{2})?-.+"
)


async def resolve_identifier(request, templates, pool, **_):
    response = SuccessResponse()

    async with request.form() as form:
        identifier = form["identifier"]
        show_locations = "show_locations" in form

        if NBN_PATTERN.match(identifier) is None:
            return response.hydrate(
                "placeholder-results",
                data=render_template(
                    templates,
                    request,
                    "invalid.j2",
                    context=dict(msg="Given nbn-identifier is not valid"),
                ),
            )

        results = []

        unfragmented_identifier = identifier.split("#")[0]
        with pool.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT L.location_url, IL.isFailover FROM identifier I JOIN identifier_location IL ON I.identifier_id = IL.identifier_id JOIN location L ON L.location_id = IL.location_id WHERE I.identifier_value=%(identifier)s ORDER BY IL.isFailover, IL.last_modified DESC",
                    dict(identifier=unfragmented_identifier),
                )
                for hit in cursor:
                    results.append(dict(zip(["location", "priority"], hit)))

        if len(results) == 0:
            return response.hydrate(
                "placeholder-results",
                data=render_template(
                    templates,
                    request,
                    "invalid.j2",
                    context=dict(
                        msg=f"Redirection failed: No location(s) available for this identifier: {identifier}"
                    ),
                ),
            )

        for result in results:
            result["location"] = result["location"].split("#")[0]

        if show_locations is True:
            return response.hydrate(
                "placeholder-results",
                data=render_template(
                    templates, request, "results.j2", context=dict(results=results)
                ),
            )

        unresolved_locations = []
        for result in sorted(results, key=lambda result: result["priority"]):
            url = result["location"]
            status, reason = await check_url(url)
            if status == 200:
                return response.redirect(url)
            else:
                unresolved_locations.append(url)

        return response.hydrate(
            "placeholder-results",
            data=render_template(
                templates,
                request,
                "invalid.j2",
                context=dict(
                    msg=f"Redirection failed: Unresolvable locations(s): "
                    + ", ".join(unresolved_locations)
                ),
            ),
        )


__actions__ = [dict(method=resolve_identifier, authenticated=False)]
