"""
How to initialize the two translation systems: Python and wxWidgets.
"""
import sys, os
import gettext
import wx
# Hack to get the locale directory
basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
localedir = os.path.join(basepath, "locale")
langid = wx.LANGUAGE_DEFAULT    # use OS default; or use LANGUAGE_JAPANESE, etc.
domain = "messages"             # the translation file is messages.mo
# Set locale for wxWidgets
mylocale = wx.Locale(langid)
mylocale.AddCatalogLookupPathPrefix(localedir)
mylocale.AddCatalog(domain)

# Set up Python's gettext
mytranslation = gettext.translation(domain, localedir,
    [mylocale.GetCanonicalName()], fallback = True)
mytranslation.install()

if __name__ == '__main__':
    # use Python's gettext
    print (_("Hello, World!"))

    # use wxWidgets' translation services
    print (wx.GetTranslation("Hello, World!"))

    # if getting unicode errors try something like this:
    #print wx.GetTranslation("Hello, World!").encode("utf-8")
        