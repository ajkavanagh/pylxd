#!/usr/bin/env python3


import logging
import threading

import pylxd

import helpers as h


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)


def run_thread_tests():
    client = pylxd.Client()
    image = h.create_image(client, "parallel_test")
    h.clean_containers(client)
    h.clean_profiles(client)

    threads = []
    for i in range(100):
        t = threading.Thread(
            target=h.build_instance, args=(image.fingerprint, i, client))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    # now delete the image
    image.delete(wait=True)


if __name__ == "__main__":
    run_thread_tests()
