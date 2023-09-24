#!/usr/bin/env python3
'''
Primary entry point for web application.
'''
# DCheck
import dcheck.web.frontend


def main():
    dcheck.web.frontend.run(
            host='localhost',
            port=8080,
            debug=True)


if __name__ == '__main__':
    main()
