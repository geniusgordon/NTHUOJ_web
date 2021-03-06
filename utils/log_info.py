"""
The MIT License (MIT)

Copyright (c) 2014 NTHUOJ team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import logging
import os

loggers = dict()


def get_logger(name='NTHU OJ', log_dir='log'):
    """Return a logger with specified settings

    Args:
        name: the name of the module.
    Returns:
        the logger with specified format.
    """

    global loggers
    logger = None
    if name in loggers:
        logger = loggers[name]

    if not logger:
        logging_format = '[%(asctime)s] %(levelname)s: %(message)s'

        if not os.path.exists(log_dir):
            os.makedirs(log_dir, 0755)
        file_path = os.path.join(log_dir, 'nthuoj.log')

        logging.basicConfig(filename=file_path, filemode='w')

        # create logger
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # create formatter for console use
        formatter = logging.Formatter(logging_format)

        # create console handler and set level to info
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        # put back into loggers
        loggers[name] = logger

    return logger
