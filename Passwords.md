## Generate Password for PSK (source: [wiki.strongswan.org](https://wiki.strongswan.org/projects/strongswan/wiki/SecurityRecommendations))

`dd if=/dev/urandom count=1 bs=32 2>/dev/null | base64`
