import concurrent.futures
import urllib.request
from typing import Generator

from lxml import html


class Requester:
    @classmethod
    def retrieve_html(cls, url: str, timeout: int = 10) -> html.HtmlElement:
        # Retrieve a single page and parse its HTML into an lxml.html Element
        with urllib.request.urlopen(url, timeout=timeout) as conn:
            return html.fromstring(conn.read())

    @classmethod
    def pool_requests(
        cls, urls: list[str], max_workers: int = 5, timeout: int = 30
    ) -> Generator[
        tuple[str, html.HtmlElement],
        None,
        None,
    ]:
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Start the load operations and mark each future with its URL
            future_url_index = {
                executor.submit(cls.retrieve_html, url, timeout): url for url in urls
            }

            # Print the results when they're ready
            for future in concurrent.futures.as_completed(future_url_index):
                url = future_url_index[future]
                try:
                    data = future.result()
                except Exception as exc:
                    print("%r generated an exception: %s" % (url, exc))
                else:
                    yield url, data
