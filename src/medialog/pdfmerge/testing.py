# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE
    PloneSandboxLayer,
)
from plone.testing import z2

import medialog.pdfmerge


class MedialogPdfmergeLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=medialog.pdfmerge)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'medialog.pdfmerge:default')


MEDIALOG_PDFMERGE_FIXTURE = MedialogPdfmergeLayer()


MEDIALOG_PDFMERGE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MEDIALOG_PDFMERGE_FIXTURE,),
    name='MedialogPdfmergeLayer:IntegrationTesting',
)


MEDIALOG_PDFMERGE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MEDIALOG_PDFMERGE_FIXTURE,),
    name='MedialogPdfmergeLayer:FunctionalTesting',
)


MEDIALOG_PDFMERGE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MEDIALOG_PDFMERGE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='MedialogPdfmergeLayer:AcceptanceTesting',
)
