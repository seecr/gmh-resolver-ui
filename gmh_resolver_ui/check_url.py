import aiohttp
import asyncio
import random

import logging

logger = logging.getLogger(__name__)


def user_agent():
    return "nbn-urlresolver - harvester@dans.knaw.nl"

    return random.choice(
        [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            + "(KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 "
            + "Firefox/15.0.1",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            + "(KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36",
        ]
    )


def create_session():
    return aiohttp.ClientSession(
        # loop=asyncio.get_event_loop(),
        timeout=aiohttp.ClientTimeout(connect=30, sock_connect=15, sock_read=15),
        connector=aiohttp.TCPConnector(limit=1000, ttl_dns_cache=300),
    )


async def check_url(url):
    status = -1
    reason = ""
    async with create_session() as session:
        try:
            resp = await session.head(
                url, allow_redirects=True, headers={"User-agent": user_agent()}
            )
            async with resp:
                status = resp.status
                reason = resp.reason

                # HEAD requests are not always allowed
                if status == 405 or status == 404:
                    resp = await session.get(
                        url, allow_redirects=True, headers={"User-agent": user_agent()}
                    )
                    async with resp:
                        status = resp.status
                        reason = resp.reason
                return (status, reason)
        except Exception as e:
            reason = str(e)
        finally:
            logger.info(f"Checking {url} -> {status} {reason}")
    return (status, reason)
