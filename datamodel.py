#!/usr/bin/env python3

from boofuzz import Request, Block, Static, String

datamodel = (
    Block(name="Request", children=(
        Static(name="Request-head",
               default_value="GET /index.html HTTP/1.1\r\n Host: "),
        String(name="Host", default_value="goiena.eus", max_len=1),
        Static(name="Request-tail", default_value="\r\n\r\n"))
    )
)

request = Request(name="HTTP-Request", children=datamodel)
