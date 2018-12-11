from pylxd import managers
from pylxd.exceptions import LXDAPIException
from pylxd.models import _model as model

class Cluster(model.Model):
    """An LXD Container.

    This class is not intended to be used directly, but rather to be used
    via `Client.containers.create`.
    """

    server_name = model.Attribute()
    enabled = model.Attribute()
    member_config = model.Attribute()

    _members = model.Manager()

    def __init__(self, *args, **kwargs):
        super(Cluster, self).__init__(*args, **kwargs)

        self._members = managers.ClusterMemberManager(self.client, self)

    @property
    def api(self):
        return self.client.api.cluster

    @classmethod
    def get(cls, client, *args):
        """Get cluster details"""
        print(args)
        response = client.api.cluster.get()
        print(response.json())

        container = cls(client, **response.json()['metadata'])
        return container


class ClusterMember(model.Model):
    """A LXD certificate."""

    server_name = model.Attribute(readonly=True)
    url = model.Attribute(readonly=True)
    database = model.Attribute(readonly=True)
    state = model.Attribute(readonly=True)
    server_name = model.Attribute(readonly=True)
    status = model.Attribute(readonly=True)
    message = model.Attribute(readonly=True)

    cluster = model.Parent()

    @property
    def api(self):
        return self.client.api.cluster.members[self.server_name]

    @classmethod
    def get(cls, client, name):
        """Get a cluster member by name."""
        response = client.api.cluster.members[name].get()

        return cls(client, **response.json()['metadata'])

    @classmethod
    def all(cls, client, *args):
        """Get all cluster members."""
        print(args)
        response = client.api.cluster.members.get()
        print(response.json())

        nodes = []
        for node in response.json()['metadata']:
            name = node.split('/')[-1]
            nodes.append(cls(client, server_name=name))
        return nodes

