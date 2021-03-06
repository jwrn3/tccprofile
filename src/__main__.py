"""Main"""
try:
    from tcclib import common
    from tcclib import menumaker
    from tcclib import payloadobj
    from tcclib import plist
    from tcclib import tccdbscan
    from tcclib import templates
    from tcclib import vers
except ImportError:
    from .tcclib import common
    from .tcclib import menumaker
    from .tcclib import payloadobj
    from .tcclib import plist
    from .tcclib import tccdbscan
    from .tcclib import templates
    from .tcclib import vers


def main():
    _services = None
    profile = None
    args = menumaker.arg_parser()

    # Version compatibility check - makes sure python
    # version is the version this has been tested against.
    vers.compatibility_check()

    # List services first if it is present.
    if args.list_services:
        tccdbscan.list_services()

    # Construct the overriding values for the profile if they're present.
    _kwargs = dict()

    if args.payload_desc:
        _kwargs['PayloadDescription'] = args.payload_desc[0]

    if args.payload_disp_name:
        _kwargs['PayloadDisplayName'] = args.payload_disp_name[0]

    if args.payload_identifier:
        _kwargs['PayloadIdentifier'] = args.payload_identifier[0]

    if args.payload_org:
        _kwargs['PayloadOrganization'] = args.payload_org[0]

    # When the 'profile_removable' argument is supplied,
    # invert the result because of how Apple has defined the
    # behaviour. Profile key 'PayloadRemovalDisallowed' = True
    # means the profile cannot be removed by user.
    if args.profile_removable:
        _kwargs['PayloadRemovalDisallowed'] = not args.profile_removable

    if args.scan:
        if args.services:
            _services = tccdbscan.user_managed(args.services)
        else:
            _services = tccdbscan.user_managed()

    if args.template:
        _available_templates = templates.available()
        _services = dict()

        # Iterate over each template and all services+apps to merge into one profile
        # if more than one template is supplied
        for _tmplate in args.template:
            if _tmplate in _available_templates:
                try:
                    _f = _available_templates[_tmplate]
                    _tmplate_services = templates.services(_f)

                    for _svc, _apps in _tmplate_services.items():
                        for _a in _apps:
                            try:
                                _services[_svc].append(_a)
                            except KeyError:
                                _services[_svc] = list()
                                _services[_svc].append(_a)
                except KeyError:
                    pass

    # No services == no profile.
    if not _services:
        common.errmsg('No matching services found. List available services with \'--list-services\' argument. Exiting.')

    if _kwargs:
        _payload_content = payloadobj.PayloadContentDict(_services, **_kwargs).payload_content
        profile = payloadobj.ProfileDict(_payload_content, **_kwargs).payload
    else:
        _payload_content = payloadobj.PayloadContentDict(_services).payload_content
        profile = payloadobj.ProfileDict(_payload_content).payload

    if profile:
        if not args.output:
            plist.writePlist(values=profile, stdout=True)
        elif args.output:
            plist.writePlist(values=profile, f=args.output[0])


if __name__ == '__main__':
    main()
