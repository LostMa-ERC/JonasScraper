import concurrent.futures
import sys
import time
import urllib.request
from typing import Generator

from lxml import html


class Requester:
    @classmethod
    def retrieve_html(
        cls,
        url: str,
        timeout: int = 10,
        throttle: bool = False,
    ) -> html.HtmlElement:
        if throttle:
            time.sleep(1)
        # Retrieve a single page and parse its HTML into an lxml.html Element
        with urllib.request.urlopen(url, timeout=timeout) as conn:
            return html.fromstring(conn.read())

    @classmethod
    def pool_requests(
        cls,
        urls: list[str],
        max_workers: int = 3,
        timeout: int = 30,
        max_errors: int = None,
    ) -> Generator[
        tuple[str, html.HtmlElement],
        None,
        None,
    ]:
        if not max_errors:
            # If a very large data set, do not allow 1000 errors
            if len(urls) > 10_000:
                max_errors = 1_000
            # If a large data set, do not allow 10% error rate
            elif len(urls) > 100:
                max_errors = round(len(urls) * 0.1)
            # Otherwise, do not allow 10 errors
            else:
                max_errors = 10
        error_count = 0
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Start the load operations and mark each future with its URL
            future_url_index = {
                executor.submit(cls.retrieve_html, url, timeout, True): url
                for url in urls
            }

            for future in concurrent.futures.as_completed(future_url_index):
                url = future_url_index[future]
                try:
                    data = future.result()
                except TimeoutError:
                    error_count += 1
                    print(
                        "%r took too long to load. Error %s / %s"
                        % (url, error_count, max_errors)
                    )
                    if error_count > max_errors:
                        print("Too many errors. Exiting program...")
                        executor.shutdown(wait=True, cancel_futures=True)
                        sys.exit()
                else:
                    yield url, data
