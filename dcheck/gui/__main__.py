#!/usr/bin/env python3
'''
Primary entry point for local (gui) application.
'''
# DCheck
import dcheck.gui.window
import dcheck.core.bootstrap


def main():
    '''
    Create a Tk container and launch the main window.
    '''
    # Application setup
    dcheck.core.bootstrap.start()
    application = dcheck.gui.window.RootWindow()

    # Application startup
    application.mainloop()


if __name__ == "__main__":
    # Increase default verbosity
    main()
