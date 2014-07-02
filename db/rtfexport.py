import PyRTF as rtf
from questions import Question

def genRtfFile(questions):
    doc = rtf.Document()
    section = rtf.Section()
    doc.Sections.append(section)

    section.append("MULTIPLE CHOICE")
    section.append("")
    for question in questions:
        q, a, ca = question.getFormattedContent()
        section.append(q)
        for ans in a:
            section.append(ans)
        section.append(ca)

    return doc

def render(questions, filename):
    DR = rtf.Renderer()
    doc3 = genRtfFile(questions)
    DR.Write(doc3, file(filename, 'w'))
