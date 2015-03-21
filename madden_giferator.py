import time
import sys
import re

total_try_counter = 0
try_count = 0
scraped_url_whitelist = set()


def handle_total_try_count():
    global total_try_counter

    total_try_counter += 1

    if total_try_counter > 1000:
        raise Exception('Too many URLs! Please report this item to the admins.')


def accept_url(url_info, record_info, verdict, reasons):
    # Unlike Wget+Lua, URLs from get_urls() are subject to the options
    # provided to the program. So we need to allow the new URLs.
    if url_info['url'] in scraped_url_whitelist:
        return True

    return verdict


def handle_response(url_info, record_info, response_info):
    global try_count

    handle_total_try_count()

    if response_info['status_code'] == 400 and 'prod-api-madden.grw.io/' in url_info['url']:
        # Meme not found
        return wpull_hook.actions.FINISH

    elif response_info['status_code'] == 403:
        try_count += 1
        time.sleep(10)
        print('Sleeping....')
        sys.stdout.flush()

        if try_count > 10:
            print('Giving up')
            sys.stdout.flush()
            return wpull_hook.actions.STOP
        else:
            return wpull_hook.actions.RETRY
    else:
        try_count = 0

    return wpull_hook.actions.NORMAL


def handle_error(url_info, record_info, error_info):
    handle_total_try_count()

    return wpull_hook.actions.NORMAL


def get_urls(filename, url_info, document_info):
    new_urls = []

    if re.match(r'http://giferator\.easports\.com/gif/\d+', url_info['url']):
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()

        # Scrape the gif
        match = re.search(r'<meta itemprop="image" content="([^"]+)" />', text)

        if not match:
            raise Exception('Could not find the image URL.')

        new_url = match.group(1)
        new_urls.append({'url': new_url})
        scraped_url_whitelist.add(new_url)

        # Scrape the thumbnail
        match = re.search(r'<meta property="og:image" content="([^"]+)" />', text)

        if not match:
            raise Exception('Could not find the thumbnail image URL.')

        new_url = match.group(1)
        new_urls.append({'url': new_url})
        scraped_url_whitelist.add(new_url)

    return new_urls


# wpull_hook.callbacks.engine_run = engine_run
# wpull_hook.callbacks.resolve_dns = resolve_dns
wpull_hook.callbacks.accept_url = accept_url
# wpull_hook.callbacks.queued_url = queued_url
# wpull_hook.callbacks.dequeued_url = dequeued_url
# wpull_hook.callbacks.handle_pre_response = handle_pre_response
wpull_hook.callbacks.handle_response = handle_response
wpull_hook.callbacks.handle_error = handle_error
wpull_hook.callbacks.get_urls = get_urls
# wpull_hook.callbacks.wait_time = wait_time
# wpull_hook.callbacks.finish_statistics = finish_statistics
# wpull_hook.callbacks.exit_status = exit_status
