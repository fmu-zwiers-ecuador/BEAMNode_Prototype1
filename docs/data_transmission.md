# DATA TRANSMISSION THROUGH BATMAN #

## Show all neighbors in mesh:
    sudo batctl n -- This command will show all neighbors in the mesh, their MAC addresses, and the time since their last connection

## To check connection to a node:
    sudo batctl ping [mac_address] -- This command will begin continuously transmitting bytes back and forth to the selected host

## To transfer a file to a node:
    sudo scp [source_path] [destination_user]@[destination_ip]:[destination_path] -- This command will copy the specified file to the destination host at the specified locaiton. It is important that the destination's BATMAN IP is used instead of their MAC address.
