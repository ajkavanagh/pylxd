#!/usr/bin/env python3


import logging
import random
import time

import pylxd

import busybox


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(processName)-10s)-(%(threadName)-10s) %(message)s',
)


def clean_containers(client):
    containers = client.containers.all()
    for c in containers:
        if c.name.startswith("parallel-container"):
            c.stop(wait=True)
            c.delete(wait=True)


def clean_profiles(client):
    profiles = client.profiles.all()
    for p in profiles:
        if p.name.startswith("parallel_profile"):
            p.delete(wait=True)


def build_instance(image_fingerprint, num, client=None):
    if client is None:
        client = pylxd.Client()
    logging.debug('Starting')
    profile_name = "parallel_profile_{}".format(num)
    instance_name = "parallel-container-{}".format(num)
    image = client.images.get(image_fingerprint)
    create_profile(client, profile_name)
    create_instance(client, instance_name, image.aliases[0], profile_name)
    time.sleep(random.random() + .5)
    delete_instance(client, instance_name)
    delete_profile(client, profile_name)
    logging.debug('Done')


def create_profile(client, profile_name):
    """Create a profile using the pylxd create function"""
    config = {'limits.memory': '1GB'}
    devices = {
        'root': {
            'type': 'disk',
            'path': '/',
        },
    }
    extensions = client.host_info.get('api_extensions', [])
    if 'storage' in extensions:
        pools = client.storage_pools.all()
        devices['root']['pool'] = pools[0].name
    client.profiles.create(profile_name, config=config, devices=devices)


def delete_profile(client, profile_name):
    client.profiles.get(profile_name).delete(wait=True)


def delete_instance(client, container_name):
    container = client.containers.get(container_name)
    container.stop(wait=True)
    container.delete(wait=True)


def create_instance(client, name, image_ref, profile_name):
    """Create an instance with a name, image and profile"""
    config = {
        'name': name,
        'profiles': [profile_name],
        'source': {
            'type': 'image',
            'alias': image_ref['name'],
        },
    }
    container = client.containers.create(config, wait=True)
    container.start(wait=True)
    return container


def create_image(client, alias):
    """Create an image in lxd."""

    # check it's not already there
    try:
        image = client.images.get_by_alias(alias)
        return image
    except pylxd.exceptions.LXDAPIException as e:
        if e.response.status_code != 404:
            raise
        # create the image in lxd
        path, fingerprint = busybox.create_busybox_image()
        with open(path, 'rb') as f:
            image = client.images.create(f.read(), public=True)

        # and create the alias
        image.add_alias(alias, "The busybox alias")
        return image


def delete_image(self, fingerprint):
    """Delete an image in lxd."""
    try:
        self.lxd.images[fingerprint].delete()
    except pylxd.exceptions.LXDAPIException as e:
        if e.response.status_code == 404:
            return
        raise
