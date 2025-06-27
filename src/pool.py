import concurrent.futures
import sys
import time
import urllib.request
import urllib.error
from typing import Generator
from rich.progress import Progress

from lxml import html


class Requester:
    def __init__(
        self,
        timeout: int = 50,
        throttle: bool = False,
        progress_bar: Progress = None,
    ):
        self.timeout = timeout
        self.throttle = throttle
        self.p = progress_bar

    def remove_task(self, url, t):
        self.p.update(t, description=f"Scraping '{url}'", completed=1, visible=False)
        self.p.remove_task(t)

    def retrieve_html(self, url: str) -> html.HtmlElement:
        if self.throttle:
            time.sleep(1)
        # Retrieve a single page and parse its HTML into an lxml.html Element
        if self.p:
            t = self.p.add_task(f"Scraping '{url}'", total=1, visible=True, start=True)
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as conn:
                self.remove_task(url=url, t=t)
                return html.fromstring(conn.read())
        except Exception as e:
            self.remove_task(url=url, t=t)
            raise e

    def pool_requests(
        self,
        urls: list[str],
        max_workers: int = 10,
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
            # Start the scraping operations and mark each future with its URL
            future_url_index = {
                executor.submit(self.retrieve_html, url): url for url in urls
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
                except urllib.error.URLError as e:
                    if "The handshake operation timed out" in e.reason:
                        print("The internet connection wasn't good enough.\n%s" % (e))
                        executor.shutdown(wait=True, cancel_futures=True)
                        sys.exit()
                    else:
                        raise e
                else:
                    yield url, data
