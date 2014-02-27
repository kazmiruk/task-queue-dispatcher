from optparse import OptionParser


def _get_options():
    parser = OptionParser()
    parser.add_option("-p", "--processor", dest="processor",
                      help="class processor for demon", metavar="CLASS")
    parser.add_option("-q", "--queue-name", dest="queue_name",
                      help="queue name for current instance")
    parser.add_option("-c", "--chunk", dest="chunk",
                      help="chunk of selected queue[default = 1]", default=1)
    parser.add_option("-l", "--logfile", dest="logfile",
                      help="file name for logging")

    return parser.parse_args()


def validate_options():
    options = _get_options()[0]

    if options.processor and options.queue_name:
        return options
    else:
        raise KeyError('You should provide at least processor and queue names')

OPTIONS = validate_options()
