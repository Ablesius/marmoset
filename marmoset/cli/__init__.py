from argparse import ArgumentParser

def parse(config):
    desc        = 'Manage libvirt and pxe configs'
    parser      = ArgumentParser(description=desc)
    commands    = parser.add_subparsers(title='commands')


    def print_config(*args):
        with open('/dev/stdout', 'w') as stdout:
            config.write(stdout)


    config_cmd = commands.add_parser(
        'config',
        help='show config directives used'
    )
    config_cmd.set_defaults(func = print_config)

    if config['Modules'].getboolean('Webserver'):
        from . import webserver_parser
        webserver_parser.add_to(
            commands,
            'webserver',
            help='start a webserver for API usage',
            aliases=['server']
        )

    if config['Modules'].getboolean('PXE'):
        from . import pxe_parser
        pxe_parser.add_to(
            commands,
            'pxe',
            help='manage client specific PXE configs'
        )

    if config['Modules'].getboolean('VM'):
        from . import virt_parser
        virt_parser.add_to(
            commands,
            'vm',
            help='manage libvirt domains and their associated resources'
        )

    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        print('No subcommand given')
        parser.print_help()

