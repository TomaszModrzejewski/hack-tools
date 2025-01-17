"""Mozilla / Netscape cookie loading / saving.

Copyright 2002-2006 John J Lee <jjl@pobox.com>
Copyright 1997-1999 Gisle Aas (original libwww-perl code)

This code is free software; you can redistribute it and/or modify it
under the terms of the BSD or ZPL 2.1 licenses (see the file
COPYING.txt included with the distribution).

"""

import re, time, logging

from _clientcookie import reraise_unmasked_exceptions, FileCookieJar, Cookie, \
     MISSING_FILENAME_TEXT, LoadError
debug = logging.getLogger("ClientCookie").debug


class MozillaCookieJar(FileCookieJar):
    """

    WARNING: you may want to backup your browser's cookies file if you use
    this class to save cookies.  I *think* it works, but there have been
    bugs in the past!

    This class differs from CookieJar only in the format it uses to save and
    load cookies to and from a file.  This class uses the Mozilla/Netscape
    `cookies.txt' format.  lynx uses this file format, too.

    Don't expect cookies saved while the browser is running to be noticed by
    the browser (in fact, Mozilla on unix will overwrite your saved cookies if
    you change them on disk while it's running; on Windows, you probably can't
    save at all while the browser is running).

    Note that the Mozilla/Netscape format will downgrade RFC2965 cookies to
    Netscape cookies on saving.

    In particular, the cookie version and port number information is lost,
    together with information about whether or not Path, Port and Discard were
    specified by the Set-Cookie2 (or Set-Cookie) header, and whether or not the
    domain as set in the HTTP header started with a dot (yes, I'm aware some
    domains in Netscape files start with a dot and some don't -- trust me, you
    really don't want to know any more about this).

    Note that though Mozilla and Netscape use the same format, they use
    slightly different headers.  The class saves cookies using the Netscape
    header by default (Mozilla can cope with that).

    """
    magic_re = "#( Netscape)? HTTP Cookie File"
    header = """\
    # Netscape HTTP Cookie File
    # http://www.netscape.com/newsref/std/cookie_spec.html
    # This is a generated file!  Do not edit.

"""

    def _really_load(self, f, filename, ignore_discard, ignore_expires):
        now = time.time()

        magic = f.readline()
        if not re.search(self.magic_re, magic):
            f.close()
            raise LoadError(
                f"{filename} does not look like a Netscape format cookies file"
            )


        try:
            while 1:
                line = f.readline()
                if line == "": break

                # last field may be absent, so keep any trailing tab
                if line.endswith("\n"): line = line[:-1]

                # skip comments and blank lines XXX what is $ for?
                if (line.strip().startswith("#") or
                    line.strip().startswith("$") or
                    line.strip() == ""):
                    continue

                domain, domain_specified, path, secure, expires, name, value = \
                        line.split("\t", 6)
                secure = (secure == "TRUE")
                domain_specified = (domain_specified == "TRUE")
                if name == "":
                    name = value
                    value = None

                initial_dot = domain.startswith(".")
                if domain_specified != initial_dot:
                    raise LoadError("domain and domain specified flag don't "
                                    "match in %s: %s" % (filename, line))

                discard = False
                if expires == "":
                    expires = None
                    discard = True

                # assume path_specified is false
                c = Cookie(0, name, value,
                           None, False,
                           domain, domain_specified, initial_dot,
                           path, False,
                           secure,
                           expires,
                           discard,
                           None,
                           None,
                           {})
                if not ignore_discard and c.discard:
                    continue
                if not ignore_expires and c.is_expired(now):
                    continue
                self.set_cookie(c)

        except:
            reraise_unmasked_exceptions((IOError, LoadError))
            raise LoadError(f"invalid Netscape format file {filename}: {line}")

    def save(self, filename=None, ignore_discard=False, ignore_expires=False):
        if filename is None:
            if self.filename is not None: filename = self.filename
            else: raise ValueError(MISSING_FILENAME_TEXT)

        f = open(filename, "w")
        try:
            debug("Saving Netscape cookies.txt file")
            f.write(self.header)
            now = time.time()
            for cookie in self:
                if not ignore_discard and cookie.discard:
                    debug("   Not saving %s: marked for discard", cookie.name)
                    continue
                if not ignore_expires and cookie.is_expired(now):
                    debug("   Not saving %s: expired", cookie.name)
                    continue
                secure = "TRUE" if cookie.secure else "FALSE"
                initial_dot = "TRUE" if cookie.domain.startswith(".") else "FALSE"
                expires = str(cookie.expires) if cookie.expires is not None else ""
                if cookie.value is None:
                    # cookies.txt regards 'Set-Cookie: foo' as a cookie
                    # with no name, whereas cookielib regards it as a
                    # cookie with no value.
                    name = ""
                    value = cookie.name
                else:
                    name = cookie.name
                    value = cookie.value
                f.write(
                    "\t".join([cookie.domain, initial_dot, cookie.path,
                               secure, expires, name, value])+
                    "\n")
        finally:
            f.close()
