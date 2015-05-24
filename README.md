Fake WHOIS Server
=================

This is a simple script to serve up fake WHOIS records. It is used to provide
WHOIS services in sandboxed training network environments.

Returned records can be scraped from live data sources to provide realistic data
or crafted to provide responses tailored to training scenarios. Environment DNS
servers must direct queries for WHOIS server hostnames to the server running
this script. The WHOIS server binds to TCP :::43, allowing it to handle both
IPv4 and IPv4 queries. The server currently handles only domain WHOIS queries
with experimental support for network WHOIS queries.

Files and Directories
---------------------

<!-- language:console -->
    /
    +-- etc/
    |   +-- fake-whois/
    |   |   +-- domains/
    |   |   |   +-- example.com
    |   |   |   +-- =example.com
    |   |   |   +-- nomatch.txt
    |   |   +-- networks/
    |   |       +-- 192.168
    |   +-- init.d/
    |       +-- fake-whois
    +-- usr/
    |   +-- local/
    |       +-- bin/
    |           +-- fake-whois.py
    +-- var/
        +-- log/
            +-- fake-whois.log

Notes
-----

The default whois client usually does two lookups for a domain query:

1. **Registry WHOIS:** Used to determine the registrar WHOIS server to query. This 
query is prefixed with an '=' which requests expanded results. Expanded results 
are necessary since they contain the "Whois Server:" line used to perform the 
registrar query. Registry queries with just the domain name may return multiple 
results. Domain queries can be prefixed with either "d " or "domain " after the 
'=' to limit results to the entry containing the "Domain Name:" line (the one 
we're looking for) 

2. **Registrar WHOIS:** Returns the WHOIS information for the domain. This query 
is not prefixed with an '='. Also, depending on the WHOIS server queried, the 
"d " or "domain " prefixes usually cause this lookup to fail.

In the domains folder, each domain needs two files:

1. =&lt;domain&gt; file: contains the registry WHOIS data
2. &lt;domain&gt; file: contains the registrar WHOIS data

Example (for the "example.com" domain):
<!-- language:console -->
    domains/
    +--- =example.com
    +--- example.com


