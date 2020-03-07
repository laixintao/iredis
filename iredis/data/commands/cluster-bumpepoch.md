Advances the cluster config epoch.

The `CLUSTER BUMPEPOCH` command triggers an increment to the cluster's config
epoch from the connected node. The epoch will be incremented if the node's
config epoch is zero, or if it is less than the cluster's greatest epoch.

**Note:** config epoch management is performed internally by the cluster, and
relies on obtaining a consensus of nodes. The `CLUSTER BUMPEPOCH` attempts to
increment the config epoch **WITHOUT** getting the consensus, so using it may
violate the "last failover wins" rule. Use it with caution.

@return

@simple-string-reply: `BUMPED` if the epoch was incremented, or `STILL` if the
node already has the greatest config epoch in the cluster.
