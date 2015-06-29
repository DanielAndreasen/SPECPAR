#!/usr/bin/python


from ConfigParser import SafeConfigParser


def read_config_file_param(section, parameter, fileconfig):
    """
    Read a parameter from a config file: 'config.file'
    that should be in the current directory
    """
    parser = SafeConfigParser()
    parser.read(fileconfig)
    return parser.get(section, parameter)


def read_config_install(section, parameter):
    return read_config_file_param(section, parameter, 'config_specpar.file')


def read_config_param(section, parameter):
    """
    Read a parameter from the config file: 'config.file'
    that should be in the current directory
    """
    return read_config_file_param(section, parameter, 'config.file')


# TODO: This last part is not really necessary...
def main():
    print "Nothing to do here"


if __name__ == "__main__":
    main()
