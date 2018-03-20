import sys
import glyxtoolms

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    #print "This is the main routine."
    #print "It should do something interesting."
    # run GUI
    app = glyxtoolms.gui.runGUI()

    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.

if __name__ == "__main__":
    main()
