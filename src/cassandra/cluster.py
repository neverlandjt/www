from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')

cluster = Cluster(['172.31.35.107'], auth_provider=auth_provider)
