"""Load / save to libwww-perl (LWP) format files.

Actually, the format is slightly extended from that used by LWP's
(libwww-perl's) HTTP::Cookies, to avoid losing some RFC 2965 information
not recorded by LWP.

It uses the version string "2.0", though really there isn't an LWP Cookies
2.0 format.  This indicates that there is extra information in here
(domain_dot and port_spec) while still being compatible with libwww-perl,
I hope.

Copyright 2002-2006 John J Lee <jjl@pobox.com>
Copyright 1997-1999 Gisle Aas (original libwww-perl code)

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD or ZPL 2.1 licenses (see the file
COPYING.txt included with the distribution).

"""

import time, re, logging

from _clientcookie import reraise_unmasked_exceptions, FileCookieJar, Cookie, \
     MISSING_FILENAME_TEXT, LoadError
from _headersutil import join_header_words, split_header_words
from _util import iso2time, time2isoz

debug = logging.getLogger("mechanize").debug


def lwp_cookie_str(cookie):
    """Return string representation of Cookie in an the LWP cookie file format.

    Actually, the format is extended a bit -- see module docstring.

    """
    h = [(cookie.name, cookie.value),
         ("path", cookie.path),
         ("domain", cookie.domain)]
    if cookie.port is not None: h.append(("port", cookie.port))
    if cookie.path_specified: h.append(("path_spec", None))
    if cookie.port_specified: h.append(("port_spec", None))
    if cookie.domain_initial_dot: h.append(("domain_dot", None))
    if cookie.secure: h.append(("secure", None))
    if cookie.expires: h.append(("expires",
                               time2isoz(float(cookie.expires))))
    if cookie.discard: h.append(("discard", None))
    if cookie.comment: h.append(("comment", cookie.comment))
    if cookie.comment_url: h.append(("commenturl", cookie.comment_url))
    if cookie.rfc2109: h.append(("rfc2109", None))

    keys = cookie.nonstandard_attr_keys()
    keys.sort()
    h.extend((k, str(cookie.get_nonstandard_attr(k))) for k in keys)
    h.append(("version", str(cookie.version)))

    return join_header_words([h])

class LWPCookieJar(FileCookieJar):
    """
    The LWPCookieJar saves a sequence of"Set-Cookie3" lines.
    "Set-Cookie3" is the format used by the libwww-perl libary, not known
    to be compatible with any browser, but which is easy to read and
    doesn't lose information about RFC 2965 cookies.

    Additional methods

    as_lwp_str(ignore_discard=True, ignore_expired=True)

    """

    magic_re = r"^\#LWP-Cookies-(\d+\.\d+)"

    def as_lwp_str(self, ignore_discard=True, ignore_expires=True):
        """Return cookies as a string of "\n"-separated "Set-Cookie3" headers.

        ignore_discard and ignore_expires: see docstring for FileCookieJar.save

        """
        now = time.time()
        r = []
        for cookie in self:
            if not ignore_discard and cookie.discard:
                debug("   Not saving %s: marked for discard", cookie.name)
                continue
            if not ignore_expires and cookie.is_expired(now):
                debug("   Not saving %s: expired", cookie.name)
                continue
            r.append(f"Set-Cookie3: {lwp_cookie_str(cookie)}")
        return "\n".join(r+[""])

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        f = open(filename, "w")
        try:
            debug("Saving LWP cookies file")
            # There really isn't an LWP Cookies 2.0 format, but this indicates
            # that there is extra information in here (domain_dot and
            # port_spec) while still being compatible with libwww-perl, I hope.
            f.write("#LWP-Cookies-2.0\n")
            f.write(self.as_lwp_str(ignore_discard, ignore_expires))
        finally:
            f.close()

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        magic = f.readline()
        if not re.search(self.magic_re, magic):
            msg = f"{filename} does not seem to contain cookies"
            raise LoadError(msg)

        now = time.time()

        header = "Set-Cookie3:"
        boolean_attrs = ("port_spec", "path_spec", "domain_dot",
                         "secure", "discard", "rfc2109")
        value_attrs = ("version",
                       "port", "path", "domain",
                       "expires",
                       "comment", "commenturl")

        try:
            while 1:
                line = f.readline()
                if line == "": break
                if not line.startswith(header):
                    continue
                line = line[len(header):].strip()

                for data in split_header_words([line]):
                    name, value = data[0]
                    rest = {}
                    standard = {k: False for k in boolean_attrs}
                    for k, v in data[1:]:
                        lc = k.lower() if k is not None else None
                        # don't lose case distinction for unknown fields
                        if (lc in value_attrs) or (lc in boolean_attrs):
                            k = lc
                        if k in boolean_attrs:
                            if v is None: v = True
                            standard[k] = v
                        elif k in value_attrs:
                            standard[k] = v
                        else:
                            rest[k] = v

                    h = standard.get
                    expires = h("expires")
                    discard = h("discard")
                    if expires is not None:
                        expires = iso2time(expires)
                    if expires is None:
                        discard = True
                    domain = h("domain")
                    domain_specified = domain.startswith(".")
                    c = Cookie(h("version"), name, value,
                               h("port"), h("port_spec"),
                               domain, domain_specified, h("domain_dot"),
                               h("path"), h("path_spec"),
                               h("secure"),
                               expires,
                               discard,
                               h("comment"),
                               h("commenturl"),
                               rest,
                               h("rfc2109"),
                               )
                    if not ignore_discard and c.discard:
                        continue
                    if not ignore_expires and c.is_expired(now):
                        continue
                    self.set_cookie(c)
        except:
            reraise_unmasked_exceptions((IOError,))
            raise LoadError(f"invalid Set-Cookie3 format file {filename}")

