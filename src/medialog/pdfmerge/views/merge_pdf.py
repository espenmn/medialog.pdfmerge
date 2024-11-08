# -*- coding: utf-8 -*-

# from medialog.pdfmerge import _
from Products.Five.browser import BrowserView
from zope.interface import Interface

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IMergePdf(Interface):
    """ Marker Interface for IMergePdf"""


class MergePdf(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('merge_pdf.pt')

    def __call__(self):
        # Implement your own actions:
        return self.index()
