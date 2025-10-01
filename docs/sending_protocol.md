# SENDING PROTOCOL DRAFT - DO NOT DELETE

# Data sent from a node to another node must not overwrite any nodes' data. To do this:
Create a "sending" directory in every pi
When sending data from a node to another node, make sure to always targer "sending" directory
Keep sending directory empty at all times, move data where it needs to go then clear.