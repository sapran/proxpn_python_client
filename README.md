# proxpn_python_client

## Description

When executed, this script will present you a list of proXPN servers all around
the world. Once you select one, **an openvpn connection will be established**.

```
Note that if you are not a premium subscriber, you won't be able to use all of
these servers. ProXPN offers a great (and cheap!) service. I highly recommend
them :)
```

## Installation

  1. Download/clone this repository
  2. Execute `sudo ./install.sh` (see the '**Details**' section below to
     understand what this command does)


## Usage

For most users, you just need to execute the script without arguments:
```
proxpn.py
```
The first time you will be asked for your ProXPN credentials (see the
'**Details**' section below to understand where they are saved for later
invocations).

A list of servers all around the world will be presented for you to choose one.
Do so and leave the terminal window open.

Once you are done, simple enter "CTRL+c" on the terminal window and the tunnel
will be automatically closed and all the network configuration will be reset to
its original state.


## Details

A few things that are worth mentioning:

  * All this script does is:
    1. Download an up-to-date list of proXPN servers
    2. Make you choose one
    3. Call '*openvpn*' with the appropiate parameters

  * This means **you must have '*openvpn*' installed** before executing this
    script.
    In Archlinux that's `pacman -S openvpn`... and I imagine in other Linux
    distros it will be something similar.

  * When '*openvpn*' is called, '*sudo*' will be prepended... This means you
    don't need to execute this script as root: it will ask for your '*sudo*'
    password just before executing '*openvpn*' (which is the only binary which
    will run with elevated privileges).

      ```
      Note that is you use the '-g' option, elevated privileges will also be
      used to modify file '/etc/resolv.conf'. More on this later.
      ```

  * The '*install.sh*' script contained in this folder does the following things:
    1. Copy '*proxpn.py*' to '*/usr/local/bin*'
    2. Create folder '*~/.proxpn*'
    3. Copy '*proxpn.ovpn*' to '*~/.proxpn*'

  * The '*proxpn.ovpn*' file is a standard '*openvpn*' configuration file that
    is included in the ProXPN Windows/MAC installation packages.
    I guess it is perfectly OK for me to include it here as it just contains
    a public certificate and some '*openvpn*' configuration options.

  * The first time you execute this script it will download the list of VPN
    servers from ProXPN's web page. This list will then be saved into the
    '*~/.proxpn*' folder for future invocations. If you want to force a
    re-download of this file, use the '*-f*' argument when executing this
    script.

  * The first time you execute this script it will ask for you login credentials
    and save them into the '*~/.proxpn*' folder for future invocations. If you
    want to enter a new login/password, use the '*-r*' argument when executing
    this script.

      ```
      WARNING: The file where these credentials are saved is actually called
      '~/.proxpn/auth.conf' and is created with read/write permissions for you
      only. However they are stored in plain text... keep this in mind as you
      might not feel comfortable with it.
      ```

  * ProXPN offers both TCP and UDP openvpn tunnels. By default all of them are
    shown to you when executing this script. If you are just interested in a
    particular type, use '*-u*' (UDP) or '*-t*' (TCP) when executing this
    script.

      ```
      'udp' tunnels are faster. In fact, I can't think of any advantage of
      choosing 'tcp'!
      ```

  * Once the VPN is established, all your traffic (including DNS queries)
    will travel through the tunnel.
    
    In addition, DNS queries will still be made
    to the "original" DNS server configured in '*/etc/resolv.conf*'.
    This shouldn't be a problem 99% of the times, **except if your ISP DNS
    servers can only be accessed from within the ISP network address space**.
    When this happens, because your DNS queries seem to come from an external
    address (ie. the VPN exit point), they won't receive a response.
    One way to fix this is to "change" file '*/etc/resolv.conf*' to point to
    Google DNS servers (which accept queries from anywhere) and later, once the
    tunnel is closed, change it back to its original form. *This is exactly
    what the '-g' options does*.



