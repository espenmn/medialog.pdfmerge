# -*- coding: utf-8 -*-

# from medialog.pdfmerge import _
from Products.Five.browser import BrowserView
from zope.interface import Interface
from plone import api
import fitz  # PyMuPDF
import pdfkit
import os
from tempfile import NamedTemporaryFile
from bs4 import BeautifulSoup

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IMergePdf(Interface):
    """ Marker Interface for IMergePdf"""


class MergePdf(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('merge_pdf.pt')
        
    def get_files(self, folder):
        """ Recursively get all PDF and HTML files in the folder and subfolders. """
        files = []
        for item in folder.listFolderContents():
            if item.portal_type == "Folder":
                # Skip folders that are not supposed to be included
                if not item.exclude_from_nav:
                    files.append(item)
                    files.extend(self.get_files(item))  # Recurse into subfolders
            elif item.portal_type == "File":
                filename = item.file.filename.lower()
                if filename.endswith(".pdf") or filename.endswith(".html"):
                    files.append(item)
            elif item.portal_type == "Document":
                files.append(item)
            
        return files
        
    def convert_html_to_pdf(self, html_data):
        """ Convert HTML content to a temporary PDF file and return the filename. """
        temp_pdf = NamedTemporaryFile(delete=False, suffix='.pdf')
        pdfkit.from_string(html_data, temp_pdf.name)
        return temp_pdf.name

    def merge_pdfs(self, pdf_files):
        """ Merge a list of PDF files into a single PDF. """
        merged_pdf = fitz.open()  # Create an empty PDF
        for pdf_file in pdf_files:
            pdf_doc = fitz.open(pdf_file)
            merged_pdf.insert_pdf(pdf_doc)
            pdf_doc.close()
        # Save merged output to a temporary file
        temp_output = NamedTemporaryFile(delete=False, suffix='.pdf')
        merged_pdf.save(temp_output.name)
        merged_pdf.close()
        return temp_output.name

    def extract_content(self, document):
        """ Render the document view and extract the #content-core part. """
        # Render the whole view
        portal = api.portal.get()
        path = '/'.join(document.getPhysicalPath())
        html = portal.restrictedTraverse(path)()
        
        # Parse the HTML to extract #content-core
        soup = BeautifulSoup(html, 'html.parser')
        # content= soup.select_one('#content-core')
        content = soup.select_one('html')
        
        if content:
            # Add custom CSS for top margin
            style_tag = soup.new_tag('style')
            style_tag.string = """
                body {
                    padding-top: 60px;
                    margin-top: 60px;  /* Adjust this value if needed */
                }
            """
            # Insert the style tag at the beginning of content
            content.insert(0, style_tag)
            viewlets = ["edit-bar",
                        "portal-top",
                        "portal-mainnavigation",
                        "portal-column-one",
                        "portal-column-two",
                        "portal-footer-wrapper",
                        "viewlet-above-content-body",
                        "form-groups-settings",
                        "viewlet-below-content-title", 
                        "viewlet-below-content", 
                        "viewlet-below-content-body", 
                        "form-groups-categorization"
                        ]
            
            for viewlet in viewlets:
            # Remove the #viewlets we dont want 
                viewlet_to_remove = content.find(id=viewlet)
                if viewlet_to_remove:
                    viewlet_to_remove.decompose()   
            return str(content)
        return ""

    def __call__(self):
        # Get the folder where this view is called
        folder = self.context

        # Step 1: Collect all PDF, HTML, and Document files in folder and subfolders
        files = self.get_files(folder)
        
        # Step 2: Prepare files for merging
        pdf_files = []
        temp_files = []  # To store temporary files for cleanup
        for file_item in files:
            if file_item.portal_type == "File":
                filename = file_item.file.filename.lower()
                if filename.endswith(".html"):
                    html_data = file_item.file.data.decode("utf-8")
                    temp_pdf_path = self.convert_html_to_pdf(html_data)
                    pdf_files.append(temp_pdf_path)
                    temp_files.append(temp_pdf_path)  # Track for cleanup
                elif filename.endswith(".pdf"):
                    pdf_path = NamedTemporaryFile(delete=False, suffix=".pdf")
                    pdf_path.write(file_item.file.data)
                    pdf_path.close()
                    pdf_files.append(pdf_path.name)
                    temp_files.append(pdf_path.name)  # Track for cleanup
            elif file_item.portal_type in ["Document", "Folder"]:
                # Extract #content-core from Document
                content_html = self.extract_content(file_item)
                if content_html:
                    temp_pdf_path = self.convert_html_to_pdf(content_html)
                    pdf_files.append(temp_pdf_path)
                    temp_files.append(temp_pdf_path)  # Track for cleanup

        # Step 3: Merge PDFs
        merged_pdf_path = self.merge_pdfs(pdf_files)

        # Step 4: Cleanup temporary files
        for temp_file in temp_files:
            os.remove(temp_file)

        # Step 5: Return the merged PDF as a download response
        with open(merged_pdf_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
        os.remove(merged_pdf_path)  # Cleanup merged file

        self.request.response.setHeader("Content-Type", "application/pdf")
        self.request.response.setHeader("Content-Disposition", 'attachment; filename="merged_output.pdf"')
        self.request.response.setHeader("Content-Length", len(pdf_data))
        
        return pdf_data