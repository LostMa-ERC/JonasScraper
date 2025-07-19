import concurrent.futures
import logging
import time
import urllib.error
import urllib.request
from typing import Generator

from lxml import html

from jonas.progress import ProgressBar

logger = logging.getLogger(__name__)
logging.basicConfig(filename="jonas.log", filemode="a", level=logging.ERROR)


class Requester:
    def __init__(
        self,
        progress_bar: ProgressBar,
        timeout: int = 50,
        throttle: bool = False,
    ):
        self.timeout = timeout
        self.throttle = throttle
        self.p = progress_bar

    def remove_task(self, t):
        if self.p:
            self.p.remove_task(t)

    def retrieve_html(self, url: str) -> html.HtmlElement | None:
        if self.throttle:
            time.sleep(1)
        # Retrieve a single page and parse its HTML into an lxml.html Element
        if self.p:
            t = self.p.add_task(
                f"Scraping '{url}'",
                total=1,
                visible=True,
                start=True,
                progress_type="blue",
            )
        try:
            with urllib.request.urlopen(url, timeout=self.timeout) as conn:
                self.remove_task(t)
                return html.fromstring(conn.read())
        except Exception as e:
            msg = "\tURL: '%s'\tError: %s" % (url, e)
            logger.error(msg=msg)
            self.remove_task(t)

    def pool_requests(
        self,
        urls: list[str],
        max_workers: int = 5,
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
                    html_tree = future.result()
                except TimeoutError as e:
                    error_count += 1
                    print(
                        "%r took too long to load. Error %s / %s"
                        % (url, error_count, max_errors)
                    )
                    if error_count > max_errors:
                        print("Too many errors. Exiting program...")
                        executor.shutdown(wait=True, cancel_futures=True)
                        raise e
                except urllib.error.URLError as e:
                    if "The handshake operation timed out" in e.reason:
                        print("The internet connection wasn't good enough.")
                        executor.shutdown(wait=True, cancel_futures=True)
                    raise e

                if html_tree is not None:
                    yield url, html_tree
