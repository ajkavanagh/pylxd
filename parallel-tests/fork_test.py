#!/usr/bin/env python3


import logging
import multiprocessing

import pylxd

import helpers as h


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(processName)-10s) %(message)s',
)


def run_processes_tests():
    client = pylxd.Client()
    image = h.create_image(client, "parallel_test")
    h.clean_containers(client)
    h.clean_profiles(client)

    processes = []
    for i in range(50):
        p = multiprocessing.Process(
            target=h.build_instance, args=(image.fingerprint, i))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()
    # now delete the image
    image.delete(wait=True)


if __name__ == "__main__":
    run_processes_tests()
