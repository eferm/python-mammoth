from . import documents, results, html_paths
from .html_generation import HtmlGenerator, satisfy_html_path


def convert_document_element_to_html(element, styles=None):
    if styles is None:
        styles = []
    html_generator = HtmlGenerator()
    converter = DocumentConverter(styles)
    converter.convert_element_to_html(element, html_generator)
    html_generator.end_all()
    return results.Result(html_generator.html_string(), converter.messages)


class DocumentConverter(object):
    def __init__(self, styles):
        self.messages = []
        self._styles = styles
        self._converters = {
            documents.Document: self._convert_document,
            documents.Paragraph: self._convert_paragraph,
            documents.Run: self._convert_run,
            documents.Text: self._convert_text,
        }


    def convert_element_to_html(self, element, html_generator):
        self._converters[type(element)](element, html_generator)


    def _convert_document(self, document, html_generator):
        self._convert_elements_to_html(document.children, html_generator)


    def _convert_paragraph(self, paragraph, html_generator):
        html_path = self._find_html_path_for_paragraph(paragraph)
        satisfy_html_path(html_generator, html_path)
        self._convert_elements_to_html(paragraph.children, html_generator)


    def _convert_run(self, run, html_generator):
        self._convert_elements_to_html(run.children, html_generator)


    def _convert_text(self, text, html_generator):
        html_generator.text(text.value)


    def _convert_elements_to_html(self, elements, html_generator):
        for element in elements:
            self.convert_element_to_html(element, html_generator)


    def _find_html_path_for_paragraph(self, paragraph):
        for style in self._styles:
            document_matcher = style.document_matcher
            if document_matcher.element_type == "paragraph" and (
                    document_matcher.style_name is None or
                    document_matcher.style_name == paragraph.style_name):
                return style.html_path
        
        if paragraph.style_name is not None:
            self.messages.append(results.warning("Unrecognised paragraph style: {0}".format(paragraph.style_name)))
        
        return html_paths.path([html_paths.element("p")])